"""Grapheme-safe text slicing. A Malayalam 'letter' is often several code points."""
import regex


def graphemes(text: str) -> list[str]:
    return regex.findall(r"\X", text)


def boundaries(text: str) -> set[int]:
    pos, out = 0, {0}
    for g in graphemes(text):
        pos += len(g)
        out.add(pos)
    return out


def is_boundary(text: str, index: int) -> bool:
    return index in boundaries(text)


def naive_cut(text: str, n: int) -> str:
    """What s[:n] does: counts code points."""
    return text[:n]


def safe_cut(text: str, n: int) -> str:
    """The first n whole graphemes."""
    return "".join(graphemes(text)[:n])
