import asyncio

from genie_common.tools import logger

from genie_radio.components.component_factory import ComponentFactory


async def run(exceptions_count: int = 0):
    if exceptions_count >= 3:
        raise RuntimeError(f"Exceptions count exceeded max allowed exceptions. Aborting")

    factory = ComponentFactory()

    try:
        async with factory.get_playlists_manager() as manager:
            await manager.run_forever()

    except PermissionError:
        logger.info("Session authorization expired. Re-creating session")
        return await run(exceptions_count=0)

    except Exception:
        logger.exception("Encountered exception! Retrying")
        return await run(exceptions_count + 1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
