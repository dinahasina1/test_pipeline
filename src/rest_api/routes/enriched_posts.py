from fastapi import APIRouter
from src.shared.config import Config
from src.storage.sqlite_repo import SQLiteRepository

router = APIRouter(prefix="/enriched-posts", tags=["enriched-posts"])


@router.get("")
def list_enriched_posts():
    repo = SQLiteRepository(Config.DB_PATH)
    posts = repo.get_all_enriched_posts()
    return [p.model_dump(mode="json") for p in posts]
