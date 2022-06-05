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
        return self.r.get(video.id) is not None

    def save(self, video: Video) -> None:
        self.r.set(video.id, video.to_json())

    def load(self, video_id: str) -> Optional[Video]:
        data = self.r.get(video_id).decode("UTF-8")
        return Video.from_json(data)
