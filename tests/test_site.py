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


def test_two_events_on_one_day_are_one_labelled_line():
    """The Championship season seats two regions on one weekend.

    Two events at one date draw one line, so two annotations land on the same x
    and the second one's opaque plate paints out the first. The figure has to
    name both or it names neither: `RC IRC China` is what the overprint reads
    as, and a reader cannot tell which event the line marks.

    Joined without repeating the class the two share, the label running up the
    side of a panel that has no height to spare for a second `RC`.
    """
    from tracker import plots

    weeks = [{"week": "2026-09-07", "chal_share": 0.1, "lists": 40, "chal": 30, "trophy_share": 0.1}]
    events = [
        {"date": "2026-09-12", "label": "RC Baltimore"},
        {"date": "2026-09-12", "label": "RC China"},
    ]
    figure, axis = plots.plt.subplots()
    plots._label_events(axis, plots._days(weeks), events)
    labels = [text.get_text() for text in axis.texts]
    plots.plt.close(figure)

    assert labels == ["RC Baltimore / China"]
    # Only the word they actually share: two events of different kinds keep
    # both names whole.
    assert plots._joined(["Pro Tour Amsterdam", "RC China"]) == "Pro Tour Amsterdam / RC China"
    assert plots._joined(["Spotlight Brisbane", "Spotlight Dallas"]) == "Spotlight Brisbane / Dallas"


def test_every_figure_carries_a_name_a_screen_reader_can_read():
    """An inline chart is a tree of paths and announces itself as nothing.

    The panel titles are `<text>` among the tick labels, so a reader that lands
    on the figure is told the axis ticks and never what it is a figure of. The
    name has to be on the `<svg>` itself, as the `role` and `<title>` pair, and
    it has to be the first child or a reader takes the first `<text>` instead.
    """
    from tracker import plots

    weeks = [
        {"week": "2026-08-31", "chal_share": 0.09, "trophy_share": 0.07, "lists": 71,
         "chal": 44, "top8_share": 0.15, "builds": 40, "copied_share": 0.1},
        {"week": "2026-09-07", "chal_share": 0.07, "trophy_share": 0.07, "lists": 28,
         "chal": 28, "top8_share": 0.10, "builds": 24, "copied_share": 0.2},
    ]
    figures = [
        plots.presence(weeks, [], []),
        plots.conversion(weeks, []),
        plots.goldfishing(weeks, []),
    ]
    for markup in figures:
        opening = markup[: markup.index(">") + 1]
        assert opening.startswith('<svg role="img"')
        # The container sizes the figure; the viewBox carries the shape.
        assert "width=" not in opening and "height=" not in opening
        assert "viewBox=" in opening
        rest = markup[len(opening):]
        assert rest.startswith("<title>"), "the name is the first child"
        name = rest[len("<title>"): rest.index("</title>")]
        assert len(name) > 20 and name.endswith(".")

    names = {markup[markup.index("<title>"):markup.index("</title>")] for markup in figures}
    assert len(names) == len(figures), "each figure says what it is, not what a figure is"
