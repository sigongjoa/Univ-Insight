"""
향상된 정보 추출 엔진

GenericUniversityCrawler의 패턴 매칭을 보완하는 고급 추출 기능
- BeautifulSoup 기반 구조적 분석
- CSS 선택자 기반 추출
- 휴리스틱 기반 검증
"""

import re
import logging
import asyncio
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from src.services.university_selectors import UniversitySelectors

logger = logging.getLogger(__name__)

# OCR 서비스 (선택사항)
try:
    from src.services.ocr_service import OCRService
except ImportError:
    OCRService = None


class ImprovedInfoExtractor:
    """향상된 정보 추출 엔진"""

    def __init__(self, html: str, base_url: str = "", university_domain: str = "", use_ocr: bool = False):
        """
        초기화

        Args:
            html: 파싱할 HTML
            base_url: 상대 URL을 절대 URL로 변환할 기본 URL
            university_domain: 대학 도메인 (선택자 매칭용)
            use_ocr: OCR 사용 여부 (이미지 기반 정보 추출)
        """
        self.html = html
        self.base_url = base_url
        self.university_domain = university_domain
        self.use_ocr = use_ocr
        self.soup = BeautifulSoup(html, 'html.parser')
        self.text = self.soup.get_text()
        self.ocr_service = None
        self.ocr_text = ""

        # 대학별 선택자 로드
        self.selector = UniversitySelectors.get_selector_by_domain(university_domain)

        logger.info(f"📄 HTML 파싱 완료 ({len(self.html)} bytes, {len(self.text)} chars)")
        if self.selector:
            logger.info(f"   🎓 {self.selector.university_name} 선택자 로드됨")

    def extract_professors(self) -> List[Dict]:
        """
        교수 정보 추출 (다층 접근)

        1. CSS 선택자 기반 (가장 정확함)
        2. 이메일 주소 기반
        3. 직급 키워드 기반
        4. 테이블/리스트 구조 기반
        """
        professors = []

        # 방법 0: CSS 선택자 기반 추출 (가장 우선)
        if self.selector:
            css_professors = self._extract_by_css_selector(
                self.selector.professor_selectors,
                confidence=0.95
            )
            professors.extend(css_professors)
            logger.info(f"   ✅ CSS 선택자로 {len(css_professors)}명 추출")

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

        1. CSS 선택자 기반 (가장 정확함)
        2. 키워드 기반 추출
        3. 헤딩 기반 추출
        """
        labs = []

        # 방법 0: CSS 선택자 기반 추출 (가장 우선)
        if self.selector:
            css_labs = self._extract_by_css_selector(
                self.selector.lab_selectors,
                confidence=0.95,
                extract_type="lab"
            )
            labs.extend(css_labs)
            logger.info(f"   ✅ CSS 선택자로 {len(css_labs)}개 추출")

        # 방법 1: 키워드 기반 추출
        keyword_labs = self._extract_by_keywords(
            self.selector.lab_keywords if self.selector
            else ["laboratory", "lab", "research group", "research center",
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
        # 이름으로 제외할 단어들 (기관명, 일반 단어 등)
        excluded_words = {
            "university", "college", "department", "institute", "school",
            "대학교", "대학", "학과", "학부", "센터", "연구소", "학교",
            "korea", "seoul", "kaist", "snu", "the", "and", "or",
            "engineering", "science", "technology", "research", "center",
            "professor", "prof", "associate", "assistant", "distinguished",
            "emeritus", "faculty", "members", "graduate", "students",
            "office", "room", "building", "administration", "email", "phone",
            "website", "notice", "news", "event", "seminar", "lab",
            "교수", "부교수", "조교수", "명예", "강사", "연구원",
            "학생", "대학원", "학부", "사무", "행정", "인포", "공지",
            "뉴스", "행사", "세미나"
        }

        # 이름 패턴
        patterns = [
            # 영문 이름: Firstname Lastname (2단어)
            r'(?:^|\W)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s|$|,|\()',
            # 한글 이름 (2-4자)
            r'([가-힣]{2,4}(?:\s[가-힣]{1,3})?)',
            # Dr./Prof. + 이름
            r'(?:Dr\.|Prof\.|Doctor|교수)\s+([A-Za-z가-힣\s]+?)(?:\s|,|\(|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                name = match.group(1).strip()

                # 길이 체크
                if not (2 < len(name) < 100):
                    continue

                # 제외 단어 체크
                name_lower = name.lower()
                if any(excluded in name_lower for excluded in excluded_words):
                    continue

                # 숫자가 많으면 제외
                if sum(c.isdigit() for c in name) > len(name) * 0.3:
                    continue

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

    # ===================== CSS 선택자 기반 추출 (NEW) =====================

    def _extract_by_css_selector(
        self,
        selectors: Dict[str, str],
        confidence: float = 0.95,
        extract_type: str = "professor"
    ) -> List[Dict]:
        """
        CSS 선택자를 사용한 구조화된 정보 추출

        Args:
            selectors: CSS 선택자 딕셔너리 {"name": "...", "email": "...", ...}
            confidence: 신뢰도 점수
            extract_type: 추출 타입 ("professor" 또는 "lab")

        Returns:
            추출된 정보 리스트
        """
        results = []

        try:
            # name 선택자가 있으면 그것을 기준으로 추출
            if "name" in selectors:
                name_selector = selectors["name"]
                name_elements = self.soup.select(name_selector)

                for elem in name_elements:
                    if not elem:
                        continue

                    name = elem.get_text().strip()
                    if not name or len(name) < 2:
                        continue

                    result = {
                        "name": name[:100],
                        "extraction_method": "css_selector",
                        "confidence": confidence,
                    }

                    # 같은 컨테이너에서 다른 정보 추출
                    parent = elem.find_parent()
                    if parent:
                        for key, selector in selectors.items():
                            if key == "name":
                                continue

                            try:
                                elem_found = parent.select_one(selector)
                                if elem_found:
                                    value = elem_found.get_text().strip()
                                    if value:
                                        result[key] = value[:200]
                            except Exception as e:
                                logger.debug(f"선택자 '{selector}' 추출 실패: {e}")

                    if extract_type == "lab" and "name" in result:
                        result["description"] = result.get("description", result["name"])

                    results.append(result)

            # name 선택자가 없으면 첫 번째 선택자 사용
            elif selectors:
                first_key = list(selectors.keys())[0]
                first_selector = selectors[first_key]
                elements = self.soup.select(first_selector)

                for elem in elements[:20]:  # 최대 20개까지
                    text = elem.get_text().strip()
                    if text and len(text) > 2:
                        results.append({
                            first_key: text[:100],
                            "extraction_method": "css_selector",
                            "confidence": confidence,
                        })

        except Exception as e:
            logger.warning(f"CSS 선택자 추출 중 오류: {e}")

        return results

    def extract_professor_links(self) -> List[Dict]:
        """
        교수 페이지 링크 발견

        Returns:
            [{"text": "...", "url": "...", "type": "..."}, ...]
        """
        links = []

        if not self.selector:
            return links

        try:
            # 교수 링크 발견 선택자 사용
            for link_type, selector in self.selector.professor_link_selectors.items():
                try:
                    elements = self.soup.select(selector)
                    for elem in elements:
                        href = elem.get("href", "")
                        text = elem.get_text().strip()

                        if href and text:
                            # 상대 URL을 절대 URL로 변환
                            abs_url = urljoin(self.base_url, href)

                            links.append({
                                "text": text[:100],
                                "url": abs_url,
                                "type": link_type,
                                "extraction_method": "css_selector",
                            })
                except Exception as e:
                    logger.debug(f"링크 선택자 '{selector}' 실패: {e}")

            # 키워드 기반 링크 발견 (선택자가 없을 때)
            if not links:
                for link in self.soup.find_all('a', href=True):
                    text = link.get_text().strip()
                    href = link.get('href', '')

                    # 키워드 매칭
                    if any(kw.lower() in (text + href).lower()
                           for kw in self.selector.professor_link_keywords):
                        abs_url = urljoin(self.base_url, href)
                        links.append({
                            "text": text[:100],
                            "url": abs_url,
                            "type": "keyword_matched",
                            "extraction_method": "keyword_based",
                        })

        except Exception as e:
            logger.warning(f"교수 링크 추출 중 오류: {e}")

        # 중복 제거
        seen_urls = set()
        unique_links = []
        for link in links:
            if link["url"] not in seen_urls:
                seen_urls.add(link["url"])
                unique_links.append(link)

        return unique_links[:20]  # 최대 20개
