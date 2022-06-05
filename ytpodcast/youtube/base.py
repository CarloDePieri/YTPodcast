from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from ytpodcast.cache import Cache
from ytpodcast.youtube import Video, Channel


class YouTubeInfo(ABC):
    def __init__(self, cache: Optional[Cache] = None):
        self.cache = cache

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def video_from_id(self, video_id: str) -> Video:
        pass

    @abstractmethod
    def playlist_from_id(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> Channel:
        pass


class YouTubeStream(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
