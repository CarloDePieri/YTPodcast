from typing import List

import pytest
import requests
from pytube import Channel, Playlist, YouTube

from ytpodcast.youtube import generate_video_list, VideoData, get_stream_url
from tests.conftest import vcr_record


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
class TestAVideoData:
    """Test: A video data..."""

    video_data: VideoData

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, vcr_setup):
        """TestAVideoData setup"""
        with vcr_setup():
            video_url = "https://www.youtube.com/watch?v=BaW_jenozKc"
            request.cls.video_data = VideoData.from_video(YouTube(video_url))

    def test_should_contain_a_title(self):
        """A video data should contain a title."""
        assert self.video_data.title == "youtube-dl test video \"'/\\ä↭𝕐"

    def test_should_contain_the_description(self):
        """A video data should contain the description."""
        assert (
            self.video_data.description
            == "test chars:  \"'/\\ä↭𝕐\ntest URL: https://github.com/rg3/youtube-dl/issues/1892\n\nThis is a test video for youtube-dl.\n\nFor more information, contact phihag@phihag.de ."
        )

    def test_should_have_an_id(self):
        """A video data should have an id."""
        assert self.video_data.id == "BaW_jenozKc"

    def test_should_have_a_thumbnail_url(self):
        """A video data should have a thumbnail url."""
        assert (
            self.video_data.thumbnail
            == "https://i.ytimg.com/vi/BaW_jenozKc/sddefault.jpg"
        )

    def test_should_have_a_stream_url(self):
        """A video data should have a stream url."""
        assert self.video_data.url == f"/api/stream/{self.video_data.id}"

    def test_should_have_the_video_length(self):
        """A video data should have the video length."""
        assert self.video_data.length == 10


@vcr_record
class TestTheStreamUrl:
    """Test: The stream url..."""

    def test_should_be_obtainable_from_the_video_id(self):
        """The stream url should be obtainable from the video id."""
        stream = get_stream_url("BaW_jenozKc")
        assert isinstance(stream, str)
        assert len(stream) > 0
