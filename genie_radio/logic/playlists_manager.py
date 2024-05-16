from time import sleep
from typing import List

from genie_common.tools import logger
from shazamio import Shazam

from genie_radio.logic.radio_streamer import RadioStreamer
from genie_radio.logic.station_config import StationConfig
from genie_radio.logic.track_searcher import TrackSearcher
from genie_radio.utils import extract_shazam_artist, extract_shazam_track, extract_shazam_track_id


class PlaylistsManager:
    def __init__(self,
                 radio_streamer: RadioStreamer,
                 shazam: Shazam,
                 track_searcher: TrackSearcher,
                 stations: List[StationConfig]):
        self._radio_streamer = radio_streamer
        self._shazam = shazam
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
            logger.info(f"Running station `{station.name}` recognition")
            await self._run_single_station(station)

    async def _run_single_station(self, station: StationConfig) -> None:
        stream = await self._radio_streamer.stream(station.url)
        recognition_output = await self._shazam.recognize(stream)

        if self._is_successful_recognition(recognition_output):
            return await self._match_and_add_recognized_track(recognition_output, station)

        logger.info("Shazam failed to recognized streamed track sample. Skipping")

    @staticmethod
    def _is_successful_recognition(recognition_output: dict) -> bool:
        artist = extract_shazam_artist(recognition_output)
        track = extract_shazam_track(recognition_output)

        return artist is not None and track is not None

    async def _match_and_add_recognized_track(self, recognition_output: dict, station: StationConfig) -> None:
        track_id = extract_shazam_track_id(recognition_output)

        if track_id != station.last_track_id:
            await self._add_track_to_playlist(
                recognition_output=recognition_output,
                station=station,
                track_id=track_id
            )
        else:
            logger.info(f"track_id `{track_id}` was already processed. Skipping")

    async def _add_track_to_playlist(self, recognition_output: dict, station: StationConfig, track_id: str) -> None:
        logger.info(f"Recognized track_id `{track_id}` as new track. Starting matching process")
        station.last_track_id = track_id
        uri = await self._track_searcher.search(recognition_output)

        if uri is not None:
            await station.updater.update(uri)
