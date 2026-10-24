from fastapi.testclient import TestClient

from board.app import app

client = TestClient(app)


def test_check_returns_nine_results_and_counts():
    r = client.get("/api/check", params={"text": "അടൂർ"})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["total"] == 9
    assert body["summary"]["mangled_before"] >= 1
    assert body["summary"]["mangled_after"] == 0
    assert len(body["results"]) == 9
    assert {"id", "title", "why", "before", "after", "mangled_before", "exposed"} <= set(body["results"][0])


def test_empty_text_is_all_zero():
    body = client.get("/api/check", params={"text": ""}).json()
    assert body["summary"]["mangled_before"] == 0


def test_text_over_the_limit_is_rejected():
    r = client.get("/api/check", params={"text": "അ" * 201})
    assert r.status_code == 422


def test_missing_text_is_rejected():
    assert client.get("/api/check").status_code == 422


def test_baseline_reports_the_whole_corpus():
    body = client.get("/api/baseline").json()
    assert body["names"] > 2000
    assert body["share_broken_by_at_least_one"] == 1.0
    assert "md_anchor" in body["per_path_share"]


def test_home_page_serves_the_box_and_the_malayalam_font():
    r = client.get("/")
    assert r.status_code == 200
    assert 'id="name"' in r.text
    assert "Manjari" in r.text


def test_font_is_served_locally():
    r = client.get("/assets/fonts/Manjari-Regular.ttf")
    assert r.status_code == 200


def test_health():
    assert client.get("/health").json() == {"ok": True}
