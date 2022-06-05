from datetime import datetime
import os
import time
import shelve

import pytest

from ytpodcast.youtube import Video
from ytpodcast.cache import RedisCache, Cache, ShelveCache
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
        key = self.cache._key_from_id(td.video_id)
        assert redis.get(key) is None
        self.cache.save(self.video)
        assert redis.get(key).decode("UTF-8") == td.video_data_str

    def test_should_be_able_to_tell_if_an_object_is_cached(
        self, redis, reset_video_cache_after_every_test
    ):
        """A redis cache should be able to tell if an object is cached."""
        assert not self.cache.is_cached(self.video.id)
        key = self.cache._key_from_id(self.video.id)
        redis.set(key, "{}")
        assert self.cache.is_cached(self.video.id)

    def test_should_be_able_to_recover_an_object_from_the_cache(
        self, redis, reset_video_cache_after_every_test
    ):
        """A redis cache should be able to recover an object from the cache."""
        key = self.cache._key_from_id(self.video.id)
        redis.set(key, td.video_data_str)
        video = self.cache.load(td.video_id)
        assert video.id == td.video_id


class TestAShelveCache:
    """Test: A Shelve Cache..."""

    db: str
    video: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAShelveCache setup"""
        request.cls.db = f"{request.config.rootdir}/testdb"
        request.cls.video = Video.from_json(td.video_data_str)

    @pytest.fixture(scope="function", autouse=True)
    def single_setup(self, request):
        yield
        os.remove(request.cls.db)

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


# This is skipped by default, it's only used to measure cache performance
@pytest.mark.skip
class TestCachePerformance:
    """Test: CachePerformance..."""

    @pytest.fixture(scope="class", autouse=True)
    def _setup(self, request):
        """TestCachePerformance setup"""
        videos = []
        for video_url in td.channel_video_list:
            video = Video.from_json(td.video_data_str)
            video.id = video_url.replace("https://www.youtube.com/watch?v=", "")
            videos.append(video)
        request.cls.videos = videos
        with open(f"{request.config.rootdir}/cache_performance_results", "a+") as f:
            request.cls.report_file = f
            f.write(f"---- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ----\n")
            yield

    def _report(self, cache: Cache, name: str) -> [float, float]:
        start = time.time()
        for video in self.videos:
            cache.save(video)
        end = time.time()
        write_time = (end - start) / len(self.videos) * 1000000

        start = time.time()
        for video in self.videos:
            _ = cache.load(video.id)
        end = time.time()
        read_time = (end - start) / len(self.videos) * 1000000

        self.report_file.write(f"{name} write: {str(write_time)} μs\n")
        self.report_file.write(f"{name} read: {str(read_time)} μs\n")

    def test_should_be_reported_for_redis_cache(self, redis):
        """Cache performance should be reported for RedisCache."""
        self._report(RedisCache(), "redis")
        # cleanup
        for video in self.videos:
            redis.delete(RedisCache._key_from_id(video.id))

    def test_should_be_reported_for_shelve_cache(self, request):
        """Cache performance should be reported for ShelveCache."""
        db = f"{request.config.rootdir}/testdb"
        self._report(ShelveCache(db), "shelve")
        # cleanup
        os.remove(db)
