import asyncio
from http import HTTPStatus

from aiohttp import ClientResponseError

from genie_radio.components.component_factory import ComponentFactory


async def run():
    factory = ComponentFactory()

    try:
        async with factory.get_playlists_manager() as manager:
            await manager.run_forever()

    except ClientResponseError as e:
        if e.status == HTTPStatus.UNAUTHORIZED:
            return await run()

        raise


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
