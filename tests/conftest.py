import dataclasses
import json
from typing import Union, Dict

import redis as _redis

from pytube import Channel, Playlist

from ytpodcast.api import get_stream_url
from tests.vcr_config import *

import pytest


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
    with open(f"{request.config.rootdir}/test_data.json", "r") as f:
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

    with my_vcr.use_cassette("cassettes/test_data.yaml"):
        test_data.channel_video_list = list(Channel(test_data.channel_url).video_urls)
        test_data.playlist_video_list = list(
            Playlist(test_data.playlist_url).video_urls
        )


@pytest.fixture(scope="session")
def redis():
    """Return a redis client valid for the whole test session."""
    return _redis.Redis(host="localhost", port=6379, db=0)


@pytest.fixture(scope="function")
def reset_video_cache_after_every_test(redis):
    """Ensure the test video cache is purged after every test."""
    yield
    redis.delete(f"ytpodcast:video:{test_data.video_id}")
