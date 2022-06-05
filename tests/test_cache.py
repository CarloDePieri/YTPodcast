import pytest

from ytpodcast.youtube import Video
from ytpodcast.cache import RedisCache
from tests.conftest import test_data as td


class TestARedisCache:
    """Test: A Redis Cache..."""

    cache: RedisCache
    video: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestARedisCache setup"""
        request.cls.cache = RedisCache()
        request.cls.video = Video.from_json(td.video_data_str)

    def test_should_be_able_to_store_a_value(
        self, redis, reset_video_cache_after_every_test
    ):
        """A redis cache should be able to store a value."""
        assert redis.get(td.video_id) is None
        self.cache.save(self.video)
        assert redis.get(td.video_id).decode("UTF-8") == td.video_data_str

    def test_should_be_able_to_tell_if_an_object_is_cached(
        self, redis, reset_video_cache_after_every_test
    ):
        """A redis cache should be able to tell if an object is cached."""
        assert not self.cache.is_cached(self.video)
        redis.set(td.video_id, "{}")
        assert self.cache.is_cached(self.video)

    def test_should_be_able_to_recover_an_object_from_the_cache(
        self, redis, reset_video_cache_after_every_test
    ):
        """A redis cache should be able to recover an object from the cache."""
        redis.set(td.video_id, td.video_data_str)
        video = self.cache.load(td.video_id)
        assert video.id == td.video_id
