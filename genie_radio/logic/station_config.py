from dataclasses import dataclass
from typing import Optional

from genie_datastores.postgres.models import SpotifyStation

from genie_radio.logic.playlist_updater import PlaylistUpdater


@dataclass
class StationConfig:
    updater: PlaylistUpdater
    name: SpotifyStation
    url: str
    last_track_id: Optional[str] = None
