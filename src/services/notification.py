"""
Notification Service for Univ-Insight.

Handles sending reports to users via Notion and Kakao Talk.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime


class NotionService:
    """
    Service for creating and managing Notion pages.
    Converts analysis results into Notion blocks.
    """

    def __init__(self, api_key: str, database_id: str):
        """
        Initialize Notion service.

        Args:
            api_key: Notion API key
            database_id: Database ID to create pages in
        """
        self.api_key = api_key
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def create_report_page(
        self,
        title: str,
        papers: List[Dict],
        user_name: str = "User"
    ) -> Optional[str]:
        """
        Create a Notion page with research report.

        Args:
            title: Page title
            papers: List of paper data dicts with 'title', 'summary', 'career_path'
            user_name: Name of the user receiving the report

        Returns:
            Notion page URL or None if failed
        """
        try:
            # Prepare page content
            children = self._prepare_report_blocks(papers, user_name)

            # Create page
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                },
                "children": children
            }

            response = requests.post(
                "https://api.notion.com/v1/pages",
                json=payload,
                headers=self.headers
            )

            if response.status_code == 200:
                page_data = response.json()
                page_url = page_data.get("url")
                print(f"[NotionService] Page created: {page_url}")
                return page_url
            else:
                print(f"[NotionService] Error creating page: {response.text}")
                return None

        except Exception as e:
            print(f"[NotionService] Exception: {e}")
            return None

    def _prepare_report_blocks(
        self,
        papers: List[Dict],
        user_name: str
    ) -> List[Dict]:
        """Prepare Notion blocks for the report"""
        blocks = []

        # Title block
        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"Weekly Research Digest for {user_name}"
                        }
                    }
                ]
            }
        })

        # Date block
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"Generated: {datetime.now().strftime('%Y-%m-%d')}"
                        },
                        "annotations": {"italic": True}
                    }
                ]
            }
        })

        # Paper blocks
        for paper in papers:
            # Paper title
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": paper.get("title", "Untitled")
                            }
                        }
                    ]
                }
            })

            # University
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"University: {paper.get('university', 'Unknown')}"
                            }
                        }
                    ]
                }
            })

            # Summary
            if paper.get("summary"):
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": paper["summary"][:500]
                                }
                            }
                        ]
                    }
                })

            # Career info
            career = paper.get("career_path", {})
            if career:
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"💼 Job: {career.get('job_title', 'N/A')} | Companies: {', '.join(career.get('companies', []))}"
                                }
                            }
                        ]
                    }
                })

            # Divider
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

        return blocks


class KakaoService:
    """
    Service for sending Kakao Talk messages.
    """

    def __init__(self, api_key: str):
        """
        Initialize Kakao service.

        Args:
            api_key: Kakao API key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }

    def send_message(
        self,
        user_id: str,
        message: str,
        link_url: Optional[str] = None
    ) -> bool:
        """
        Send a Kakao Talk message to user.

        Args:
            user_id: Kakao user ID
            message: Message content
            link_url: Optional link to include in message

        Returns:
            True if successful, False otherwise
        """
        try:
            # Kakao API endpoint for sending messages
            url = "https://kapi.kakao.com/v2/api/talk/memo/send"

            payload = {
                "template_object": {
                    "object_type": "text",
                    "text": message,
                    "link": {
                        "web_url": link_url or "https://univ-insight.com"
                    }
                }
            }

            response = requests.post(
                url,
                json=payload,
                headers=self.headers
            )

            if response.status_code == 200:
                print(f"[KakaoService] Message sent to {user_id}")
                return True
            else:
                print(f"[KakaoService] Error sending message: {response.text}")
                return False

        except Exception as e:
            print(f"[KakaoService] Exception: {e}")
            return False

    def send_report_notification(
        self,
        user_id: str,
        report_url: str,
        paper_count: int
    ) -> bool:
        """
        Send a report notification to user.

        Args:
            user_id: Kakao user ID
            report_url: URL to the Notion report page
            paper_count: Number of papers in the report

        Returns:
            True if successful, False otherwise
        """
        message = f"📚 Your weekly research digest is ready! {paper_count} papers have been curated based on your interests. Check it out here: {report_url}"

        return self.send_message(user_id, message, report_url)


class NotificationManager:
    """
    Unified notification service managing multiple channels.
    """

    def __init__(
        self,
        notion_api_key: Optional[str] = None,
        notion_database_id: Optional[str] = None,
        kakao_api_key: Optional[str] = None
    ):
        """
        Initialize notification manager.

        Args:
            notion_api_key: Notion API key
            notion_database_id: Notion database ID
            kakao_api_key: Kakao API key
        """
        self.notion_service = None
        self.kakao_service = None

        if notion_api_key and notion_database_id:
            self.notion_service = NotionService(notion_api_key, notion_database_id)

        if kakao_api_key:
            self.kakao_service = KakaoService(kakao_api_key)

    def send_report(
        self,
        user_id: str,
        user_name: str,
        papers: List[Dict],
        channels: List[str] = ["notion", "kakao"]
    ) -> Dict:
        """
        Send report to user via specified channels.

        Args:
            user_id: User identifier
            user_name: User name
            papers: List of papers to include
            channels: Channels to send to ("notion", "kakao")

        Returns:
            Dict with delivery status for each channel
        """
        results = {}

        # Send via Notion
        if "notion" in channels and self.notion_service:
            notion_url = self.notion_service.create_report_page(
                title=f"Research Report - {user_name}",
                papers=papers,
                user_name=user_name
            )
            results["notion"] = {
                "status": "success" if notion_url else "failed",
                "url": notion_url
            }

        # Send via Kakao
        if "kakao" in channels and self.kakao_service:
            kakao_success = self.kakao_service.send_report_notification(
                user_id=user_id,
                report_url=results.get("notion", {}).get("url", ""),
                paper_count=len(papers)
            )
            results["kakao"] = {
                "status": "success" if kakao_success else "failed"
            }

        return results
