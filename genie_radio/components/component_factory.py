import os
from typing import List, Optional

from aiohttp import ClientSession
from genie_common.tools import AioPoolExecutor, EmailSender
from genie_common.utils import env_var_to_bool
from genie_datastores.postgres.models import SpotifyStation
from shazamio import Shazam
from spotipyio import SpotifyClient, SpotifySession

from genie_radio.components.search_item_builders_factory import SearchItemBuildersFactory
from genie_radio.components.spotify_factory import SpotifyFactory
from genie_radio.logic.application_runner import ApplicationRunner
from genie_radio.logic.playlist_updater import PlaylistUpdater
from genie_radio.logic.playlists_manager import PlaylistsManager
from genie_radio.logic.radio_streamer import RadioStreamer
from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.streams_archiver import StreamsArchiver
from genie_radio.logic.track_searcher import TrackSearcher


class ComponentFactory:
    def __init__(self,
                 spotify: SpotifyFactory = SpotifyFactory(),
                 search_item_builder: SearchItemBuildersFactory = SearchItemBuildersFactory()):
        self.spotify = spotify
        self.search_item_builder = search_item_builder

    async def get_application_runner(self,
                                     client_session: ClientSession,
                                     spotify_session: SpotifySession) -> ApplicationRunner:
        playlists_manager = await self.get_playlists_manager(
            client_session=client_session,
            spotify_session=spotify_session
        )
        return ApplicationRunner(
            email_sender=self.get_email_sender(),
            playlists_manager=playlists_manager
        )

    @staticmethod
    def get_email_sender() -> EmailSender:
        return EmailSender(
            user=os.environ["EMAIL_USER"],
            password=os.environ["EMAIL_PASSWORD"]
        )

    async def get_playlists_manager(self,
                                    client_session: ClientSession,
                                    spotify_session: SpotifySession) -> PlaylistsManager:
        spotify_client = self.spotify.get_spotify_client(spotify_session)
        stations = self.get_stations(spotify_client)

        return PlaylistsManager(
            radio_streamer=self.get_radio_streamer(client_session),
            shazam=Shazam("EN"),
            track_searcher=self.get_track_searcher(spotify_client),
            stations=stations,
            pool_executor=AioPoolExecutor(pool_size=len(stations), validate_results=False),
        )

    def get_track_searcher(self, spotify_client: SpotifyClient) -> TrackSearcher:
        return TrackSearcher(
            spotify_client=spotify_client,
            entity_matcher=self.spotify.get_entity_matcher(),
            prioritized_search_item_builders=self.search_item_builder.get_prioritized_builders()
        )

    def get_radio_streamer(self, session: ClientSession) -> RadioStreamer:
        return RadioStreamer(
            session=session,
            streams_archiver=self.get_streams_archiver()
        )

    @staticmethod
    def get_streams_archiver() -> Optional[StreamsArchiver]:
        if env_var_to_bool("SHOULD_ARCHIVE_STREAMS"):
            return StreamsArchiver(os.environ["STREAMS_ARCHIVER_BASE_DIR"])

    @staticmethod
    def get_stations(spotify_client: SpotifyClient) -> List[StationConfig]:
        return [
            StationConfig(
                name=SpotifyStation.GLGLZ,
                url="https://glzwizzlv.bynetcdn.com/glglz_mp3",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="2KYmOoAcygHFPWmrSlGpHo"
                )
            ),
            StationConfig(
                name=SpotifyStation.KAN_GIMEL,
                url="https://23603.live.streamtheworld.com/KAN_GIMMEL.mp3",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="3w2tquPLXoq6pEQUzLYG3J"
                )
            ),
            StationConfig(
                name=SpotifyStation.KAN_88,
                url="https://27343.live.streamtheworld.com/KAN_88.mp3",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="07xAi6MxL60MOdoDwmAL4k"
                )
            ),
            StationConfig(
                name=SpotifyStation.FM_103,
                url="https://cdn.cybercdn.live/103FM/Live/icecast.audio",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="4sTLFJN8Kv4R6zqKibmtFG"
                )
            ),
            StationConfig(
                name=SpotifyStation.KZ_RADIO,
                url="https://kzradio.mediacast.co.il/kzradio_live/kzradio/icecast.audio",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="14dzmMSk7h9MxelRjwXZRj"
                )
            ),
            StationConfig(
                name=SpotifyStation.ECO_99,
                url="https://eco01.mediacast.co.il/ecolive/99fm_aac/icecast.audio",
                updater=PlaylistUpdater(
                    spotify_client=spotify_client,
                    playlist_id="1LgY4vKWZl3Uw2yWNd3GKX"
                )
            ),
        ]
