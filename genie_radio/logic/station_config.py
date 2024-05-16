from dataclasses import dataclass
from typing import Optional

from genie_radio.logic.playlist_updater import PlaylistUpdater


@dataclass
class StationConfig:
    updater: PlaylistUpdater
    name: str
    url: str
    last_track_id: Optional[str] = None
