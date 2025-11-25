
import asyncio
import os
import sys

# 프로젝트 루트를 sys.path에 추가
# 이 스크립트는 루트 디렉토리에 있으므로, src를 경로에 추가합니다.
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.article_crawler import ArticleCrawler
from services.llm import OllamaLLM
from services.pipeline_service import PipelineService

async def main():
    """
    실제 크롤러와 LLM을 사용하여 E2E 파이프라인을 실행합니다.
    """
    # 1. 설정
    # 이전에 소프트 404를 반환했던 실제 URL
    # URL이 유효하지 않으면, 이제 예외 처리 없이 바로 오류가 발생합니다.
    target_url = "https://cs.kaist.ac.kr/news/read?id=5218"
    db_path = "univ_insight.db"
    
    print("--- Univ-Insight Real-Run Pipeline ---")
    print(f"Target URL: {target_url}")
    print(f"Database: {db_path}")
    print("------------------------------------")

    # 2. 실제 서비스 컴포넌트 초기화
    # 로컬에서 Ollama 서버가 실행 중이어야 합니다.
    # 예: ollama run llama2
    crawler = ArticleCrawler()
    llm_service = OllamaLLM(model="llama2") 
    
    pipeline = PipelineService(
        crawler=crawler,
        llm_service=llm_service,
        db_path=db_path
    )

    # 3. 파이프라인 실행
    print("\n[1/2] Starting Article Crawling...")
    try:
        analysis_result = await pipeline.process_url(
            url=target_url,
            university="KAIST",
            department="CS"
        )
        
        if analysis_result:
            print("\n[2/2] Pipeline Completed Successfully!")
            print("--- Analysis Result ---")
            print(f"Title: {analysis_result.title}")
            print(f"Summary: {analysis_result.research_summary}")
            print(f"Job Title: {analysis_result.career_path.job_title}")
            print("-----------------------")
        else:
            print("\n[2/2] Pipeline Failed. See logs for details.")

    except Exception as e:
        print(f"\n--- PIPELINE FAILED ---")
        print(f"An unhandled exception occurred: {type(e).__name__}")
        print(f"Error details: {e}")
        print("-----------------------")


if __name__ == '__main__':
    # 경고: 이 스크립트는 예외 처리가 대부분 제거된 서비스를 사용하므로,
    # 외부 서비스(웹사이트, Ollama)의 상태에 따라 예기치 않게 중단될 수 있습니다.
    asyncio.run(main())
