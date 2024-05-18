from genie_common.utils import contains_any_non_english_character


def decide_target_language(text: str) -> str:
    return "en" if contains_any_non_english_character(text) else "he"
