from contextlib import asynccontextmanager
from typing import List

from aiohttp import ClientSession
from shazamio import Shazam
from spotipyio import SpotifyClient
from spotipyio.logic.authentication.spotify_session import SpotifySession

from genie_radio.components.spotify_factory import SpotifyFactory
from genie_radio.logic.playlist_updater import PlaylistUpdater
from genie_radio.logic.playlists_manager import PlaylistsManager
from genie_radio.logic.radio_streamer import RadioStreamer
from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.track_searcher import TrackSearcher


class ComponentFactory:
    def __init__(self, spotify: SpotifyFactory = SpotifyFactory()):
        self.spotify = spotify

    @asynccontextmanager
    async def get_playlists_manager(self) -> PlaylistsManager:
        client_session = ClientSession()
        spotify_session = self.spotify.get_spotify_session()

        try:
            await client_session.__aenter__()
            await spotify_session.__aenter__()
            spotify_client = self.spotify.get_spotify_client(spotify_session)

            yield PlaylistsManager(
                radio_streamer=self.get_radio_streamer(client_session),
                track_searcher=self.get_track_searcher(spotify_client),
                stations=self.get_stations(spotify_client)
            )

        finally:
            await client_session.__aexit__(None, None, None)
            await spotify_session.__aexit__(None, None, None)

    def get_track_searcher(self, spotify_client: SpotifyClient) -> TrackSearcher:
        return TrackSearcher(
            shazam=Shazam("EN"),
            spotify_client=spotify_client,
            entity_matcher=self.spotify.get_entity_matcher()
        )

    @staticmethod
    def get_radio_streamer(session: ClientSession) -> RadioStreamer:
        return RadioStreamer(session)

    @staticmethod
    def get_stations(spotify_client: SpotifyClient) -> List[StationConfig]:
        return [
            StationConfig(
                url="https://glzicylv01.bynetcdn.com/glglz_mp3",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="1t0YzRn0CNKjBWBZUQX0Kz"
                )
            )
        ]
