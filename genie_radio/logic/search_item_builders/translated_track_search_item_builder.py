from typing import Optional

from genie_common.tools import logger
from genie_datastores.models import EntityType
from spotipyio import SearchItem

from genie_radio.logic.search_item_builders import ISearchItemBuilder
from genie_radio.tools import Translator
from genie_radio.utils import extract_shazam_artist, extract_shazam_track, build_search_item, extract_shazam_track_id, \
    decide_target_language


class TranslatedTrackSearchItemBuilder(ISearchItemBuilder):
    def __init__(self, translator: Translator):
        self._translator = translator

    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        track_id = extract_shazam_track_id(recognition_output)

        if track_id is not None:
            return await self._build_item(recognition_output, track_id)

        logger.warning(f"Was not able to extract Shazam track id. Skipping `{self.__class__.__name__}` logic")

    async def _build_item(self, recognition_output: dict, track_id: str) -> Optional[SearchItem]:
        text = extract_shazam_track(recognition_output)
        target_language = decide_target_language(text)

        if target_language != "he":
            return

        translated_track = await self._translator.translate(
            record_id=track_id,
            text=text,
            entity_type=EntityType.TRACK,
            target_language=target_language
        )

        if translated_track:
            artist = extract_shazam_artist(recognition_output)
            return build_search_item(artist=artist, track=translated_track)
