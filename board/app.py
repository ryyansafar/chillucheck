"""The type-your-name board: runs a name through nine real code paths, before and after the patches."""
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from chillucheck.corpus import baseline
from chillucheck.paths import run_all, summarise

ROOT = Path(__file__).resolve().parent.parent
MAX_TEXT = 200

app = FastAPI(title="chillucheck board")
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/check")
def check(text: str = Query(..., max_length=MAX_TEXT)) -> dict:
    return {"text": text, "summary": summarise(text), "results": [asdict(r) for r in run_all(text)]}


@lru_cache(maxsize=1)
def _baseline() -> dict:
    return baseline()


@app.get("/api/baseline")
def get_baseline() -> dict:
    return _baseline()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
