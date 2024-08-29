import asyncio

from aiohttp import ClientSession
from genie_common.tools import logger

from genie_radio.components.component_factory import ComponentFactory


async def run():
    logger.info("Starting application!")
    factory = ComponentFactory()

    async with ClientSession() as client_session:
        async with factory.spotify.create_spotify_session() as spotify_session:
            app_runner = await factory.get_application_runner(client_session, spotify_session)
            await app_runner.run()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
