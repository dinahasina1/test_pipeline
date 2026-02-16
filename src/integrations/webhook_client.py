import httpx
from typing import List

from src.shared.config import Config
from src.storage.sqlite_repo import SQLiteRepository


class WebhookClient:
    def __init__(self, url: str):
        self.url = url

    def send_sample(self, sample: List) -> None:
        with httpx.Client() as client:
            client.post(self.url, json=[p.model_dump(mode="json") for p in sample])

    def send_first_chunk_to_external(self, repo: SQLiteRepository) -> None:
        """Vérifie le dernier id des enriched posts, récupère le premier chunk stocké,
        et l'envoie vers EXTERNAL_WEBHOOK_URL (save-posts)."""
        max_id = repo.get_max_id()
        if max_id == 0:
            return
        first_chunk = repo.get_enriched_posts_by_range(1, Config.CHUNK_SIZE)
        if first_chunk:
            self.send_sample(first_chunk)
