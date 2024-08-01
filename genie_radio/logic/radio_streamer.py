from io import BytesIO
from time import time
from typing import Optional

from aiohttp import ClientSession, ClientResponse
from genie_common.tools import logger

from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.streams_archiver import StreamsArchiver


class RadioStreamer:
    def __init__(self, session: ClientSession, streams_archiver: Optional[StreamsArchiver], sample_window: int = 8):
        self._session = session
        self._streams_archiver = streams_archiver
        self._sample_window = sample_window

    async def stream(self, station: StationConfig) -> bytes:
        logger.info(f"Streaming station `{station.name}` for the next {self._sample_window} seconds")

        async with self._session.get(station.url) as response:
            stream = BytesIO()
            await self._write(response, stream)

        if self._streams_archiver is not None:
            self._streams_archiver.archive(stream=stream, station=station.name)

        return stream.getvalue()

    async def _write(self, response: ClientResponse, stream: BytesIO) -> None:
        start_time = time()

        while time() - start_time < self._sample_window:
            chunk = await response.content.read(1024)

            if not chunk:
                break

            stream.write(chunk)
            stream.flush()
