from spotipyio import SearchItem, SearchItemFilters, SearchItemMetadata, SpotifySearchType


def build_search_item(artist: str, track: str) -> SearchItem:
    return SearchItem(
        text=f"{artist} - {track}",
        metadata=SearchItemMetadata(
            search_types=[SpotifySearchType.TRACK],
            quote=False
        )
    )
