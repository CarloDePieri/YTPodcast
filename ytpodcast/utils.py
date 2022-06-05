def video_url_from_id(video_id: str) -> str:
    """Return the full video ulr starting from the id."""
    return f"https://www.youtube.com/watch?v={video_id}"


def playlist_url_from_id(playlist_id: str) -> str:
    """Return the full playlist ulr starting from the id."""
    return f"https://www.youtube.com/playlist?list={playlist_id}"
