import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_exact_100_apps_and_10_categories():
    apps = json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))["applications"]
    assert len(apps) == 100
    assert len({row["id"] for row in apps}) == 100
    assert len({row["name"] for row in apps}) == 100
    assert len({row["category"] for row in apps}) == 10

def test_apps_have_site_and_docs_hints():
    apps = json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))["applications"]
    assert all(row.get("official_website_hint") for row in apps)
    assert all(row.get("docs_hint") for row in apps)
