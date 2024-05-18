from http import HTTPStatus
from time import sleep
from typing import List, Any

from aiohttp import ClientResponseError
from genie_common.tools import logger, AioPoolExecutor
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
                 stations: List[StationConfig],
                 pool_executor: AioPoolExecutor):
        self._radio_streamer = radio_streamer
        self._shazam = shazam
        self._track_searcher = track_searcher
        self._stations = stations
        self._pool_executor = pool_executor

    async def run_forever(self) -> None:
        while True:
            await self.run()
            logger.info("Sleeping Until next round")
            sleep(60)

    async def run(self) -> None:
        results = await self._pool_executor.run(
            iterable=self._stations,
            func=self._run_single_station_wrapper,
            expected_type=type(None)
        )

        if any(self._is_unauthorized(result) for result in results):
            raise PermissionError

        if all(isinstance(result, Exception) for result in results):
            raise RuntimeError("All requests ran into unknown exception")

    async def _run_single_station_wrapper(self, station: StationConfig) -> None:
        try:
            await self._run_single_station(station)

        except:
            logger.exception(f"Received exception from station `{station.name}` process")
            raise

    async def _run_single_station(self, station: StationConfig) -> None:
        logger.info(f"Running station `{station.name}` recognition")
        stream = await self._radio_streamer.stream(station)
        recognition_output = await self._shazam.recognize(stream)

        if self._is_successful_recognition(recognition_output):
            return await self._match_and_add_recognized_track(recognition_output, station)

        logger.info(f"Shazam failed to recognized station `{station.name}` streamed track sample. Skipping")

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
        logger.info(f"Recognized track `{track_id}` played on `{station.name}` as new track. Starting matching process")
        station.last_track_id = track_id
        uri = await self._track_searcher.search(recognition_output)

        if uri is not None:
            await station.updater.update(uri)

    @staticmethod
    def _is_unauthorized(result: Any) -> bool:
        if isinstance(result, ClientResponseError):
            return result.status == HTTPStatus.UNAUTHORIZED

        return False
