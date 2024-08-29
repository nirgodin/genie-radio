from typing import Optional, List

from genie_common.tools import logger
from genie_common.utils import safe_nested_get
from spotipyio import SpotifyClient, SearchItem, EntityMatcher, MatchingEntity

from genie_radio.logic.search_item_builders import ISearchItemBuilder


class TrackSearcher:
    def __init__(self,
                 prioritized_search_item_builders: List[ISearchItemBuilder],
                 spotify_client: SpotifyClient,
                 entity_matcher: EntityMatcher):
        self._prioritized_search_item_builders = prioritized_search_item_builders
        self._spotify_client = spotify_client
        self._entity_matcher = entity_matcher

    async def search(self, recognition_output: dict) -> Optional[str]:
        for builder in self._prioritized_search_item_builders:
            uri = await self._apply_single_builder(builder, recognition_output)

            if uri is not None:
                return uri

        logger.info("Failed to match recognized track using any search item builder. Skipping")

    def refresh_session(self) -> None:
        self._spotify_client.session.refresh()

    async def _apply_single_builder(self, builder: ISearchItemBuilder, recognition_output: dict) -> Optional[str]:
        builder_name = builder.__class__.__name__
        logger.info(f"Building search item using `{builder_name}`")
        search_item = await builder.build(recognition_output)

        if search_item is not None:
            logger.info(f"Search item `{search_item.text}` built using `{builder_name}`")
            return await self._search_track(search_item)

        logger.info(f"Builder `{builder_name}` did not return any search item. Skipping")

    async def _search_track(self, search_item: SearchItem) -> Optional[str]:
        search_result = await self._spotify_client.search.search_item.run_single(search_item)
        entity = self._build_matching_entity(search_item)
        matching_candidate = self._match_candidates(search_result, entity)

        if matching_candidate:
            return matching_candidate

        logger.info(f"Did not find any track that matches `{search_item.text}`. Skipping")

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

    def _build_matching_entity(self, search_item: SearchItem) -> MatchingEntity:
        if search_item.filters.track and search_item.filters.artist:
            return MatchingEntity(
                track=search_item.filters.track,
                artist=search_item.filters.artist
            )

        if search_item.text:
            return self._build_matching_entity_from_text(search_item.text)

        raise ValueError("Invalid search item. Was not able to extract track and artist names")

    @staticmethod
    def _build_matching_entity_from_text(text: str) -> MatchingEntity:
        split_text = text.split(" - ")
        split_text_length = len(split_text)
        artist = split_text[0]

        if split_text_length < 2:
            logger.warning(f"Text `{text}` is invalid and has no track name. Using empty string as track name")
            track = ""

        elif split_text_length == 2:
            track = split_text[1]

        else:
            track = " - ".join(split_text[1:])

        return MatchingEntity(
            artist=artist,
            track=track
        )
