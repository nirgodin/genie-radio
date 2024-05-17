from io import BytesIO
from time import time

from aiohttp import ClientSession, ClientResponse
from genie_common.tools import logger

from genie_radio.logic.station_config import StationConfig


class RadioStreamer:
    def __init__(self, session: ClientSession, sample_window: int = 8):
        self._session = session
        self._sample_window = sample_window

    async def stream(self, station: StationConfig) -> bytes:
        logger.info(f"Streaming station `{station.name}` for the next {self._sample_window} seconds")

        async with self._session.get(station.url) as response:
            stream = BytesIO()
            await self._write(response, stream)

        return stream.getvalue()

    async def _write(self, response: ClientResponse, stream: BytesIO) -> None:
        start_time = time()

        while time() - start_time < self._sample_window:
            chunk = await response.content.read(1024)

            if not chunk:
                break

            stream.write(chunk)
            stream.flush()
