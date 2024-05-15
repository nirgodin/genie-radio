from typing import Optional, List

from genie_common.tools import logger
from genie_common.utils import safe_nested_get
from spotipyio import SpotifyClient


class PlaylistUpdater:
    def __init__(self,
                 spotify_client: SpotifyClient,
                 playlist_id: str,
                 max_items: int = 100,
                 snapshot_id: Optional[str] = None,
                 playlist_uris: Optional[List[str]] = None):
        self._spotify_client = spotify_client
        self._playlist_id = playlist_id
        self._max_items = max_items
        self._snapshot_id = snapshot_id
        self._playlist_uris = playlist_uris

    async def update(self, uri: str) -> None:
        if self._snapshot_id is None or self._playlist_uris is None:
            await self._initialize_playlist_state()

        if self._is_new_uri(uri):
            if len(self._playlist_uris) >= self._max_items:
                await self._remove_oldest_uri()

            await self._update_playlist(uri)

        else:
            logger.info(f"URI `{uri}` is already the newest URI in the playlist. Skipping")

    async def _initialize_playlist_state(self) -> None:
        logger.info("Initializing playlist state")
        playlist = await self._spotify_client.playlists.info.run_single(self._playlist_id)
        self._playlist_uris = self._extract_playlist_uris(playlist)
        self._snapshot_id = playlist["snapshot_id"]
        logger.info("Successfully initialized playlist state")

    @staticmethod
    def _extract_playlist_uris(playlist: dict) -> List[str]:
        items = safe_nested_get(playlist, ["tracks", "items"])
        uris = []

        for item in items:
            item_uri = safe_nested_get(item, ["track", "uri"])
            uris.append(item_uri)

        return uris

    def _is_new_uri(self, uri: str) -> bool:
        if not self._playlist_uris:
            return True

        return uri != self._playlist_uris[0]

    async def _update_playlist(self, uri: str) -> None:
        logger.info(f"Adding newest uri `{uri}` to playlist `{self._playlist_id}`")
        response = await self._spotify_client.playlists.add_items.run(
            playlist_id=self._playlist_id,
            uris=[uri],
            position=0
        )
        self._playlist_uris.insert(0, uri)
        self._snapshot_id = response["snapshot_id"]

    async def _remove_oldest_uri(self):
        oldest_uri = self._playlist_uris.pop(-1)
        logger.info(f"Detected playlist `{self._playlist_id}` reached max uris. Removing oldest uris `{oldest_uri}`")
        await self._spotify_client.playlists.remove_items.run(
            playlist_id=self._playlist_id,
            uris=[oldest_uri],
            snapshot_id=self._snapshot_id
        )
