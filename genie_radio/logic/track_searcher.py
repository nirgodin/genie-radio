from typing import Optional

from genie_common.tools import logger
from genie_common.utils import safe_nested_get
from shazamio import Shazam
from spotipyio import SpotifyClient, SearchItem, SearchItemMetadata, SpotifySearchType, SearchItemFilters, \
    EntityMatcher, MatchingEntity


class TrackSearcher:
    def __init__(self, shazam: Shazam, spotify_client: SpotifyClient, entity_matcher: EntityMatcher):
        self._shazam = shazam
        self._spotify_client = spotify_client
        self._entity_matcher = entity_matcher

    async def search(self, stream: bytes) -> Optional[str]:
        recognition_output = await self._shazam.recognize(stream)
        search_item = self._build_search_item(recognition_output)

        if search_item is not None:
            return await self._search_track(search_item)

    @staticmethod
    def _build_search_item(recognition_output: dict) -> Optional[SearchItem]:
        track = safe_nested_get(recognition_output, ["track", "title"])
        artist = safe_nested_get(recognition_output, ["track", "subtitle"])

        if track and artist:
            text = f"{artist} - {track}"
            logger.info(f"Shazam recognized `{text}` as the playing track")
            return SearchItem(
                text=text,
                # filters=SearchItemFilters(
                #     track=track,
                #     artist=artist
                # ),
                metadata=SearchItemMetadata(
                    search_types=[SpotifySearchType.TRACK],
                    quote=False
                )
            )

    async def _search_track(self, search_item: SearchItem) -> Optional[str]:
        search_result = await self._spotify_client.search.run_single(search_item)
        entity = MatchingEntity(
            track=search_item.filters.track or " - ".join(search_item.text.split(" - ")[1:]),
            artist=search_item.filters.artist or search_item.text.split(" - ")[0]
        )
        candidates = safe_nested_get(search_result, ["tracks", "items"])

        for candidate in candidates:
            is_matching, score = self._entity_matcher.match(entity=entity, candidate=candidate)

            if is_matching:
                return candidate["uri"]

        logger.info(f"Did not find any track that matches `{search_item.text}`. Skipping")
