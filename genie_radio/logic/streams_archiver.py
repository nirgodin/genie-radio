import os.path
from datetime import datetime
from io import BytesIO

from genie_common.tools import logger
from genie_datastores.postgres.models import SpotifyStation


class StreamsArchiver:
    def __init__(self, base_dir: str):
        self._base_dir = base_dir

    def archive(self, stream: BytesIO, station: SpotifyStation) -> None:
        self._create_station_dir_if_needed(station)
        self._write_stream_to_file(stream, station)
        stream.seek(0)

    def _create_station_dir_if_needed(self, station: SpotifyStation) -> None:
        dir_path = self._build_station_dir_path(station)

        if not os.path.exists(dir_path):
            logger.info(f"Missing archives dir for station {station}. Creating")
            os.mkdir(dir_path)

    def _build_station_dir_path(self, station: SpotifyStation) -> str:
        return os.path.join(self._base_dir, station.name.lower())

    def _write_stream_to_file(self, stream: BytesIO, station: SpotifyStation) -> None:
        dir_path = self._build_station_dir_path(station)
        timestamp_path = self._get_current_timestamp_path()
        file_path = os.path.join(dir_path, timestamp_path)

        with open(file_path, "wb") as f:
            f.write(stream.getvalue())

        logger.info(f"Stored current stream for station `{station.name}` in `{file_path}`")

    @staticmethod
    def _get_current_timestamp_path() -> str:
        timestamp = datetime.timestamp(datetime.now())
        formatted_timestamp = str(timestamp).replace(".", "_")

        return f"{formatted_timestamp}.mp3"
