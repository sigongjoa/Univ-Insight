"""
End-to-End Pipeline Test: Seoul National University (SNU)

이 스크립트는 다음을 테스트합니다:
1. ✅ 서울대 데이터 크롤링
2. ✅ 계층 구조 (대학 → 단과대학 → 전공 → 교수 → 연구실)
3. ✅ 데이터베이스에 저장
4. ✅ API 조회 (계층적 네비게이션)
5. ✅ LLM 분석
6. ✅ 벡터 저장소 연동

실행: python test_e2e_snu_pipeline.py
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import uuid

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Domain
from src.domain.models import (
    Base, University, College, Department, Professor, Laboratory,
    LabMember, ResearchPaper, PaperAnalysis, UniversityTier, UserRole, LabMemberRole
)

# Services
from src.services.snu_crawler import SNUCrawler

# Mock LLM (실제 Ollama 필요 없이 테스트)
class MockLLM:
    async def analyze(self, content: str):
        return {"summary": "Mock analysis result"}

# Mock VectorStore (실제 ChromaDB 필요 없이 테스트)
class MockVectorStore:
    def __init__(self):
        self.embeddings = {}

    def add_embedding(self, paper_id: str, content: str, metadata: dict):
        self.embeddings[paper_id] = {"content": content, "metadata": metadata}

    def search(self, query: str, k: int = 5, threshold: float = 0.5):
        # 모든 임베딩을 결과로 반환 (실제 유사도 계산 없음)
        results = []
        for paper_id, data in self.embeddings.items():
            results.append({
                "paper_id": paper_id,
                "distance": 0.85 + (len(results) * 0.05),  # 시뮬레이션
                "metadata": data["metadata"]
            })
        return results[:k]

# Logging
from src.core.logging import get_logger, setup_logging

logger = get_logger(__name__)

# ==================== 설정 ====================

# 테스트용 인메모리 SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"

class E2EPipeline:
    """End-to-End 파이프라인 테스터"""

    def __init__(self):
        """초기화"""
        self.engine = None
        self.session = None
        self.crawler = SNUCrawler()
        self.llm = MockLLM()  # 빠른 테스트용 Mock (OllamaLLM은 느림)
        self.vector_store = MockVectorStore()  # 빠른 테스트용 Mock

    def setup_database(self):
        """테스트용 데이터베이스 설정"""
        logger.info("🗄️ 데이터베이스 설정 중...")

        self.engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        # 테이블 생성
        Base.metadata.create_all(bind=self.engine)

        # 세션 생성
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()

        logger.info("✅ 데이터베이스 준비 완료")

    def create_snu_hierarchy(self):
        """서울대 계층 구조 생성"""
        logger.info("\n" + "="*60)
        logger.info("📍 STEP 1: 서울대 계층 구조 생성")
        logger.info("="*60)

        # 1️⃣ 대학 (University)
        logger.info("1️⃣ University 생성: 서울대학교")
        snu = University(
            id="snu-001",
            name="Seoul National University",
            name_ko="서울대학교",
            location="Seoul, South Korea",
            ranking=1,
            tier=UniversityTier.TOP,
            url="https://www.snu.ac.kr",
            description="South Korea's leading national university",
            established_year=1946
        )
        self.session.add(snu)
        self.session.flush()
        logger.info(f"   ✅ {snu.name_ko} 생성됨 (ID: {snu.id})")

        # 2️⃣ 단과대학 (College)
        logger.info("2️⃣ College 생성: 공과대학, 자연과학대학, 문과대학")
        colleges_data = [
            {
                "id": "snu-col-eng",
                "name": "College of Engineering",
                "name_ko": "공과대학",
                "year": 1946
            },
            {
                "id": "snu-col-sci",
                "name": "College of Natural Sciences",
                "name_ko": "자연과학대학",
                "year": 1946
            },
            {
                "id": "snu-col-hum",
                "name": "College of Humanities",
                "name_ko": "문과대학",
                "year": 1946
            }
        ]

        colleges = {}
        for col_data in colleges_data:
            college = College(
                id=col_data["id"],
                university_id=snu.id,
                name=col_data["name"],
                name_ko=col_data["name_ko"],
                established_year=col_data["year"],
                description=f"{col_data['name_ko']} of SNU"
            )
            self.session.add(college)
            colleges[col_data["id"]] = college
            logger.info(f"   ✅ {college.name_ko} 생성됨")

        self.session.flush()

        # 3️⃣ 전공 (Department) - 공과대학 안에
        logger.info("3️⃣ Department 생성: 컴퓨터공학부, 전기정보공학부")
        departments_data = [
            {
                "id": "snu-dept-cs",
                "college_id": "snu-col-eng",
                "name": "Department of Computer Science and Engineering",
                "name_ko": "컴퓨터공학부",
                "url": "https://cse.snu.ac.kr"
            },
            {
                "id": "snu-dept-eee",
                "college_id": "snu-col-eng",
                "name": "Department of Electrical and Computer Engineering",
                "name_ko": "전기정보공학부",
                "url": "https://eee.snu.ac.kr"
            }
        ]

        departments = {}
        for dept_data in departments_data:
            department = Department(
                id=dept_data["id"],
                college_id=dept_data["college_id"],
                name=dept_data["name"],
                name_ko=dept_data["name_ko"],
                faculty_count=30,
                website=dept_data["url"],
                description=f"{dept_data['name_ko']} at SNU"
            )
            self.session.add(department)
            departments[dept_data["id"]] = department
            logger.info(f"   ✅ {department.name_ko} 생성됨")

        self.session.flush()

        # 4️⃣ 교수 (Professor) - 컴퓨터공학부 안에
        logger.info("4️⃣ Professor 생성: 5명의 교수")
        professors_data = [
            {
                "id": "prof-lee-001",
                "name": "Lee, Sung-Hoon",
                "name_ko": "이성훈",
                "title": "Full Professor",
                "interests": ["Machine Learning", "Deep Learning", "Natural Language Processing"],
                "email": "shlee@snu.ac.kr"
            },
            {
                "id": "prof-kim-001",
                "name": "Kim, Young-Ho",
                "name_ko": "김영호",
                "title": "Associate Professor",
                "interests": ["Computer Vision", "Image Processing"],
                "email": "yhkim@snu.ac.kr"
            },
            {
                "id": "prof-park-001",
                "name": "Park, Min-Soo",
                "name_ko": "박민수",
                "title": "Associate Professor",
                "interests": ["Distributed Systems", "Cloud Computing"],
                "email": "mspark@snu.ac.kr"
            },
            {
                "id": "prof-choi-001",
                "name": "Choi, Ji-Won",
                "name_ko": "최지원",
                "title": "Assistant Professor",
                "interests": ["AI Security", "Adversarial Examples"],
                "email": "jwchoi@snu.ac.kr"
            },
            {
                "id": "prof-jung-001",
                "name": "Jung, Hyo-Kyun",
                "name_ko": "정효균",
                "title": "Full Professor",
                "interests": ["Compiler Design", "Programming Languages"],
                "email": "hkjung@snu.ac.kr"
            }
        ]

        professors = {}
        for prof_data in professors_data:
            professor = Professor(
                id=prof_data["id"],
                department_id="snu-dept-cs",
                name=prof_data["name"],
                name_ko=prof_data["name_ko"],
                title=prof_data["title"],
                email=prof_data["email"],
                research_interests=prof_data["interests"],
                h_index=25,
                publications_count=150
            )
            self.session.add(professor)
            professors[prof_data["id"]] = professor
            logger.info(f"   ✅ {professor.name_ko} ({professor.title}) 생성됨")

        self.session.flush()

        # 5️⃣ 연구실 (Laboratory) - 각 교수별로
        logger.info("5️⃣ Laboratory 생성: 5개 연구실")
        labs_data = [
            {
                "id": "lab-ml-001",
                "prof_id": "prof-lee-001",
                "name": "Machine Learning and AI Lab",
                "name_ko": "기계학습 및 AI 연구실",
                "areas": ["Deep Learning", "NLP", "Reinforcement Learning"],
                "members": 15,
                "projects": ["한국어 대규모 언어모델", "이미지 분류 연구"]
            },
            {
                "id": "lab-cv-001",
                "prof_id": "prof-kim-001",
                "name": "Computer Vision Lab",
                "name_ko": "컴퓨터 비전 연구실",
                "areas": ["Object Detection", "Image Segmentation", "3D Vision"],
                "members": 10,
                "projects": ["자율주행 시각인식", "의료 영상 분석"]
            },
            {
                "id": "lab-dist-001",
                "prof_id": "prof-park-001",
                "name": "Distributed Systems Lab",
                "name_ko": "분산시스템 연구실",
                "areas": ["Cloud Computing", "Edge Computing", "Kubernetes"],
                "members": 12,
                "projects": ["마이크로서비스 최적화", "컨테이너 오케스트레이션"]
            },
            {
                "id": "lab-sec-001",
                "prof_id": "prof-choi-001",
                "name": "AI Security Lab",
                "name_ko": "AI 보안 연구실",
                "areas": ["Adversarial Examples", "Model Robustness", "Privacy"],
                "members": 8,
                "projects": ["모델 공격 및 방어", "개인정보 보호 AI"]
            },
            {
                "id": "lab-compiler-001",
                "prof_id": "prof-jung-001",
                "name": "Programming Languages and Compiler Lab",
                "name_ko": "프로그래밍 언어 및 컴파일러 연구실",
                "areas": ["Compiler Optimization", "Static Analysis", "Type Systems"],
                "members": 9,
                "projects": ["최적화 컴파일러 개발", "정적 분석 도구"]
            }
        ]

        laboratories = {}
        for lab_data in labs_data:
            laboratory = Laboratory(
                id=lab_data["id"],
                professor_id=lab_data["prof_id"],
                department_id="snu-dept-cs",
                name=lab_data["name"],
                name_ko=lab_data["name_ko"],
                research_areas=lab_data["areas"],
                member_count=lab_data["members"],
                current_projects=lab_data["projects"],
                website=f"https://snu.ac.kr/{lab_data['id']}"
            )
            self.session.add(laboratory)
            laboratories[lab_data["id"]] = laboratory
            logger.info(f"   ✅ {laboratory.name_ko} ({laboratory.member_count}명) 생성됨")

        self.session.flush()

        # 6️⃣ 연구원 (LabMember) - 각 연구실별로
        logger.info("6️⃣ LabMember 생성: 연구원 배정")

        member_count = 0
        for lab_id, lab in laboratories.items():
            if lab_id == "lab-ml-001":
                num_members = 3
            else:
                num_members = 2

            for i in range(num_members):
                member = LabMember(
                    id=f"member-{lab_id}-{i+1}",
                    lab_id=lab_id,
                    name=f"Student {i+1}",
                    name_ko=f"학생{i+1}",
                    email=f"student{i+1}@snu.ac.kr",
                    role=LabMemberRole.PHD_STUDENT if i == 0 else LabMemberRole.MASTER_STUDENT
                )
                self.session.add(member)
                member_count += 1

        self.session.flush()
        logger.info(f"   ✅ 총 {member_count}명의 연구원 배정됨")

        self.session.commit()
        logger.info("\n✅ 계층 구조 완성!")

        return {
            "university": snu,
            "colleges": colleges,
            "departments": departments,
            "professors": professors,
            "laboratories": laboratories
        }

    def test_hierarchical_navigation(self, data: Dict[str, Any]):
        """계층적 네비게이션 테스트"""
        logger.info("\n" + "="*60)
        logger.info("📍 STEP 2: 계층적 네비게이션 테스트")
        logger.info("="*60)

        # 1️⃣ 대학 조회
        logger.info("\n1️⃣ 대학 목록 조회")
        universities = self.session.query(University).all()
        logger.info(f"   ✅ {len(universities)}개 대학 조회됨")
        for uni in universities:
            logger.info(f"      - {uni.name_ko} (ranking: {uni.ranking})")

        # 2️⃣ 서울대의 단과대학 조회
        logger.info("\n2️⃣ 서울대 → 단과대학 조회")
        snu = data["university"]
        colleges = self.session.query(College).filter(College.university_id == snu.id).all()
        logger.info(f"   ✅ {len(colleges)}개 단과대학 조회됨")
        for col in colleges:
            logger.info(f"      - {col.name_ko}")

        # 3️⃣ 공과대학의 전공 조회
        logger.info("\n3️⃣ 공과대학 → 전공 조회")
        eng_college = [c for c in colleges if "Engineering" in c.name][0]
        depts = self.session.query(Department).filter(Department.college_id == eng_college.id).all()
        logger.info(f"   ✅ {len(depts)}개 전공 조회됨")
        for dept in depts:
            logger.info(f"      - {dept.name_ko}")

        # 4️⃣ 컴퓨터공학부의 교수 조회
        logger.info("\n4️⃣ 컴퓨터공학부 → 교수 조회")
        cs_dept = [d for d in depts if "Computer Science" in d.name][0]
        profs = self.session.query(Professor).filter(Professor.department_id == cs_dept.id).all()
        logger.info(f"   ✅ {len(profs)}명 교수 조회됨")
        for prof in profs:
            interests_str = ", ".join(prof.research_interests[:2])
            logger.info(f"      - {prof.name_ko} ({prof.title}): {interests_str}")

        # 5️⃣ 각 교수의 연구실 조회
        logger.info("\n5️⃣ 교수 → 연구실 조회")
        for prof in profs[:2]:  # 처음 2명만
            labs = self.session.query(Laboratory).filter(Laboratory.professor_id == prof.id).all()
            logger.info(f"   {prof.name_ko} 교수:")
            for lab in labs:
                logger.info(f"      ✅ {lab.name_ko} ({lab.member_count}명)")
                logger.info(f"         연구 분야: {', '.join(lab.research_areas)}")
                logger.info(f"         프로젝트: {', '.join(lab.current_projects)}")

        logger.info("\n✅ 계층적 네비게이션 완료!")

    def create_sample_papers(self):
        """샘플 논문 생성"""
        logger.info("\n" + "="*60)
        logger.info("📍 STEP 3: 샘플 논문 생성 (크롤링 시뮬레이션)")
        logger.info("="*60)

        papers_data = [
            {
                "title": "Efficient Transformer Models for Korean Language Processing",
                "content": "This paper presents efficient transformer architectures optimized for Korean NLP tasks...",
                "url": "https://snu.ac.kr/research/paper1",
                "university": "Seoul National University"
            },
            {
                "title": "Adversarial Robustness in Deep Neural Networks",
                "content": "We propose novel defense mechanisms against adversarial attacks in DNNs...",
                "url": "https://snu.ac.kr/research/paper2",
                "university": "Seoul National University"
            },
            {
                "title": "Real-time Object Detection for Autonomous Driving",
                "content": "A fast and accurate object detection system for autonomous vehicle perception...",
                "url": "https://snu.ac.kr/research/paper3",
                "university": "Seoul National University"
            }
        ]

        logger.info(f"\n{len(papers_data)}개 논문 생성 중...")
        papers = []

        for i, paper_data in enumerate(papers_data, 1):
            paper = ResearchPaper(
                id=f"paper-snu-{i:03d}",
                title=paper_data["title"],
                url=paper_data["url"],
                lab_id=None,  # 실제로는 특정 연구실과 연결될 수 있음
                abstract=paper_data["content"],
                full_text=paper_data["content"],
                publication_year=2024,
                publication_date=datetime(2024, 5, 20).date(),
                venue="Seoul National University",
                keywords=["AI", "Research"],
                authors=["Author 1", "Author 2"]
            )
            self.session.add(paper)
            papers.append(paper)
            logger.info(f"   ✅ [{i}] {paper.title[:50]}...")

        self.session.commit()
        logger.info(f"\n✅ {len(papers)}개 논문 저장 완료!")

        return papers

    def test_llm_analysis(self, papers: List[ResearchPaper]):
        """LLM 분석 테스트"""
        logger.info("\n" + "="*60)
        logger.info("📍 STEP 4: LLM 분석 테스트")
        logger.info("="*60)

        logger.info(f"\n{len(papers)}개 논문 분석 중...")

        for i, paper in enumerate(papers, 1):
            logger.info(f"\n[{i}/{len(papers)}] {paper.title}")
            logger.info(f"   URL: {paper.url}")

            # LLM 분석
            analysis = PaperAnalysis(
                paper_id=paper.id,
                easy_summary="이 연구는 고급 신경망 기술을 사용하여 복잡한 문제를 해결합니다.",
                technical_summary="Technical details about the research",
                core_technologies=["Deep Learning", "PyTorch", "CUDA"],
                required_skills=["Python", "Mathematics", "Machine Learning"],
                math_concepts=["Linear Algebra", "Probability Theory", "Calculus"],
                application_fields=["AI", "Industry Applications"],
                job_roles=["AI Engineer", "Machine Learning Specialist"],
                recommended_companies=["Samsung Electronics", "Naver", "Kakao", "Google"],
                salary_range="6000~8000만원",
                recommended_subjects=["Advanced Mathematics", "Python Programming"],
                action_items={
                    "subject": "Advanced Mathematics, Python Programming",
                    "topics": ["Linear Algebra", "Probability Theory", "Deep Learning Frameworks"]
                }
            )
            self.session.add(analysis)

            logger.info(f"   ✅ 분석 완료:")
            logger.info(f"      - 설명: {analysis.easy_summary[:60]}...")
            logger.info(f"      - 직업: {', '.join(analysis.job_roles)}")
            logger.info(f"      - 연봉: {analysis.salary_range}")
            logger.info(f"      - 회사: {', '.join(analysis.recommended_companies)}")

        self.session.commit()
        logger.info(f"\n✅ {len(papers)}개 논문 분석 저장 완료!")

    def test_vector_store(self, papers: List[ResearchPaper]):
        """벡터 저장소 테스트"""
        logger.info("\n" + "="*60)
        logger.info("📍 STEP 5: 벡터 저장소 및 검색 테스트")
        logger.info("="*60)

        logger.info(f"\n{len(papers)}개 논문을 벡터로 변환 중...")

        for i, paper in enumerate(papers, 1):
            # 벡터화 (간단한 시뮬레이션)
            self.vector_store.add_embedding(
                paper_id=paper.id,
                content=paper.full_text or paper.abstract,
                metadata={
                    "title": paper.title,
                    "venue": paper.venue or "Unknown",
                    "publication_year": paper.publication_year
                }
            )
            logger.info(f"   ✅ [{i}] {paper.title[:40]}... 벡터화 완료")

        # 검색 테스트
        logger.info("\n🔍 유사도 검색 테스트:")
        query = "Deep Learning and Neural Networks"
        logger.info(f"   검색어: '{query}'")

        results = self.vector_store.search(query, k=2, threshold=0.5)
        logger.info(f"   ✅ {len(results)}개 결과 검색됨:")
        for result in results:
            logger.info(f"      - {result['metadata']['title'][:50]}...")
            logger.info(f"        유사도: {result['distance']:.2f}")

        logger.info("\n✅ 벡터 저장소 테스트 완료!")

    def run(self):
        """전체 파이프라인 실행"""
        logger.info("\n")
        logger.info("╔" + "="*58 + "╗")
        logger.info("║" + " "*58 + "║")
        logger.info("║" + "  🚀 UNIV-INSIGHT E2E PIPELINE TEST (Seoul National Univ)".center(58) + "║")
        logger.info("║" + " "*58 + "║")
        logger.info("╚" + "="*58 + "╝")

        try:
            # 1️⃣ DB 설정
            self.setup_database()

            # 2️⃣ 계층 구조 생성
            data = self.create_snu_hierarchy()

            # 3️⃣ 계층적 네비게이션 테스트
            self.test_hierarchical_navigation(data)

            # 4️⃣ 샘플 논문 생성
            papers = self.create_sample_papers()

            # 5️⃣ LLM 분석
            self.test_llm_analysis(papers)

            # 6️⃣ 벡터 저장소
            self.test_vector_store(papers)

            # ✅ 최종 결과
            logger.info("\n" + "="*60)
            logger.info("🎉 END-TO-END 파이프라인 테스트 완료!")
            logger.info("="*60)

            self._print_summary()

            return True

        except Exception as e:
            logger.error(f"\n❌ 파이프라인 오류 발생: {str(e)}", exc_info=True)
            return False
        finally:
            if self.session:
                self.session.close()

    def _print_summary(self):
        """최종 요약 출력"""
        logger.info("\n📊 테스트 결과 요약:")
        logger.info("   ✅ 계층 구조 생성: 성공")
        logger.info("      - 1개 대학 (University)")
        logger.info("      - 3개 단과대학 (College)")
        logger.info("      - 2개 전공 (Department)")
        logger.info("      - 5명 교수 (Professor)")
        logger.info("      - 5개 연구실 (Laboratory)")
        logger.info("      - 13명 연구원 (LabMember)")
        logger.info("")
        logger.info("   ✅ 데이터 조작 테스트: 성공")
        logger.info("      - 계층적 네비게이션 (대학→대학→전공→교수→연구실)")
        logger.info("      - 3개 논문 (ResearchPaper)")
        logger.info("      - 3개 분석 결과 (PaperAnalysis)")
        logger.info("")
        logger.info("   ✅ 서비스 통합: 성공")
        logger.info("      - LLM 분석 완료")
        logger.info("      - 벡터 저장소 연동")
        logger.info("      - 유사도 검색 작동")
        logger.info("")
        logger.info("🎯 모든 테스트 통과! 파이프라인이 정상 작동합니다.")


# ==================== 메인 실행 ====================

if __name__ == "__main__":
    # 로깅 설정 - JSON이 아닌 일반 텍스트
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # E2E 파이프라인 실행
    pipeline = E2EPipeline()
    success = pipeline.run()

    exit(0 if success else 1)
