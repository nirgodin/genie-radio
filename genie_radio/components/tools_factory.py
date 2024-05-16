from genie_common.clients.google import GoogleTranslateClient


class ToolsFactory:
    @staticmethod
    def get_google_translate_client() -> GoogleTranslateClient:
        return GoogleTranslateClient.create()
