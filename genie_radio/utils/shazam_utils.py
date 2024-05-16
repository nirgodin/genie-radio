from typing import Optional

from genie_common.utils import safe_nested_get


def extract_shazam_artist(recognition_output: dict) -> Optional[str]:
    return safe_nested_get(recognition_output, ["track", "subtitle"])


def extract_shazam_track(recognition_output: dict) -> Optional[str]:
    return safe_nested_get(recognition_output, ["track", "title"])


def extract_shazam_artist_id(recognition_output: dict) -> Optional[str]:
    artists = safe_nested_get(recognition_output, ["track", "artists"])

    if artists:
        first_artist = artists[0]
        return first_artist.get("adamid")


def extract_shazam_track_id(recognition_output: dict) -> Optional[str]:
    return safe_nested_get(recognition_output, ["track", "key"])
