import httpx
from typing import Generator, List
from src.core.models import Post

def fetch_posts_stream(url: str, chunk_size: int = 10) -> Generator[List[Post], None, None]:
    """
    Fetches posts from the API and yields them in small chunks.
    This prevents blocking the pipeline while waiting for the full dataset.
    """
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        all_posts = response.json()
        
        for i in range(0, len(all_posts), chunk_size):
            yield [Post(**p) for p in all_posts[i : i + chunk_size]]