from datetime import datetime
import json
import os
import time
from typing import Tuple, Dict, Union

import pytest

from ytpodcast.youtube import Video
from ytpodcast.cache import RedisCache, ShelveCache
from tests.conftest import test_data as td


EntryType = Dict[str, Union[str, Dict[str, Dict[str, float]]]]


@pytest.mark.performance
class TestCachePerformance:
    """Test: CachePerformance..."""

    LOG_FILE_NAME = "cache_performance_results.json"
    new_entry: EntryType
    db: Dict[str, EntryType]

    @pytest.fixture(scope="class", autouse=True)
    def _setup(self, request):
        """TestCachePerformance setup"""
        videos = []
        for video_url in td.channel_video_list:
            video = Video.from_json(td.video_data_str)
            video.id = video_url.replace("https://www.youtube.com/watch?v=", "")
            videos.append(video)
        request.cls.videos = videos

        db_path = f"{request.config.rootdir}/tests/{self.LOG_FILE_NAME}"
        if os.path.isfile(db_path):
            with open(db_path, "r") as f:
                db = json.load(f)
        else:
            db = {"entries": []}

        request.cls.new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        request.cls.db = db

        yield
        db["entries"].append(request.cls.new_entry)
        with open(db_path, "w+") as f:
            json.dump(db, f, indent=4)

    @pytest.fixture
    def redis_performance_test(self, redis) -> Tuple[RedisCache, str]:
        """Setup and Teardown for redis cache performance test."""
        cache = RedisCache()
        yield cache, "redis"
        for video in self.videos:
            redis.delete(cache._key_from_id(video.id))

    @pytest.fixture
    def shelve_performance_test(
        self, test_shelve_cache_db_path
    ) -> Tuple[ShelveCache, str]:
        """Setup and Teardown for shelve cache performance test."""
        cache = ShelveCache(db_file=test_shelve_cache_db_path)
        yield cache, "shelve"
        os.remove(test_shelve_cache_db_path)

    @pytest.mark.parametrize(
        "cache_fixture",
        ["redis_performance_test", "shelve_performance_test"],
        ids=["redis_cache", "shelve_cache"],
    )
    def test_should_be_acceptable(self, cache_fixture, fixture_from_param):
        """Cache performance should be acceptable."""
        # Enable the setup&teardown fixture: must be called here at the start, so it will always trigger on teardown
        cache, name = fixture_from_param(cache_fixture)

        start = time.time()
        for video in self.videos:
            cache.save(video)
        end = time.time()
        write_time = (end - start) / len(self.videos) * 1000

        start = time.time()
        for video in self.videos:
            _ = cache.load(video.id)
        end = time.time()
        read_time = (end - start) / len(self.videos) * 1000

        self.new_entry[name] = {"read": read_time, "write": write_time}

        if len(self.db["entries"]) > 0 and self.db["entries"][-1].get(name):
            # There are past data for this cache, check against that
            last_entry = self.db["entries"][-1][name]

            # A difference of more than 30% should fail the test:
            #   these values are highly dependent on the OS load and machine specs, so this test is only meant
            #   as a quick way to notice if something is wrong and to compare different caches.
            tolerance = 0.3

            assert_new_time_is_close_enough(last_entry, "read", read_time, tolerance)
            assert_new_time_is_close_enough(last_entry, "write", write_time, tolerance)


def assert_new_time_is_close_enough(
    last_entry: Dict[str, float], name: str, new: float, tolerance: float
) -> None:
    if last_entry.get(name):
        max_time = last_entry[name] + last_entry[name] * tolerance

        if new > max_time:
            pytest.fail(
                f"There's a {tolerance * 100}% difference with the last {name} measure! Something is wrong."
            )
        else:
            pass
