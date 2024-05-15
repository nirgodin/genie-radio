from time import sleep
from typing import List

from genie_common.tools import logger

from genie_radio.logic.radio_streamer import RadioStreamer
from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.track_searcher import TrackSearcher


class PlaylistsManager:
    def __init__(self,
                 radio_streamer: RadioStreamer,
                 track_searcher: TrackSearcher,
                 stations: List[StationConfig]):
        self._radio_streamer = radio_streamer
        self._track_searcher = track_searcher
        self._stations = stations

    async def run_forever(self) -> None:
        while True:
            try:
                await self.run()
                logger.info("Sleeping Until next round")
                sleep(60)

            except KeyboardInterrupt:
                logger.info(f"Program stopped manually. Aborting")

    async def run(self) -> None:
        for station in self._stations:
            stream = await self._radio_streamer.stream(station.url)
            uri = await self._track_searcher.search(stream)

            if uri is not None:
                await station.updater.update(uri)