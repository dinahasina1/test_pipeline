import sqlite3
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
        data = [p.to_db_row() for p in posts]
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(query, data)
            conn.commit()

    def get_all_enriched_posts(self) -> List[EnrichedPost]:
        query = "SELECT id, user_id, email, title, body, title_length, ingested_at FROM posts_enriched"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
        return [EnrichedPost.from_db_row(row) for row in rows]

    def get_enriched_post_by_id(self, post_id: int) -> Optional[EnrichedPost]:
        query = "SELECT id, user_id, email, title, body, title_length, ingested_at FROM posts_enriched WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(query, (post_id,)).fetchone()
        return EnrichedPost.from_db_row(row) if row else None

    def get_enriched_posts_by_range(self, start_id: int, end_id: int) -> List[EnrichedPost]:
        query = "SELECT id, user_id, email, title, body, title_length, ingested_at FROM posts_enriched WHERE id BETWEEN ? AND ? ORDER BY id"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (start_id, end_id)).fetchall()
        return [EnrichedPost.from_db_row(row) for row in rows]

    def get_max_id(self) -> int:
        query = "SELECT COALESCE(MAX(id), 0) FROM posts_enriched"
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query).fetchone()[0]
