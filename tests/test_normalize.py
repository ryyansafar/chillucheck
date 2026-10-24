"""Chillu folding: the two encodings of a chillu letter must be unifiable for matching."""
import unicodedata

from chillucheck.normalize import fold_chillu, has_old_chillu, has_atomic_chillu, to_old_form

ZWJ = "‍"
VIRAMA = "്"


def old(letter: str, base: str) -> str:
    return base + VIRAMA + ZWJ


def test_old_form_folds_to_atomic_for_all_chillus():
    pairs = {
        "ൺ": old("ൺ", "ണ"),  # ൺ NNA
        "ൻ": old("ൻ", "ന"),  # ൻ NA
        "ർ": old("ർ", "ര"),  # ർ RA
        "ൽ": old("ൽ", "ല"),  # ൽ LA
        "ൾ": old("ൾ", "ള"),  # ൾ LLA
        "ൿ": old("ൿ", "ക"),  # ൿ KA
    }
    for atomic, legacy in pairs.items():
        assert fold_chillu(legacy) == atomic


def test_unicode_normalisation_alone_does_not_unify_them():
    atomic, legacy = "അവൻ", "അവ" + old("ൻ", "ന")
    for form in ("NFC", "NFD", "NFKC", "NFKD"):
        assert unicodedata.normalize(form, atomic) != unicodedata.normalize(form, legacy)
    assert fold_chillu(atomic) == fold_chillu(legacy)


def test_fold_is_idempotent_and_leaves_plain_text_alone():
    s = "ക്ഷേത്രം ഉത്സവം kochi 123"
    assert fold_chillu(s) == s
    legacy = "അടൂ" + old("ർ", "ര")
    assert fold_chillu(fold_chillu(legacy)) == fold_chillu(legacy)


def test_fold_does_not_touch_a_virama_without_zwj():
    s = "അടൂര്"  # ര + virama, no joiner: a bare virama, not a chillu
    assert fold_chillu(s) == s


def test_to_old_form_round_trips():
    atomic = "അടൂർ അവൻ കൽ"
    assert fold_chillu(to_old_form(atomic)) == atomic


def test_detectors():
    assert has_atomic_chillu("അവൻ")
    assert not has_atomic_chillu("കേരളം")
    assert has_old_chillu("അവ" + old("ൻ", "ന"))
    assert not has_old_chillu("അവൻ")
