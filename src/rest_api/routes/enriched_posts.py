from typing import List

from fastapi import APIRouter
from src.core.models import EnrichedPost
from src.shared.config import Config
from src.storage.sqlite_repo import SQLiteRepository

router = APIRouter(prefix="/enriched-posts", tags=["enriched-posts"])


@router.get("", response_model=List[EnrichedPost])
def list_enriched_posts() -> List[EnrichedPost]:
    repo = SQLiteRepository(Config.DB_PATH)
    return repo.get_all_enriched_posts()
