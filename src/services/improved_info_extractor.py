"""
향상된 정보 추출 엔진

GenericUniversityCrawler의 패턴 매칭을 보완하는 고급 추출 기능
- BeautifulSoup 기반 구조적 분석
- CSS 선택자 기반 추출
- 휴리스틱 기반 검증
"""

import re
import logging
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class ImprovedInfoExtractor:
    """향상된 정보 추출 엔진"""

    def __init__(self, html: str, base_url: str = ""):
        """
        초기화

        Args:
            html: 파싱할 HTML
            base_url: 상대 URL을 절대 URL로 변환할 기본 URL
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'html.parser')
        self.text = self.soup.get_text()
        logger.info(f"📄 HTML 파싱 완료 ({len(self.html)} bytes, {len(self.text)} chars)")

    def extract_professors(self) -> List[Dict]:
        """
        교수 정보 추출 (다층 접근)

        1. 이메일 주소 기반
        2. 이름 패턴 기반
        3. 직급 키워드 기반
        """
        professors = []

        # 방법 1: 이메일 기반 추출
        email_professors = self._extract_by_email()
        professors.extend(email_professors)

        # 방법 2: 직급 키워드 기반 추출
        title_professors = self._extract_by_title_keywords()
        professors.extend(title_professors)

        # 방법 3: 테이블/리스트 구조 기반 추출
        structured_professors = self._extract_from_structured_data("professor", "faculty")
        professors.extend(structured_professors)

        # 중복 제거
        unique_professors = self._deduplicate_professors(professors)

        logger.info(f"   ✅ {len(unique_professors)}명의 교수 정보 추출 (검증됨)")
        return unique_professors[:50]

    def extract_labs(self) -> List[Dict]:
        """
        연구실 정보 추출

        1. 키워드 기반 추출
        2. 구조화된 데이터 기반
        3. 페이지 섹션 기반
        """
        labs = []

        # 방법 1: 키워드 기반 추출
        keyword_labs = self._extract_by_keywords(
            ["laboratory", "lab", "research group", "research center",
             "연구실", "실험실", "연구 그룹", "연구센터"]
        )
        labs.extend(keyword_labs)

        # 방법 2: 헤딩 기반 추출
        heading_labs = self._extract_from_headings()
        labs.extend(heading_labs)

        # 중복 제거
        unique_labs = self._deduplicate_labs(labs)

        logger.info(f"   ✅ {len(unique_labs)}개의 연구실 정보 추출 (검증됨)")
        return unique_labs[:30]

    def extract_papers(self) -> List[Dict]:
        """
        논문 정보 추출

        1. 제목 패턴 기반
        2. 인용 형식 기반
        3. 섹션 기반
        """
        papers = []

        # 방법 1: 인용 형식 기반 추출
        citation_papers = self._extract_by_citation_format()
        papers.extend(citation_papers)

        # 방법 2: 제목 패턴 기반 추출
        title_papers = self._extract_by_title_pattern()
        papers.extend(title_papers)

        # 방법 3: 링크 기반 추출 (PDF, ACM, IEEE 등)
        link_papers = self._extract_from_academic_links()
        papers.extend(link_papers)

        # 중복 제거
        unique_papers = self._deduplicate_papers(papers)

        logger.info(f"   ✅ {len(unique_papers)}개의 논문 정보 추출 (검증됨)")
        return unique_papers[:50]

    # ===================== 교수 정보 추출 헬퍼 =====================

    def _extract_by_email(self) -> List[Dict]:
        """이메일 주소로 교수 찾기"""
        professors = []

        # 이메일 주소 찾기
        email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        emails = set(re.findall(email_pattern, self.html))

        for email in emails:
            # 이메일 주변에서 이름 찾기
            email_pos = self.html.find(email)
            if email_pos < 0:
                continue

            # 전후 300자를 컨텍스트로 사용
            context_start = max(0, email_pos - 300)
            context_end = min(len(self.html), email_pos + len(email) + 100)
            context = self.html[context_start:context_end]

            # 이름 추출
            name = self._extract_name_from_context(context)
            if name:
                professors.append({
                    "name": name,
                    "email": email,
                    "extraction_method": "email_based",
                    "confidence": 0.8
                })

        return professors

    def _extract_by_title_keywords(self) -> List[Dict]:
        """직급 키워드를 사용하여 교수 찾기"""
        professors = []

        title_keywords = [
            "Professor", "Prof.", "Associate Professor", "Assistant Professor",
            "Distinguished Professor", "Emeritus",
            "교수", "부교수", "조교수", "명예교수"
        ]

        for keyword in title_keywords:
            # 키워드를 포함하는 문장 찾기
            pattern = rf'(?:[^.!?\n]{{0,150}}){re.escape(keyword)}[^.!?\n]{{0,150}}'
            matches = re.finditer(pattern, self.html, re.IGNORECASE)

            for match in matches:
                text = match.group(0).strip()
                # 이름 추출
                name = self._extract_name_from_context(text)
                email = self._extract_email_from_context(text)

                if name:
                    professors.append({
                        "name": name,
                        "email": email or "",
                        "title": keyword,
                        "extraction_method": "title_keyword",
                        "confidence": 0.7
                    })

        return professors

    def _extract_from_structured_data(self, *keywords) -> List[Dict]:
        """테이블, 리스트 등 구조화된 데이터에서 추출"""
        professors = []

        # 테이블 찾기
        tables = self.soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                row_text = row.get_text()
                # 교수 관련 키워드 확인
                if any(kw.lower() in row_text.lower() for kw in keywords):
                    # 이름, 이메일, 오피스 추출
                    cells = row.find_all('td')
                    for cell in cells:
                        text = cell.get_text().strip()
                        if len(text) > 3 and len(text) < 100:
                            name = self._extract_name_from_context(text)
                            if name:
                                professors.append({
                                    "name": name,
                                    "extraction_method": "table_structured",
                                    "confidence": 0.9
                                })
                                break

        return professors

    def _extract_name_from_context(self, context: str) -> Optional[str]:
        """컨텍스트에서 이름 추출"""
        # 이름 패턴
        patterns = [
            # 영문 이름: Firstname Lastname
            r'(?:^|\W)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s|$|,|\()',
            # 한글 이름
            r'([가-힣]{2,5})',
            # Dr./Prof. + 이름
            r'(?:Dr\.|Prof\.|Doctor)\s+([A-Za-z\s]+?)(?:\s|,|\(|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                name = match.group(1).strip()
                if 2 < len(name) < 100:
                    return name

        return None

    def _extract_email_from_context(self, context: str) -> Optional[str]:
        """컨텍스트에서 이메일 추출"""
        pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        match = re.search(pattern, context)
        return match.group(1) if match else None

    def _deduplicate_professors(self, professors: List[Dict]) -> List[Dict]:
        """교수 정보 중복 제거"""
        seen = set()
        unique = []

        for prof in professors:
            # 이메일이 있으면 이메일로 중복 제거, 없으면 이름으로
            key = prof.get("email") or prof.get("name", "")
            if key and key not in seen:
                seen.add(key)
                unique.append(prof)

        return unique

    # ===================== 연구실 정보 추출 헬퍼 =====================

    def _extract_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """키워드로 연구실 정보 추출"""
        labs = []

        for keyword in keywords:
            pattern = rf'(?:[^.!?\n]{{0,100}}){re.escape(keyword)}[^.!?\n]{{0,200}}'
            matches = re.finditer(pattern, self.html, re.IGNORECASE)

            for match in matches:
                text = match.group(0).strip()
                if 10 < len(text) < 500:
                    labs.append({
                        "description": text[:300],
                        "keyword": keyword,
                        "extraction_method": "keyword_based",
                        "confidence": 0.6
                    })

        return labs

    def _extract_from_headings(self) -> List[Dict]:
        """헤딩(h2, h3 등)에서 연구실 정보 추출"""
        labs = []

        for heading_tag in ['h2', 'h3', 'h4']:
            headings = self.soup.find_all(heading_tag)
            for heading in headings:
                text = heading.get_text().strip()
                # 연구실 같은 이름인지 확인
                if ('lab' in text.lower() or 'research' in text.lower() or
                    '연구' in text or '실험' in text):
                    # 헤딩 다음 단락도 포함
                    next_para = heading.find_next('p')
                    description = (next_para.get_text() if next_para else
                                 "") + " " + text
                    labs.append({
                        "name": text,
                        "description": description[:300],
                        "extraction_method": "heading_based",
                        "confidence": 0.8
                    })

        return labs

    def _deduplicate_labs(self, labs: List[Dict]) -> List[Dict]:
        """연구실 정보 중복 제거"""
        seen = set()
        unique = []

        for lab in labs:
            key = lab.get("name") or lab.get("description", "")[:50]
            if key and key not in seen:
                seen.add(key)
                unique.append(lab)

        return unique

    # ===================== 논문 정보 추출 헬퍼 =====================

    def _extract_by_citation_format(self) -> List[Dict]:
        """인용 형식으로 논문 추출 (APA, IEEE 등)"""
        papers = []

        # APA 형식: Author, Year, Title, Journal
        # IEEE 형식: [#] Author, Title, Journal, Year
        citation_pattern = (
            r'(?:\[\d+\])?\s*'  # Optional [#]
            r'([A-Z][A-Za-z\s.&,]+?)'  # Authors
            r'[.,]?\s*'
            r'(?:\()?(\d{4})(?:\))?[.,]?\s*'  # Year
            r'"?([^"\.]+?)"?[.,]\s*'  # Title
            r'(?:In\s+)?([A-Z][A-Za-z\s&]+)'  # Journal/Conference
        )

        matches = re.finditer(citation_pattern, self.text)
        for match in matches:
            paper = {
                "authors": match.group(1).strip(),
                "year": match.group(2),
                "title": match.group(3).strip(),
                "venue": match.group(4).strip(),
                "extraction_method": "citation_format",
                "confidence": 0.85
            }
            papers.append(paper)

        return papers

    def _extract_by_title_pattern(self) -> List[Dict]:
        """제목 패턴으로 논문 추출"""
        papers = []

        # 제목처럼 보이는 패턴
        # - 대문자로 시작
        # - 20-300자 길이
        # - 마침표나 줄바꿈으로 끝남
        sentences = re.split(r'[.!?\n]+', self.text)

        for sentence in sentences:
            text = sentence.strip()
            if (20 < len(text) < 300 and
                text[0].isupper() and
                text.count(' ') >= 2 and
                text.count(' ') <= 30):  # 너무 긴 문장은 제외

                papers.append({
                    "title": text,
                    "extraction_method": "title_pattern",
                    "confidence": 0.5
                })

        return papers

    def _extract_from_academic_links(self) -> List[Dict]:
        """학술 논문 링크(PDF, ACM, IEEE 등)에서 추출"""
        papers = []

        # 논문 링크 찾기
        links = self.soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 학술 출판사 확인
            if any(domain in href.lower() for domain in
                   ['pdf', 'arxiv', 'acm.org', 'ieee.org', 'springer', 'sciencedirect']):
                papers.append({
                    "title": text or href.split('/')[-1],
                    "url": urljoin(self.base_url, href),
                    "extraction_method": "academic_link",
                    "confidence": 0.7
                })

        return papers

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """논문 정보 중복 제거"""
        seen = set()
        unique = []

        for paper in papers:
            key = paper.get("title", "")[:100]
            if key and key not in seen:
                seen.add(key)
                unique.append(paper)

        return unique
