from dataclasses import dataclass
from typing import Optional, List

from pytube import Playlist, YouTube


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


@dataclass
class VideoData:
    id: str
    title: str
    description: str
    thumbnail: str


def get_video_data(video: YouTube) -> VideoData:
    return VideoData(
        id=video.video_id,
        title=video.title,
        description=video.description,
        thumbnail=video.thumbnail_url,
    )
