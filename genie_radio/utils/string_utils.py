from string import ascii_letters, punctuation

ASCII_PUNCTUATION_LETTERS = ascii_letters + punctuation


def contains_any_non_ascii_or_punctuation_char(text: str) -> bool:
    return any(letter not in ASCII_PUNCTUATION_LETTERS for letter in text)
