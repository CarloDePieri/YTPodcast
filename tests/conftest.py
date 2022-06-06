import dataclasses
import json
import uuid
from typing import Union, Dict

import redis as _redis
from pytube import Channel, Playlist
from vcr.errors import CannotOverwriteExistingCassetteException

from ytpodcast.cache import RedisCache, ShelveCache
from ytpodcast.api import get_stream_url
from tests.vcr_config import *


@dataclasses.dataclass
class TestVideoData:
    id: str
    title: str
    description: str
    thumbnail: str
    url: str
    length: int


class TestData:
    video_id: str
    video_url: str
    stream_url: str
    video_data_str: str
    video_data_dict: Dict[str, Union[str, int]]
    video_data: TestVideoData
    channel_url: str
    playlist_id: str
    playlist_url: str
    channel_video_list: List[str]
    playlist_video_list: List[str]


# This will be populated by the fixture below after the session starts
test_data = TestData()


@pytest.fixture(scope="session", autouse=True)
def prep_test_data(request):
    """Cache some test data."""
    test_root_dir = f"{request.config.rootdir}/tests"
    with open(f"{test_root_dir}/test_data.json", "r") as f:
        data = json.load(f)

    test_data.video_id = data["video_id"]
    test_data.video_url = f"https://www.youtube.com/watch?v={test_data.video_id}"
    test_data.stream_url = get_stream_url(test_data.video_id)
    test_data.video_data_str = data["video_data"].replace(
        "test_stream_url", test_data.stream_url
    )
    data_dict = json.loads(test_data.video_data_str)
    test_data.video_data_dict = data_dict
    test_data.video_data = TestVideoData(**data_dict)
    test_data.channel_url = data["channel_url"]
    test_data.playlist_id = data["playlist_id"]
    test_data.playlist_url = data["playlist_url"]

    with my_vcr.use_cassette(f"{test_root_dir}/cassettes/test_data.yaml"):
        test_data.channel_video_list = list(Channel(test_data.channel_url).video_urls)
        test_data.playlist_video_list = list(
            Playlist(test_data.playlist_url).video_urls
        )


@pytest.fixture
def fixture_from_param(request):
    """Hack to request a fixture passed by parametrize."""

    def wrapped(fixture_name: str):
        return request.getfixturevalue(fixture_name)

    return wrapped


@pytest.fixture(scope="session")
def redis():
    """Return a redis client valid for the whole test session."""
    return _redis.Redis(host="localhost", port=6379, db=0)


@pytest.fixture(scope="function")
def test_redis_cache():
    """Build a RedisCache usable in a test."""
    return RedisCache()


@pytest.fixture(scope="function")
def reset_test_video_redis_cache(redis):
    """Ensure the test video redis cache is purged after every test."""
    yield
    redis.delete(f"ytpodcast:video:{test_data.video_id}")


def _test_shelve_cache_db_path(request):
    return f"{request.config.rootdir}/tests/testdb"


@pytest.fixture(scope="function")
def test_shelve_cache_db_path(request):
    """Return the test ShelveCache db file path."""
    return _test_shelve_cache_db_path(request)


@pytest.fixture(scope="class")
def test_shelve_cache_db_path_cls(request):
    """Return the test ShelveCache db file path for a class setup."""
    return _test_shelve_cache_db_path(request)


@pytest.fixture(scope="function")
def test_shelve_cache(test_shelve_cache_db_path):
    """Build a ShelveCache usable in a test."""
    return ShelveCache(db_file=test_shelve_cache_db_path)


@pytest.fixture(scope="function")
def reset_test_video_shelve_cache(test_shelve_cache_db_path):
    """Ensure the test video Shelve cache is purged after every test."""
    yield
    os.remove(test_shelve_cache_db_path)


class NetworkCallMade(Exception):
    """Exception called if a network call has been made in a no_network_calls block."""


@contextmanager
def forbid_network_calls():
    """Trick to ensure no network call is made in a block, using vcrpy."""
    try:
        with my_vcr.use_cassette(str(uuid.uuid4()), record_mode="none"):
            yield
    except CannotOverwriteExistingCassetteException as e:
        raise NetworkCallMade(
            f"Made a network call to {e.failed_request.url} when it was not supposed to!"
        )
