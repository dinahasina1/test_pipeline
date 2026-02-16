from typing import Generator, List, Dict
from src.core.models import User, Post, EnrichedPost

def stream_enrichment(
    post_chunks: Generator[List[Post], None, None], 
    users_map: Dict[int, User]
) -> Generator[List[EnrichedPost], None, None]:
    """
    Processes post chunks and yields enriched data as soon as matching users are found.
    Non-blocking transformation logic.
    """
    for chunk in post_chunks:
        enriched_chunk = []
        for post in chunk:
            user = users_map.get(post.user_id)
            if user:
                enriched_chunk.append(EnrichedPost.create(post, user))
        
        yield enriched_chunk