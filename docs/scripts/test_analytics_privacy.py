"""Regression checks for the public docs analytics privacy boundary."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUNNEL = (ROOT / "theme" / "aa-funnel-events.js").read_text(encoding="utf-8")
HEAD = (ROOT / "theme" / "head.hbs").read_text(encoding="utf-8")


def test_ga_config_denies_automatic_page_view_and_referrer() -> None:
    assert "'send_page_view': false" in HEAD
    assert "'page_referrer': ''" in HEAD


def test_event_payload_uses_closed_page_and_domain_values() -> None:
    assert "page_id: pageId()" in FUNNEL
    assert "link_url" not in FUNNEL
    assert "location.hostname" not in FUNNEL
    assert "document.title" not in FUNNEL


def test_feedback_does_not_capture_visitor_url() -> None:
    assert "var body = 'Page: ' + location.href" not in HEAD
    assert "page_id': 'docs'" in HEAD
