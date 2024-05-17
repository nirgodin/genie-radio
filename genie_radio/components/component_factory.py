from contextlib import asynccontextmanager
from typing import List

from aiohttp import ClientSession
from shazamio import Shazam
from spotipyio import SpotifyClient

from genie_radio.components.search_item_builders_factory import SearchItemBuildersFactory
from genie_radio.components.spotify_factory import SpotifyFactory
from genie_radio.logic.playlist_updater import PlaylistUpdater
from genie_radio.logic.playlists_manager import PlaylistsManager
from genie_radio.logic.radio_streamer import RadioStreamer
from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.track_searcher import TrackSearcher


class ComponentFactory:
    def __init__(self,
                 spotify: SpotifyFactory = SpotifyFactory(),
                 search_item_builder: SearchItemBuildersFactory = SearchItemBuildersFactory()):
        self.spotify = spotify
        self.search_item_builder = search_item_builder

    @asynccontextmanager
    async def get_playlists_manager(self) -> PlaylistsManager:
        client_session = ClientSession()
        session_creator = self.spotify.get_spotify_session_creator()
        spotify_session = await session_creator.create()

        try:
            await client_session.__aenter__()
            spotify_client = self.spotify.get_spotify_client(spotify_session)

            yield PlaylistsManager(
                radio_streamer=self.get_radio_streamer(client_session),
                shazam=Shazam("EN"),
                track_searcher=self.get_track_searcher(spotify_client),
                stations=self.get_stations(spotify_client)
            )

        finally:
            await client_session.__aexit__(None, None, None)
            await spotify_session.__aexit__(None, None, None)

    def get_track_searcher(self, spotify_client: SpotifyClient) -> TrackSearcher:
        return TrackSearcher(
            spotify_client=spotify_client,
            entity_matcher=self.spotify.get_entity_matcher(),
            prioritized_search_item_builders=self.search_item_builder.get_prioritized_builders()
        )

    @staticmethod
    def get_radio_streamer(session: ClientSession) -> RadioStreamer:
        return RadioStreamer(session)

    @staticmethod
    def get_stations(spotify_client: SpotifyClient) -> List[StationConfig]:
        return [
            StationConfig(
                name="glglz",
                url="https://glzicylv01.bynetcdn.com/glglz_mp3",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="1t0YzRn0CNKjBWBZUQX0Kz"
                )
            )
        ]
