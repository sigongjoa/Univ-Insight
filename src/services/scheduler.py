"""
Scheduler Service for Univ-Insight.

Handles periodic tasks like weekly crawling and report generation.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from typing import Callable, Optional
from src.core.database import SessionLocal
from src.services.crawler import KaistCrawler
from src.services.llm import OllamaLLM
from src.domain.models import ResearchPaper, AnalysisResult


class SchedulerService:
    """
    Background scheduler for periodic tasks.
    """

    def __init__(self):
        """Initialize APScheduler"""
        self.scheduler = BackgroundScheduler()

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            print("[SchedulerService] Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[SchedulerService] Scheduler stopped")

    def schedule_weekly_crawler(
        self,
        crawler_func: Callable,
        day_of_week: str = "monday",
        hour: int = 9,
        minute: int = 0
    ):
        """
        Schedule weekly crawler job.

        Args:
            crawler_func: Function to execute
            day_of_week: Day to run (e.g., "monday", "wednesday")
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
        """
        try:
            trigger = CronTrigger(
                day_of_week=day_of_week,
                hour=hour,
                minute=minute
            )

            self.scheduler.add_job(
                crawler_func,
                trigger=trigger,
                id="weekly_crawler",
                name="Weekly Crawler Job",
                replace_existing=True
            )

            print(f"[SchedulerService] Scheduled weekly crawler for {day_of_week} {hour}:{minute}")

        except Exception as e:
            print(f"[SchedulerService] Error scheduling crawler: {e}")

    def schedule_daily_report_generation(
        self,
        report_func: Callable,
        hour: int = 18,
        minute: int = 0
    ):
        """
        Schedule daily report generation job.

        Args:
            report_func: Function to execute
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
        """
        try:
            trigger = CronTrigger(
                hour=hour,
                minute=minute
            )

            self.scheduler.add_job(
                report_func,
                trigger=trigger,
                id="daily_report_gen",
                name="Daily Report Generation Job",
                replace_existing=True
            )

            print(f"[SchedulerService] Scheduled daily report generation for {hour}:{minute}")

        except Exception as e:
            print(f"[SchedulerService] Error scheduling report generation: {e}")

    def schedule_interval_job(
        self,
        func: Callable,
        seconds: int,
        job_id: str,
        job_name: str
    ):
        """
        Schedule a job to run at regular intervals.

        Args:
            func: Function to execute
            seconds: Interval in seconds
            job_id: Job identifier
            job_name: Job name
        """
        try:
            self.scheduler.add_job(
                func,
                trigger="interval",
                seconds=seconds,
                id=job_id,
                name=job_name,
                replace_existing=True
            )

            print(f"[SchedulerService] Scheduled {job_name} every {seconds} seconds")

        except Exception as e:
            print(f"[SchedulerService] Error scheduling job: {e}")

    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            print(f"[SchedulerService] Removed job: {job_id}")
        except Exception as e:
            print(f"[SchedulerService] Error removing job: {e}")

    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()


class CrawlerTask:
    """Task for running crawler jobs"""

    @staticmethod
    def run_kaist_crawler():
        """Run KAIST crawler"""
        print("[CrawlerTask] Starting KAIST crawler...")
        db = SessionLocal()

        try:
            crawler = KaistCrawler()
            paper = crawler.crawl()

            if paper:
                # Save paper to database
                research_paper = ResearchPaper(
                    url=paper.url,
                    title=paper.title,
                    university=paper.source,
                    content_raw=paper.content,
                    pub_date=None  # Would be parsed from paper.date
                )
                db.add(research_paper)
                db.commit()

                print(f"[CrawlerTask] Saved paper: {paper.title}")
            else:
                print("[CrawlerTask] Crawler returned no result")

        except Exception as e:
            print(f"[CrawlerTask] Error: {e}")
            db.rollback()

        finally:
            db.close()

    @staticmethod
    def run_analysis_on_new_papers():
        """Analyze papers that haven't been analyzed yet"""
        print("[CrawlerTask] Starting analysis on new papers...")
        db = SessionLocal()

        try:
            # Find papers without analysis
            papers_without_analysis = db.query(ResearchPaper).filter(
                ~ResearchPaper.analysis_results.any()
            ).limit(10).all()

            llm = OllamaLLM()

            for paper in papers_without_analysis:
                # Import here to avoid circular imports
                from src.domain.schemas import ResearchPaper as ResearchPaperSchema

                paper_schema = ResearchPaperSchema(
                    source=paper.university,
                    title=paper.title,
                    content=paper.content_raw,
                    date=paper.pub_date.isoformat() if paper.pub_date else "",
                    url=paper.url
                )

                # Analyze using LLM
                result = llm.analyze(paper_schema)

                # Save analysis
                analysis = AnalysisResult(
                    paper_id=paper.id,
                    summary=result.research_summary,
                    job_title=result.career_path.job_title,
                    salary_hint=result.career_path.avg_salary_hint,
                    related_companies=result.career_path.companies,
                    action_items={
                        "subjects": result.action_item.subjects,
                        "research_topic": result.action_item.research_topic
                    }
                )
                db.add(analysis)

            db.commit()
            print(f"[CrawlerTask] Analyzed {len(papers_without_analysis)} papers")

        except Exception as e:
            print(f"[CrawlerTask] Error during analysis: {e}")
            db.rollback()

        finally:
            db.close()


def setup_default_scheduler() -> SchedulerService:
    """
    Set up scheduler with default jobs.

    Returns:
        Configured SchedulerService instance
    """
    scheduler = SchedulerService()

    # Schedule weekly crawler (Monday at 9 AM)
    scheduler.schedule_weekly_crawler(
        crawler_func=CrawlerTask.run_kaist_crawler,
        day_of_week="monday",
        hour=9,
        minute=0
    )

    # Schedule daily analysis (6 PM every day)
    scheduler.schedule_daily_report_generation(
        report_func=CrawlerTask.run_analysis_on_new_papers,
        hour=18,
        minute=0
    )

    return scheduler
