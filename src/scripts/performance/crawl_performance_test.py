
import asyncio
import time
import statistics
import os
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.article_crawler import ArticleCrawler

class CrawlPerformanceTest:
    """
    ArticleCrawler의 성능을 측정합니다.
    """

    def __init__(self, urls_to_test: list):
        self.urls = urls_to_test
        self.crawler = ArticleCrawler()

    async def measure_crawl_speed(self):
        """
        지정된 URL 목록에 대해 크롤링 속도를 측정하고 통계를 출력합니다.
        """
        if not self.urls:
            print("테스트할 URL이 없습니다.")
            return None

        print(f"총 {len(self.urls)}개의 URL에 대한 성능 측정을 시작합니다...")
        times = []

        for i, url in enumerate(self.urls, 1):
            print(f"[{i}/{len(self.urls)}] 크롤링 중: {url}")
            start_time = time.time()
            
            paper = await self.crawler.crawl(url=url, university="KAIST", department="CS")
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            if paper:
                print(f"  -> 완료: {elapsed:.2f}초, 제목: {paper.title[:30]}...")
                times.append(elapsed)
            else:
                print(f"  -> 실패: {elapsed:.2f}초")

        if not times:
            print("\n모든 크롤링에 실패하여 성능을 측정할 수 없습니다.")
            return None

        results = {
            "total_urls": len(self.urls),
            "successful_crawls": len(times),
            "failed_crawls": len(self.urls) - len(times),
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "min_time": min(times),
            "max_time": max(times),
            "stdev_time": statistics.stdev(times) if len(times) > 1 else 0.0
        }

        print("\n--- 성능 측정 결과 ---")
        print(f"총 URL 수: {results['total_urls']}")
        print(f"성공한 크롤링: {results['successful_crawls']}")
        print(f"실패한 크롤링: {results['failed_crawls']}")
        print(f"평균 소요 시간: {results['mean_time']:.2f}초")
        print(f"중앙값 소요 시간: {results['median_time']:.2f}초")
        print(f"최소 소요 시간: {results['min_time']:.2f}초")
        print(f"최대 소요 시간: {results['max_time']:.2f}초")
        print(f"표준 편차: {results['stdev_time']:.2f}초")
        print("------------------------")

        return results

def main():
    # KAIST CS 연구 뉴스 페이지의 실제 URL 목록
    # 이 URL들은 변경될 수 있습니다.
    test_urls = [
        "https://cs.kaist.ac.kr/news/read?id=5218",
        "https://cs.kaist.ac.kr/news/read?id=5214",
        "https://cs.kaist.ac.kr/news/read?id=5212",
        "https://cs.kaist.ac.kr/news/read?id=5209",
        "https://cs.kaist.ac.kr/news/read?id=5205",
    ]
    
    performance_tester = CrawlPerformanceTest(urls_to_test=test_urls)
    asyncio.run(performance_tester.measure_crawl_speed())

if __name__ == '__main__':
    main()
