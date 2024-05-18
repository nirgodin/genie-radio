from typing import Optional

from genie_common.tools import logger
from genie_datastores.postgres.models import EntityType
from spotipyio import SearchItem

from genie_radio.logic.search_item_builders import ISearchItemBuilder
from genie_radio.tools import Translator
from genie_radio.utils import extract_shazam_artist, extract_shazam_track, build_search_item, extract_shazam_track_id, \
    extract_shazam_artist_id, decide_target_language


class TranslatedSongSearchItemBuilder(ISearchItemBuilder):
    def __init__(self, translator: Translator):
        self._translator = translator

    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        track_id = extract_shazam_track_id(recognition_output)
        artist_id = extract_shazam_artist_id(recognition_output)

        if track_id is not None and artist_id is not None:
            return await self._build_item(
                recognition_output=recognition_output,
                track_id=track_id,
                artist_id=artist_id
            )

        logger.warning(f"Was not able to extract Shazam track or artist id. Skipping `{self.__class__.__name__}` logic")

    async def _build_item(self, recognition_output: dict, track_id: str, artist_id: str) -> Optional[SearchItem]:
        track_name = extract_shazam_track(recognition_output)
        track_target_language = decide_target_language(track_name)

        if track_target_language != "he":
            return

        translated_track = await self._translator.translate(
            record_id=track_id,
            text=track_name,
            entity_type=EntityType.TRACK,
            target_language=track_target_language
        )
        translated_artist = await self._translator.translate(
            record_id=artist_id,
            text=extract_shazam_artist(recognition_output),
            entity_type=EntityType.ARTIST
        )

        if translated_track and translated_artist:
            return build_search_item(artist=translated_artist, track=translated_track)
