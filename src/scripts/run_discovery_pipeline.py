
import asyncio
import os
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.index_crawler import IndexCrawler
from services.article_crawler import ArticleCrawler
from services.llm import OllamaLLM
from services.pipeline_service import PipelineService

async def main():
    """
    새로운 동적 디스커버리 파이프라인을 실행합니다.
    1. IndexCrawler로 기사 목록을 찾습니다.
    2. 찾은 기사 중 하나를 ArticleCrawler와 LLM으로 처리합니다.
    """
    # 1. 설정
    # 실패했던 동적 탐색 대신, 알려진 연구소식 인덱스 페이지에서 직접 시작
    index_url = "https://cs.kaist.ac.kr/news/research"
    db_path = "univ_insight.db"
    
    print("--- Univ-Insight Dynamic Discovery Pipeline ---")
    print(f"Starting from index URL: {index_url}")
    print("-------------------------------------------")

    # 2. 서비스 컴포넌트 초기화
    index_crawler = IndexCrawler()
    article_crawler = ArticleCrawler()
    llm_service = OllamaLLM(model="llama2")
    pipeline = PipelineService(
        crawler=article_crawler,
        llm_service=llm_service,
        db_path=db_path
    )

    # 3. 기사 목록 동적 탐색
    print("\n[1/3] Discovering article links...")
    article_links = await index_crawler.extract_links_from_index(index_url)

    if not article_links:
        print("\n[FAIL] No articles found. Aborting pipeline.")
        return

    print(f"\n[SUCCESS] Discovered {len(article_links)} articles.")
    
    # 4. 첫 번째 기사에 대해 전체 파이프라인 실행
    target_title, target_url = article_links[0]
    print(f"\n[2/3] Processing first article: '{target_title}'")
    print(f"URL: {target_url}")

    try:
        analysis_result = await pipeline.process_url(
            url=target_url,
            university="KAIST",
            department="CS"
        )
        
        if analysis_result:
            print("\n[3/3] Pipeline Completed Successfully!")
            print("--- Analysis Result ---")
            print(f"Title: {analysis_result.title}")
            print(f"Summary: {analysis_result.research_summary}")
            print(f"Job Title: {analysis_result.career_path.job_title}")
            print("-----------------------")
        else:
            print("\n[3/3] Pipeline Failed for the selected article.")

    except Exception as e:
        print(f"\n--- PIPELINE FAILED ---")
        print(f"An unhandled exception occurred: {type(e).__name__}")
        print(f"Error details: {e}")
        print("-----------------------")


if __name__ == '__main__':
    # 경고: 이 스크립트는 실제 웹사이트와 Ollama 서비스에 직접 접근합니다.
    # 외부 요인에 의해 실패할 수 있습니다.
    # 로컬에서 'ollama run llama2'가 실행 중이어야 합니다.
    asyncio.run(main())
