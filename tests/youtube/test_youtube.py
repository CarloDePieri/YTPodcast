from typing import Type

import pytest

from ytpodcast.cache import Cache
from ytpodcast.utils import video_url_from_id
from ytpodcast.youtube import Video, Playlist, PytubeInfo
from ytpodcast.youtube.base import YouTubeInfo
from tests.conftest import vcr_record, test_data as td, forbid_network_calls


@vcr_record
@pytest.mark.parametrize("info_cls", [PytubeInfo])
class TestAYouTubeInfoImplementation:
    """Test: A YouTubeInfo implementation..."""

    def test_should_be_able_to_get_a_video_from_the_id(
        self, info_cls: Type[YouTubeInfo]
    ):
        """A YouTubeInfo implementation should be able to get a Video from the id."""
        video = info_cls().video_from_id(td.video_id)
        assert isinstance(video, Video)
        assert video.id == td.video_id

    def test_should_be_able_to_get_a_playlist_from_the_id(
        self, info_cls: Type[YouTubeInfo]
    ):
        """A YouTubeInfo implementation should be able to get a Playlist from the id."""
        playlist = info_cls().playlist_from_id(td.playlist_id)
        assert isinstance(playlist, Playlist)
        assert playlist.id == td.playlist_id
        assert len(playlist.videos) == len(td.playlist_video_list)
        assert len(playlist.thumbnail) > 0
        for video in playlist.videos:
            assert video_url_from_id(video.id) in td.playlist_video_list

    def test_should_be_able_to_get_part_of_a_playlist_from_the_id(
        self, info_cls: Type[YouTubeInfo]
    ):
        """A YouTubeInfo implementation should be able to get part of a playlist from the id."""
        limit = 2
        playlist = info_cls().playlist_from_id(td.playlist_id, limit=limit)
        assert isinstance(playlist, Playlist)
        assert len(playlist.videos) == limit
        for video in playlist.videos[:2]:
            assert video_url_from_id(video.id) in td.playlist_video_list

    @pytest.mark.parametrize(
        "cache_obj_fixture_name,teardown_fixture_name",
        [
            ["test_shelve_cache", "reset_test_video_shelve_cache"],
            ["test_redis_cache", "reset_test_video_redis_cache"],
        ],
        ids=["shelve_cache", "redis_cache"],
    )
    def test_can_write_to_a_cache(
        self,
        info_cls: Type[YouTubeInfo],
        cache_obj_fixture_name,
        teardown_fixture_name,
        fixture_from_param,
    ):
        """A YouTubeInfo implementation can write to a Cache."""
        # Enable the teardown fixture: must be called here at the start, so it will trigger on teardown even on error
        fixture_from_param(teardown_fixture_name)

        cache = fixture_from_param(cache_obj_fixture_name)  # type: Cache
        info = info_cls(cache=cache)
        video = info.video_from_id(td.video_id)
        assert cache.is_cached(video.id)

    @pytest.mark.parametrize(
        "cache_obj_fixture_name,teardown_fixture_name",
        [
            ["test_shelve_cache", "reset_test_video_shelve_cache"],
            ["test_redis_cache", "reset_test_video_redis_cache"],
        ],
        ids=["shelve_cache", "redis_cache"],
    )
    def test_can_read_from_a_cache(
        self,
        info_cls: Type[YouTubeInfo],
        cache_obj_fixture_name,
        teardown_fixture_name,
        fixture_from_param,
    ):
        """A YouTubeInfo implementation can read from a Cache."""
        # Enable the teardown fixture: must be called here at the start, so it will trigger on teardown even on error
        fixture_from_param(teardown_fixture_name)

        cache = fixture_from_param(cache_obj_fixture_name)  # type: Cache
        info = info_cls(cache=cache)
        video = info.video_from_id(td.video_id)
        with forbid_network_calls():
            cached_video = info.video_from_id(td.video_id)
        assert video.id == cached_video.id
