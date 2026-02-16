from datetime import datetime
from typing import Any
from pydantic import BaseModel, EmailStr, Field

from src.core.models.post import Post
from src.core.models.user import User


class EnrichedPost(BaseModel):
    """
    Domain entity representing the final enriched data structure.
    Includes calculated metrics and ingestion metadata.
    """
    id: int
    user_id: int
    email: EmailStr
    title: str
    body: str
    
    title_length: int
    ingested_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def create(cls, post: Post, user: User):
        """
        Factory method to merge Post and User entities.
        Encapsulates the transformation and length calculation logic.
        """
        return cls(
            id=post.id,
            user_id=post.user_id,
            email=user.email,
            title=post.title,
            body=post.body,
            title_length=len(post.title)
        )

    def to_db_row(self) -> tuple:
        return (
            self.id,
            self.user_id,
            self.email,
            self.title,
            self.body,
            self.title_length,
            self.ingested_at,
        )

    @classmethod
    def from_db_row(cls, row: Any) -> "EnrichedPost":
        ingested = row["ingested_at"]
        if isinstance(ingested, str):
            ingested = datetime.fromisoformat(ingested.replace("Z", "+00:00"))
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            email=row["email"],
            title=row["title"],
            body=row["body"],
            title_length=row["title_length"],
            ingested_at=ingested,
        )