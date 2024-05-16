from typing import Optional, List

from genie_common.clients.google.google_translate_client import GoogleTranslateClient
from genie_common.models.google import TranslationResponse
from genie_common.tools import logger
from spotipyio import SearchItem

from genie_radio.logic.search_item_builders import ISearchItemBuilder
from genie_radio.utils import extract_shazam_artist, contains_any_non_ascii_or_punctuation_char, extract_shazam_track, \
    build_search_item


class TranslatedArtistSearchItemBuilder(ISearchItemBuilder):
    def __init__(self, translation_client: GoogleTranslateClient):
        self._translation_client = translation_client

    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        translated_artist = await self._translate_artist_name(recognition_output)

        if translated_artist:
            track = extract_shazam_track(recognition_output)
            return build_search_item(artist=translated_artist, track=track)

    async def _translate_artist_name(self, recognition_output: dict) -> Optional[str]:
        artist = extract_shazam_artist(recognition_output)
        target_language = self._decide_target_langauge(artist)
        logger.info(f"Translating artist name `{artist}` to language `{target_language}`")
        responses = await self._translation_client.translate(
            texts=[artist],
            target_language=target_language
        )

        return self._extract_translation_response(responses, artist)

    @staticmethod
    def _decide_target_langauge(artist: str) -> str:
        if contains_any_non_ascii_or_punctuation_char(artist):
            return "en"

        return "he"

    @staticmethod
    def _extract_translation_response(responses: List[TranslationResponse], artist: str) -> Optional[str]:
        if responses:
            translation = responses[0].translation
            logger.info(f"Successfully translated `{artist}` to {translation}")

            return translation

        logger.info(f"Translation service did not return any response. Returning None instead")
