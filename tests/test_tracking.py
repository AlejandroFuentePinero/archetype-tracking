"""The tracked deck's readings: membership, the weekly figures, the timeline.

Same seam as the rest of the suite: synthetic payloads written as the site
publishes them, in one end, and the verdict a reader would act on out the other.
Nothing here asserts on a query, a column or an intermediate table.

The series are written rather than captured for the reason `synthetic.py`
gives. Every claim below is about a card moving, or failing to move, across
particular fortnights either side of the regime boundary, and no captured day
holds one of those disentangled from everything else the deck was doing.
"""

import json
from pathlib import Path

import duckdb
import pytest

from tracker import config, store, timeline, tracking, weekly
from tracker.classify import classify_cache
from tests import synthetic
from tests.synthetic import blink, challenge, entry, league

# Bins are anchored at the regime boundary and run a fortnight each, so these
# are bin -1, bin 0 and bin 1: the fortnight before the boundary, the one that
# opens on it, and the one after.
BEFORE, FIRST, SECOND = "2026-05-06", "2026-05-20", "2026-06-03"


def _built(tmp_path: Path, events: list[dict]) -> Path:
    """A store built from written payloads, as a refresh would leave it."""
    raw = synthetic.write_cache(tmp_path / "raw", events)
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    return db


def _mixed(day: str, registered: list[dict], event_id: str) -> dict:
    """One event whose lists differ, so a card can hold part of a bin rather than all."""
    entries = [
        blink(f"p{day}{i}", placement=i + 1, points=15, cards=cards)
        for i, cards in enumerate(registered)
    ]
    return challenge(day, entries, event_id)


def _lists(day: str, count: int, **kwargs) -> dict:
    entries = [blink(f"pilot{day}{i}", placement=i + 1, points=15, **kwargs) for i in range(count)]
    return challenge(day, entries, event_id=f"{day.replace('-', '')}01")


def test_goryos_is_tested_first(tmp_path):
    """A list answering to both rules takes one name, and it is Goryo's.

    The rules are ordered rather than independent because a list counted in two
    decks is counted twice by anything summing the field, and Goryo's is the one
    whose population must not move.
    """
    both = entry("ambidextrous", cards={card: (2, 0) for card in synthetic.BLINK_SIGNATURE})
    db = _built(tmp_path, [challenge(FIRST, [both | {"placement": 1, "points": 18}], "e1")])
    with duckdb.connect(db, read_only=True) as con:
        assert con.execute("SELECT DISTINCT archetype FROM decklists").fetchall() == [("goryos",)]


def test_an_off_colour_source_is_a_different_deck(tmp_path):
    """Holding every signature card is not enough: the deck is Esper or Orzhov.

    The build that shares the four and splashes red is a real population, not a
    stray list, and reading it as a variant would put its numbers inside the
    deck's own.
    """
    clean = blink("orzhov_pilot", variant="orzhov", placement=1, points=15)
    red = blink("mardu_pilot", variant="orzhov", placement=2, points=15,
                off_colour="Sacred Foundry")
    db = _built(tmp_path, [challenge(FIRST, [clean, red], "e1")])
    rows = tracking.weekly(db, "blink", "orzhov", since=FIRST)
    assert sum(row["chal"] for row in rows) == 1
    assert tracking.excluded(db, "blink", since=FIRST) == 1


@pytest.mark.parametrize("variant,expected", [("esper", 1), ("orzhov", 0)])
def test_the_variant_rule_splits_on_the_one_card(tmp_path, variant, expected):
    """Presence of the blue source is the whole of the split, not a count."""
    db = _built(tmp_path, [_lists(FIRST, 1, variant="esper")])
    assert sum(row["chal"] for row in tracking.weekly(db, "blink", variant, since=FIRST)) == expected


def test_presence_is_a_share_of_what_the_week_published(tmp_path):
    """The denominator is the field, so a busier week does not flatter the deck.

    Two identical weeks for the deck, one of them twice the size for everyone
    else: a count would call them the same week and the share says which is
    which.
    """
    quiet = challenge(FIRST, [blink("a", placement=1, points=15)] +
                      [entry(f"other{i}", placement=i + 2, points=12) for i in range(3)], "e1")
    busy = challenge(SECOND, [blink("b", placement=1, points=15)] +
                     [entry(f"more{i}", placement=i + 2, points=12) for i in range(7)], "e2")
    db = _built(tmp_path, [quiet, busy])
    weeks = {row["week"]: row for row in tracking.weekly(db, "blink", "esper", since=FIRST)}
    assert weeks["2026-05-18"]["chal"] == weeks["2026-06-01"]["chal"] == 1
    assert weeks["2026-05-18"]["chal_share"] == pytest.approx(0.25)
    assert weeks["2026-06-01"]["chal_share"] == pytest.approx(0.125)


def test_league_trophies_are_never_capped_per_pilot(tmp_path):
    """One pilot's repeats are part of how much of the stratum the deck holds.

    The cap belongs to the rate readings. What this panel measures is occupancy,
    and a grinder trophying three times has occupied three of the day's slots.
    """
    dump = league(FIRST, [blink("grinder"), blink("grinder"), blink("grinder")])
    db = _built(tmp_path, [dump])
    assert sum(row["trophies"] for row in tracking.weekly(db, "blink", "esper", since=FIRST)) == 3


def test_a_delta_never_crosses_the_regime_boundary(tmp_path):
    """What the deck played before the ban is not what it put down after it.

    A card every pre-regime list ran and no post-regime list does is the largest
    move the detector could see, and it must not report one: the two fortnights
    are different eras and the glossary forbids a window spanning them.
    """
    db = _built(tmp_path, [
        _lists(BEFORE, 8, cards={"Orcish Bowmasters": (4, 0)}),
        _lists(FIRST, 8),
    ])
    opening = timeline.findings(db, config.REPORTS["blink"])[0]
    assert opening["start"] == "2026-05-18"
    assert not [row for row in opening["found"] if row["card"] == "Orcish Bowmasters"]


def test_a_card_that_only_skipped_a_fortnight_is_not_a_return(tmp_path):
    """A staple missing one thin bin is a dropout, not the field rediscovering it.

    This is the failure the absence window exists for: at a fortnight's lookback
    a card running at a few lists a week clears the bar on chance alone, and the
    timeline fills with staples announcing themselves.
    """
    db = _built(tmp_path, [
        _lists(FIRST, 8, cards={"Ghost Vacuum": (0, 3)}),
        _lists(SECOND, 8),
        _lists("2026-06-17", 8, cards={"Ghost Vacuum": (0, 3)}),
    ])
    third = timeline.findings(db, config.REPORTS["blink"])[2]
    assert not [row for row in third["found"] if row["kind"] == "return"]


def test_a_return_has_to_beat_what_the_card_ever_held(tmp_path):
    """A one-off coming back as a one-off is not news; coming back bigger is.

    Both cards here are gone the same length of time and come back in the same
    bin. Only the one the deck actually turned to is a row.
    """
    vacuum, emrakul = {"Ghost Vacuum": (0, 3)}, {"Emrakul, the Aeons Torn": (0, 3)}
    db = _built(tmp_path, [
        # Before the gap: the vacuum is a two-list one-off, Emrakul is in every list.
        _mixed(BEFORE, [vacuum | emrakul] * 2 + [emrakul] * 6, "e0"),
        _lists(FIRST, 8),
        _lists(SECOND, 8),
        # After it, they swap: the deck turned to one and remembered the other.
        _mixed("2026-06-17", [vacuum] * 8 + [emrakul] * 4, "e3"),
    ])
    returns = {
        row["card"]
        for entry_ in timeline.findings(db, config.REPORTS["blink"])
        for row in entry_["found"]
        if row["kind"] == "return"
    }
    assert "Ghost Vacuum" in returns
    assert "Emrakul, the Aeons Torn" not in returns


def test_a_card_crossing_the_boards_is_a_migration_and_says_so(tmp_path):
    """Moving a card to the mainboard is not the deck discovering it.

    Read one zone at a time the card is new to the mainboard, which is true and
    reads as novelty. The row has to say which it is, or a sideboard staple
    being promoted looks like an innovation every time it happens.
    """
    db = _built(tmp_path, [
        _lists(FIRST, 8, cards={"Wrath of the Skies": (0, 3)}),
        _lists(SECOND, 8, cards={"Wrath of the Skies": (3, 0)}),
    ])
    texts = [row["text"] for row in timeline.findings(db, config.REPORTS["blink"])[1]["found"]]
    assert any("Wrath of the Skies moves to the mainboard" in text for text in texts)


def _report(**changes) -> dict:
    """The tracked deck's report with something changed, to test one mechanism.

    Written against a report rather than against `config.REPORTS` so the tests
    say what the reading does and not what this week's configuration happens to
    watch. Which slots Goryo's watches is the pilot's call and moves; that a
    watched slot is read by copy count does not.
    """
    return config.REPORTS["blink"] | changes


def test_a_pooled_report_counts_every_camp(tmp_path):
    """A report reading the archetype counts all of it, camps included.

    The weekly figures are a share of the field, and a share read on one camp of
    three answers a third of the question. Which is why the population is the
    report's decision and not the membership rule's.
    """
    both = challenge(
        FIRST,
        [
            entry("fallaji_pilot", camp="fallaji", placement=1, points=15),
            entry("plain_pilot", camp="non-fallaji", placement=2, points=15),
        ],
        "e1",
    )
    db = _built(tmp_path, [both])
    pooled = sum(row["chal"] for row in tracking.weekly(db, "goryos", None, since=FIRST))
    one_camp = sum(row["chal"] for row in tracking.weekly(db, "goryos", "fallaji", since=FIRST))
    assert (pooled, one_camp) == (2, 1)


def test_the_camp_moving_its_manabase_earns_a_row(tmp_path):
    """A land count is a configuration of the list, and moving it is a finding.

    The land a camp adds is a different card in every list, so no card's
    adoption moves and no card's copies move either. Read card by card the
    decision is invisible, which is what this reading is for.
    """
    db = _built(
        tmp_path,
        [
            _lists(FIRST, 10),
            _lists(SECOND, 10, cards={"Plains": (3, 0)}),
        ],
    )
    second = timeline.findings(db, _report(manabase=True))[1]
    texts = [row["text"] for row in second["found"] if row["kind"] == "manabase"]
    assert any(text.startswith("13 lands climbed") for text in texts)
    assert not [row for row in timeline.findings(db, _report())[1]["found"]
                if row["kind"] == "manabase"]


def test_a_watched_slot_reports_a_copy_count_the_mean_would_hide(tmp_path):
    """Two copies going to three in part of the camp, which no mean can see.

    Six lists of twenty moving a card from two copies to three shifts the mean
    by three tenths of a copy, under the bar a copies reading answers to and
    rightly so: at that bar every slot in the deck would earn a row. The same
    decision read as a distribution is six lists changing their minds.
    """
    db = _built(
        tmp_path,
        [
            _mixed(FIRST, [{"Spell Snare": (2, 0)}] * 20, "e1"),
            _mixed(SECOND, [{"Spell Snare": (3, 0)}] * 6 + [{"Spell Snare": (2, 0)}] * 14, "e2"),
        ],
    )
    watched = timeline.findings(db, _report(watch=("Spell Snare",)))[1]["found"]
    # Both sides of the move, which is where the copies went and not two findings.
    assert [row["text"] for row in watched if row["card"] == "Spell Snare"] == [
        "Spell Snare at 2 copies fell, 20/20 to 14/20 lists (100% to 70%)",
        "Spell Snare at 3 copies climbed, 0/20 to 6/20 lists (0% to 30%)",
    ]
    averaged = timeline.findings(db, _report())[1]["found"]
    assert not [row for row in averaged if row["card"] == "Spell Snare"]


def test_a_staple_changing_its_count_is_a_row_and_a_fringe_card_is_not(tmp_path):
    """The copies reading finds the deck's staples rather than being told them.

    A card every list holds cannot move a share, so a count change is the whole
    of what the deck decided about it. A card a few lists hold is one the
    adoption reading answers for, and its mean moves when different pilots turn
    up rather than when anybody changes a number. A land is a staple like any
    other: a change in any card of the deck is what the timeline is for.
    """
    db = _built(
        tmp_path,
        [
            _mixed(FIRST, [{"Fatal Push": (4, 0), "Spell Snare": (1, 0), "Polluted Delta": (4, 0)}] * 3
                   + [{"Fatal Push": (4, 0), "Polluted Delta": (4, 0)}] * 7, "e1"),
            _mixed(SECOND, [{"Fatal Push": (3, 0), "Spell Snare": (2, 0), "Polluted Delta": (2, 0)}] * 3
                   + [{"Fatal Push": (3, 0), "Polluted Delta": (2, 0)}] * 7, "e2"),
        ],
    )
    found = timeline.findings(db, _report())[1]["found"]
    assert [row["text"] for row in found if row["kind"] == "copies"] == [
        "Fatal Push down from 4.0 to 3.0 copies on average",
        "Polluted Delta down from 4.0 to 2.0 copies on average",
    ]


def test_the_fortnight_closing_with_the_reported_week_is_frozen(tmp_path, monkeypatch):
    """A fortnight that ended on the reported week's own Sunday has closed.

    Frozen against the week's Sunday and not its Monday key, or the report shows
    the fortnight it is reporting on as still filling and freezes it a week late,
    under a later run's phrasing.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    # Bin 0 runs 18 to 31 May; the week keyed 25 May is the one that closes it.
    db = _built(tmp_path, [_lists("2026-05-27", 3)])
    weekly.freeze(db, "blink", through="2026-05-25")
    rows = weekly._read(weekly.deck_dir("blink") / "timeline.csv")
    assert {row["start"] for row in rows} == {"2026-05-18"}


def test_a_frozen_week_is_never_rewritten(tmp_path, monkeypatch):
    """What was reported stands, even when the store changes under it.

    A league dump gains trophies through its own day, so a past week really can
    move. The report renders the row that was written, because a timeline whose
    history is rebuilt every Monday is a timeline nobody can cite.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    db = _built(tmp_path, [league(FIRST, [blink("a")])])
    weekly.freeze(db, "blink", through="2026-05-18")

    fuller = _built(tmp_path / "again", [league(FIRST, [blink("a"), blink("b"), blink("c")])])
    added = weekly.freeze(fuller, "blink", through="2026-05-18")

    assert added["weeks_added"] == 0
    rows = weekly._read(weekly.deck_dir("blink") / "weekly.csv")
    assert [row["trophies"] for row in rows] == ["1"]


def test_the_reported_week_is_the_last_one_that_closed():
    """Monday's report covers the week behind it, never the one it is in.

    MTGO's density is on the weekend, so a week read before its Sunday is a week
    missing most of its own evidence.
    """
    assert weekly.last_complete_week("2026-09-14") == "2026-09-07"
    assert weekly.last_complete_week("2026-09-11") == "2026-08-31"
    assert weekly.last_complete_week("2026-09-13") == "2026-08-31"


def test_a_week_is_stored_by_its_monday_and_read_by_its_sunday():
    """The label is the day the week closed, not the day it opened.

    Both names are for the same seven days, and the stored one has to stay the
    Monday because every frozen row and summary file is written under it. What
    a reader sees is the Sunday: a chart whose last point says the Monday reads
    as a chart missing the week it is actually showing.
    """
    assert weekly.week_label("2026-08-31") == "2026-09-06"


def test_a_deck_with_no_variant_rule_is_one_population(tmp_path):
    """Simic Neoform forks on nothing, so its members carry no camp and the
    pooled reading is the whole of the deck."""
    rule = config.TRACKED_DECKS["neoform"]
    pilot = {
        "pilot": "simic",
        "points": 15,
        "placement": 1,
        "main": {card: 4 for card in rule["signature"]} | synthetic.FILLER_MAIN | synthetic.FILLER_LANDS,
        "side": dict(synthetic.FILLER_SIDE),
    }
    db = _built(tmp_path, [challenge(FIRST, [pilot], "e1")])
    assert sum(row["chal"] for row in tracking.weekly(db, "neoform", None, since=FIRST)) == 1
    with duckdb.connect(db, read_only=True) as con:
        assert con.execute(
            "SELECT camp FROM decklists WHERE archetype = 'neoform'"
        ).fetchall() == [(None,)]


def test_membership_is_read_off_the_rule_and_not_a_list_of_names(tmp_path):
    """A rule that grows a card takes effect everywhere, including here."""
    raw = synthetic.write_cache(tmp_path / "raw", [_lists(FIRST, 1)])
    assert {deck.archetype for deck in classify_cache(raw)} == {"blink"}


def test_a_list_short_of_one_signature_card_is_not_the_deck(tmp_path):
    """Membership is every signature card, so three of four is another deck."""
    short = blink("nearly", placement=1, points=15, cards={"Flickerwisp": (0, 0)})
    db = _built(tmp_path, [challenge(FIRST, [short], "e1")])
    assert sum(row["chal"] for row in tracking.weekly(db, "blink", "esper", since=FIRST)) == 0


def test_a_grinder_republishing_one_list_is_not_the_field_copying(tmp_path):
    """The goldfishing reading counts a pilot's build, never their publications.

    A league dump publishes every 5-0, so one pilot on one list can appear five
    times in a week. Counted per publication that is five lists the field failed
    to build, and the reading inverts: it reports copying where the evidence is
    one pilot entering a lot of leagues.
    """
    settled = {"Spell Snare": (2, 0)}
    first = league(FIRST, [blink("grinder", cards=settled)])
    # The same pilot's same 60 four times over, beside three other builds.
    repeats = [blink("grinder", cards=settled) for _ in range(4)]
    # Three other pilots on three other 60s, none of them the grinder's two.
    others = [blink(f"other{n}", cards={"Spell Snare": (n, 0)}) for n in (1, 3, 4)]
    db = _built(tmp_path, [first, league(SECOND, repeats + others)])

    week = [row for row in tracking.goldfishing(db, "blink", "esper", since=FIRST)
            if row["week"] == "2026-06-01"][0]
    assert week["lists"] == 7
    assert week["builds"] == 4
    # One pilot kept last week's list, not four of seven.
    assert (week["copied"], week["copied_share"]) == (1, 0.25)


def test_the_goldfishing_reading_is_the_same_on_every_run(tmp_path):
    """Two 75s tied for most-registered resolve the same way every time.

    Left to whichever the max reached first, the winner depends on set ordering,
    which for strings is the hash seed. The same store then published different
    figures on different runs of the same code, and this history has six tied
    weeks.
    """
    tied = [blink("a", cards={"Spell Snare": (1, 0)}), blink("b", cards={"Spell Snare": (1, 0)}),
            blink("c", cards={"Spell Snare": (2, 0)}), blink("d", cards={"Spell Snare": (2, 0)})]
    followers = [blink(f"f{i}", cards={"Spell Snare": (2, 0)}) for i in range(3)]
    db = _built(tmp_path, [league(FIRST, tied), league(SECOND, followers)])

    reading = [row for row in tracking.goldfishing(db, "blink", "esper", since=FIRST)
               if row["week"] == "2026-06-01"][0]
    assert reading["copied"] == tracking.goldfishing(db, "blink", "esper", since=FIRST)[-1]["copied"]
    # Whichever of the two the tie-break picks, it picks it by the mainboard and
    # not by where the iteration happened to start.
    assert tracking._most_registered(["b", "a", "a", "b"]) == "a"
    assert tracking._most_registered(["a", "b", "b", "a"]) == "a"


def test_a_deck_settled_at_a_new_level_is_not_still_spiking(tmp_path, monkeypatch):
    """A spike is a week's departure, and a level held is the level.

    Read against the whole post-regime history the banner never turns off, the
    median staying held down by the weeks before the deck got there. Esper Blink
    ran 27, 33, 36 and 43 against a post-regime median of 10 and flagged on all
    four. The trailing median takes two weeks of the new level to cross, which
    is the step arriving rather than the rule failing to settle: what it may not
    do is still be flagging on the fourth.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    thin = [_lists(day, 2) for day in ("2026-05-20", "2026-05-27", "2026-06-03", "2026-06-10")]
    fat = [_lists(day, 12) for day in ("2026-06-17", "2026-06-24", "2026-07-01", "2026-07-08",
                                       "2026-07-15", "2026-07-22")]
    db = _built(tmp_path, thin + fat)
    weekly.freeze(db, "blink", through="2026-07-20")

    weeks = ("2026-06-15", "2026-06-22", "2026-06-29", "2026-07-06", "2026-07-13", "2026-07-20")
    spiking = [weekly.facts(db, "blink", week)["challenge"]["spiking"] for week in weeks]
    assert spiking == [True, True, False, False, False, False]


def test_a_past_week_keeps_the_baseline_it_was_reported_against(tmp_path, monkeypatch):
    """The median is the deck's history to that week and never past it.

    Taken over the whole file, a week re-rendered months later quotes a baseline
    that did not exist when it was written, and the clause comparing the deck to
    its own history stops being checkable against the report it came from.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    db = _built(tmp_path, [_lists("2026-05-20", 2), _lists("2026-05-27", 2),
                           _lists("2026-06-03", 20), _lists("2026-06-10", 20)])
    weekly.freeze(db, "blink", through="2026-06-08")

    early = weekly.facts(db, "blink", "2026-05-25")["challenge"]["median_lists"]
    late = weekly.facts(db, "blink", "2026-06-08")["challenge"]["median_lists"]
    assert early == 2
    assert late == 11


def test_the_report_renders_the_rows_it_froze(tmp_path, monkeypatch):
    """The figures and the table come from the frozen file, not from the store.

    Otherwise the summary is written from one population and printed above plots
    drawn from another, and a league dump filling in behind a past week moves the
    figures while the prose above them stands.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    db = _built(tmp_path, [league(FIRST, [blink("a")])])
    weekly.freeze(db, "blink", through="2026-05-18")

    fuller = _built(tmp_path / "again", [league(FIRST, [blink("a"), blink("b"), blink("c")])])
    rendered = weekly.weeks_through(fuller, "blink", config.REPORTS["blink"], "2026-05-18")
    assert [row["trophies"] for row in rendered] == [1]


def _paper_event(day: str, entries: list[dict]) -> tuple[dict, dict]:
    """A major event and its payload, the lists shaped as melee publishes them."""
    spot = {"id": 99, "label": "Pro Tour Test", "date": day}
    lists = [
        {
            "decklist_id": f"d{rank}", "rank": rank, "pilot": e["pilot"], "name": "Esper Blink",
            "record": "8-4-0", "wins": 8, "losses": 4, "draws": 0, "points": 24,
            "main": e["main"], "side": e["side"],
        }
        for rank, e in enumerate(entries, start=1)
    ]
    payload = {
        "tournament": {"id": 99, "name": spot["label"], "organiser": "t", "start": day,
                       "round": "Finals", "players": len(lists)},
        "lists": lists,
    }
    return spot, payload


def test_the_fortnight_holding_a_major_event_is_read_against_the_event(tmp_path):
    """A Pro Tour moves what turns up on MTGO, so the chain runs through it.

    The fortnight before, then the event, then the fortnight the event fell in:
    each read against the one before. A card the whole field sideboarded at the
    event and every MTGO list sideboarded after it is the field copying the
    event, which read against the fortnight before would be the deck discovering
    the card a fortnight late. The reverse holds for a card the event dropped.
    """
    from tracker import spotlight

    adopted = {"Clarion Conqueror": (0, 3)}
    db = _built(tmp_path, [_lists(FIRST, 10), _lists(SECOND, 10, cards=adopted)])
    spot, payload = _paper_event("2026-06-06", [blink(f"pt{i}", cards=adopted) for i in range(10)])
    spotlight.cached(spot, tmp_path).write_text(json.dumps(payload), encoding="utf-8")

    plain = timeline.findings(db, config.REPORTS["blink"], spotlights=())[1]
    assert plain["against"] == "the fortnight to 2026-05-31"
    assert [row["card"] for row in plain["found"] if row["kind"] == "return"] == ["Clarion Conqueror"]

    chained = timeline.findings(db, config.REPORTS["blink"], spotlights=(spot,), directory=tmp_path)[1]
    assert chained["against"] == "Pro Tour Test"
    assert chained["cross_population"] is True
    assert not [row for row in chained["found"] if row["card"] == "Clarion Conqueror"]

    # And the event itself is read against the fortnight that closed before it.
    event = spotlight.chain(db, config.REPORTS["blink"], (spot,), tmp_path)[0]
    assert event["against"] == "the fortnight to 2026-05-31"
    assert [row["card"] for row in event["found"] if row["kind"] == "adoption"] == ["Clarion Conqueror"]


def test_a_paper_event_carries_a_land_count_off_the_names_mtgo_has_typed(tmp_path):
    """Melee publishes the cards without their types, and the lands are still lands.

    A camp walking to 13 lands at the Pro Tour is the manabase reading's whole
    question, and the fetch not keeping the type headings is no reason to leave
    it unanswered: MTGO has typed every land the deck plays.
    """
    from tracker import spotlight

    db = _built(tmp_path, [_lists(FIRST, 10), _lists(SECOND, 10)])
    spot, payload = _paper_event(
        "2026-06-06", [blink(f"pt{i}", cards={"Plains": (3, 0)}) for i in range(10)]
    )
    spotlight.cached(spot, tmp_path).write_text(json.dumps(payload), encoding="utf-8")

    event = spotlight.chain(db, _report(manabase=True), (spot,), tmp_path)[0]
    assert any(row["text"].startswith("13 lands climbed") for row in event["found"])
    after = timeline.findings(db, _report(manabase=True), spotlights=(spot,), directory=tmp_path)[1]
    assert any(row["text"].startswith("13 lands fell") for row in after["found"])


def test_a_card_the_fortnight_dropped_entirely_is_a_row(tmp_path):
    """Putting a card down is as much a decision as taking one up.

    Read only over the cards the bin registers, a card at every list one
    fortnight and no list the next has nowhere to be seen from, and the largest
    move a deck can make goes unreported.
    """
    db = _built(tmp_path, [
        _lists(FIRST, 10, cards={"Orcish Bowmasters": (4, 0)}),
        _lists(SECOND, 10),
    ])
    second = timeline.findings(db, config.REPORTS["blink"], spotlights=())[1]
    texts = [row["text"] for row in second["found"] if row["card"] == "Orcish Bowmasters"]
    assert texts == ["Orcish Bowmasters fell in the mainboard, 10/10 to 0/10 lists (100% to 0%)"]
