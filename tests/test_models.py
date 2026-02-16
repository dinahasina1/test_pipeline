import pytest
from datetime import datetime
from src.core.models import Post, User, EnrichedPost


class TestEnrichedPost:
    def test_create_merges_post_and_user(self, sample_post, sample_user):
        enriched = EnrichedPost.create(sample_post, sample_user)
        assert enriched.id == sample_post.id
        assert enriched.user_id == sample_post.user_id
        assert enriched.email == sample_user.email
        assert enriched.title_length == len(sample_post.title)

    def test_to_db_row_returns_tuple(self, sample_post, sample_user):
        enriched = EnrichedPost.create(sample_post, sample_user)
        row = enriched.to_db_row()
        assert isinstance(row, tuple)
        assert len(row) == 7
        assert row[0] == enriched.id
        assert row[2] == enriched.email

    def test_from_db_row_restores_enriched_post(self, sample_post, sample_user):
        enriched = EnrichedPost.create(sample_post, sample_user)
        row = {
            "id": enriched.id,
            "user_id": enriched.user_id,
            "email": str(enriched.email),
            "title": enriched.title,
            "body": enriched.body,
            "title_length": enriched.title_length,
            "ingested_at": enriched.ingested_at.isoformat(),
        }
        restored = EnrichedPost.from_db_row(row)
        assert restored.id == enriched.id
        assert restored.email == enriched.email
