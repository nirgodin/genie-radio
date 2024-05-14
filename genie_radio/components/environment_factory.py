import os


class EnvironmentFactory:
    @staticmethod
    def get_refresh_token() -> str:
        return os.environ["SPOTIPY_REFRESH_TOKEN"]
