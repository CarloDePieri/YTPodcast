from __future__ import annotations
import dataclasses
import json
from typing import Optional, List, Dict, Union

from pytube import Playlist, YouTube
from pytube.extract import video_id as extract_video_id
import youtube_dl
import redis as _redis


def redis():
    return _redis.Redis(host="localhost", port=6379, db=0)


def generate_video_list(entity: Playlist, limit: Optional[int] = None) -> List[str]:
    """Return a list of all the videos from a pytube.Playlist or pytube.Channel."""
    if limit:
        videos = []
        for video in entity.video_urls.gen:
            videos.append(video)
            if len(videos) >= limit:
                break
        return videos
    else:
        return list(entity.video_urls)


class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON encoder that supports dataclasses."""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class Video:
    id: str
    title: str
    description: str
    thumbnail: str
    url: str
    length: int

    def toJSON(self):
        return json.dumps(self, cls=EnhancedJSONEncoder)


class VideoFactory:
    @staticmethod
    def from_url(url: str) -> Video:
        video = YouTube(url)
        return Video(
            id=video.video_id,
            title=video.title,
            description=video.description,
            thumbnail=video.thumbnail_url,
            url=f"/api/stream/{video.video_id}",
            length=video.length,
        )

    @staticmethod
    def from_dict(data: Dict[str, Union[str, int]]) -> Video:
        return Video(**data)


class CachedVideoFactory(VideoFactory):

    redis = redis()

    @classmethod
    def from_url(cls, url: str) -> Video:
        video_id = extract_video_id(url)
        if cls._is_cached(video_id):
            video = cls._load_from_cache(video_id)
        else:
            video = super(cls, cls).from_url(url)
            cls._save_to_cache(video)
        return video

    @classmethod
    def _save_to_cache(cls, video: Video) -> None:
        cls.redis.set(video.id, video.toJSON())

    @classmethod
    def _load_from_cache(cls, video_id: str) -> Video:
        data_str = cls.redis.get(video_id)
        data = json.loads(data_str)
        return cls.from_dict(data)

    @classmethod
    def _is_cached(cls, video_id: str) -> bool:
        return cls.redis.get(video_id) is not None


def get_stream_url(video_id: str) -> str:
    ydl_opts = {
        "format": "bestaudio",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_id, download=False)
    return info.get("url")
