from __future__ import annotations
import dataclasses
import json
from typing import List


class EnhancedJSONEncoder(json.JSONEncoder):
    """A JSON encoder that supports dataclasses."""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class Video:
    """TODO"""

    id: str
    title: str
    description: str
    thumbnail: str
    url: str
    length: int

    def to_json(self) -> str:
        """TODO"""
        return json.dumps(self, cls=EnhancedJSONEncoder)

    @staticmethod
    def from_json(json_str: str) -> Video:
        """TODO"""
        data = json.loads(json_str)
        return Video(**data)


@dataclasses.dataclass
class Playlist:
    """TODO"""

    id: str
    title: str
    description: str
    thumbnail: str
    url: str
    videos: List[Video]


@dataclasses.dataclass
class Channel(Playlist):
    """TODO"""
