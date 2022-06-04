from typing import List
from unittest.mock import patch

import pytest
import json

from pytube import Channel, Playlist, YouTube

from ytpodcast.youtube import (
    generate_video_list,
    Video,
    get_stream_url,
    VideoFactory,
    CachedVideoFactory,
)
from tests.conftest import (
    vcr_record,
    test_video_id,
    test_video_data,
    test_channel_video_list,
    test_channel_url,
    test_playlist_url,
    test_video_url,
)


@vcr_record
class TestAGeneratedVideoList:
    """Test: A generated video list..."""

    channel_url: str
    video_list: List[str]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, vcr_setup):
        """Test setup"""
        with vcr_setup():
            request.cls.channel_url = test_channel_url
            channel = Channel(request.cls.channel_url)
            request.cls.video_list = generate_video_list(channel)

    def test_should_actually_be_a_list(self):
        """A generated video list should actually be a list."""
        assert isinstance(self.video_list, List)
        assert isinstance(self.video_list[0], str)
        assert len(self.video_list) == len(test_channel_video_list)
        assert self.video_list[0] == test_channel_video_list[0]

    def test_should_accept_a_limit_argument(self):
        """A generated video list should accept a limit argument."""
        limit = 5
        video_list = generate_video_list(Channel(self.channel_url), limit=limit)
        assert len(video_list) == limit
        assert video_list[0] == self.video_list[0]

    def test_should_also_support_playlists(self):
        """A generated video list should also support playlists."""
        playlist = Playlist(test_playlist_url)
        video_list = generate_video_list(playlist)
        assert len(video_list) == 6


@vcr_record
class TestAVideo:
    """Test: A Video..."""

    video_data: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAVideo setup"""
        request.cls.video_data = Video(
            id=test_video_data["id"],
            title=test_video_data["title"],
            description=test_video_data["description"],
            thumbnail=test_video_data["thumbnail"],
            url=test_video_data["url"],
            length=test_video_data["length"],
        )

    def test_should_have_all_required_fields(self):
        """A video should have all required fields."""

        assert self.video_data.id == test_video_data["id"]
        assert self.video_data.title == test_video_data["title"]
        assert self.video_data.description == test_video_data["description"]
        assert self.video_data.thumbnail == test_video_data["thumbnail"]
        assert self.video_data.url == test_video_data["url"]
        assert self.video_data.length == test_video_data["length"]

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
        video = VideoFactory.from_url(test_video_url)
        assert isinstance(video, Video)
        assert video.id == test_video_id

    def test_should_be_able_to_build_a_video_from_a_dict(self):
        """A video factory should be able to build a Video from a dict."""
        video = VideoFactory.from_dict(test_video_data)
        assert video.id == test_video_id


@vcr_record
@pytest.mark.usefixtures("reset_video_cache_after_every_test")
class TestACachedVideoFactory:
    """Test: A cached video factory..."""

    def test_should_reach_youtube_on_the_first_call(self):
        """A cached video factory should reach youtube on the first call."""
        video_url = test_video_url
        video = YouTube(video_url)
        with patch("ytpodcast.youtube.YouTube", return_value=video) as f:
            CachedVideoFactory.from_url(video_url)
            f.assert_called()

    def test_should_cache_the_video_on_first_call(self, redis):
        """A cached video factory should cache the Video on first call."""
        CachedVideoFactory.from_url(test_video_url)
        assert redis.get(test_video_id)

    def test_should_use_the_cache_after_the_first_call(self):
        """A cached video factory should use the cache after the first call."""
        video_url = test_video_url
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
        stream = get_stream_url(test_video_id)
        assert isinstance(stream, str)
        assert len(stream) > 0
