import json
import pytest
from ytpodcast.youtube import Video

from tests.conftest import test_data as td


class TestAVideo:
    """Test: A Video..."""

    video: Video

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAVideo setup"""
        request.cls.video = Video(
            id=td.video_data.id,
            title=td.video_data.title,
            description=td.video_data.description,
            thumbnail=td.video_data.thumbnail,
            url=td.video_data.url,
            length=td.video_data.length,
        )

    def test_should_have_all_required_fields(self):
        """A video should have all required fields."""
        assert self.video.id == td.video_data.id
        assert self.video.title == td.video_data.title
        assert self.video.description == td.video_data.description
        assert self.video.thumbnail == td.video_data.thumbnail
        assert self.video.url == td.video_data.url
        assert self.video.length == td.video_data.length

    def test_object_should_be_serializable(self):
        """A video object should be serializable."""
        d = json.loads(self.video.to_json())
        assert isinstance(d, dict)
        assert d["id"] == self.video.id

    def test_object_can_be_built_from_json(self):
        """A video object can be built from json."""
        video = Video.from_json(td.video_data_str)
        assert isinstance(video, Video)
        assert video.id == self.video.id
