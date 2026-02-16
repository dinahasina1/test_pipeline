import sqlite3
from typing import List

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
