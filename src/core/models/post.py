from pydantic import BaseModel, Field

class Post(BaseModel):
    """
    Represents a raw post fetched from the external JSON API.
    Handles field mapping for consistent internal usage.
    """
    id: int
    user_id: int = Field(alias="userId")
    title: str
    body: str

    class Config:
        populate_by_name = True