from typing import Optional

from genie_common.tools import logger
from genie_datastores.models import EntityType
from spotipyio import SearchItem

from genie_radio.logic.search_item_builders import ISearchItemBuilder
from genie_radio.tools import Translator
from genie_radio.utils import extract_shazam_artist, extract_shazam_track, build_search_item, extract_shazam_artist_id


class TranslatedArtistSearchItemBuilder(ISearchItemBuilder):
    def __init__(self, translator: Translator):
        self._translator = translator

    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        artist_id = extract_shazam_artist_id(recognition_output)

        if artist_id is not None:
            return await self._build_item(recognition_output, artist_id)

        logger.warning(f"Was not able to extract Shazam artist id. Skipping `{self.__class__.__name__}` logic")

    async def _build_item(self, recognition_output: dict, artist_id: str) -> Optional[SearchItem]:
        translated_artist = await self._translator.translate(
            record_id=artist_id,
            text=extract_shazam_artist(recognition_output),
            entity_type=EntityType.ARTIST
        )

        if translated_artist:
            track = extract_shazam_track(recognition_output)
            return build_search_item(artist=translated_artist, track=track)
