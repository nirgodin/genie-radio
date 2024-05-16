from typing import Optional

from spotipyio import SearchItem

from genie_radio.logic.search_item_builders.search_item_builder_interface import ISearchItemBuilder
from genie_radio.utils import extract_shazam_track, extract_shazam_artist, build_search_item


class PlainSearchItemBuilder(ISearchItemBuilder):
    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        artist = extract_shazam_artist(recognition_output)
        track = extract_shazam_track(recognition_output)

        return build_search_item(artist, track)
