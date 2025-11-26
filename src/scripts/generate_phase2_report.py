import sys
import os
import json
from datetime import date, datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.domain.schemas import ResearchPaper
from src.services.llm import OllamaLLM, MockLLM
from src.services.pdf_generator import PDFGenerator

def generate_phase2_report():
    print("🚀 Starting Phase 2 Report Generation (Progressive Disclosure)...")

    # 1. Prepare Input Data (Mock Paper for Demo)
    paper = ResearchPaper(
        id="demo-paper-001",
        url="https://example.com/paper",
        title="Vision-Language Grounding for Robot Navigation",
        university="Seoul National University",
        department="Computer Science",
        pub_date=date(2024, 1, 1),
        content_raw="""
        This paper proposes a novel method for Vision-Language Grounding in the context of robot navigation.
        Vision-Language Grounding refers to the ability of an AI system to link natural language descriptions to visual objects in the real world.
        For example, when a user says "Go to the red chair near the window," the robot must identify the "red chair" and "window" in its visual input and understand the spatial relationship "near".
        We introduce a Transformer-based architecture that aligns visual features from a camera with textual embeddings from a language model.
        Our method achieves state-of-the-art performance on the REVERIE benchmark.
        The key contribution is a cross-modal attention mechanism that effectively filters out irrelevant visual information based on the linguistic query.
        This technology is crucial for service robots, autonomous vehicles, and smart home assistants.
        """
    )
    
    print(f"📄 Analyzing Paper: {paper.title}")

    # 2. Analyze with LLM
    # Try using OllamaLLM, fallback to MockLLM if it fails (or if you want to test the prompt, use Ollama)
    try:
        llm = OllamaLLM(model="qwen2.5:14b") # Use a capable model if available, or qwen2:7b
        # Check if ollama is reachable? Just try calling analyze.
        print("   Using OllamaLLM...")
        analysis_result = llm.analyze(paper)
    except Exception as e:
        print(f"⚠️  OllamaLLM failed: {e}")
        print("   Falling back to MockLLM (for demonstration purposes)...")
        llm = MockLLM()
        analysis_result = llm.analyze(paper)

    print("✅ Analysis Complete!")
    print(f"   Topic (Easy): {analysis_result.topic_easy}")
    print(f"   Topic (Tech): {analysis_result.topic_technical}")

    # 3. Prepare Data for PDF Report
    report_data = {
        "user_name": "Student",
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "interests": "AI, Robotics, Computer Vision",
        "analysis_results": [
            {
                "topic_easy": analysis_result.topic_easy,
                "topic_technical": analysis_result.topic_technical,
                "explanation": analysis_result.explanation,
                "reference_link": analysis_result.reference_link,
                "deep_dive": {
                    "keywords": analysis_result.deep_dive.keywords,
                    "recommendations": analysis_result.deep_dive.recommendations,
                    "related_concepts": analysis_result.deep_dive.related_concepts
                },
                "career_path": {
                    "job_title": analysis_result.career_path.job_title,
                    "companies": analysis_result.career_path.companies,
                    "avg_salary_hint": analysis_result.career_path.avg_salary_hint
                },
                "action_item": {
                    "subjects": analysis_result.action_item.subjects,
                    "research_topic": analysis_result.action_item.research_topic
                }
            }
        ]
    }

    # 4. Generate PDF
    pdf_generator = PDFGenerator(output_dir="docs/reports")
    filename = "Phase2_Progressive_Report.pdf"
    
    try:
        pdf_path = pdf_generator.generate(report_data, filename)
        print(f"\n🎉 Report Generated Successfully: {pdf_path}")
    except Exception as e:
        print(f"\n❌ PDF Generation Failed: {e}")

if __name__ == "__main__":
    generate_phase2_report()
