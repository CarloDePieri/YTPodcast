from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

import shelve
from redis import Redis

if TYPE_CHECKING:
    from ytpodcast.youtube import Video


class Cache(ABC):
    """TODO"""

    @abstractmethod
    def is_cached(self, video: Video) -> bool:
        pass

    @abstractmethod
    def save(self, video: Video) -> None:
        pass

    @abstractmethod
    def load(self, video_id: str) -> Optional[Video]:
        pass


class RedisCache(Cache):
    """TODO"""

    r: Redis

    def __init__(self):
        self.r = Redis(host="localhost", port=6379, db=0)

    def is_cached(self, video: Video) -> bool:
        key = self._key_from_id(video.id)
        return self.r.get(key) is not None

    def save(self, video: Video) -> None:
        key = self._key_from_id(video.id)
        self.r.set(key, video.to_json())

    def load(self, video_id: str) -> Optional[Video]:
        key = self._key_from_id(video_id)
        data = self.r.get(key).decode("UTF-8")
        return Video.from_json(data)

    @staticmethod
    def _key_from_id(video_id: str) -> str:
        return f"ytpodcast:video:{video_id}"


class ShelveCache(Cache):
    def __init__(self, db_file: str = "db"):
        self.db = shelve.open(db_file)

    def is_cached(self, video: Video) -> bool:
        return self.db.get(video.id) is not None

    def save(self, video: Video) -> None:
        self.db[video.id] = video.to_json()

    def load(self, video_id: str) -> Optional[Video]:
        data_str = self.db[video_id]
        return Video.from_json(data_str)

    def __del__(self):
        # NOTE: cache is persisted on disk only when the object is destroyed
        # NOTE 2: writing to disk is costly, but it should not impact api answers; TODO verify this
        self.db.close()
