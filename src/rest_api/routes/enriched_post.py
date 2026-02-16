from fastapi import APIRouter, HTTPException
from src.shared.config import Config
from src.storage.sqlite_repo import SQLiteRepository

router = APIRouter(prefix="/enriched-posts", tags=["enriched-posts"])


@router.get("/{post_id:int}")
def get_enriched_post(post_id: int):
    repo = SQLiteRepository(Config.DB_PATH)
    post = repo.get_enriched_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.model_dump(mode="json")
