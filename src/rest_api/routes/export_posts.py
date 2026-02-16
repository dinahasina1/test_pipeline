import json
import os
from datetime import datetime

from fastapi import APIRouter
from src.shared.config import Config
from src.shared.logger import setup_logger
from src.storage.sqlite_repo import SQLiteRepository

router = APIRouter(prefix="/export-posts", tags=["export-posts"])
logger = setup_logger(__name__)


@router.get("/{start_id:int}/{end_id:int}")
def export_posts(start_id: int, end_id: int) -> dict:
    if start_id > end_id:
        logger.warning(f"export-posts: start_id {start_id} > end_id {end_id}")
        return {"success": 0, "error": "start_id must be <= end_id"}

    repo = SQLiteRepository(Config.DB_PATH)
    posts = repo.get_enriched_posts_by_range(start_id, end_id)

    if not posts:
        logger.warning(f"export-posts: aucun post trouvé pour la plage {start_id}-{end_id}")
        return {"success": 0, "error": "aucun post trouvé"}

    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"EXPORT-{start_id}-{end_id}-{timestamp}.json"
    filepath = os.path.join(Config.BASE_DIR, "data", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in posts], f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error(f"export-posts: erreur écriture {filename} - {e}")
        return {"success": 0, "error": str(e)}

    return {"success": len(posts), "file": filename}
