"""Nine real code paths that mangle Malayalam, each with the shipped behaviour (BEFORE) and a patched one (AFTER)."""
from __future__ import annotations

import bisect
import re
import unicodedata
from dataclasses import dataclass
from typing import Callable

import markdown.extensions.toc as md_toc
from slugify import slugify

from .graphemes import graphemes, is_boundary, naive_cut, safe_cut
from .normalize import ZWJ, fold_chillu, has_atomic_chillu, has_old_chillu, to_old_form

CUT_LENGTH = 5
# Malayalam block plus the joiners, ASCII letters and digits: everything slugs may keep
_DISALLOWED = re.compile(r"[^ഀ-ൿ‌‍a-zA-Z0-9-]+")
_MD_STRIP = re.compile(r"[^ഀ-ൿ‌‍\w\s-]")


def expected_slug(text: str) -> str:
    return "-".join(unicodedata.normalize("NFC", text).split())


def slug_fixed(text: str) -> str:
    return slugify(text, allow_unicode=True, regex_pattern=_DISALLOWED)


def md_slug_fixed(value: str, separator: str = "-") -> str:
    value = unicodedata.normalize("NFC", value)
    value = _MD_STRIP.sub("", value).strip()
    return re.sub(r"[%s\s]+" % re.escape(separator), separator, value)


def _variant(text: str) -> str:
    """The same text in the other chillu encoding."""
    if has_atomic_chillu(text):
        return to_old_form(text)
    if has_old_chillu(text):
        return fold_chillu(text)
    return text


def _exposed_to_encoding(text: str) -> bool:
    return has_atomic_chillu(text) or has_old_chillu(text)


def _search(text: str, fold: bool) -> str:
    query = _variant(text)
    if fold:
        return "FOUND" if fold_chillu(query) in fold_chillu(text) else "NOT FOUND"
    return "FOUND" if query in text else "NOT FOUND"


_SORTED_CORPUS: list[str] | None = None


def _sorted_corpus() -> list[str]:
    global _SORTED_CORPUS
    if _SORTED_CORPUS is None:
        from .corpus import load_corpus  # local import: corpus imports this module

        _SORTED_CORPUS = sorted(load_corpus())
    return _SORTED_CORPUS


def _between(a: str, b: str) -> int:
    """How many real corpus names sort strictly between the two spellings of the same word."""
    lo, hi = sorted((a, b))
    names = _sorted_corpus()
    return bisect.bisect_left(names, hi) - bisect.bisect_right(names, lo)


def _sort_demo(text: str, fold: bool) -> str:
    other = _variant(text)
    if fold:
        k = _between(fold_chillu(text), fold_chillu(other))
    else:
        k = _between(text, other)
    return f"{k} real names sort between the two spellings"


def _sort_mangled(text: str, out: str) -> bool:
    return int(out.split(" ", 1)[0]) > 0


@dataclass(frozen=True)
class Path:
    id: str
    title: str
    why: str
    before: Callable[[str], str]
    after: Callable[[str], str]
    mangled: Callable[[str, str], bool]
    exposed: Callable[[str], bool] = lambda text: bool(text)


@dataclass(frozen=True)
class Result:
    id: str
    title: str
    why: str
    exposed: bool
    before: str
    after: str
    mangled_before: bool
    mangled_after: bool


PATHS: tuple[Path, ...] = (
    Path("slug_ascii", "python-slugify (default)",
         "Transliterates to ASCII and drops what it cannot, so the name is lost.",
         lambda t: slugify(t), slug_fixed,
         lambda t, o: o != expected_slug(t)),
    Path("slug_unicode", "python-slugify (allow_unicode)",
         "Treats vowel signs as punctuation and turns them into hyphens.",
         lambda t: slugify(t, allow_unicode=True), slug_fixed,
         lambda t, o: o != expected_slug(t)),
    Path("md_anchor", "Python-Markdown heading anchor",
         "The anchor comes out empty, so the heading gets a numbered id.",
         lambda t: md_toc.slugify(t, "-"), md_slug_fixed,
         lambda t, o: o != expected_slug(t)),
    Path("md_anchor_unicode", "Python-Markdown anchor (unicode option)",
         "Even the unicode option strips every vowel sign and virama.",
         lambda t: md_toc.slugify_unicode(t, "-"), md_slug_fixed,
         lambda t, o: o != expected_slug(t)),
    Path("cut", f"Cut to {CUT_LENGTH} characters (s[:{CUT_LENGTH}])",
         "Counts code points, so it can cut a letter in half.",
         lambda t: naive_cut(t, CUT_LENGTH), lambda t: safe_cut(t, CUT_LENGTH),
         lambda t, o: len(t) > CUT_LENGTH and not is_boundary(t, len(o)) if o == t[:len(o)] else False),
    Path("search", "Search across the two chillu encodings",
         "The old and the new way of writing a chillu never match, though they look identical.",
         lambda t: _search(t, False), lambda t: _search(t, True),
         lambda t, o: o == "NOT FOUND", _exposed_to_encoding),
    Path("sort", "Default sort",
         "The two encodings of the same word sort far apart.",
         lambda t: _sort_demo(t, False), lambda t: _sort_demo(t, True),
         _sort_mangled, _exposed_to_encoding),
    Path("strip_zwj", "Strip the joiner (replace U+200D)",
         "Removes the zero-width joiner, so a chillu turns into a bare virama.",
         lambda t: t.replace(ZWJ, ""), lambda t: t,
         lambda t, o: o != t, lambda t: ZWJ in t),
    Path("reverse", "Reverse the text (s[::-1])",
         "Reverses code points, so vowel signs jump to the wrong letter.",
         lambda t: t[::-1], lambda t: "".join(reversed(graphemes(t))),
         lambda t, o: o != "".join(reversed(graphemes(t)))),
)


def run_all(text: str) -> list[Result]:
    results = []
    for p in PATHS:
        exposed = bool(text) and p.exposed(text)
        before = p.before(text) if text else ""
        after = p.after(text) if text else ""
        results.append(Result(
            p.id, p.title, p.why, exposed, before, after,
            exposed and p.mangled(text, before),
            exposed and p.mangled(text, after),
        ))
    return results


def summarise(text: str) -> dict:
    results = run_all(text)
    return {
        "total": len(results),
        "mangled_before": sum(r.mangled_before for r in results),
        "mangled_after": sum(r.mangled_after for r in results),
    }
