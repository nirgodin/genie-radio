from typing import Optional, List

from genie_common.tools import logger
from genie_common.utils import safe_nested_get
from shazamio import Shazam
from spotipyio import SpotifyClient, SearchItem, SearchItemMetadata, SpotifySearchType, SearchItemFilters, \
    EntityMatcher, MatchingEntity

from genie_radio.logic.search_item_builders import ISearchItemBuilder
from genie_radio.utils import extract_shazam_artist, extract_shazam_track


class TrackSearcher:
    def __init__(self,
                 shazam: Shazam,
                 prioritized_search_item_builders: List[ISearchItemBuilder],
                 spotify_client: SpotifyClient,
                 entity_matcher: EntityMatcher):
        self._shazam = shazam
        self._prioritized_search_item_builders = prioritized_search_item_builders
        self._spotify_client = spotify_client
        self._entity_matcher = entity_matcher

    async def search(self, stream: bytes) -> Optional[str]:
        recognition_output = await self._shazam.recognize(stream)

        if self._is_successful_recognition(recognition_output):
            return await self._match_recognized_track(recognition_output)

        logger.info("Shazam failed to recognized streamed track sample. Skipping")

    @staticmethod
    def _is_successful_recognition(recognition_output: dict) -> bool:
        artist = extract_shazam_artist(recognition_output)
        track = extract_shazam_track(recognition_output)

        return artist is not None and track is not None

    async def _match_recognized_track(self, recognition_output: dict) -> Optional[str]:
        for builder in self._prioritized_search_item_builders:
            uri = await self._apply_single_builder(builder, recognition_output)

            if uri is not None:
                return uri

        logger.info("Failed to match recognized track using any search item builder. Skipping")

    async def _apply_single_builder(self, builder: ISearchItemBuilder, recognition_output: dict) -> Optional[str]:
        builder_name = builder.__class__.__name__
        logger.info(f"Building search item using `{builder_name}`")
        search_item = await builder.build(recognition_output)

        if search_item is not None:
            item_name = self._to_item_name(search_item)
            logger.info(f"Search item `{item_name}` built using `{builder_name}`")
            return await self._search_track(search_item)

        logger.info(f"Builder `{builder_name}` did not return any search item. Skipping")

    async def _search_track(self, search_item: SearchItem) -> Optional[str]:
        search_result = await self._spotify_client.search.run_single(search_item)
        entity = MatchingEntity(
            track=search_item.filters.track,
            artist=search_item.filters.artist
        )
        matching_candidate = self._match_candidates(search_result, entity)

        if matching_candidate:
            return matching_candidate

        item_name = self._to_item_name(search_item)
        logger.info(f"Did not find any track that matches `{item_name}`. Skipping")

    def _match_candidates(self, search_result: dict, entity: MatchingEntity) -> Optional[str]:
        candidates = safe_nested_get(search_result, ["tracks", "items"])
        logger.info(f"Matching {len(candidates)} candidates against entity")

        for candidate in candidates:
            uri = self._match_single_candidate(entity, candidate)

            if uri is not None:
                return uri

    def _match_single_candidate(self, entity: MatchingEntity, candidate: dict) -> Optional[str]:
        is_matching, score = self._entity_matcher.match(entity=entity, candidate=candidate)

        if is_matching:
            logger.info(f"Successfully matched candidate against entity with score of {score}")  # TODO: Add candidate name for better logging
            return candidate["uri"]

        logger.info(f"Failed matching candidate against entity. Score {score} is below threshold")  # TODO: Add candidate name for better logging

    @staticmethod
    def _to_item_name(search_item: SearchItem) -> str:
        return f"{search_item.filters.artist} - {search_item.filters.track}"
