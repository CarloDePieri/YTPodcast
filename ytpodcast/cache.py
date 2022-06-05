from abc import ABC, abstractmethod
from typing import Optional

from redis import Redis

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
