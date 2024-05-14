import asyncio
from time import sleep

from aiohttp import ClientSession
from genie_common.tools import logger

from genie_radio.components.component_factory import ComponentFactory


async def run():
    factory = ComponentFactory()

    async with ClientSession() as client_session:
        raw_session = factory.spotify.get_spotify_session()

        async with raw_session as spotify_session:
            manager = factory.get_playlists_manager(client_session, spotify_session)

            while True:
                try:
                    await manager.run()
                    logger.info("Sleeping Until next round")
                    sleep(60)
                except KeyboardInterrupt:
                    logger.info(f"Program stopped manually. Aborting")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
