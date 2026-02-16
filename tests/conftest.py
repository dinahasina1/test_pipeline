import pytest
from src.core.models import Post, User, EnrichedPost


@pytest.fixture
def sample_user():
    return User(userId=1, name="Test User", email="test@example.com")


@pytest.fixture
def sample_post():
    return Post(id=1, userId=1, title="Test title", body="Test body")


@pytest.fixture
def sample_post_no_user():
    return Post(id=99, userId=999, title="Orphan post", body="No matching user")


@pytest.fixture
def users_map(sample_user):
    return {1: sample_user, 2: User(userId=2, name="User 2", email="user2@example.com")}


@pytest.fixture
def post_chunks():
    def _chunks():
        yield [
            Post(id=1, userId=1, title="First", body="Body 1"),
            Post(id=2, userId=2, title="Second", body="Body 2"),
        ]
        yield [
            Post(id=3, userId=1, title="Third", body="Body 3"),
        ]
        yield [Post(id=4, userId=999, title="Orphan", body="No user")]
    return _chunks
