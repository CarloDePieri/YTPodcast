from ytpodcast.utils import video_url_from_id, playlist_url_from_id
from tests.conftest import test_data as td


def test_can_return_the_full_video_url_from_an_id():
    """Can return the full video url from an id."""
    url = video_url_from_id(td.video_id)
    assert url == td.video_url


def test_can_return_the_full_playlist_url_from_the_id():
    """Can return the full playlist url from the id."""
    url = playlist_url_from_id(td.playlist_id)
    assert url == td.playlist_url
