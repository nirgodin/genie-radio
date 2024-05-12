import os.path
import time

from aiohttp import ClientSession, ClientResponse
from genie_common.tools import logger


class RadioStreamer:
    def __init__(self, session: ClientSession):
        self._session = session

    async def stream(self, dir_path: str, url: str) -> str:
        file_path = os.path.join(dir_path, "radio.ogg")

        async with self._session.get(url) as response:
            with open(file_path, "wb") as file:
                await self._write(response, file)

        return file_path

    @staticmethod
    async def _write(response: ClientResponse, file):
        start_time = time.time()

        while time.time() - start_time < 8:
            logger.info("Streaming")
            chunk = await response.content.read(1024)

            if not chunk:
                break

            file.write(chunk)
            file.flush()
