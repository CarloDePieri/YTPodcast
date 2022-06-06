import shelve

import pytest

from ytpodcast.youtube import Video
from ytpodcast.cache import RedisCache, ShelveCache
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

    def test_should_be_able_to_store_a_value(self, redis, reset_test_video_redis_cache):
        """A redis cache should be able to store a value."""
        key = self.cache._key_from_id(td.video_id)
        assert redis.get(key) is None
        self.cache.save(self.video)
        assert redis.get(key).decode("UTF-8") == td.video_data_str

    def test_should_be_able_to_tell_if_an_object_is_cached(
        self, redis, reset_test_video_redis_cache
    ):
        """A redis cache should be able to tell if an object is cached."""
        assert not self.cache.is_cached(self.video.id)
        key = self.cache._key_from_id(self.video.id)
        redis.set(key, "{}")
        assert self.cache.is_cached(self.video.id)

    def test_should_be_able_to_recover_an_object_from_the_cache(
        self, redis, reset_test_video_redis_cache
    ):
        """A redis cache should be able to recover an object from the cache."""
        key = self.cache._key_from_id(self.video.id)
        redis.set(key, td.video_data_str)
        video = self.cache.load(td.video_id)
        assert video.id == td.video_id


@pytest.mark.usefixtures("reset_test_video_shelve_cache")
class TestAShelveCache:
    """Test: A Shelve Cache..."""

    db: str
    video: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, test_shelve_cache_db_path_cls):
        """TestAShelveCache setup"""
        request.cls.db = test_shelve_cache_db_path_cls
        request.cls.video = Video.from_json(td.video_data_str)

    def test_should_be_able_to_store_a_value(self):
        """A Shelve Cache should be able to store a value."""
        with shelve.open(self.db) as db:
            assert db.get(td.video_id) is None
        cache = ShelveCache(self.db)
        cache.save(self.video)
        assert cache.db[td.video_id] is not None
        del cache  # This is needed to access the db, since it will close shelve connection with the db file
        with shelve.open(self.db) as db:
            assert db.get(td.video_id) == td.video_data_str

    def test_should_be_able_to_tell_if_an_object_is_cached(self):
        """A Shelve cache should be able to tell if an object is cached."""
        cache = ShelveCache(self.db)
        assert not cache.is_cached(self.video.id)
        del cache  # This is needed to access the db, since it will close shelve connection with the db file
        with shelve.open(self.db) as db:
            db[td.video_id] = td.video_data_str
        cache = ShelveCache(self.db)
        assert cache.is_cached(self.video.id)

    def test_should_be_able_to_recover_an_object_from_the_cache(self):
        """A shelve cache should be able to recover an object from the cache."""
        with shelve.open(self.db) as db:
            db[td.video_id] = td.video_data_str
        cache = ShelveCache(self.db)
        video = cache.load(td.video_id)
        assert video.id == td.video_id
