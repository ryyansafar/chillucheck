"""The nine real code paths: each has a BEFORE (library as shipped) and an AFTER (patched) behaviour."""
import pytest

from chillucheck.paths import PATHS, run_all, summarise

ZWJ = "‍"
VIRAMA = "്"
ATOMIC_NAME = "അവൻ"                      # chillu written with U+0D7B
OLD_NAME = "അവ" + "ന" + VIRAMA + ZWJ  # the same name, old encoding


def path(pid):
    return next(p for p in PATHS if p.id == pid)


def test_there_are_nine_paths_with_unique_ids():
    assert len(PATHS) == 9
    assert len({p.id for p in PATHS}) == 9


def test_markdown_anchor_is_empty_before_and_kept_after():
    p = path("md_anchor")
    assert p.before("ക്ഷേത്രം ഉത്സവം") == ""
    assert p.after("ക്ഷേത്രം ഉത്സവം") == "ക്ഷേത്രം-ഉത്സവം"
    assert p.mangled("ക്ഷേത്രം ഉത്സവം", p.before("ക്ഷേത്രം ഉത്സവം"))
    assert not p.mangled("ക്ഷേത്രം ഉത്സവം", p.after("ക്ഷേത്രം ഉത്സവം"))


def test_markdown_unicode_anchor_drops_signs_before_and_keeps_them_after():
    p = path("md_anchor_unicode")
    assert p.before("ക്ഷേത്രം ഉത്സവം") == "കഷതര-ഉതസവ"
    assert p.after("ക്ഷേത്രം ഉത്സവം") == "ക്ഷേത്രം-ഉത്സവം"


def test_slugify_unicode_splits_a_vowel_sign_before_and_keeps_it_after():
    p = path("slug_unicode")
    assert p.before("അടൂർ") == "അട-ർ"
    assert p.after("അടൂർ") == "അടൂർ"


def test_slugify_ascii_loses_the_letters():
    p = path("slug_ascii")
    assert p.before("അടൂർ") == "attuu"
    assert p.mangled("അടൂർ", p.before("അടൂർ"))
    assert p.after("അടൂർ") == "അടൂർ"


def test_naive_cut_splits_a_letter_before_and_not_after():
    p = path("cut")
    text = "ക്ഷേത്രം ഉത്സവം"
    assert p.mangled(text, p.before(text))
    assert not p.mangled(text, p.after(text))


def test_search_misses_the_other_encoding_before_and_finds_it_after():
    p = path("search")
    assert p.exposed(ATOMIC_NAME)
    assert p.mangled(ATOMIC_NAME, p.before(ATOMIC_NAME))
    assert not p.mangled(ATOMIC_NAME, p.after(ATOMIC_NAME))
    assert not p.exposed("കേരളം")        # no chillu, not exposed to this bug


def test_sort_splits_the_two_encodings_before_and_keeps_them_together_after():
    p = path("sort")
    assert p.exposed(ATOMIC_NAME)
    assert p.mangled(ATOMIC_NAME, p.before(ATOMIC_NAME))
    assert not p.mangled(ATOMIC_NAME, p.after(ATOMIC_NAME))


def test_joiner_strip_changes_old_encoding_text_and_after_preserves_it():
    p = path("strip_zwj")
    assert p.exposed(OLD_NAME)
    assert p.mangled(OLD_NAME, p.before(OLD_NAME))
    assert p.after(OLD_NAME) == OLD_NAME
    assert not p.exposed(ATOMIC_NAME)


def test_reverse_breaks_clusters_before_and_not_after():
    p = path("reverse")
    text = "ക്ഷേത്രം"
    assert p.mangled(text, p.before(text))
    assert p.after(text) == "ത്രംക്ഷേ"
    assert not p.mangled(text, p.after(text))


@pytest.mark.parametrize("name", ["അടൂർ", "ക്ഷേത്രം ഉത്സവം", "കൊച്ചി", "അവൻ", "തിരുവനന്തപുരം"])
def test_after_never_mangles_what_before_mangles(name):
    for r in run_all(name):
        assert not r.mangled_after, (r.id, name)


def test_summary_counts_paths():
    s = summarise("ക്ഷേത്രം ഉത്സവം")
    assert s["total"] == 9
    assert s["mangled_before"] >= 5
    assert s["mangled_after"] == 0
    s2 = summarise("")
    assert s2["mangled_before"] == 0


def test_run_all_is_stable_over_ten_runs():
    first = [(r.id, r.before, r.after, r.mangled_before) for r in run_all("അടൂർ")]
    for _ in range(10):
        assert [(r.id, r.before, r.after, r.mangled_before) for r in run_all("അടൂർ")] == first
