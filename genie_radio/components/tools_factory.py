from functools import lru_cache

from genie_common.clients.google import GoogleTranslateClient
from genie_datastores.postgres.operations import get_database_engine

from genie_radio.tools import Translator


class ToolsFactory:
    @lru_cache
    def get_translator(self) -> Translator:
        return Translator(
            translation_client=self.get_google_translate_client(),
            db_engine=get_database_engine()
        )

    @staticmethod
    def get_google_translate_client() -> GoogleTranslateClient:
        return GoogleTranslateClient.create()
