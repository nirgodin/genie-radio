from typing import Dict

from genie_common.clients.utils import create_client_session, build_authorization_headers
from genie_common.encoders import GzipJsonEncoder
from genie_common.tools import logger
from redis import Redis
from spotipyio import AccessTokenGenerator
from spotipyio.logic.authentication.spotify_grant_type import SpotifyGrantType
from spotipyio.logic.authentication.spotify_session import SpotifySession


class SpotifySessionCreator:
    REDIS_AUTH_KEY = "genie_radio_auth"

    def __init__(self,
                 redis: Redis,
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str,
                 encoder: GzipJsonEncoder = GzipJsonEncoder()):
        self._redis = redis
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._encoder = encoder

    async def create(self) -> SpotifySession:
        refresh_token = self._fetch_existing_refresh_token()
        access_token = await self._fetch_new_access_token(refresh_token)
        headers = build_authorization_headers(access_token)
        raw_session = create_client_session(headers)
        session = await raw_session.__aenter__()

        return SpotifySession(session=session)

    def _fetch_existing_refresh_token(self) -> str:
        logger.info("Fetching existing refresh token from Redis")
        encoded_response = self._redis.get(self.REDIS_AUTH_KEY)
        decoded_response = self._encoder.decode(encoded_response)

        return decoded_response["refresh_token"]

    async def _fetch_new_access_token(self, refresh_token: str) -> str:
        logger.info("Fetching new Spotify access token")

        async with AccessTokenGenerator(self._client_id, self._client_secret, self._redirect_uri) as token_generator:
            response = await token_generator.generate(
                grant_type=SpotifyGrantType.REFRESH_TOKEN,
                access_code=refresh_token
            )
            self._set_new_auth_if_needed(response)

        return response["access_token"]

    def _set_new_auth_if_needed(self, response: Dict[str, str]) -> None:
        if "refresh_token" in response.keys():
            logger.info("Updating Redis refresh token")
            encoded_response = self._encoder.encode(response)
            self._redis.set(name=self.REDIS_AUTH_KEY, value=encoded_response)

        else:
            logger.info("Did not receive a new refresh token. Keeping current auth")
