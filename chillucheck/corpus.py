"""Fixture corpus: SMC person names and places (CC BY-SA 3.0, https://gitlab.com/smc/corpus)."""
import unicodedata
from pathlib import Path

from .paths import PATHS, run_all

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load_corpus() -> list[str]:
    names: dict[str, None] = {}
    for fname in ("smc-person-names.txt", "smc-places.txt"):
        for line in (FIXTURES / fname).read_text(encoding="utf-8").splitlines():
            line = unicodedata.normalize("NFC", line.strip())
            if line:
                names[line] = None
    return list(names)


def baseline(names: list[str] | None = None) -> dict:
    names = names if names is not None else load_corpus()
    per_path = {p.id: 0 for p in PATHS}
    broken_any = 0
    for n in names:
        results = run_all(n)
        for r in results:
            per_path[r.id] += r.mangled_before
        broken_any += any(r.mangled_before for r in results)
    total = len(names)
    return {
        "names": total,
        "broken_by_at_least_one": broken_any,
        "share_broken_by_at_least_one": broken_any / total if total else 0.0,
        "per_path_share": {k: v / total for k, v in per_path.items()},
    }
