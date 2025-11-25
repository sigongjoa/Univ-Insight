"""
실제 SNUCrawler를 사용하여 서울대 데이터를 수집하고 저장하는 파이프라인

실행: python run_real_pipeline.py
"""

import sys
import json
from datetime import datetime
import uuid

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Domain
from src.domain.models import (
    Base, University, College, Department, Professor, Laboratory,
    LabMember, ResearchPaper, PaperAnalysis, UniversityTier, LabMemberRole
)

# Services
from src.services.snu_crawler import SNUCrawler
from src.core.logging import get_logger, setup_logging

# Logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_database():
    """데이터베이스 초기화"""
    logger.info("\n" + "="*60)
    logger.info("🗄️ 데이터베이스 초기화 중...")
    logger.info("="*60)

    Base.metadata.create_all(bind=engine)
    logger.info("✅ 데이터베이스 준비 완료\n")


def insert_snu_data(snu_data: dict, session):
    """SNUCrawler에서 받은 데이터를 DB에 저장"""
    logger.info("="*60)
    logger.info("📊 서울대 데이터 저장 중...")
    logger.info("="*60)

    # 1️⃣ University 저장
    uni_data = snu_data["university"]
    university = University(
        id=uni_data["id"],
        name=uni_data["name"],
        name_ko=uni_data["name_ko"],
        location=uni_data["location"],
        ranking=uni_data["ranking"],
        tier=UniversityTier.TOP if uni_data["tier"] == "TOP" else UniversityTier.HIGH,
        url=uni_data["url"],
        description=uni_data["description"],
        established_year=uni_data["established_year"]
    )
    session.add(university)
    session.flush()
    logger.info(f"✅ 대학 저장: {university.name_ko}")

    # 2️⃣ Colleges 저장
    college_count = 0
    for college_data in snu_data.get("colleges", []):
        college = College(
            id=college_data["college"]["id"],
            university_id=university.id,
            name=college_data["college"]["name"],
            name_ko=college_data["college"]["name_ko"],
            description=college_data["college"].get("description"),
            established_year=college_data["college"].get("established_year")
        )
        session.add(college)
        session.flush()
        college_count += 1
        logger.info(f"   ✅ 단과대학: {college.name_ko}")

        # 3️⃣ Departments 저장
        for dept_data in college_data.get("departments", []):
            department = Department(
                id=dept_data["department"]["id"],
                college_id=college.id,
                name=dept_data["department"]["name"],
                name_ko=dept_data["department"]["name_ko"],
                description=dept_data["department"].get("description"),
                website=dept_data["department"].get("website"),
                faculty_count=len(dept_data.get("professors", []))
            )
            session.add(department)
            session.flush()
            logger.info(f"      ✅ 전공: {department.name_ko}")

            # 4️⃣ Professors 저장
            for prof_data in dept_data.get("professors", []):
                professor = Professor(
                    id=prof_data["professor"]["id"],
                    department_id=department.id,
                    name=prof_data["professor"]["name"],
                    name_ko=prof_data["professor"]["name_ko"],
                    title=prof_data["professor"].get("title"),
                    email=prof_data["professor"].get("email"),
                    research_interests=prof_data["professor"].get("research_interests", []),
                    h_index=prof_data["professor"].get("h_index"),
                    publications_count=prof_data["professor"].get("publications_count"),
                    profile_url=prof_data["professor"].get("profile_url")
                )
                session.add(professor)
                session.flush()
                logger.info(f"         ✅ 교수: {professor.name_ko} ({professor.title})")

                # 5️⃣ Laboratories 저장
                for lab_data in prof_data.get("laboratories", []):
                    # lab_data가 {"laboratory": {...}} 또는 {...} 구조일 수 있음
                    lab_info = lab_data.get("laboratory", lab_data)

                    laboratory = Laboratory(
                        id=lab_info["id"],
                        professor_id=professor.id,
                        department_id=department.id,
                        name=lab_info["name"],
                        name_ko=lab_info["name_ko"],
                        research_areas=lab_info.get("research_areas", []),
                        description=lab_info.get("description"),
                        member_count=lab_info.get("member_count"),
                        website=lab_info.get("website"),
                        current_projects=lab_info.get("current_projects", [])
                    )
                    session.add(laboratory)
                    session.flush()
                    logger.info(f"            ✅ 연구실: {laboratory.name_ko} ({laboratory.member_count}명)")

    session.commit()
    logger.info(f"\n✅ 데이터 저장 완료!")
    logger.info(f"   - 대학: 1개")
    logger.info(f"   - 단과대학: {college_count}개")


def create_sample_papers(session):
    """샘플 논문 생성"""
    logger.info("\n" + "="*60)
    logger.info("📄 샘플 논문 생성 중...")
    logger.info("="*60)

    papers_data = [
        {
            "title": "Korean Language Model Optimization using Transformer Architecture",
            "abstract": "이 논문은 한국어 처리에 최적화된 트랜스포머 아키텍처를 제시합니다. 기존의 영어 중심 모델과 달리 한국어의 특성을 반영한 임베딩 메커니즘과 어휘 최적화를 통해 더욱 효율적인 언어 모델을 개발했습니다.",
            "authors": ["Lee, S.H.", "Kim, J.W.", "Park, M.S."],
            "venue": "NeurIPS 2024",
            "year": 2024,
            "keywords": ["Deep Learning", "NLP", "Transformer", "Korean Language"]
        },
        {
            "title": "Adversarial Robustness in Computer Vision: Defense Mechanisms",
            "abstract": "컴퓨터 비전 시스템의 적대적 공격에 대한 강건성을 높이기 위한 새로운 방어 메커니즘을 제안합니다. 다양한 공격 패턴에 대응할 수 있는 다층 방어 구조를 설계하고, 실제 응용에서의 효과를 검증합니다.",
            "authors": ["Choi, J.W.", "Lee, J.M."],
            "venue": "ICCV 2024",
            "year": 2024,
            "keywords": ["Computer Vision", "Adversarial Examples", "Robustness"]
        },
        {
            "title": "Real-time Object Detection for Autonomous Vehicles",
            "abstract": "자율주행 자동차를 위한 실시간 객체 탐지 시스템을 개발합니다. 고속 처리가 필요한 자동차 환경에서 정확도와 속도의 균형을 맞추기 위해 경량 신경망을 설계하고 최적화합니다.",
            "authors": ["Kim, Y.H.", "Park, J.H."],
            "venue": "CVPR 2024",
            "year": 2024,
            "keywords": ["Computer Vision", "Object Detection", "Autonomous Driving"]
        },
        {
            "title": "Distributed Systems Optimization for Cloud Computing",
            "abstract": "클라우드 컴퓨팅 환경에서의 분산 시스템 최적화에 관한 연구입니다. 마이크로서비스 아키텍처와 컨테이너 오케스트레이션의 성능을 향상시키기 위한 새로운 알고리즘과 전략을 제시합니다.",
            "authors": ["Park, M.S.", "Lee, S.J."],
            "venue": "OSDI 2024",
            "year": 2024,
            "keywords": ["Distributed Systems", "Cloud Computing", "Microservices"]
        },
        {
            "title": "Compiler Optimization for Next-Generation Programming Languages",
            "abstract": "차세대 프로그래밍 언어를 위한 컴파일러 최적화 기법을 제안합니다. 정적 분석과 동적 최적화를 결합하여 코드 생성 효율을 높이고, 실행 속도를 개선합니다.",
            "authors": ["Jung, H.K.", "Kim, S.H."],
            "venue": "PLDI 2024",
            "year": 2024,
            "keywords": ["Compiler Design", "Programming Languages", "Optimization"]
        }
    ]

    papers = []
    for i, paper_data in enumerate(papers_data, 1):
        paper = ResearchPaper(
            id=f"paper-snu-{i:03d}",
            title=paper_data["title"],
            abstract=paper_data["abstract"],
            full_text=paper_data["abstract"],
            authors=paper_data["authors"],
            publication_year=paper_data["year"],
            publication_date=datetime(2024, 6, 15).date(),
            venue=paper_data["venue"],
            venue_type="conference",
            keywords=paper_data["keywords"],
            url=f"https://snu.ac.kr/research/papers/{i}"
        )
        session.add(paper)
        papers.append(paper)
        logger.info(f"✅ [{i}] {paper.title[:50]}...")

    session.commit()
    logger.info(f"\n✅ {len(papers)}개 논문 저장 완료!\n")
    return papers


def analyze_papers_with_mock_llm(papers, session):
    """논문 분석 (Mock LLM)"""
    logger.info("="*60)
    logger.info("🤖 논문 분석 중... (Mock LLM)")
    logger.info("="*60)

    analyses_templates = [
        {
            "easy_summary": "한국어를 잘 이해하는 인공지능을 만드는 연구입니다. 기존 기술보다 더 효율적이고 정확합니다.",
            "job_roles": ["AI 엔지니어", "NLP 전문가", "머신러닝 엔지니어"],
            "companies": ["네이버", "카카오", "삼성 AI", "구글"],
            "salary_range": "70,000,000 - 100,000,000원"
        },
        {
            "easy_summary": "인공지능 모델을 공격으로부터 보호하는 방법을 연구합니다. 자율주행, 의료 AI 등 안전이 중요한 분야에서 필수적입니다.",
            "job_roles": ["AI 보안 전문가", "사이버 보안 엔지니어", "AI 연구원"],
            "companies": ["삼성 보안", "LG AI", "NCSoft", "마이크로소프트"],
            "salary_range": "75,000,000 - 110,000,000원"
        },
        {
            "easy_summary": "자동차가 스스로 주변 물체를 인식하는 기술을 개발합니다. 안전하고 정확한 인식이 매우 중요합니다.",
            "job_roles": ["자율주행 AI 엔지니어", "컴퓨터 비전 전문가", "로봇공학자"],
            "companies": ["현대/기아 자동차", "테슬라", "웨이모", "배두"],
            "salary_range": "80,000,000 - 120,000,000원"
        },
        {
            "easy_summary": "많은 컴퓨터를 효율적으로 관리하는 방법을 연구합니다. 클라우드 서비스 제공업체에서 매우 필요로 합니다.",
            "job_roles": ["클라우드 아키텍트", "분산 시스템 엔지니어", "DevOps 엔지니어"],
            "companies": ["아마존 AWS", "마이크로소프트 Azure", "구글 클라우드", "카카오 클라우드"],
            "salary_range": "75,000,000 - 115,000,000원"
        },
        {
            "easy_summary": "프로그래밍을 더 빠르고 효율적으로 하기 위한 컴파일러 기술을 개발합니다. 많은 회사에서 이 기술을 필요로 합니다.",
            "job_roles": ["컴파일러 엔지니어", "언어 설계자", "시스템 프로그래머"],
            "companies": ["Apple", "Google", "Meta", "JetBrains"],
            "salary_range": "80,000,000 - 130,000,000원"
        }
    ]

    for i, paper in enumerate(papers):
        template = analyses_templates[i % len(analyses_templates)]

        analysis = PaperAnalysis(
            id=str(uuid.uuid4()),
            paper_id=paper.id,
            easy_summary=template["easy_summary"],
            technical_summary=f"이 연구는 {paper.venue}에 발표된 고급 기술 연구입니다.",
            core_technologies=paper.keywords[:3],
            required_skills=["Python", "딥러닝 프레임워크", "수학"],
            math_concepts=["선형대수", "확률론", "최적화"],
            application_fields=paper.keywords,
            job_roles=template["job_roles"],
            recommended_companies=template["companies"],
            salary_range=template["salary_range"],
            recommended_subjects=["고등수학", "프로그래밍", "확률통계"],
            action_items={
                "subjects": ["Advanced Math", "Python Programming", "Deep Learning"],
                "timeline": "6개월 학습 권장"
            },
            learning_path=[
                "Python 기초",
                "선형대수 및 확률론",
                "머신러닝 기초",
                "심화 학습"
            ]
        )
        session.add(analysis)

        logger.info(f"✅ [{i+1}] {paper.title[:40]}... 분석 완료")
        logger.info(f"   - 요약: {template['easy_summary'][:50]}...")
        logger.info(f"   - 직업: {', '.join(template['job_roles'])}")
        logger.info(f"   - 연봉: {template['salary_range']}")

    session.commit()
    logger.info(f"\n✅ {len(papers)}개 논문 분석 저장 완료!\n")


def run_pipeline():
    """전체 파이프라인 실행"""
    logger.info("\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "  🚀 UNIV-INSIGHT REAL PIPELINE (Seoul National Univ)".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("╚" + "="*58 + "╝")

    try:
        # 1️⃣ 데이터베이스 초기화
        init_database()

        # 2️⃣ SNUCrawler로 서울대 데이터 수집
        logger.info("\n" + "="*60)
        logger.info("🌐 SNUCrawler로 서울대 데이터 수집 중...")
        logger.info("="*60 + "\n")

        crawler = SNUCrawler()
        snu_data = crawler.crawl_snu_complete()

        # 디버깅: 수집된 데이터 출력
        logger.info(f"\n📊 수집된 데이터:")
        logger.info(f"   - 대학: {snu_data['university']['name_ko']}")
        logger.info(f"   - 단과대학: {len(snu_data['colleges'])}개")

        total_colleges = len(snu_data['colleges'])
        total_departments = 0
        total_professors = 0
        total_labs = 0

        for college in snu_data['colleges']:
            total_departments += len(college.get('departments', []))
            for dept in college.get('departments', []):
                total_professors += len(dept.get('professors', []))
                for prof in dept.get('professors', []):
                    total_labs += len(prof.get('laboratories', []))

        logger.info(f"   - 전공: {total_departments}개")
        logger.info(f"   - 교수: {total_professors}명")
        logger.info(f"   - 연구실: {total_labs}개\n")

        # 3️⃣ 데이터베이스에 저장
        session = SessionLocal()

        # 기존 데이터 삭제 (테스트용)
        session.query(PaperAnalysis).delete()
        session.query(ResearchPaper).delete()
        session.query(LabMember).delete()
        session.query(Laboratory).delete()
        session.query(Professor).delete()
        session.query(Department).delete()
        session.query(College).delete()
        session.query(University).delete()
        session.commit()

        insert_snu_data(snu_data, session)

        # 4️⃣ 샘플 논문 생성
        papers = create_sample_papers(session)

        # 5️⃣ 논문 분석
        analyze_papers_with_mock_llm(papers, session)

        # ✅ 최종 결과
        logger.info("\n" + "="*60)
        logger.info("🎉 실제 파이프라인 완료!")
        logger.info("="*60)

        logger.info("\n📊 최종 요약:")
        logger.info("   ✅ 서울대 계층 구조 저장: 완료")
        logger.info(f"      - 대학: 1개")
        logger.info(f"      - 단과대학: {total_colleges}개")
        logger.info(f"      - 전공: {total_departments}개")
        logger.info(f"      - 교수: {total_professors}명")
        logger.info(f"      - 연구실: {total_labs}개")
        logger.info("")
        logger.info("   ✅ 샘플 논문: 5개 저장")
        logger.info("   ✅ 논문 분석: 5개 완료")
        logger.info("")
        logger.info("🎯 데이터베이스: univ_insight.db")
        logger.info("🎯 준비 완료: API와 Notion/Kakao 연동 가능!\n")

        session.close()
        return True

    except Exception as e:
        logger.error(f"\n❌ 파이프라인 오류: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
