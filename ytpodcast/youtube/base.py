from abc import ABC, abstractmethod
from typing import Optional

from ytpodcast.youtube import Video, Channel


class YouTubeInfo(ABC):
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
