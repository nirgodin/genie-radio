from unittest.mock import MagicMock

from _pytest.fixtures import fixture
from genie_common.clients.google import GoogleTranslateClient
from genie_common.utils import random_alphanumeric_string, random_enum_value
from genie_datastores.postgres.models import Translation, EntityType
from genie_datastores.postgres.operations import insert_records
from genie_datastores.testing.postgres import postgres_session, PostgresMockFactory
from sqlalchemy.ext.asyncio import AsyncEngine

from genie_radio.tools import Translator


class TestTranslator:
    @fixture(autouse=True)
    async def set_up(self, postgres_engine: AsyncEngine, existing_translation: Translation):
        async with postgres_session(postgres_engine):
            await insert_records(engine=postgres_engine, records=[existing_translation])

            yield

    async def test_translate__result_from_cache__returns_existing_result(self, translator: Translator, existing_translation: Translation, translation_client: MagicMock):
        actual = await translator.translate(
            record_id=existing_translation.entity_id,
            text=random_alphanumeric_string(),
            entity_type=random_enum_value(EntityType),
        )

        assert actual == existing_translation.translation
        translation_client.assert_not_called()

    async def test_translate__result_not_in_cache__requests_translation_and_stores_in_cache(self):
        pass

    async def test_translate__result_not_in_cache_and_invalid_response_from_client__returns_none(self):
        pass

    @fixture
    def existing_translation(self) -> Translation:
        return PostgresMockFactory.translation()

    @fixture(scope="class")
    def translator(self, translation_client: MagicMock, postgres_engine: AsyncEngine) -> Translator:
        return Translator(
            db_engine=postgres_engine,
            translation_client=translation_client
        )

    @fixture(scope="class")
    def translation_client(self) -> MagicMock:
        return MagicMock(GoogleTranslateClient)
