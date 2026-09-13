"""The pipeline's single test seam: real cached payloads in, verdicts out.

Fixtures are the immutable raw cache of every Modern event published on
2026-08-05, captured from the live site. Nothing here asserts on parser
internals, schema shape, or intermediate tables.

One reading is driven on written payloads instead, for the reason
`tests/synthetic.py` gives: the captured days hold no camp split finely enough
to tell it apart from the reading it would be confused with.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import duckdb
import pytest

from tracker import index, mtgo, store
from tracker.classify import classify_cache
from tracker.refresh import refresh
from tests import synthetic

FIXTURE_RAW = Path(__file__).parent / "fixtures" / "raw"
# One captured Last Chance: a Swiss-only event of a kind the day's cache lacks.
FIXTURE_KINDS = Path(__file__).parent / "fixtures" / "kinds"
# The 2026-07-08 challenge as the site served it: under its own slug, and again
# under a second slug dated 2026-07-24 that the site later withdrew.
FIXTURE_DUPLICATE = Path(__file__).parent / "fixtures" / "duplicate"
# Two captured challenges holding a list of every camp shape, plus a near-miss.
FIXTURE_CAMPS = Path(__file__).parent / "fixtures" / "camps"
# The 2026-08-02 Challenge 64, whose 32 lists hold four builds on the trio: three
# Esper, and Arcbound_Papi's Grixis reanimator deck, which is a different deck.
FIXTURE_GRIXIS = Path(__file__).parent / "fixtures" / "grixis"

# The day's Goryo's lists, read off the published decklists by hand.
GORYOS_PILOTS_2026_08_05 = {
    "frekinsmart",
    "pepeteam",
    "_must_be_nice",
    "AldenCates",
    "Kollslaw",
    "Acecalna",
}

# AldenCates' 15-card sideboard from Modern Challenge 32 12849509, read off the
# published decklist by hand.
ALDENCATES_SIDEBOARD = {
    "Celestial Purge": 1,
    "Consign to Memory": 3,
    "March of Otherworldly Light": 2,
    "Mystical Dispute": 3,
    "Nihil Spellbomb": 2,
    "Teferi, Time Raveler": 1,
    "Wrath of the Skies": 3,
}


def test_trio_rule_selects_exactly_the_days_goryos_lists():
    lists = classify_cache(FIXTURE_RAW)

    members = {d.pilot for d in lists if d.archetype == "goryos"}
    assert members == GORYOS_PILOTS_2026_08_05


def test_a_list_carries_its_published_sideboard_alongside_its_mainboard():
    """A list is a 75, and the 15 are where sideboard plans live.

    Their absence would read a main-to-side migration as a straight cut, so the
    sideboard is loaded as published, next to the mainboard it was registered
    with.
    """
    lists = classify_cache(FIXTURE_RAW)

    alden = next(d for d in lists if d.pilot == "AldenCates")
    assert alden.sideboard == ALDENCATES_SIDEBOARD
    assert sum(alden.sideboard.values()) == 15
    assert sum(alden.mainboard.values()) == 60


def test_placement_is_the_published_finish_not_the_swiss_standing():
    lists = classify_cache(FIXTURE_RAW)

    # BowBloBiw took the second challenge of the day; JustAnotherGuy83 led the
    # Swiss and lost in the playoff.
    won = [d.pilot for d in lists if d.event_id.endswith("12850696") and d.placement == 1]
    assert won == ["BowBloBiw"]


def test_query_returns_the_days_goryos_lists_with_their_provenance(tmp_path):
    db = tmp_path / "engine.duckdb"
    store.build(FIXTURE_RAW, db)

    rows = {row["pilot"]: row for row in store.goryos_lists(db, "2026-08-05")}
    assert set(rows) == GORYOS_PILOTS_2026_08_05

    # A league trophy: published as a 5-0, with no placement to speak of.
    trophy = rows["frekinsmart"]
    assert (trophy["event"], trophy["event_class"], trophy["date"]) == (
        "Modern League",
        "league",
        "2026-08-05",
    )
    assert (trophy["record"], trophy["placement"]) == ("5-0", None)

    # A challenge finish: published with a rank within the top 32.
    finish = rows["AldenCates"]
    assert (finish["event"], finish["event_class"], finish["date"]) == (
        "Modern Challenge 32",
        "challenge-32",
        "2026-08-05",
    )
    assert (finish["record"], finish["placement"]) == ("4-3", 23)

    # Two Modern Challenge 32 events ran that day; a shared name is not identity.
    assert rows["Kollslaw"]["event_id"] == finish["event_id"]
    assert rows["Acecalna"]["event_id"] != finish["event_id"]


def test_challenge_rows_carry_swiss_points_and_leagues_carry_none(tmp_path):
    db = tmp_path / "engine.duckdb"
    store.build(FIXTURE_RAW, db)

    rows = {row["pilot"]: row for row in store.goryos_lists(db, "2026-08-05")}

    # Read off the published standings: AldenCates finished 23rd on 12 points.
    assert (rows["AldenCates"]["placement"], rows["AldenCates"]["swiss_points"]) == (23, 12)
    # A league publishes 5-0s only: no standings, so no placement and no points.
    assert (rows["frekinsmart"]["placement"], rows["frekinsmart"]["swiss_points"]) == (None, None)


def test_points_are_swiss_only_so_the_winner_can_trail_a_lower_finisher():
    """The published `score` is the Swiss total, untouched by the playoff.

    Challenge 12850696 on 2026-08-05 proves it: BowBloBiw won the event on 15
    Swiss points while JustAnotherGuy83, who led the Swiss and lost the final,
    holds 18. A points-weighted metric therefore measures Swiss performance, not
    the bracket.
    """
    lists = classify_cache(FIXTURE_RAW)

    finishes = {
        d.pilot: (d.placement, d.swiss_points)
        for d in lists
        if d.event_id.endswith("12850696")
    }
    assert finishes["BowBloBiw"] == (1, 15)
    assert finishes["JustAnotherGuy83"] == (2, 18)


def test_every_published_event_kind_lands_under_its_own_class():
    """The class is the kind the site publishes, whatever that kind is.

    So a `last-chance` is not filed as a `last`, an `rc-super-qualifier` is not
    filed as an `rc`, and a `challenge-32` is not blended with a `challenge-64`.
    """
    day = classify_cache(FIXTURE_RAW)
    other_kinds = classify_cache(FIXTURE_KINDS)

    assert {d.event_class for d in day} == {"league", "challenge-32"}
    assert {d.event_class for d in other_kinds} == {"last-chance"}


def test_a_no_playoff_event_finishes_on_the_swiss_order():
    """A Last Chance runs Swiss only, so the standings are the finish."""
    lists = classify_cache(FIXTURE_KINDS)

    finishes = {d.pilot: (d.placement, d.swiss_points) for d in lists}
    assert finishes["ShowTime_"] == (1, 15)
    assert finishes["Lollopollo2001"] == (2, 15)


def test_an_event_listed_under_two_slugs_is_one_event():
    """The site occasionally lists an event a second time under a wrong date.

    Both slugs serve the same 32 lists, and the payload names the event it
    really is, so counting the cache by slug would inflate every metric.
    """
    lists = classify_cache(FIXTURE_DUPLICATE)

    assert len(lists) == 32
    assert len({d.pilot for d in lists}) == 32
    assert {d.date for d in lists} == {"2026-07-08"}


def test_camps_split_the_archetype_by_the_divergence_card():
    """Fallaji Archaeologist is the fork in the archetype's construction.

    Read off the two captured challenges: Rvng on three copies and BERNASTORRES
    on four are the Fallaji camp, Walker735 and Darkchrome6538 on none are the
    non-Fallaji camp, and Gerardo94 on two has committed to neither.
    """
    lists = classify_cache(FIXTURE_CAMPS)

    camps = {d.pilot: d.camp for d in lists if d.archetype == "goryos"}
    assert camps == {
        "Rvng": "fallaji",
        "BERNASTORRES": "fallaji",
        "Gerardo94": "hybrid",
        "Walker735": "non-fallaji",
        "Darkchrome6538": "non-fallaji",
    }


def test_a_camps_consensus_population_is_its_own_lists_and_never_the_hybrids(tmp_path):
    """Consensus is computed per camp, so a camp's population is only its own.

    Gerardo94's two copies are an experiment in neither direction: counting that
    list into either camp would move that camp's consensus towards a build no
    pilot in it registered. It stays in the archetype, and out of both.
    """
    db = tmp_path / "engine.duckdb"
    store.build(FIXTURE_CAMPS, db)

    fallaji = {row["pilot"] for row in store.goryos_lists(db, camp="fallaji")}
    non_fallaji = {row["pilot"] for row in store.goryos_lists(db, camp="non-fallaji")}

    assert fallaji == {"Rvng", "BERNASTORRES"}
    assert non_fallaji == {"Walker735", "Darkchrome6538"}
    assert "Gerardo94" in {row["pilot"] for row in store.goryos_lists(db)}


class CapturedSite:
    """The live site as it was, serving every captured payload it published.

    The network layer itself is out of the test seam; this stands in for it so
    the cache's refetch-free promise can be observed.
    """

    EVENTS = {
        path.stem: path for path in [*FIXTURE_RAW.glob("*.json"), *FIXTURE_KINDS.glob("*.json")]
    }

    def __init__(self):
        self.fetches: list[str] = []

    def event_slugs(self, since, fmt, until, today):
        """Everything it published, July and August alike. Which days the index
        lists is the site's business, and is verified against the live site."""
        return sorted(self.EVENTS)

    def fetch_payload(self, slug):
        self.fetches.append(slug)
        return json.loads(self.EVENTS[slug].read_text(encoding="utf-8"))


def test_refresh_backfills_a_range_of_months_then_fetches_nothing(tmp_path):
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    backfilled = store.goryos_lists(db)
    assert len(site.fetches) == 4, "every event published in the range"
    assert {row["date"] for row in backfilled} == {"2026-07-19", "2026-08-05"}
    assert {row["pilot"] for row in backfilled} >= GORYOS_PILOTS_2026_08_05

    refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    assert len(site.fetches) == 4, "settled events must never be refetched"
    assert store.goryos_lists(db) == backfilled


def test_refresh_refetches_only_the_days_that_can_still_grow(tmp_path):
    """A league dump gains 5-0s through its own day, so a day captured while it
    is still running is a partial capture the immutable cache would keep forever.

    The recent tail of the range is therefore refetched on every run; everything
    behind it has settled and is never fetched twice.
    """
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")
    assert len(site.fetches) == 4

    site.fetches.clear()
    refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")

    # 2026-08-05 is inside the unsettled tail of a run made on 2026-08-06.
    assert {mtgo.slug_day(slug) for slug in site.fetches} == {"2026-08-05"}
    assert len(site.fetches) == 3


def test_a_day_captured_before_it_finished_publishing_is_refetched(tmp_path):
    """The calendar settling and the capture settling are two different facts.

    A run made on the day itself catches a league dump part filled, and the day
    then ages out of the unsettled window carrying whatever was caught: in the
    live cache 2026-08-23 froze at 7 lists and 2026-08-28 at 25, against a
    median league day of 60. Read off the calendar alone those two files are
    settled forever. What settles a capture is the lag between the day it covers
    and the moment it was taken.
    """
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"
    refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")
    assert len(site.fetches) == 4

    # Every capture restamped as taken on the day it covers, which is what a run
    # made on the day leaves behind.
    for path in raw_dir.glob("*.json"):
        stamp = datetime.fromisoformat(f"{mtgo.slug_day(path.stem)}T12:00:00").timestamp()
        os.utime(path, (stamp, stamp))

    site.fetches.clear()
    refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    assert len(site.fetches) == 4, "a same-day capture is refetched however old the day is"


class GrowingSite(CapturedSite):
    """The site mid-dump: a league day serving only the trophies it has so far.

    `published` is how many of the day's 5-0s exist when it is asked, so a run
    can be made against a day still filling and then again once it has filled.
    """

    def __init__(self, published: int):
        super().__init__()
        self.published = published

    def fetch_payload(self, slug):
        payload = super().fetch_payload(slug)
        if "league" in slug:
            payload["decklists"] = payload["decklists"][: self.published]
        return payload


def test_a_run_says_what_a_day_it_already_held_gained(tmp_path):
    """The reading the ingest could not make before the index was kept.

    A league dump gains 5-0s through its own day, so the unsettled window
    refetches days the cache already holds and overwrites them in place. A record
    kept at the event reports such a day as unchanged, and the cache it would
    have to be checked against is not committed; only a record kept at the list
    can say that pilots turned up inside a capture that was already there.

    The archetype's arrival is named because that is the answer a session
    actually wants, and it is read out of the store against the ingest's own
    keys rather than out of the index, which does not know the rule.
    """
    site = GrowingSite(published=23)
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    first = refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")
    assert "_must_be_nice" not in {row["pilot"] for row in store.goryos_lists(db)}

    site.published = 41
    grown = refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")

    assert {row.event_id for row in grown.added} == {"modern-league-2026-08-0510847"}
    assert len(grown.added) == 18, "the day's trophies published after the first run"
    assert not grown.withdrawn, "a day that grew has taken nothing back"
    assert [row["pilot"] for row in store.arrivals(grown.added, db)] == ["_must_be_nice"]
    # The first run reported the whole cache, an empty index being a first run
    # and not a claim that the history is new.
    assert len(first.added) > len(grown.added) and not first.withdrawn


def test_a_rebuild_that_changed_nothing_reports_nothing(tmp_path):
    """The index has to be the same bytes for the same cache, or every run would
    report the whole history as new and the one that mattered would be lost in
    it."""
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    again = refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")

    assert not again.added and not again.withdrawn


def test_the_index_holds_every_published_list_and_not_only_the_archetype(tmp_path):
    """It is the record of what the site published, so the membership rule is
    not in it: a file carrying the rule restates itself the day the rule moves,
    and an ingest diff has to be the field's news rather than this engine's."""
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    change = refresh("2026-07-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")

    with duckdb.connect(db, read_only=True) as con:
        published = con.execute("SELECT count(*) FROM decklists").fetchone()[0]
    # A first run's arrivals are the whole file, in the file's own order, which
    # is what makes the diff of a later one an insertion rather than a shuffle.
    assert len(change.added) == published > len(store.goryos_lists(db))
    assert index.read(db) == change.added


def test_a_withdrawn_event_leaves_the_history_out_loud(tmp_path):
    """The site republishes an event under a wrongly dated slug and later takes
    one down. Lists leaving the history quietly is the same failure as lists
    arriving quietly, so the run says so."""
    site = GrowingSite(published=41)
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")
    site.published = 23
    shrunk = refresh("2026-07-01", "2026-08-06", raw_dir, db, source=site, today="2026-08-06")

    assert len(shrunk.withdrawn) == 18 and not shrunk.added


def test_a_range_running_past_today_still_refetches_the_days_that_can_grow(tmp_path):
    """The unsettled tail is the last few days of real time, not of the range.

    Asking for everything by naming an `until` beyond today is the natural way
    to say it, and it must not quietly settle a day the site is still filling.
    """
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-07-01", "2026-12-31", raw_dir, db, source=site, today="2026-08-06")
    assert len(site.fetches) == 4

    site.fetches.clear()
    refresh("2026-07-01", "2026-12-31", raw_dir, db, source=site, today="2026-08-06")
    assert {mtgo.slug_day(slug) for slug in site.fetches} == {"2026-08-05"}


def test_a_first_run_that_caches_nothing_still_says_what_it_could_not_reach(tmp_path):
    """The gap report is the whole value of a run that captured nothing.

    A first run against a site serving none of what it published leaves an empty
    cache, and the rebuild of an empty cache must not fail on its own account:
    that would bury the one thing the run has to say under a database error.
    """

    class WithholdingSite(CapturedSite):
        def fetch_payload(self, slug):
            raise mtgo.Unavailable(slug)

    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    with pytest.raises(mtgo.Unavailable, match="published event"):
        refresh("2026-08-01", "2026-08-31", raw_dir, db, source=WithholdingSite(), today="2026-08-31")

    assert store.goryos_lists(db) == []


def test_refresh_caches_the_rest_when_the_site_withholds_an_event(tmp_path):
    """The site intermittently serves a page with the listing missing.

    A backfill of hundreds of events must not lose the run to one of them, nor
    quietly pretend the gap isn't there: it caches everything else, then says
    what it could not reach.
    """

    class FlakySite(CapturedSite):
        WITHHELD = "modern-challenge-32-2026-08-0512850696"

        def fetch_payload(self, slug):
            if slug == self.WITHHELD:
                raise mtgo.Unavailable(slug)
            return super().fetch_payload(slug)

    site = FlakySite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    with pytest.raises(mtgo.Unavailable, match=FlakySite.WITHHELD):
        refresh("2026-08-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")

    cached = store.goryos_lists(db, "2026-08-05")
    assert {row["pilot"] for row in cached} == GORYOS_PILOTS_2026_08_05 - {"Acecalna"}

    # The site recovers; the re-run fetches only what the gap left behind.
    site.fetches.clear()
    refresh("2026-08-01", "2026-08-31", raw_dir, db, source=CapturedSite(), today="2026-08-31")
    assert {row["pilot"] for row in store.goryos_lists(db, "2026-08-05")} == GORYOS_PILOTS_2026_08_05


def test_a_withheld_refetch_leaves_the_capture_already_cached_standing(tmp_path):
    """An unsettled day is refetched for what it may have gained since, not
    because what is cached is wrong.

    So the site withholding one is nothing like it withholding an event never
    captured: the run keeps the capture it has and succeeds. Only an event with
    nothing on disk is a gap, since only that one costs lists.
    """
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"

    refresh("2026-08-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    captured = store.goryos_lists(db, "2026-08-05")

    class WithholdingSite(CapturedSite):
        def fetch_payload(self, slug):
            raise mtgo.Unavailable(slug)

    # 2026-08-05 is unsettled on 2026-08-06, so every event on it is refetched.
    refresh("2026-08-01", "2026-08-31", raw_dir, db, source=WithholdingSite(), today="2026-08-06")
    assert store.goryos_lists(db, "2026-08-05") == captured


def test_a_capture_interrupted_mid_write_is_not_left_in_the_cache(tmp_path, monkeypatch):
    """A settled event on disk is never refetched, so a payload left half
    written by a run that died would be kept forever, and every later rebuild
    would fail to parse it.

    A capture therefore lands whole or not at all. Killing the process is stood
    in for by truncating the write itself, since the cost is the same either way.
    """
    site = CapturedSite()
    raw_dir, db = tmp_path / "raw", tmp_path / "engine.duckdb"
    killed = "modern-challenge-32-2026-08-0512850696"
    whole_write = Path.write_text

    def die_partway(self, data, *args, **kwargs):
        if killed not in self.name:
            return whole_write(self, data, *args, **kwargs)
        whole_write(self, data[: len(data) // 2], *args, **kwargs)
        raise KeyboardInterrupt(self.name)

    monkeypatch.setattr(Path, "write_text", die_partway)
    with pytest.raises(KeyboardInterrupt):
        refresh("2026-08-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    monkeypatch.undo()

    assert not (raw_dir / f"{killed}.json").exists()

    # Nothing on disk is a gap, so the re-run captures it and the day is whole.
    site.fetches.clear()
    refresh("2026-08-01", "2026-08-31", raw_dir, db, source=site, today="2026-08-31")
    assert killed in site.fetches
    assert {row["pilot"] for row in store.goryos_lists(db, "2026-08-05")} == GORYOS_PILOTS_2026_08_05


def _ids(db) -> dict[str, str]:
    """Each pilot's list id, the store's lists being one per pilot here."""
    with duckdb.connect(db, read_only=True) as con:
        return dict(con.execute("SELECT pilot, list_id FROM decklists").fetchall())


def test_a_list_keeps_its_id_when_an_event_slugged_earlier_is_cached(tmp_path):
    """An id names the list, not its place in the cache.

    The cache is read in filename order, so an event fetched later under an
    earlier slug shifted the id of every list behind it. That happened on
    2026-09-13: 64 lists cached whose slugs sort early moved every id from June
    on, and the ids quoted across the archived reviews and in `HEURISTICS.md`
    came to name other lists with nothing saying so.
    """
    raw = tmp_path / "raw"
    synthetic.write_cache(
        raw,
        [synthetic.league("2026-07-14", [synthetic.entry("ador"), synthetic.entry("Outsid3r")])],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    before = _ids(db)

    synthetic.write_cache(
        raw,
        [
            synthetic.challenge(
                "2026-07-10", [synthetic.entry("inf1nitus", points=21, placement=1)], "12712"
            )
        ],
    )
    store.build(raw, db)

    after = _ids(db)
    assert {pilot: after[pilot] for pilot in before} == before
    assert after.keys() == {"ador", "Outsid3r", "inf1nitus"}


def test_a_pilots_second_trophy_in_a_dump_leaves_his_first_lists_id_alone(tmp_path):
    """A league dump gains 5-0s through its own day, and one pilot can take two.

    The two are two lists and answer to two ids, which is why an id is not the
    event and the pilot alone. The second carries the ordinal so that the first,
    which a document may already quote, is the same id the day the second lands.
    """
    raw = tmp_path / "raw"
    db = tmp_path / "engine.duckdb"
    synthetic.write_cache(raw, [synthetic.league("2026-07-14", [synthetic.entry("ador")])])
    store.build(raw, db)
    first = _ids(db)["ador"]

    synthetic.write_cache(
        raw,
        [
            synthetic.league(
                "2026-07-14",
                [synthetic.entry("ador"), synthetic.entry("ador", cards={"Persist": (3, 0)})],
            )
        ],
    )
    store.build(raw, db)

    with duckdb.connect(db, read_only=True) as con:
        ids = [row[0] for row in con.execute("SELECT list_id FROM decklists").fetchall()]
    assert first in ids and len(set(ids)) == 2


def test_the_same_card_under_two_printings_is_one_card_with_its_copies_summed(tmp_path):
    """Superior Spider-Man is Kavaero, Mind-Bitten with the Marvel IP on it.

    MTGO publishes a list under whichever printing its pilot registered, and a
    pilot may register both: Rvng ran one of each in the 2026-07-29 challenge,
    which is a two-of. Read as published, one card's adoption history splits
    down the middle and that list reads as two separate one-ofs, which is not a
    configuration anybody registered.
    """
    db = tmp_path / "engine.duckdb"
    store.build(FIXTURE_CAMPS, db)

    with duckdb.connect(db, read_only=True) as con:
        registered = con.execute(
            "SELECT card, main, side FROM configurations JOIN decklists USING (list_id)"
            " WHERE pilot = 'Rvng' AND card IN ('Kavaero, Mind-Bitten', 'Superior Spider-Man')"
        ).fetchall()
    assert registered == [("Kavaero, Mind-Bitten", 2, 0)]


def test_a_grixis_build_on_the_trio_is_a_near_miss_and_not_the_archetype(tmp_path):
    """The membership rule has to name the shell, not just the payoff.

    Goryo's Vengeance, Atraxa and Psychic Frog are as at home in a Grixis
    reanimator deck as in this one, so the trio alone lets a deck with another
    manabase and another gameplan into the population every camp figure is read
    over. Ephemerate is the blink half of the Esper shell and the line the two
    versions fall either side of.

    Arcbound_Papi finished 24th at the 2026-08-02 challenge on the trio with no
    Ephemerate, on Faithless Looting and Blood Crypt. It leaves the archetype.
    """
    db = tmp_path / "engine.duckdb"
    store.build(FIXTURE_GRIXIS, db)

    members = {row["pilot"] for row in store.goryos_lists(db)}
    assert members == {"billskillz", "jussupinator", "DskBayWolf"}


def test_a_persist_deck_on_the_four_is_its_own_deck_and_not_the_archetype(tmp_path):
    """A card that names another deck puts a list outside, whatever else it holds.

    GabbaAndrewTeam and chapaking8 went 5-0 in the July leagues on all four
    signature cards under a Persist reanimator package, and Malikrobinson93
    registered a Shifting Woodland Omniscience combo on the Goryo's core at
    Spotlight Dallas. Both are their own deck with Goryo's as a second angle.
    ador's list with Blink's creatures beside the whole Goryo's engine is not:
    it stays.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw",
        [
            synthetic.league(
                "2026-07-14",
                [
                    synthetic.entry("GabbaAndrewTeam", cards={"Persist": (3, 0)}),
                    synthetic.entry(
                        "Malikrobinson93", cards={"Omniscience": (3, 0), "Shifting Woodland": (4, 0)}
                    ),
                    synthetic.entry("ador", cards={"Phelia, Exuberant Shepherd": (3, 0)}),
                ],
            )
        ],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)

    assert {row["pilot"] for row in store.goryos_lists(db)} == {"ador"}


def test_a_list_turned_away_by_another_decks_engine_is_named_in_the_fall_out(tmp_path):
    """Every exclusion is visible, grouped by the deck whose core the list holds
    and by the engine that turned it away.

    A deck that starts adopting another deck's engine card would otherwise read
    as a silent decline in its storyline. GabbaAndrewTeam's Persist package on
    the Goryo's four is the case: out of Goryo's, and said so under Persist.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw",
        [
            synthetic.league(
                "2026-07-14",
                [
                    synthetic.entry("GabbaAndrewTeam", cards={"Persist": (3, 0)}),
                    synthetic.entry("ador", cards={"Phelia, Exuberant Shepherd": (3, 0)}),
                ],
            )
        ],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)

    assert [(row["archetype"], row["reason"], row["pilot"]) for row in store.fallout(db)] == [
        ("goryos", "persist", "GabbaAndrewTeam")
    ]
