"""
JavaScript 렌더링 최적화 서비스

주요 기능:
1. 동적 페이지 감지 및 JS 렌더링 필요 판단
2. 스마트 렌더링 (필요한 경우에만)
3. 성능 메트릭 수집
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class JSRendererOptimizer:
    """JavaScript 렌더링 최적화"""

    def __init__(self):
        """초기화"""
        self.js_heavy_indicators = [
            r'<script[^>]*>.*?document\.write',
            r'<script[^>]*>.*?window\.onload',
            r'<script[^>]*>.*?ajax',
            r'<script[^>]*>.*?fetch\(',
            r'<script[^>]*>.*?XMLHttpRequest',
            r'data-\w+="[^"]*\{',  # JSON in data attributes
            r'ng-\w+',  # Angular
            r'v-\w+',  # Vue.js
            r'react',  # React
        ]

        self.js_light_indicators = [
            r'<h1[^>]*>',  # Basic HTML structure
            r'<table[^>]*>',  # Tables
            r'<p[^>]*>',  # Paragraphs
            r'<div[^>]*class="[^"]*content[^"]*"',  # Content divs
        ]

        logger.info("🚀 JSRendererOptimizer 초기화")

    def should_use_js_rendering(self, html: str, base_url: str = "") -> Tuple[bool, str]:
        """
        JavaScript 렌더링이 필요한지 판단

        Args:
            html: HTML 콘텐츠
            base_url: URL (선택사항, 도메인 기반 판단용)

        Returns:
            (필요_여부, 판단_이유)
        """
        if not html:
            return False, "비어 있는 HTML"

        html_lower = html.lower()
        score = 0
        reasons = []

        # JS Heavy 지표 확인
        for indicator in self.js_heavy_indicators:
            if re.search(indicator, html_lower, re.DOTALL | re.IGNORECASE):
                score += 10
                reasons.append(indicator[:30])

        # JS Light 지표 확인
        for indicator in self.js_light_indicators:
            if re.search(indicator, html_lower, re.IGNORECASE):
                score -= 5

        # 이미지 태그만 있고 콘텐츠가 없는 경우 (KAIST 같은 이미지 기반 페이지)
        img_count = len(re.findall(r'<img[^>]*>', html_lower))
        text_length = len(re.sub(r'<[^>]+>', '', html_lower).strip())

        if img_count > 5 and text_length < 200:
            score += 15
            reasons.append("이미지_기반_페이지")

        # URL 기반 판단 (과거 경험)
        if base_url:
            if "kaist.ac.kr" in base_url:
                score += 5  # KAIST는 JS 렌더링 자주 필요
            elif "snu.ac.kr" in base_url:
                score -= 3  # SNU는 정적 페이지 많음

        # 최종 판단
        needs_rendering = score > 5
        reason = " + ".join(reasons) if reasons else f"점수={score}"

        if needs_rendering:
            logger.debug(f"✅ JS 렌더링 필요: {reason} (점수={score})")
        else:
            logger.debug(f"❌ JS 렌더링 불필요: {reason} (점수={score})")

        return needs_rendering, reason

    def get_content_completeness(self, html: str) -> Dict:
        """
        콘텐츠 완성도 측정

        Returns:
            {
                "completeness": 0-100,
                "has_structure": bool,
                "has_content": bool,
                "has_forms": bool,
                "metrics": {...}
            }
        """
        html_lower = html.lower()

        # 구조 확인
        has_table = bool(re.search(r'<table[^>]*>', html_lower))
        has_list = bool(re.search(r'<[ou]l[^>]*>', html_lower))
        has_divs = bool(re.search(r'<div[^>]*class="[^"]*(?:row|grid|container)[^"]*"', html_lower))
        has_structure = has_table or has_list or has_divs

        # 콘텐츠 확인
        text = re.sub(r'<[^>]+>', '', html_lower).strip()
        has_content = len(text) > 100

        # 폼 확인
        has_forms = bool(re.search(r'<form[^>]*>|<input[^>]*>|<select[^>]*>', html_lower))

        # 메트릭
        metrics = {
            "html_size": len(html),
            "text_length": len(text),
            "table_count": len(re.findall(r'<table[^>]*>', html_lower)),
            "img_count": len(re.findall(r'<img[^>]*>', html_lower)),
            "script_count": len(re.findall(r'<script[^>]*>', html_lower)),
            "link_count": len(re.findall(r'<a[^>]*href', html_lower)),
        }

        # 완성도 계산
        completeness = 0
        if has_structure:
            completeness += 30
        if has_content:
            completeness += 40
        if has_forms:
            completeness += 10
        if metrics["link_count"] > 10:
            completeness += 20

        return {
            "completeness": min(100, completeness),
            "has_structure": has_structure,
            "has_content": has_content,
            "has_forms": has_forms,
            "metrics": metrics
        }

    def estimate_render_time(self, html: str) -> Dict:
        """
        JavaScript 렌더링 시간 추정

        Returns:
            {
                "estimated_time_ms": int,
                "complexity": "low|medium|high",
                "reasons": [...]
            }
        """
        html_lower = html.lower()

        # 복잡도 계산
        script_count = len(re.findall(r'<script[^>]*>', html_lower))
        api_calls = len(re.findall(r'(?:ajax|fetch|xhr)', html_lower))
        heavy_frameworks = len(re.findall(r'(?:react|angular|vue)', html_lower))

        complexity_score = script_count + (api_calls * 2) + (heavy_frameworks * 5)

        if complexity_score < 5:
            complexity = "low"
            estimated_time = 2000  # 2초
        elif complexity_score < 15:
            complexity = "medium"
            estimated_time = 5000  # 5초
        else:
            complexity = "high"
            estimated_time = 10000  # 10초

        reasons = []
        if script_count > 5:
            reasons.append(f"{script_count}개 스크립트")
        if api_calls > 0:
            reasons.append(f"{api_calls}개 API 호출")
        if heavy_frameworks > 0:
            reasons.append("복잡한 프레임워크")

        return {
            "estimated_time_ms": estimated_time,
            "complexity": complexity,
            "reasons": reasons
        }

    def optimize_rendering_config(self, html: str, base_url: str = "") -> Dict:
        """
        렌더링 설정 최적화

        Returns:
            {
                "use_playwright": bool,
                "wait_for_selector": Optional[str],
                "wait_for_timeout_ms": int,
                "js_disable_after_load": bool
            }
        """
        needs_rendering, reason = self.should_use_js_rendering(html, base_url)
        completeness = self.get_content_completeness(html)
        time_estimate = self.estimate_render_time(html)

        # Playwright 사용 여부
        use_playwright = needs_rendering

        # 대기 선택자 (콘텐츠가 로드될 때까지)
        wait_for_selector = None
        if needs_rendering:
            # 일반적인 콘텐츠 컨테이너 선택자 추측
            if ".container" in html.lower():
                wait_for_selector = ".container"
            elif "[data-content]" in html.lower():
                wait_for_selector = "[data-content]"
            else:
                wait_for_selector = "main, .main-content, #content"

        # 대기 시간 (추정 시간 + 여유)
        wait_timeout_ms = time_estimate["estimated_time_ms"] + 2000

        # JS 렌더링 후 비활성화 (성능 개선)
        js_disable_after_load = needs_rendering and completeness["completeness"] > 70

        return {
            "use_playwright": use_playwright,
            "wait_for_selector": wait_for_selector,
            "wait_for_timeout_ms": wait_timeout_ms,
            "js_disable_after_load": js_disable_after_load,
            "reason": reason
        }


# ===================== 사용 예시 =====================

def example_js_optimizer():
    """JS 렌더링 최적화 예시"""
    optimizer = JSRendererOptimizer()

    html = """
    <html>
        <head>
            <script src="https://example.com/app.js"></script>
        </head>
        <body>
            <div id="app"></div>
            <script>
                fetch('/api/data').then(r => r.json()).then(data => {
                    document.getElementById('app').innerHTML = data.html;
                });
            </script>
        </body>
    </html>
    """

    # JS 렌더링 필요 여부
    needs_rendering, reason = optimizer.should_use_js_rendering(html)
    print(f"\nJS 렌더링 필요: {needs_rendering} ({reason})")

    # 콘텐츠 완성도
    completeness = optimizer.get_content_completeness(html)
    print(f"콘텐츠 완성도: {completeness['completeness']}%")

    # 렌더링 시간 추정
    time_est = optimizer.estimate_render_time(html)
    print(f"예상 렌더링 시간: {time_est['estimated_time_ms']}ms ({time_est['complexity']} 복잡도)")

    # 최적화된 설정
    config = optimizer.optimize_rendering_config(html, "https://kaist.ac.kr")
    print(f"최적화된 설정: {config}")


if __name__ == "__main__":
    example_js_optimizer()
