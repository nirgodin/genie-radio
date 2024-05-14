from typing import Any, Optional

from spotipyio.contract import IEntityExtractor


class ArtistEntityExtractor(IEntityExtractor):
    def extract(self, entity: dict) -> Optional[str]:
        artists = entity.get("artists")

        if artists:
            first_artist = artists[0]
            return first_artist.get("name")

    @property
    def name(self) -> str:
        return "artist"
