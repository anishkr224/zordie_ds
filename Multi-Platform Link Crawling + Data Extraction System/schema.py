from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EngagementStats(BaseModel):
    followers: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0

class ContentTypes(BaseModel):
    projects: list = []
    posts: list = []
    contributions: list = []

class ProfileMetadata(BaseModel):
    platform: str
    link_type: str
    url: str
    is_public: bool
    engagement_stats: EngagementStats
    content_types: ContentTypes
    relevance_score: float = 0.0
    last_activity: Optional[datetime] = None
    crawl_date: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_schema_extra": {  # Changed from schema_extra to json_schema_extra
            "example": {
                "platform": "github",
                "link_type": "profile",
                "url": "https://github.com/username",
                "is_public": True,
                "engagement_stats": {
                    "followers": 100,
                    "likes": 500,
                    "comments": 200,
                    "shares": 50
                },
                "content_types": {
                    "projects": ["project1", "project2"],
                    "posts": [],
                    "contributions": ["contrib1"]
                },
                "relevance_score": 85.5,
                "last_activity": "2025-05-18T10:30:00"
            }
        }
    }