from typing import Optional, List

from pytube import Playlist


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
