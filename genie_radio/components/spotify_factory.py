from spotipyio import SpotifyClient, EntityMatcher, TrackEntityExtractor
from spotipyio.logic.authentication.spotify_grant_type import SpotifyGrantType
from spotipyio.logic.authentication.spotify_session import SpotifySession

from genie_radio.components.environment_factory import EnvironmentFactory
from genie_radio.logic.artist_entity_extractor import ArtistEntityExtractor


class SpotifyFactory:
    def __init__(self, env: EnvironmentFactory = EnvironmentFactory()):
        self._env = env

    def get_spotify_session(self) -> SpotifySession:
        return SpotifySession(
            grant_type=SpotifyGrantType.REFRESH_TOKEN,
            access_code=self._env.get_refresh_token()
        )

    @staticmethod
    def get_spotify_client(session: SpotifySession) -> SpotifyClient:
        return SpotifyClient.create(session)

    @staticmethod
    def get_entity_matcher() -> EntityMatcher:
        extractors = {TrackEntityExtractor(): 0.65, ArtistEntityExtractor(): 0.35}
        return EntityMatcher(extractors=extractors)
