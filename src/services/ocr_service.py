"""
OCR 기반 이미지 텍스트 추출 서비스

주요 기능:
1. 이미지에서 텍스트 추출 (Paddle-OCR)
2. HTML 이미지 태그에서 텍스트 추출
3. 캐싱을 통한 성능 최적화
4. 오류 처리 및 폴백
"""

import asyncio
import logging
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, urljoin
from io import BytesIO
import re

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


class OCRService:
    """Paddle-OCR 기반 이미지 텍스트 추출"""

    def __init__(self, use_gpu: bool = False, lang: str = "ko"):
        """
        초기화

        Args:
            use_gpu: GPU 사용 여부 (True면 더 빠름)
            lang: OCR 언어 (ko=한국어, en=영어, ch=중국어)
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self.ocr = None
        self.cache: Dict[str, str] = {}  # URL hash -> 추출 텍스트
        logger.info(f"🚀 OCRService 초기화 (GPU={use_gpu}, 언어={lang})")

    async def initialize(self):
        """비동기 초기화 (필요시)"""
        if PaddleOCR and self.ocr is None:
            try:
                self.ocr = PaddleOCR(use_gpu=self.use_gpu, lang=self.lang)
                logger.info("✅ Paddle-OCR 초기화 완료")
            except Exception as e:
                logger.warning(f"⚠️  Paddle-OCR 초기화 실패: {e}")
                self.ocr = None

    async def extract_text_from_image_url(self, image_url: str, base_url: str = "") -> str:
        """
        이미지 URL에서 텍스트 추출

        Args:
            image_url: 이미지 URL (상대 또는 절대)
            base_url: 기본 URL (상대 URL 변환용)

        Returns:
            추출된 텍스트
        """
        if not self.ocr and not PaddleOCR:
            return ""

        # 상대 URL을 절대 URL로 변환
        full_url = urljoin(base_url, image_url)

        # 캐시 확인
        cache_key = self._get_cache_key(full_url)
        if cache_key in self.cache:
            logger.debug(f"📦 OCR 캐시 hit: {full_url[:50]}...")
            return self.cache[cache_key]

        try:
            logger.info(f"🔍 OCR 처리: {full_url[:60]}...")

            # 이미지 다운로드
            image_data = await self._download_image(full_url)
            if not image_data:
                return ""

            # OCR 수행 (동기 처리를 스레드 풀에서 실행)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._ocr_image, image_data
            )

            text = result if result else ""

            # 캐시 저장
            if text:
                self.cache[cache_key] = text
                logger.info(f"   ✅ OCR 완료 ({len(text)} 글자)")

            return text

        except Exception as e:
            logger.warning(f"   ⚠️  OCR 추출 실패: {e}")
            return ""

    async def extract_text_from_html_images(
        self, html: str, base_url: str = ""
    ) -> Tuple[str, List[Dict]]:
        """
        HTML에서 img 태그를 찾아 텍스트 추출

        Args:
            html: HTML 콘텐츠
            base_url: 기본 URL

        Returns:
            (추출된 모든 텍스트, [{"src": "...", "alt": "...", "text": "..."}])
        """
        if not self.ocr and not PaddleOCR:
            return "", []

        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
        matches = re.finditer(img_pattern, html, re.IGNORECASE)

        all_text = []
        image_results = []

        for match in matches:
            src = match.group(1)
            alt = match.group(2) or ""

            # OCR 수행
            ocr_text = await self.extract_text_from_image_url(src, base_url)

            if ocr_text or alt:
                all_text.append(ocr_text or alt)
                image_results.append({
                    "src": src,
                    "alt": alt,
                    "ocr_text": ocr_text,
                    "combined": f"{alt} {ocr_text}".strip()
                })

        combined_text = " ".join(all_text)
        logger.info(f"📊 HTML 이미지 처리 완료: {len(image_results)}개 이미지, {len(combined_text)} 글자")

        return combined_text, image_results

    async def extract_text_from_html_with_ocr(
        self, html: str, base_url: str = "", skip_ocr: bool = False
    ) -> Dict:
        """
        HTML에서 텍스트와 이미지 텍스트를 모두 추출

        Args:
            html: HTML 콘텐츠
            base_url: 기본 URL
            skip_ocr: OCR 스킵 여부 (빠른 처리용)

        Returns:
            {
                "html_text": "...",        # HTML에서 직접 추출한 텍스트
                "image_text": "...",       # OCR로 추출한 텍스트
                "combined_text": "...",    # 통합 텍스트
                "image_results": [...]
            }
        """
        # HTML 텍스트 추출 (기본)
        html_text = self._extract_text_from_html_tags(html)

        # OCR 처리
        image_text = ""
        image_results = []

        if not skip_ocr and (self.ocr or PaddleOCR):
            image_text, image_results = await self.extract_text_from_html_images(
                html, base_url
            )

        combined_text = f"{html_text} {image_text}".strip()

        return {
            "html_text": html_text,
            "image_text": image_text,
            "combined_text": combined_text,
            "image_results": image_results,
            "stats": {
                "html_chars": len(html_text),
                "image_chars": len(image_text),
                "image_count": len(image_results),
            }
        }

    # ===================== 내부 메서드 =====================

    def _ocr_image(self, image_data: BytesIO) -> str:
        """OCR 처리 (동기)"""
        if not self.ocr:
            return ""

        try:
            import cv2
            import numpy as np

            # BytesIO를 numpy 배열로 변환
            nparr = np.frombuffer(image_data.getvalue(), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return ""

            # OCR 실행
            result = self.ocr.ocr(img, cls=True)

            # 결과 추출
            texts = []
            if result:
                for line in result:
                    if line:
                        for word_info in line:
                            if word_info and len(word_info) > 1:
                                text = word_info[1]  # 텍스트
                                confidence = word_info[2]  # 신뢰도

                                # 신뢰도 90% 이상인 텍스트만 추가
                                if confidence > 0.90:
                                    texts.append(text)

            return " ".join(texts)

        except Exception as e:
            logger.warning(f"⚠️  OCR 처리 중 오류: {e}")
            return ""

    async def _download_image(self, url: str) -> Optional[BytesIO]:
        """이미지 다운로드"""
        if not aiohttp:
            logger.warning("⚠️  aiohttp 미설치 - 이미지 다운로드 불가")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return BytesIO(data)
                    else:
                        logger.warning(f"   ⚠️  HTTP {resp.status}: {url}")
                        return None
        except Exception as e:
            logger.warning(f"   ⚠️  이미지 다운로드 실패: {e}")
            return None

    def _extract_text_from_html_tags(self, html: str) -> str:
        """HTML 태그에서 텍스트 추출"""
        # 스크립트/스타일 제거
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # 태그 제거
        text = re.sub(r'<[^>]+>', ' ', html)

        # 공백 정리
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _get_cache_key(self, url: str) -> str:
        """URL을 캐시 키로 변환"""
        return hashlib.md5(url.encode()).hexdigest()

    def clear_cache(self):
        """캐시 초기화"""
        self.cache.clear()
        logger.info("🗑️  OCR 캐시 초기화")

    def get_cache_size(self) -> int:
        """캐시 크기 반환"""
        return len(self.cache)


# ===================== 사용 예시 =====================

async def example_ocr():
    """OCR 서비스 예시"""
    ocr_service = OCRService(use_gpu=False, lang="ko")
    await ocr_service.initialize()

    try:
        # 예시 1: 이미지 URL에서 직접 텍스트 추출
        html = """
        <html>
            <body>
                <h1>교수 정보</h1>
                <img src="https://example.com/professor.jpg" alt="Prof. Kim">
                <img src="https://example.com/paper_list.png" alt="Publications">
            </body>
        </html>
        """

        result = await ocr_service.extract_text_from_html_with_ocr(
            html, "https://example.com"
        )

        print(f"\n📊 OCR 결과:")
        print(f"   HTML 텍스트: {result['html_text'][:50]}...")
        print(f"   이미지 텍스트: {result['image_text'][:50]}...")
        print(f"   이미지 개수: {result['stats']['image_count']}개")

    finally:
        pass


if __name__ == "__main__":
    asyncio.run(example_ocr())
