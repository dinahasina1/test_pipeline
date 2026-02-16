from fastapi import APIRouter
from src.shared.config import Config
from src.shared.logger import setup_logger
from src.storage.sqlite_repo import SQLiteRepository

router = APIRouter(prefix="/duplicate-posts", tags=["duplicate-posts"])
logger = setup_logger(__name__)


@router.get("/{start_id:int}/{end_id:int}")
def duplicate_posts(start_id: int, end_id: int) -> dict:
    if start_id > end_id:
        logger.warning(f"duplicate-posts: start_id {start_id} > end_id {end_id}")
        return {"success": 0, "error": "start_id must be <= end_id"}

    repo = SQLiteRepository(Config.DB_PATH)
    posts = repo.get_enriched_posts_by_range(start_id, end_id)

    if not posts:
        logger.warning(f"duplicate-posts: aucun post trouvé pour la plage {start_id}-{end_id}")
        return {"success": 0, "error": "aucun post trouvé"}

    max_id = repo.get_max_id()
    duplicates = [p.model_copy(update={"id": max_id + i + 1}) for i, p in enumerate(posts)]

    try:
        repo.save_enriched_posts(duplicates)
    except Exception as e:
        logger.error(f"duplicate-posts: erreur sauvegarde DB - {e}")
        return {"success": 0, "error": str(e)}
    return {"success": len(duplicates)}
