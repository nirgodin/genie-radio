from genie_common.clients.google.google_translate_client import GoogleTranslateClient


class ToolsFactory:
    @staticmethod
    def get_google_translate_client() -> GoogleTranslateClient:
        return GoogleTranslateClient.create()