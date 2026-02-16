import pytest
from src.core.models import Post, User, EnrichedPost
from src.core.processing.transform import stream_enrichment


def post_chunk_generator(*chunk_sizes):
    post_id = 1
    for size in chunk_sizes:
        chunk = []
        for _ in range(size):
            user_id = (post_id % 2) + 1
            chunk.append(
                Post(
                    id=post_id,
                    userId=user_id,
                    title=f"Title {post_id}",
                    body=f"Body {post_id}",
                )
            )
            post_id += 1
        yield chunk


class TestStreamChunkByChunk:
    def test_yields_immediately_per_chunk(self, users_map):
        gen = stream_enrichment(post_chunk_generator(2, 1, 3), users_map)
        first = next(gen)
        assert len(first) == 2
        second = next(gen)
        assert len(second) == 1
        third = next(gen)
        assert len(third) == 3

    def test_empty_chunk_yields_empty_list(self, users_map):
        gen = stream_enrichment(post_chunk_generator(0, 1), users_map)
        first = next(gen)
        assert first == []
        second = next(gen)
        assert len(second) == 1

    def test_all_enriched_are_pydantic_models(self, users_map):
        for chunk in stream_enrichment(post_chunk_generator(2, 2), users_map):
            for item in chunk:
                assert isinstance(item, EnrichedPost)
                assert hasattr(item, "model_dump")
