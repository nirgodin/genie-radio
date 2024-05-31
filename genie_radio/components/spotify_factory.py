from genie_datastores.redis.operations import get_redis
from spotipyio import SpotifyClient, EntityMatcher, TrackEntityExtractor
from spotipyio.logic.authentication.spotify_session import SpotifySession

from genie_radio.components.environment_factory import EnvironmentFactory
from spotipyio import TrackSearchResultArtistEntityExtractor
from genie_radio.logic.spotify_session_creator import SpotifySessionCreator


class SpotifyFactory:
    def __init__(self, env: EnvironmentFactory = EnvironmentFactory()):
        self._env = env

    def get_spotify_session_creator(self) -> SpotifySessionCreator:
        return SpotifySessionCreator(
            redis=get_redis(),
            client_id=self._env.get_spotify_client_id(),
            client_secret=self._env.get_spotify_client_secret(),
            redirect_uri=self._env.get_spotify_redirect_uri()
        )

    @staticmethod
    def get_spotify_client(session: SpotifySession) -> SpotifyClient:
        return SpotifyClient.create(session)

    @staticmethod
    def get_entity_matcher() -> EntityMatcher:
        extractors = {TrackEntityExtractor(): 0.65, TrackSearchResultArtistEntityExtractor(): 0.35}
        return EntityMatcher(extractors=extractors)
