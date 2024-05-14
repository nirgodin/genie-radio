from dataclasses import dataclass

from genie_radio.logic.playlist_updater import PlaylistUpdater


@dataclass
class StationConfig:
    updater: PlaylistUpdater
    url: str
