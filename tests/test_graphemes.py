"""Grapheme-safe slicing: cutting by code points splits Malayalam letters."""
from chillucheck.graphemes import graphemes, is_boundary, safe_cut, naive_cut


def test_conjunct_is_one_grapheme_cluster():
    assert graphemes("ക്ഷേത്രം") == ["ക്ഷേ", "ത്രം"]


def test_naive_cut_splits_a_letter_and_safe_cut_does_not():
    s = "ക്ഷേത്രം ഉത്സവം"
    assert naive_cut(s, 3) == "ക്ഷ"              # drops the vowel sign േ: half a letter
    assert not is_boundary(s, 3)
    assert safe_cut(s, 3) == "ക്ഷേത്രം "           # three whole graphemes
    assert is_boundary(s, len(safe_cut(s, 3)))


def test_safe_cut_returns_everything_when_short():
    assert safe_cut("കേരളം", 50) == "കേരളം"
    assert safe_cut("", 3) == ""


def test_boundary_at_ends():
    assert is_boundary("അടൂർ", 0)
    assert is_boundary("അടൂർ", len("അടൂർ"))
