from typing import Optional

from genie_common.utils import safe_nested_get


def extract_shazam_artist(recognition_output: dict) -> Optional[str]:
    return safe_nested_get(recognition_output, ["track", "subtitle"])


def extract_shazam_track(recognition_output: dict) -> Optional[str]:
    return safe_nested_get(recognition_output, ["track", "title"])
