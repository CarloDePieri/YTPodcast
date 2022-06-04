import redis as _redis


from tests.vcr_config import *


test_video_id = "BaW_jenozKc"
test_video_data_bytes = b'{"id": "BaW_jenozKc", "title": "youtube-dl test video \\"\'/\\\\\\u00e4\\u21ad\\ud835\\udd50", "description": "test chars:  \\"\'/\\\\\\u00e4\\u21ad\\ud835\\udd50\\ntest URL: https://github.com/rg3/youtube-dl/issues/1892\\n\\nThis is a test video for youtube-dl.\\n\\nFor more information, contact phihag@phihag.de .", "thumbnail": "https://i.ytimg.com/vi/BaW_jenozKc/sddefault.jpg", "url": "/api/stream/BaW_jenozKc", "length": 10}'


@pytest.fixture(scope="session")
def redis():
    """Return a redis client valid for the whole test session."""
    return _redis.Redis(host="localhost", port=6379, db=0)


@pytest.fixture(scope="function")
def reset_cache_after_every_test(redis):
    """Ensure the test video cache is purged after every test."""
    yield
    redis.delete(test_video_id)
