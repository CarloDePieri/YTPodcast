import json
import redis as _redis

from tests.vcr_config import *
from pytube import Channel, Playlist


#
# Cache some test data
#
with open("test_data.json", "r") as f:
    test_data = json.load(f)

test_video_id = test_data["video_id"]
test_video_url = f"https://www.youtube.com/watch?v={test_video_id}"
test_video_data = json.loads(test_data["video_data"])
test_channel_url = test_data["channel_url"]
test_playlist_url = test_data["playlist_url"]

with my_vcr.use_cassette("cassettes/test_data.yaml"):
    test_channel_video_list = list(Channel(test_channel_url).video_urls)
    test_playlist_video_list = list(Playlist(test_playlist_url).video_urls)


@pytest.fixture(scope="session")
def redis():
    """Return a redis client valid for the whole test session."""
    return _redis.Redis(host="localhost", port=6379, db=0)


@pytest.fixture(scope="function")
def reset_video_cache_after_every_test(redis):
    """Ensure the test video cache is purged after every test."""
    yield
    redis.delete(test_video_id)
