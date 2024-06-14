from typing import Optional, List

from genie_common.clients.google import GoogleTranslateClient
from genie_common.models.google import TranslationResponse
from genie_common.tools import logger
from genie_common.utils import contains_any_alpha_character
from genie_datastores.postgres.models import Translation, DataSource, EntityType
from genie_datastores.postgres.operations import execute_query, insert_records
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from genie_radio.utils import decide_target_language


class Translator:
    def __init__(self, translation_client: GoogleTranslateClient, db_engine: AsyncEngine):
        self._translation_client = translation_client
        self._db_engine = db_engine

    async def translate(self,
                        record_id: str,
                        text: str,
                        entity_type: EntityType,
                        target_language: Optional[str] = None) -> Optional[str]:
        logger.info(f"Translating record id `{record_id}` with value `{text}`")
        translation = await self._retrieve_cached_translation(record_id)

        if translation is not None:
            return translation

        return await self._request_translation(
            record_id=record_id,
            text=text,
            entity_type=entity_type,
            target_language=target_language
        )

    async def _retrieve_cached_translation(self, record_id: str) -> Optional[str]:
        logger.info(f"Retrieving record id `{record_id}` translation from cache")
        query = (
            select(Translation.translation)
            .where(Translation.id == record_id)
            .limit(1)
        )
        query_result = await execute_query(engine=self._db_engine, query=query)
        translation = query_result.scalars().first()

        if translation is None:
            logger.info(f"Did not find record id `{record_id}` in translations cache")

        logger.info(f"Found record id `{record_id}` translation in cache")
        return translation

    async def _request_translation(self,
                                   record_id: str,
                                   text: str,
                                   entity_type: EntityType,
                                   target_language: Optional[str]) -> Optional[str]:
        language = self._determine_target_language(target_language, text)
        logger.info(f"Sending translation request to language `{language}` for text `{text}`")
        responses = await self._translation_client.translate(
            texts=[text],
            target_language=language
        )
        first_response = self._extract_first_translation_response(responses, text)

        if first_response is not None:
            first_response.translation = first_response.translation.replace("&amp;", "&")
            await self._store_translation_in_cache(
                record_id=record_id,
                text=text,
                response=first_response,
                entity_type=entity_type
            )

        return first_response.translation

    @staticmethod
    def _determine_target_language(target_language: Optional[str], text: str) -> str:
        if target_language is not None:
            return target_language

        return decide_target_language(text)

    @staticmethod
    def _extract_first_translation_response(responses: List[TranslationResponse],
                                            text: str) -> Optional[TranslationResponse]:
        if responses:
            first_response = responses[0]
            logger.info(f"Successfully translated `{text}` to `{first_response.translation}`")

            return first_response

        logger.info(f"Translation service did not return any response. Returning None instead")

    async def _store_translation_in_cache(self,
                                          record_id: str,
                                          text: str,
                                          response: TranslationResponse,
                                          entity_type: EntityType) -> None:
        logger.info(f"Inserting record id `{record_id}` translation to cache")
        entity_source = self._detect_entity_source(record_id)
        record = Translation(
            entity_id=record_id,
            entity_source=entity_source,
            entity_type=entity_type,
            text=text,
            translation=response.translation,
            source_language=response.source_language,
            target_language=response.target_language
        )
        await insert_records(engine=self._db_engine, records=[record])
        logger.info(f"Successfully inserted record id `{record_id}` translation to cache")

    @staticmethod
    def _detect_entity_source(record_id: str) -> DataSource:
        if not contains_any_alpha_character(record_id):
            return DataSource.SHAZAM

        if len(record_id) == 22:
            return DataSource.SPOTIFY

        raise ValueError(f"Did not recognize record id `{record_id}` as any of the following source: Shazam, Spotify")
