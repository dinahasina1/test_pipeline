from datetime import datetime
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