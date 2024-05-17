from typing import List

from genie_radio.components.tools_factory import ToolsFactory
from genie_radio.logic.search_item_builders import (
    ISearchItemBuilder,
    PlainSearchItemBuilder,
    TranslatedArtistSearchItemBuilder,
    TranslatedTrackSearchItemBuilder,
    TranslatedSongSearchItemBuilder
)


class SearchItemBuildersFactory:
    def __init__(self, tools: ToolsFactory = ToolsFactory()):
        self._tools = tools

    def get_prioritized_builders(self) -> List[ISearchItemBuilder]:
        return [
            self.get_plain_builder(),
            self.get_translated_artist_builder(),
            self.get_translated_song_track_builder(),
            self.get_translated_song_track_builder()
        ]

    @staticmethod
    def get_plain_builder() -> PlainSearchItemBuilder:
        return PlainSearchItemBuilder()

    def get_translated_artist_builder(self) -> TranslatedArtistSearchItemBuilder:
        return TranslatedArtistSearchItemBuilder(self._tools.get_translator())

    def get_translated_track_builder(self) -> TranslatedTrackSearchItemBuilder:
        return TranslatedTrackSearchItemBuilder(self._tools.get_translator())

    def get_translated_song_track_builder(self) -> TranslatedSongSearchItemBuilder:
        return TranslatedSongSearchItemBuilder(self._tools.get_translator())
