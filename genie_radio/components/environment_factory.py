import os


class EnvironmentFactory:
    @staticmethod
    def get_spotify_client_id() -> str:
        return os.environ["SPOTIPY_CLIENT_ID"]

    @staticmethod
    def get_spotify_client_secret() -> str:
        return os.environ["SPOTIPY_CLIENT_SECRET"]

    @staticmethod
    def get_spotify_redirect_uri() -> str:
        return os.environ["SPOTIPY_REDIRECT_URI"]

    @staticmethod
    def get_spotify_session_cache_key() -> str:
        return os.environ["SPOTIFY_SESSION_CACHE_KEY"]
