from io import BytesIO
from time import time

from aiohttp import ClientSession, ClientResponse
from genie_common.tools import logger


class RadioStreamer:
    def __init__(self, session: ClientSession):
        self._session = session

    async def stream(self, url: str) -> bytes:
        async with self._session.get(url) as response:
            stream = BytesIO()
            await self._write(response, stream)

        return stream.getvalue()

    @staticmethod
    async def _write(response: ClientResponse, stream: BytesIO) -> None:
        logger.info("Streaming track for the next 8 seconds")
        start_time = time()

        while time() - start_time < 8:
            chunk = await response.content.read(1024)

            if not chunk:
                break

            stream.write(chunk)
            stream.flush()
