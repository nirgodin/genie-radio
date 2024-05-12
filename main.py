import asyncio
from tempfile import TemporaryDirectory

from aiohttp import ClientSession
from shazamio import Shazam

from genie_radio.radio_streamer import RadioStreamer


async def run():
    shazam = Shazam()

    async with ClientSession() as session:
        streamer = RadioStreamer(session)

        with TemporaryDirectory() as dir_path:
            file_path = await streamer.stream(dir_path, "https://glzicylv01.bynetcdn.com/glglz_mp3")
            out = await shazam.recognize_song(file_path)
            print('b')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
