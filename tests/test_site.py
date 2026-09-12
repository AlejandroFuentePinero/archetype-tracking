"""The Space is a menu over one week's reports, and refuses to be anything less."""

import pytest

from tracker import config, site


def _render(reports, deck, week, summary=True):
    body = "<p>written</p>" if summary else '<p class="pending">No summary written for this week yet.</p>'
    (reports / f"{deck}-{week}.html").write_text(f"<html><body>{body}</body></html>", encoding="utf-8")


def _render_all(reports, week="2026-08-31"):
    for deck in config.REPORTS:
        _render(reports, deck, week)


def test_the_index_lists_every_deck_alphabetically_under_the_week(tmp_path):
    reports, out = tmp_path / "reports", tmp_path / "site"
    reports.mkdir()
    _render_all(reports)

    assert site.build(out, reports) == "2026-08-31"
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "week ending 2026-09-06" in page
    names = sorted(report["name"] for report in config.REPORTS.values())
    positions = [page.index(f">{name}</a>") for name in names]
    assert positions == sorted(positions), "cards are alphabetical"
    assert {p.name for p in out.iterdir()} == {"index.html", "README.md", *(f"{d}.html" for d in config.REPORTS)}
    assert 'href="blink.html"' in page
    assert site.CONTACT_EMAIL in page


def test_the_latest_report_per_deck_is_the_one_shipped(tmp_path):
    reports, out = tmp_path / "reports", tmp_path / "site"
    reports.mkdir()
    _render_all(reports, "2026-09-07")
    _render_all(reports, "2026-08-31")
    (reports / "blink-2026-09-07.html").write_text("<html><body>newest</body></html>", encoding="utf-8")

    assert site.build(out, reports) == "2026-09-07"
    assert "newest" in (out / "blink.html").read_text(encoding="utf-8")


def test_a_report_without_a_summary_is_refused(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    _render_all(reports)
    _render(reports, "tron", "2026-08-31", summary=False)

    with pytest.raises(SystemExit, match="tron has no summary"):
        site.build(tmp_path / "site", reports)


def test_reports_on_different_weeks_are_refused(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    _render_all(reports)
    _render(reports, "tron", "2026-09-07")

    with pytest.raises(SystemExit, match="disagree on the week"):
        site.build(tmp_path / "site", reports)
