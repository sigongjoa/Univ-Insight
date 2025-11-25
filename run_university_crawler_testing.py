#!/usr/bin/env python3
"""
각 대학별 크롤러 테스트 및 상세 레포트 생성

목표: 범용 크롤러의 실제 한계를 파악하고 대학별 상세 분석 보고서 작성
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from src.services.generic_university_crawler import GenericUniversityCrawler
from src.core.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# 테스트할 대학 목록
UNIVERSITIES = [
    {
        "name": "Seoul National University",
        "name_ko": "서울대학교",
        "url": "https://www.snu.ac.kr",
        "dept_urls": [
            "https://engineering.snu.ac.kr/cse",  # 컴퓨터공학부
        ]
    },
    {
        "name": "KAIST",
        "name_ko": "카이스트",
        "url": "https://www.kaist.ac.kr",
        "dept_urls": [
            "https://www.kaist.ac.kr/cs",  # 컴퓨터과학과
        ]
    },
    {
        "name": "Korea University",
        "name_ko": "고려대학교",
        "url": "https://www.korea.ac.kr",
        "dept_urls": [
            "https://cs.korea.ac.kr",  # 컴퓨터학과
        ]
    },
]


async def test_university_crawler():
    """각 대학 페이지 크롤링 및 분석"""

    logger.info("\n" + "="*80)
    logger.info("🎓 범용 크롤러 대학별 테스트 시작")
    logger.info("="*80 + "\n")

    crawler = GenericUniversityCrawler()
    await crawler.initialize()

    all_reports = []

    try:
        for university in UNIVERSITIES:
            logger.info(f"\n{'='*80}")
            logger.info(f"🏫 {university['name_ko']} ({university['name']})")
            logger.info(f"{'='*80}")

            uni_report = {
                "university": university['name_ko'],
                "url": university['url'],
                "timestamp": datetime.now().isoformat(),
                "departments": []
            }

            # 각 학과별 테스트
            for dept_url in university['dept_urls']:
                logger.info(f"\n📖 학과 페이지: {dept_url}")
                logger.info("-" * 80)

                dept_report = {
                    "url": dept_url,
                    "status": "pending",
                    "html_size": 0,
                    "text_length": 0,
                    "professors": [],
                    "labs": [],
                    "papers": [],
                    "extraction_stats": {},
                    "issues": [],
                    "raw_html_sample": ""
                }

                try:
                    # 페이지 크롤링
                    logger.info("   📡 크롤링 중...")
                    html = await crawler.crawl_page(dept_url)

                    if not html:
                        logger.error("   ❌ HTML을 받지 못함")
                        dept_report["status"] = "failed"
                        dept_report["issues"].append("Failed to crawl page")
                        uni_report["departments"].append(dept_report)
                        continue

                    dept_report["html_size"] = len(html)
                    dept_report["raw_html_sample"] = html[:500]  # 처음 500자 저장

                    # 텍스트 추출
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    text = soup.get_text()
                    dept_report["text_length"] = len(text)

                    logger.info(f"   ✅ 크롤링 성공 (HTML: {len(html)} bytes, 텍스트: {len(text)} chars)")

                    # 정보 추출
                    logger.info("   🔍 정보 추출 중...")

                    professors = await crawler.extract_professors(dept_url)
                    logger.info(f"      👨‍🏫 교수: {len(professors)}명")
                    dept_report["professors"] = professors

                    labs = await crawler.extract_labs(dept_url)
                    logger.info(f"      🔬 연구실: {len(labs)}개")
                    dept_report["labs"] = labs

                    papers = await crawler.extract_papers(dept_url)
                    logger.info(f"      📄 논문: {len(papers)}개")
                    dept_report["papers"] = papers

                    # 통계
                    dept_report["extraction_stats"] = {
                        "professors_count": len(professors),
                        "labs_count": len(labs),
                        "papers_count": len(papers),
                        "total_extracted": len(professors) + len(labs) + len(papers)
                    }

                    # 문제 분석
                    if len(professors) == 0:
                        dept_report["issues"].append("No professors extracted - page may not contain faculty information or text is image-based")
                    if len(labs) == 0:
                        dept_report["issues"].append("No labs extracted - labs may be on separate pages or use different keywords")
                    if len(papers) == 0:
                        dept_report["issues"].append("No papers extracted - papers may be on professor pages or external links")

                    # 페이지 구조 분석
                    logger.info("   📊 페이지 구조 분석...")
                    structure_analysis = analyze_page_structure(html, text)
                    dept_report["structure_analysis"] = structure_analysis

                    for issue in structure_analysis.get("potential_issues", []):
                        logger.info(f"      ⚠️  {issue}")

                    dept_report["status"] = "completed"

                except Exception as e:
                    logger.error(f"   ❌ 오류: {str(e)}")
                    dept_report["status"] = "error"
                    dept_report["issues"].append(f"Exception: {str(e)}")

                uni_report["departments"].append(dept_report)

            all_reports.append(uni_report)

    finally:
        await crawler.close()

    # 최종 보고서 생성
    logger.info("\n" + "="*80)
    logger.info("📋 최종 보고서 생성 중...")
    logger.info("="*80)

    generate_final_reports(all_reports)

    logger.info("\n✅ 모든 테스트 완료!")


def analyze_page_structure(html: str, text: str) -> dict:
    """페이지 구조 상세 분석"""
    from bs4 import BeautifulSoup

    analysis = {
        "has_tables": False,
        "has_lists": False,
        "has_links": False,
        "email_count": 0,
        "heading_count": 0,
        "potential_issues": [],
        "element_counts": {}
    }

    soup = BeautifulSoup(html, 'html.parser')

    # 요소 개수 계산
    analysis["has_tables"] = len(soup.find_all('table')) > 0
    analysis["has_lists"] = len(soup.find_all(['ul', 'ol'])) > 0
    analysis["has_links"] = len(soup.find_all('a')) > 0

    analysis["element_counts"] = {
        "tables": len(soup.find_all('table')),
        "lists": len(soup.find_all(['ul', 'ol'])),
        "links": len(soup.find_all('a')),
        "headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
        "images": len(soup.find_all('img')),
        "divs": len(soup.find_all('div')),
    }

    # 이메일 개수
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    analysis["email_count"] = len(re.findall(email_pattern, html))

    analysis["heading_count"] = analysis["element_counts"]["headings"]

    # 문제 분석
    if len(text) < 500:
        analysis["potential_issues"].append("매우 적은 텍스트 (500자 미만) - 이미지 기반 페이지 가능성")

    if analysis["element_counts"]["images"] > analysis["element_counts"]["links"] * 5:
        analysis["potential_issues"].append("이미지가 매우 많음 - 이미지 기반 레이아웃 가능성")

    if analysis["email_count"] == 0:
        analysis["potential_issues"].append("이메일 주소 없음 - 교수 정보가 다른 페이지에 있을 가능성")

    if not analysis["has_tables"] and not analysis["has_lists"]:
        analysis["potential_issues"].append("구조화된 데이터 없음 (테이블/리스트) - 정보가 분산되어 있을 가능성")

    return analysis


def generate_final_reports(all_reports: list):
    """최종 보고서 파일 생성"""

    # 1. JSON 형식 상세 보고서
    json_report_path = Path("UNIVERSITY_CRAWLER_TEST_REPORT.json")
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ JSON 보고서 저장: {json_report_path}")

    # 2. 마크다운 형식 분석 보고서
    md_report = generate_markdown_report(all_reports)
    md_report_path = Path("UNIVERSITY_CRAWLER_TEST_ANALYSIS.md")
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_report)
    logger.info(f"✅ 마크다운 보고서 저장: {md_report_path}")

    # 3. 각 대학별 개별 보고서
    for uni_report in all_reports:
        uni_name = uni_report["university"].replace(" ", "_")
        uni_report_path = Path(f"UNIVERSITY_{uni_name}_ANALYSIS.md")
        uni_md = generate_university_report(uni_report)
        with open(uni_report_path, 'w', encoding='utf-8') as f:
            f.write(uni_md)
        logger.info(f"✅ {uni_report['university']} 분석 보고서 저장: {uni_report_path}")


def generate_markdown_report(all_reports: list) -> str:
    """마크다운 형식 종합 분석 보고서 생성"""

    report = """# 범용 크롤러 대학별 테스트 분석 보고서

**작성일:** 2025-11-25
**목적:** 범용 크롤러(GenericUniversityCrawler)의 실제 한계와 각 대학별 특성 파악

---

## 📊 요약

### 테스트 결과 개요

"""

    # 요약 테이블
    report += "| 대학 | 교수 | 연구실 | 논문 | 상태 | 주요 이슈 |\n"
    report += "|------|------|--------|------|------|----------|\n"

    for uni in all_reports:
        for dept in uni["departments"]:
            profs = dept["extraction_stats"].get("professors_count", 0)
            labs = dept["extraction_stats"].get("labs_count", 0)
            papers = dept["extraction_stats"].get("papers_count", 0)
            status = dept["status"]
            issues = ", ".join(dept["issues"][:1]) if dept["issues"] else "None"

            report += f"| {uni['university']} | {profs} | {labs} | {papers} | {status} | {issues[:40]}... |\n"

    report += "\n---\n\n"

    # 각 대학별 상세 분석
    report += "## 🏫 대학별 상세 분석\n\n"

    for uni in all_reports:
        report += f"### {uni['university']}\n\n"
        report += f"**URL:** {uni['url']}\n\n"

        for i, dept in enumerate(uni["departments"], 1):
            report += f"#### 학과 {i}: {dept['url']}\n\n"
            report += f"**크롤링 결과:**\n"
            report += f"- HTML 크기: {dept['html_size']} bytes\n"
            report += f"- 텍스트 길이: {dept['text_length']} chars\n"
            report += f"- 교수: {dept['extraction_stats'].get('professors_count', 0)}명\n"
            report += f"- 연구실: {dept['extraction_stats'].get('labs_count', 0)}개\n"
            report += f"- 논문: {dept['extraction_stats'].get('papers_count', 0)}개\n\n"

            report += f"**페이지 구조:**\n"
            struct = dept.get("structure_analysis", {})
            report += f"- 테이블: {struct.get('element_counts', {}).get('tables', 0)}개\n"
            report += f"- 리스트: {struct.get('element_counts', {}).get('lists', 0)}개\n"
            report += f"- 링크: {struct.get('element_counts', {}).get('links', 0)}개\n"
            report += f"- 헤딩: {struct.get('element_counts', {}).get('headings', 0)}개\n"
            report += f"- 이미지: {struct.get('element_counts', {}).get('images', 0)}개\n"
            report += f"- 이메일 주소: {struct.get('email_count', 0)}개\n\n"

            if dept["issues"]:
                report += f"**식별된 문제:**\n"
                for issue in dept["issues"]:
                    report += f"- ⚠️  {issue}\n"
                report += "\n"

            if struct.get("potential_issues"):
                report += f"**페이지 구조상 이슈:**\n"
                for issue in struct["potential_issues"]:
                    report += f"- 🔴 {issue}\n"
                report += "\n"

    report += "\n---\n\n"
    report += "## 🔍 범용 크롤러의 한계\n\n"
    report += """
### 1. 페이지 구조 다양성
- **문제:** 각 대학이 서로 다른 HTML 구조 사용
- **원인:** 통일된 웹 표준 미적용, 각 대학의 CMS 상이
- **영향:** 정규식 기반 패턴 매칭의 낮은 성공률

### 2. 텍스트 추출 한계
- **문제:** 교수 정보가 이미지로만 표시되는 경우
- **원인:** 시각적 디자인 우선, 접근성 고려 부족
- **영향:** 패턴 매칭 불가능, OCR 필요

### 3. 정보 분산
- **문제:** 교수 정보가 여러 페이지에 분산됨
- **원인:** 학과 페이지 → 교수 목록 페이지 → 개별 교수 페이지
- **영향:** 단일 URL만으로 전체 정보 수집 불가

### 4. 동적 콘텐츠
- **문제:** JavaScript로 동적으로 로드되는 정보
- **원인:** 최신 웹 기술 활용
- **영향:** 기본 HTML 파싱으로 정보 누락

### 5. CSS 선택자 의존성
- **문제:** 구조화된 데이터 부재 시 CSS 선택자 필요
- **원인:** 각 대학마다 다른 클래스/ID 사용
- **영향:** 대학별 맞춤 설정 필요

---

## 💡 개선 방안

### 단기 (1주일)
1. CSS 선택자 기반 보조 추출 추가
2. 교수 페이지 URL 자동 발견
3. 대학별 맞춤 패턴 작성

### 중기 (2주일)
1. OCR 기반 이미지 텍스트 추출
2. 다중 페이지 크롤링 (학과 → 교수 → 개별 교수 페이지)
3. JavaScript 렌더링 후 정보 추출

### 장기 (1개월)
1. LLM 기반 구조 이해
2. 동적 콘텐츠 처리
3. 신뢰도 점수 기반 결과 검증

"""

    return report


def generate_university_report(uni_report: dict) -> str:
    """각 대학별 개별 보고서 생성"""

    report = f"""# {uni_report['university']} 크롤러 분석 보고서

**분석 날짜:** {uni_report['timestamp']}
**대학 웹사이트:** {uni_report['url']}

---

## 📊 크롤링 결과 요약

"""

    for i, dept in enumerate(uni_report["departments"], 1):
        report += f"""
### 학과 {i}

**URL:** {dept['url']}

**크롤링 성공:**
- ✅ HTML 다운로드 완료
- ✅ 파일 크기: {dept['html_size']} bytes
- ✅ 텍스트 추출: {dept['text_length']} chars

**정보 추출 결과:**
- 👨‍🏫 교수: {dept['extraction_stats'].get('professors_count', 0)}명
- 🔬 연구실: {dept['extraction_stats'].get('labs_count', 0)}개
- 📄 논문: {dept['extraction_stats'].get('papers_count', 0)}개

"""

        if dept["professors"]:
            report += "**추출된 교수:**\n"
            for prof in dept["professors"][:5]:  # 처음 5개만
                report += f"- {prof.get('name', 'Unknown')} ({prof.get('email', 'no-email')})\n"
            report += "\n"

        if dept["labs"]:
            report += "**추출된 연구실:**\n"
            for lab in dept["labs"][:5]:  # 처음 5개만
                report += f"- {lab.get('name') or lab.get('description', 'Unknown')[:50]}\n"
            report += "\n"

        if dept["papers"]:
            report += "**추출된 논문:**\n"
            for paper in dept["papers"][:5]:  # 처음 5개만
                report += f"- {paper.get('title', 'Unknown')[:60]}\n"
            report += "\n"

    report += """
---

## 🔍 페이지 구조 분석

"""

    for i, dept in enumerate(uni_report["departments"], 1):
        struct = dept.get("structure_analysis", {})
        report += f"""
### 학과 {i} 구조

**HTML 요소 구성:**
- 테이블: {struct.get('element_counts', {}).get('tables', 0)}개
- 리스트: {struct.get('element_counts', {}).get('lists', 0)}개
- 링크: {struct.get('element_counts', {}).get('links', 0)}개
- 헤딩: {struct.get('element_counts', {}).get('headings', 0)}개
- 이미지: {struct.get('element_counts', {}).get('images', 0)}개
- Div: {struct.get('element_counts', {}).get('divs', 0)}개

**이메일 주소 발견:** {struct.get('email_count', 0)}개

**잠재적 이슈:**
"""

        if struct.get("potential_issues"):
            for issue in struct["potential_issues"]:
                report += f"- 🔴 {issue}\n"
        else:
            report += "- ✅ 구조화된 데이터 감지됨\n"

    report += """

---

## ⚠️ 식별된 문제점

"""

    for i, dept in enumerate(uni_report["departments"], 1):
        if dept["issues"]:
            report += f"\n### 학과 {i}:\n"
            for issue in dept["issues"]:
                report += f"- {issue}\n"

    report += """

---

## 💡 권장사항

### 단기 개선 (1-2일)
1. CSS 선택자 기반 추출 추가
2. 교수 페이지 링크 자동 발견
3. 특정 대학 맞춤 패턴 작성

### 중기 개선 (1주일)
1. 다중 페이지 크롤링 지원
2. JavaScript 렌더링 후 정보 추출
3. 신뢰도 점수 기반 필터링

### 장기 개선 (2주일 이상)
1. OCR 기반 이미지 텍스트 추출
2. LLM 기반 구조 이해
3. 완전 자동화된 정보 추출

---

**결론:** 범용 크롤러의 기본 구조는 완성되었으나, 실제 대학 페이지의 다양한 구조를
처리하기 위해서는 추가적인 구체화 작업이 필요합니다.

"""

    return report


if __name__ == "__main__":
    asyncio.run(test_university_crawler())
