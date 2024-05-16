from spotipyio import SearchItem, SearchItemFilters, SearchItemMetadata, SpotifySearchType


def build_search_item(artist: str, track: str) -> SearchItem:
    return SearchItem(
        filters=SearchItemFilters(
            track=track,
            artist=artist
        ),
        metadata=SearchItemMetadata(
            search_types=[SpotifySearchType.TRACK],
            quote=False
        )
    )
