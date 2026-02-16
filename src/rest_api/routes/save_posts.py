import json
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter
from src.core.models import EnrichedPost
from src.shared.config import Config

router = APIRouter(prefix="/save-posts", tags=["save-posts"])


@router.post("")
def save_post(posts: List[EnrichedPost]) -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"POST-{timestamp}.json"
    filepath = os.path.join(Config.BASE_DIR, "data", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([p.model_dump(mode="json") for p in posts], f, ensure_ascii=False, indent=2)
    return {"saved": filename, "count": len(posts)}
