from unittest.mock import MagicMock, AsyncMock

from _pytest.fixtures import fixture
from genie_common.clients.google import GoogleTranslateClient
from genie_common.models.google import TranslationResponse
from genie_common.utils import random_alphanumeric_string, random_enum_value
from genie_datastores.postgres.models import Translation, EntityType
from genie_datastores.postgres.operations import insert_records, execute_query
from genie_datastores.testing.postgres import postgres_session, PostgresMockFactory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from genie_radio.tools import Translator


class TestTranslator:
    @fixture(autouse=True)
    async def set_up(self, postgres_engine: AsyncEngine, existing_translation: Translation):
        async with postgres_session(postgres_engine):
            await insert_records(engine=postgres_engine, records=[existing_translation])

            yield

    async def test_translate__result_from_cache__returns_existing_result(
            self,
            translator: Translator,
            existing_translation: Translation,
            translation_client: MagicMock
    ):
        actual = await translator.translate(
            record_id=existing_translation.entity_id,
            text=random_alphanumeric_string(),
            entity_type=random_enum_value(EntityType),
        )

        assert actual == existing_translation.translation
        translation_client.assert_not_called()

    async def test_translate__result_not_in_cache__requests_translation_and_stores_in_cache(
            self,
            translator: Translator,
            non_existing_translation: Translation,
            translation_client: MagicMock,
            postgres_engine: AsyncEngine
    ):
        translation_client.translate.return_value = [
            TranslationResponse(
                text=non_existing_translation.text,
                translation=non_existing_translation.translation,
                source_language=non_existing_translation.source_language,
                target_language=non_existing_translation.target_language
            )
        ]
        actual = await translator.translate(
            record_id=non_existing_translation.entity_id,
            text=non_existing_translation.text,
            entity_type=non_existing_translation.entity_type,
        )

        assert actual == non_existing_translation.translation
        translation_client.translate.assert_called_once_with(
            texts=[non_existing_translation.text],
            target_language="he"
        )
        await self._assert_record_exists(postgres_engine, non_existing_translation)

    async def test_translate__result_not_in_cache_and_invalid_response_from_client__returns_none(self):
        pass

    @fixture
    def existing_translation(self) -> Translation:
        return PostgresMockFactory.translation()

    @fixture
    def non_existing_translation(self) -> Translation:
        return PostgresMockFactory.translation(
            entity_id=random_alphanumeric_string(22, 22)
        )

    @fixture(scope="class")
    def translator(self, translation_client: AsyncMock, postgres_engine: AsyncEngine) -> Translator:
        return Translator(
            db_engine=postgres_engine,
            translation_client=translation_client
        )

    @fixture(scope="class")
    def translation_client(self) -> AsyncMock:
        return AsyncMock(GoogleTranslateClient)

    @staticmethod
    async def _assert_record_exists(postgres_engine: AsyncEngine, non_existing_translation: Translation) -> None:
        query = (
            select(Translation)
            .where(Translation.entity_id == non_existing_translation.entity_id)
        )
        query_result = await execute_query(engine=postgres_engine, query=query)
        records = query_result.scalars().all()

        assert len(records) == 1
        assert records[0].text == non_existing_translation.text
        assert records[0].translation == non_existing_translation.translation
