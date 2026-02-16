import pytest
from src.core.models import Post, User, EnrichedPost
from src.core.processing.transform import stream_enrichment


class TestStreamEnrichment:
    def test_enriches_post_with_matching_user(self, sample_post, sample_user, users_map):
        chunks = iter([[sample_post]])
        result = list(stream_enrichment(chunks, users_map))
        assert len(result) == 1
        assert len(result[0]) == 1
        enriched = result[0][0]
        assert isinstance(enriched, EnrichedPost)
        assert enriched.id == 1
        assert enriched.user_id == 1
        assert enriched.email == sample_user.email
        assert enriched.title == sample_post.title
        assert enriched.body == sample_post.body
        assert enriched.title_length == len(sample_post.title)

    def test_excludes_post_without_matching_user(self, sample_post_no_user, users_map):
        chunks = iter([[sample_post_no_user]])
        result = list(stream_enrichment(chunks, users_map))
        assert len(result) == 1
        assert len(result[0]) == 0

    def test_streams_chunk_by_chunk(self, post_chunks, users_map):
        result = list(stream_enrichment(post_chunks(), users_map))
        assert len(result) == 3
        assert len(result[0]) == 2
        assert len(result[1]) == 1
        assert len(result[2]) == 0

    def test_enriched_data_integrity_per_chunk(self, post_chunks, users_map):
        for chunk in stream_enrichment(post_chunks(), users_map):
            for enriched in chunk:
                assert enriched.id > 0
                assert enriched.user_id in users_map
                assert enriched.email == users_map[enriched.user_id].email
                assert enriched.title_length == len(enriched.title)
