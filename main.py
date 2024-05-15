import asyncio

from genie_radio.components.component_factory import ComponentFactory


async def run():
    factory = ComponentFactory()

    async with factory.get_playlists_manager() as manager:
        await manager.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
