from typing import Optional, Any, List
from functools import partial

from pytube import YouTube, Playlist as _Playlist

from ytpodcast.utils import video_url_from_id, playlist_url_from_id
from ytpodcast.api import get_stream_url
from ytpodcast.youtube import Video, Channel, Playlist
from ytpodcast.youtube.base import YouTubeInfo


class PytubeInfo(YouTubeInfo):
    """TODO"""

    name = "pytube"

    def video_from_id(self, video_id: str) -> Video:
        if self.cache and self.cache.is_cached(video_id):
            video = self.cache.load(video_id)
        else:
            url = video_url_from_id(video_id)
            video = self._video_from_url(url)
            if self.cache:
                self.cache.save(video)
        return video

    @staticmethod
    def _video_from_url(url: str) -> Video:
        video = YouTube(url)
        return Video(
            id=video.video_id,
            title=video.title,
            description=video.description,
            thumbnail=video.thumbnail_url,
            url=get_stream_url(video.video_id),
            length=video.length,
        )

    def playlist_from_id(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> Channel:
        url = playlist_url_from_id(playlist_id)
        playlist = _Playlist(url)
        get = partial(self._get_field, playlist)
        videos = []
        for video_url in self._generate_video_list(playlist, limit):
            videos.append(self._video_from_url(video_url))
        thumbnail = videos[0].thumbnail
        return Playlist(
            id=playlist_id,
            title=get("title", playlist_id),
            description=get("description"),
            url=get("playlist_url", url),
            videos=videos,
            thumbnail=thumbnail,
        )

    @staticmethod
    def _get_field(obj: Any, name: str, default: str = "") -> str:
        """Since pytube delays getting single attributes (which are properties), they can fail when accessed."""
        try:
            return getattr(obj, name)
        except (Exception,):
            return default

    @staticmethod
    def _generate_video_list(
        entity: _Playlist, limit: Optional[int] = None
    ) -> List[str]:
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
