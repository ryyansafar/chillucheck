"""Chillu letters have two encodings. Unicode normalisation treats them as different text."""
ZWJ = "‍"
VIRAMA = "്"

# atomic chillu (Unicode 5.1) -> the consonant that the old "consonant + virama + ZWJ" form uses
_ATOMIC_TO_BASE = {
    "ൺ": "ണ",  # NNA
    "ൻ": "ന",  # NA
    "ർ": "ര",  # RA
    "ൽ": "ല",  # LA
    "ൾ": "ള",  # LLA
    "ൿ": "ക",  # KA
}
_OLD_TO_ATOMIC = {base + VIRAMA + ZWJ: atomic for atomic, base in _ATOMIC_TO_BASE.items()}
_ATOMIC_TO_OLD = {atomic: old for old, atomic in _OLD_TO_ATOMIC.items()}


def fold_chillu(text: str) -> str:
    """Fold old-form chillus to the atomic form. Use for MATCHING and SORTING only, never to rewrite data."""
    for old, atomic in _OLD_TO_ATOMIC.items():
        text = text.replace(old, atomic)
    return text


def to_old_form(text: str) -> str:
    """The reverse: atomic chillus written the legacy way."""
    for atomic, old in _ATOMIC_TO_OLD.items():
        text = text.replace(atomic, old)
    return text


def has_atomic_chillu(text: str) -> bool:
    return any(ch in _ATOMIC_TO_BASE for ch in text)


def has_old_chillu(text: str) -> bool:
    return any(old in text for old in _OLD_TO_ATOMIC)
