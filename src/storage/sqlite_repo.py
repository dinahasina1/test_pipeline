import sqlite3
from datetime import datetime
from typing import List, Optional

from src.core.models import EnrichedPost


class SQLiteRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS posts_enriched (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            email TEXT,
            title TEXT,
            body TEXT,
            title_length INTEGER,
            ingested_at DATETIME
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query)

    def save_enriched_posts(self, posts: List[EnrichedPost]):
        query = """
        INSERT OR IGNORE INTO posts_enriched 
        (id, user_id, email, title, body, title_length, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        data = [
            (p.id, p.user_id, p.email, p.title, p.body, p.title_length, p.ingested_at)
            for p in posts
        ]
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(query, data)
            conn.commit()

    def get_all_enriched_posts(self) -> List[EnrichedPost]:
        query = "SELECT id, user_id, email, title, body, title_length, ingested_at FROM posts_enriched"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
        return [_row_to_enriched_post(row) for row in rows]

    def get_enriched_post_by_id(self, post_id: int) -> Optional[EnrichedPost]:
        query = "SELECT id, user_id, email, title, body, title_length, ingested_at FROM posts_enriched WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(query, (post_id,)).fetchone()
        return _row_to_enriched_post(row) if row else None


def _row_to_enriched_post(row: sqlite3.Row) -> EnrichedPost:
    ingested = row["ingested_at"]
    if isinstance(ingested, str):
        ingested = datetime.fromisoformat(ingested.replace("Z", "+00:00"))
    return EnrichedPost(
        id=row["id"],
        user_id=row["user_id"],
        email=row["email"],
        title=row["title"],
        body=row["body"],
        title_length=row["title_length"],
        ingested_at=ingested,
    )
