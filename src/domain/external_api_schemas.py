"""
Pydantic models for external API requests and responses.

Provides type-safe models for:
- Notion API (page creation, block updates)
- Kakao API (message delivery)
- GitHub API (trending repositories)
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum


# ==================== Notion API Models ====================

class NotionRichTextObject(BaseModel):
    """Notion rich text object for text content."""

    type: Literal["text"] = "text"
    text: Dict[str, str] = Field(...)  # {"content": "...", "link": null or url}
    annotations: Dict[str, bool] = Field(
        default_factory=lambda: {
            "bold": False, "italic": False, "strikethrough": False,
            "underline": False, "code": False, "color": "default"
        }
    )


class NotionParagraphBlock(BaseModel):
    """Notion paragraph block."""

    object: Literal["block"] = "block"
    type: Literal["paragraph"] = "paragraph"
    paragraph: Dict[str, Any] = Field(
        default_factory=lambda: {"rich_text": [], "color": "default"}
    )

    def set_text(self, text: str, bold: bool = False) -> "NotionParagraphBlock":
        """Set paragraph text."""
        self.paragraph["rich_text"] = [{
            "type": "text",
            "text": {"content": text},
            "annotations": {
                "bold": bold,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            }
        }]
        return self


class NotionHeadingBlock(BaseModel):
    """Notion heading block."""

    object: Literal["block"] = "block"
    type: Literal["heading_1", "heading_2", "heading_3"]
    heading_level: Optional[int] = None  # 1, 2, or 3

    def __init__(self, level: int = 1, **kwargs):
        """Initialize heading with level (1-3)."""
        super().__init__(**kwargs)
        self.type = f"heading_{level}"  # type: ignore

    def set_text(self, text: str) -> "NotionHeadingBlock":
        """Set heading text."""
        heading_key = self.type
        setattr(self, heading_key, {
            "rich_text": [{
                "type": "text",
                "text": {"content": text}
            }]
        })
        return self


class NotionPageCreateRequest(BaseModel):
    """Request body for creating a Notion page."""

    parent: Dict[str, str] = Field(...)  # {"database_id": "..."}
    properties: Dict[str, Any] = Field(...)
    children: Optional[List[Dict[str, Any]]] = None

    class Config:
        # Allow extra fields from Notion API
        extra = "allow"


class NotionPageUpdateRequest(BaseModel):
    """Request body for updating a Notion page."""

    properties: Dict[str, Any] = Field(...)


class NotionBlockAppendRequest(BaseModel):
    """Request body for appending blocks to a page."""

    children: List[Dict[str, Any]] = Field(...)


class NotionSearchRequest(BaseModel):
    """Request body for searching Notion."""

    query: str
    sort: Optional[Dict[str, str]] = None
    filter: Optional[Dict[str, str]] = None
    page_size: Optional[int] = 100


class NotionDatabaseQueryRequest(BaseModel):
    """Request body for querying a Notion database."""

    filter: Optional[Dict[str, Any]] = None
    sorts: Optional[List[Dict[str, Any]]] = None
    start_cursor: Optional[str] = None
    page_size: Optional[int] = 100


# ==================== Kakao API Models ====================

class KakaoTextMessage(BaseModel):
    """Kakao Text message."""

    object_type: Literal["text"] = "text"
    text: str = Field(..., max_length=1000)
    link: Optional[Dict[str, str]] = None


class KakaoCommerceMessage(BaseModel):
    """Kakao Commerce (product) message."""

    object_type: Literal["commerce"] = "commerce"
    title: str
    description: str
    image_url: HttpUrl
    link_web: str


class KakaoFeedMessage(BaseModel):
    """Kakao Feed message."""

    object_type: Literal["feed"] = "feed"
    id: str
    content: Dict[str, Any] = Field(...)
    social: Optional[Dict[str, Any]] = None
    buttons: Optional[List[Dict[str, Any]]] = None


class KakaoListMessage(BaseModel):
    """Kakao List message."""

    object_type: Literal["list"] = "list"
    buttons: List[Dict[str, str]]
    header_title: str
    header_image_url: Optional[HttpUrl] = None
    item_height: Optional[Literal["small", "medium", "large"]] = "medium"
    items: List[Dict[str, Any]] = Field(min_items=2, max_items=5)


class KakaoButton(BaseModel):
    """Kakao message button."""

    title: str = Field(..., max_length=14)
    type: Literal["WL", "WEB", "AL", "BK", "MD", "BC", "BT"] = "WEB"
    value: str


class KakaoTemplateObject(BaseModel):
    """Base Kakao template object."""

    object_type: str
    version: str = "2.0"
    template_id: Optional[str] = None
    template_args: Optional[Dict[str, str]] = None


class KakaoSendMessageRequest(BaseModel):
    """Request body for sending Kakao message."""

    receiver_uuid: str
    receiver_id: Optional[str] = None
    template_id: Optional[str] = None
    template_object: Optional[KakaoTemplateObject] = None
    text: Optional[str] = None
    button_title: Optional[str] = None
    button_url: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None

    @validator('receiver_uuid', 'receiver_id', pre=True)
    def require_receiver(cls, v):
        """Ensure at least one receiver is specified."""
        if not v:
            raise ValueError("Either receiver_uuid or receiver_id must be provided")
        return v


class KakaoSendMessageResponse(BaseModel):
    """Response from sending Kakao message."""

    success: bool
    message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


# ==================== GitHub API Models ====================

class GitHubRepository(BaseModel):
    """GitHub repository object."""

    id: int
    name: str
    full_name: str
    owner: Dict[str, Any]
    description: Optional[str] = None
    url: HttpUrl
    stars: int = Field(..., alias="stargazers_count")
    language: Optional[str] = None
    topics: Optional[List[str]] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class GitHubSearchRepositoriesRequest(BaseModel):
    """Request to search GitHub repositories."""

    query: str
    sort: Literal["stars", "forks", "updated"] = "stars"
    order: Literal["asc", "desc"] = "desc"
    per_page: int = Field(10, ge=1, le=100)
    page: int = Field(1, ge=1)


# ==================== Report Models ====================

class ReportSection(BaseModel):
    """A section of a generated report."""

    title: str
    content: str
    subsections: Optional[List["ReportSection"]] = None


class GeneratedReport(BaseModel):
    """A complete generated report."""

    title: str
    summary: str
    sections: List[ReportSection]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


# ==================== API Response Models ====================

class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Standard paginated response."""

    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# Update forward references for nested models
ReportSection.update_forward_refs()
