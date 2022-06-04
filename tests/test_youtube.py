from typing import List
from unittest.mock import patch

import pytest
import json

import pytube.extract
from pytube import Channel, Playlist, YouTube

from ytpodcast.youtube import (
    generate_video_list,
    Video,
    get_stream_url,
    VideoFactory,
    CachedVideoFactory,
)
from tests.conftest import vcr_record, test_video_id, test_video_data_bytes


@vcr_record
class TestAGeneratedVideoList:
    """Test: A generated video list..."""

    channel_url: str
    video_list: List[str]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, vcr_setup):
        """Test setup"""
        with vcr_setup():
            request.cls.channel_url = "https://www.youtube.com/c/PhilippHagemeister"
            channel = Channel(request.cls.channel_url)
            request.cls.video_list = generate_video_list(channel)

    def test_should_actually_be_a_list(self):
        """A generated video list should actually be a list."""
        assert isinstance(self.video_list, List)
        assert isinstance(self.video_list[0], str)
        assert len(self.video_list) > 100

    def test_should_accept_a_limit_argument(self):
        """A generated video list should accept a limit argument."""
        limit = 5
        video_list = generate_video_list(Channel(self.channel_url), limit=limit)
        assert len(video_list) == limit
        assert video_list[0] == self.video_list[0]

    def test_should_also_support_playlists(self):
        """A generated video list should also support playlists."""
        playlist = Playlist(
            "https://www.youtube.com/playlist?list=PLzsAfrTnv2gok8tVkG25yhFyenRTcBnVM"
        )
        video_list = generate_video_list(playlist)
        assert len(video_list) == 6


@vcr_record
class TestAVideo:
    """Test: A Video..."""

    video_data: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, vcr_setup):
        """TestAVideo setup"""
        with vcr_setup():
            video_url = "https://www.youtube.com/watch?v=BaW_jenozKc"
            video = YouTube(video_url)
            request.cls.video_data = Video(
                id=video.video_id,
                title=video.title,
                description=video.description,
                thumbnail=video.thumbnail_url,
                url=f"/api/stream/{video.video_id}",
                length=video.length,
            )

    def test_should_have_all_required_fields(self):
        """A video should have all required fields."""
        assert self.video_data.id == "BaW_jenozKc"
        assert self.video_data.title == "youtube-dl test video \"'/\\ä↭𝕐"
        assert (
            self.video_data.description
            == "test chars:  \"'/\\ä↭𝕐\ntest URL: https://github.com/rg3/youtube-dl/issues/1892\n\nThis is a test video for youtube-dl.\n\nFor more information, contact phihag@phihag.de ."
        )
        assert (
            self.video_data.thumbnail
            == "https://i.ytimg.com/vi/BaW_jenozKc/sddefault.jpg"
        )
        assert self.video_data.url == f"/api/stream/{self.video_data.id}"
        assert self.video_data.length == 10

    def test_object_should_be_serializable(self):
        """A video object should be serializable."""
        d = json.loads(self.video_data.toJSON())
        assert isinstance(d, dict)
        assert d["id"] == self.video_data.id


@vcr_record
class TestAVideoFactory:
    """Test: A video factory..."""

    def test_should_be_able_to_produce_a_video_from_a_url(self):
        """A video factory should be able to produce a Video from a url."""
        video_id = "BaW_jenozKc"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video = VideoFactory.from_url(video_url)
        assert isinstance(video, Video)
        assert video.id == video_id

    def test_should_be_able_to_build_a_video_from_a_dict(self):
        """A video factory should be able to build a Video from a dict."""
        d = json.loads(test_video_data_bytes.decode("UTF-8"))
        video = VideoFactory.from_dict(d)
        assert video.id == test_video_id


@vcr_record
@pytest.mark.usefixtures("reset_cache_after_every_test")
class TestACachedVideoFactory:
    """Test: A cached video factory..."""

    def test_should_reach_youtube_on_the_first_call(self):
        """A cached video factory should reach youtube on the first call."""
        video_url = f"https://www.youtube.com/watch?v={test_video_id}"
        video = YouTube(video_url)
        with patch("ytpodcast.youtube.YouTube", return_value=video) as f:
            CachedVideoFactory.from_url(video_url)
            f.assert_called()

    def test_should_cache_the_video_on_first_call(self, redis):
        """A cached video factory should cache the Video on first call."""
        video_url = f"https://www.youtube.com/watch?v={test_video_id}"
        CachedVideoFactory.from_url(video_url)
        assert redis.get("BaW_jenozKc")

    def test_should_use_the_cache_after_the_first_call(self):
        """A cached video factory should use the cache after the first call."""
        video_url = f"https://www.youtube.com/watch?v={test_video_id}"
        first_result = CachedVideoFactory.from_url(video_url)
        mock_video = YouTube(video_url)
        with patch("ytpodcast.youtube.YouTube", return_value=mock_video) as f:
            second_result = CachedVideoFactory.from_url(video_url)
            f.assert_not_called()
        assert first_result.id == second_result.id

    def test_should_recognize_cached_video(self, redis):
        """A cached video factory should recognize cached video."""
        assert not CachedVideoFactory._is_cached(test_video_id)
        redis.set(test_video_id, "{}")
        assert CachedVideoFactory._is_cached(test_video_id)


@vcr_record
class TestTheStreamUrl:
    """Test: The stream url..."""

    def test_should_be_obtainable_from_the_video_id(self):
        """The stream url should be obtainable from the video id."""
        stream = get_stream_url("BaW_jenozKc")
        assert isinstance(stream, str)
        assert len(stream) > 0
