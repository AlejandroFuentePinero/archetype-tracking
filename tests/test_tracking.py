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


def test_a_light_splash_stays_and_five_off_colour_spells_or_a_playset_leave(tmp_path):
    """Holding every signature card is not enough: the deck is Esper or Orzhov.

    The line is the off-colour spells the mainboard casts, never its sources
    (Alejandro, 2026-09-13): a Sacred Foundry held for a sideboard card says
    nothing, two Bolts off it are a splash, five red cards are the Mardu deck
    and a playset of one red card is the Mardu deck whatever the total.
    """
    foundry = blink("foundry_pilot", variant="orzhov", placement=1, points=15,
                    off_colour="Sacred Foundry")
    splash = blink("splash_pilot", variant="orzhov", placement=2, points=15,
                   cards={"Lightning Bolt": (2, 0), "Sacred Foundry": (2, 0)})
    deep = blink("mardu_pilot", variant="orzhov", placement=3, points=15,
                 cards={"Lightning Bolt": (3, 0), "Galvanic Discharge": (2, 0), "Sacred Foundry": (2, 0)})
    playset = blink("playset_pilot", variant="orzhov", placement=4, points=15,
                    cards={"Galvanic Discharge": (4, 0), "Sacred Foundry": (2, 0)})
    db = _built(tmp_path, [challenge(FIRST, [foundry, splash, deep, playset], "e1")])
    rows = tracking.weekly(db, "blink", "orzhov", since=FIRST)
    assert sum(row["chal"] for row in rows) == 2
    assert tracking.excluded(db, "blink", since=FIRST) == 2


def test_a_card_that_names_another_deck_puts_a_list_outside(tmp_path):
    """The four creatures also sit inside decks a blink pilot would name as others.

    The energy engine (dabigatran, Jeppebc and TOP_AI in March to May), the
    Estrid's Invocation Overlords deck (taku123, July), Stoneblade (JJ, March)
    and the Tidehollow Sculler taxes deck (UomoComune26490, September) each held
    every signature card on the deck's own colours. Aether Vial is not such a
    card: JJ's Orzhov Vial lists are a version of this deck and stay.
    """
    clean = blink("vial_pilot", variant="orzhov", placement=1, points=15,
                  cards={"Aether Vial": (4, 0)})
    energy = blink("energy_pilot", variant="orzhov", placement=2, points=15,
                   cards={"Guide of Souls": (4, 0), "Ocelot Pride": (4, 0)})
    taxes = blink("taxes_pilot", variant="esper", placement=3, points=15,
                  cards={"Aether Vial": (4, 0), "Tidehollow Sculler": (4, 0)})
    db = _built(tmp_path, [challenge(FIRST, [clean, energy, taxes], "e1")])
    with duckdb.connect(db, read_only=True) as con:
        members = con.execute("SELECT pilot FROM decklists WHERE archetype = 'blink'").fetchall()
    assert members == [("vial_pilot",)]


def test_a_list_published_with_its_sideboard_in_the_main_is_no_member(tmp_path):
    """EvoPride's 2026-06-20 challenge list arrived as 75 mainboard cards and none
    in the side: an ordinary deck, but its boards cannot be read, so it joins no
    population rather than putting fifteen sideboard cards into a build reading."""
    clean = entry("clean_pilot", placement=1, points=15)
    merged = entry("merged_pilot", placement=2, points=15, cards={"Consign to Memory": (15, 0)})
    db = _built(tmp_path, [challenge(FIRST, [clean, merged], "e1")])
    with duckdb.connect(db, read_only=True) as con:
        members = con.execute("SELECT pilot FROM decklists WHERE archetype = 'goryos'").fetchall()
    assert members == [("clean_pilot",)]


def _list_of(mainboard: dict[str, int]):
    """A list as the classifier reads one, colourless and typed by the filler lands."""
    from types import SimpleNamespace
    return SimpleNamespace(mainboard=mainboard, colours={}, land_names=frozenset(synthetic.FILLER_LANDS))


def test_a_supporting_tier_is_read_as_a_count_and_a_floor_reads_copies():
    """Izzet Prowess is Steam Vents and Lava Dart with four of six staples
    (Alejandro, 2026-09-13): a list that cuts Channeler is the same deck in a
    different build, and Bosseidon's Talent decks on three staples are not.
    Duduk123's Gruul list of 2026-06-15 held one Steam Vents for its sideboard
    Consign to Memory; every Izzet list runs two.
    """
    from tracker import classify

    staples = ("Cori-Steel Cutter", "Monastery Swiftspear", "Dragon's Rage Channeler",
               "Slickshot Show-Off", "Mutagenic Growth", "Stormchaser's Talent")
    shell = {"Steam Vents": 4, "Lava Dart": 4} | {card: 4 for card in staples[:4]}
    assert classify.archetype(_list_of(shell)) == "prowess"
    assert classify.archetype(_list_of(shell | {"Steam Vents": 1})) is None
    three = {card: 4 for card in staples[:3]}
    assert classify.archetype(_list_of({"Steam Vents": 4, "Lava Dart": 4} | three)) is None


def test_a_deck_can_have_a_second_entry_path():
    """A Kavu-less list on Scion, Leyline of the Guildpact and Psychic Frog is
    Domain Zoo's Frog version (Alejandro, 2026-09-13); the Shardless Agent
    cascade decks on the same two leylines are not.
    """
    from tracker import classify

    frog = {"Scion of Draco": 4, "Leyline of the Guildpact": 4, "Psychic Frog": 4, "Ragavan, Nimble Pilferer": 4}
    assert classify.archetype(_list_of(frog)) == "zoo"
    assert classify.variant("zoo", _list_of(frog)) == "frog"
    assert classify.archetype(_list_of(frog | {"Shardless Agent": 4})) is None
    assert classify.archetype(_list_of({"Scion of Draco": 4, "Leyline of the Guildpact": 4})) is None


def test_trudge_reads_the_eldrazi_shell_and_not_one_of_its_lands():
    """The shell rather than Ugin's Labyrinth alone (Alejandro, 2026-09-14).

    The Labyrinth stood in for the shell while every list in the history held
    it. TheJV's RC Baltimore list is the shell whole on a manabase without the
    land, and the mono-green Springheart Nantuko decks run the two creatures as
    mana dorks and none of the shell, so the land cannot tell the two apart.
    """
    from tracker import classify

    dorks = {"Slumbering Trudge": 4, "Fanatic of Rhonas": 4}
    for card in ("Ugin's Labyrinth", "Eldrazi Temple", "Kozilek's Command", "Fight Rigging"):
        assert classify.archetype(_list_of(dorks | {card: 4})) == "trudge", card
    nantuko = {"Quirion Ranger": 4, "Summoner's Pact": 4, "Springheart Nantuko": 4}
    assert classify.archetype(_list_of(dorks | nantuko)) is None
    assert classify.archetype(_list_of(dorks)) is None


def test_a_pair_that_names_another_deck_is_outweighed_by_the_shell_s_own_card():
    """Tamiyo beside Mox Amber is the Tamiyo artifact deck, unless Weapons
    Manufacturing sits beside them, when Manufacturing outweighs it and the list
    is Affinity (Alejandro, 2026-09-13).
    """
    from tracker import classify

    shell = {"Kappa Cannoneer": 4, "Pinnacle Emissary": 4, "Engineered Explosives": 4}
    tamiyo = shell | {"Tamiyo, Inquisitive Student": 4, "Mox Amber": 4}
    assert classify.archetype(_list_of(shell)) == "affinity"
    assert classify.archetype(_list_of(tamiyo)) is None
    assert classify.archetype(_list_of(tamiyo | {"Weapons Manufacturing": 2})) == "affinity"


def _control(spells: dict[str, int]):
    """A control list as the classifier reads one: the shell's spells on its own lands."""
    from types import SimpleNamespace

    lands = {"Hallowed Fountain": 4, "Steam Vents": 2, "Island": 3, "Plains": 3, "Marsh Flats": 4}
    colours = {
        "Teferi, Time Raveler": frozenset("WU"), "Wrath of the Skies": frozenset("W"),
        "Supreme Verdict": frozenset("WU"), "Terminus": frozenset("W"),
        "Temporary Lockdown": frozenset("W"), "Narset, Parter of Veils": frozenset("U"),
        "Wan Shi Tong, Librarian": frozenset("U"), "Solitude": frozenset("W"),
        "Fatal Push": frozenset("B"), "Questing Druid": frozenset("G"),
        "Ephemerate": frozenset("W"),
    }
    return SimpleNamespace(
        mainboard=lands | spells, colours=colours, land_names=frozenset(lands), archetype=None
    )


def test_control_s_sweeper_is_a_slot_and_not_one_card():
    """Control fills its sweeper slot to the meta (Alejandro, 2026-09-13), so
    Teferi with any one of Wrath of the Skies, Supreme Verdict, Terminus or
    Temporary Lockdown is the deck.

    bobthedog's 13th on Terminus and Brainsurge and Ivc's build on Temporary
    Lockdown are the shape: Wrath in the signature kept 23 such lists out of
    every report, and out of the fall-out table too, the core being what the
    fall-out is read over. A list on no sweeper at all is not the deck.
    """
    from tracker import classify

    engine = {"Narset, Parter of Veils": 4, "Solitude": 4}
    for sweeper in ("Wrath of the Skies", "Supreme Verdict", "Terminus", "Temporary Lockdown"):
        assert classify.archetype(_control(engine | {"Teferi, Time Raveler": 3, sweeper: 3})) == "jeskai"
    assert classify.archetype(_control(engine | {"Teferi, Time Raveler": 3})) is None
    assert classify.archetype(_control({"Teferi, Time Raveler": 3, "Terminus": 4})) is None


def test_an_off_colour_removal_playset_is_still_control():
    """Removal is a slot control fills to the meta too (Alejandro, 2026-09-13):
    stefansson30952's 9th ran 4 Fatal Push as its only card outside UWr and the
    playset line read it as another deck's. A playset of an engine or a threat
    still does, the exemption naming removal and nothing else.
    """
    from tracker import classify

    shell = {"Teferi, Time Raveler": 3, "Wrath of the Skies": 3, "Narset, Parter of Veils": 4}
    assert classify.archetype(_control(shell | {"Fatal Push": 4})) == "jeskai"
    assert classify.archetype(_control(shell | {"Questing Druid": 4})) is None
    assert classify.archetype(_control(shell | {"Fatal Push": 4, "Questing Druid": 2})) is None


def test_an_ephemerate_package_inside_a_control_suite_is_not_control():
    """Ephemerate beside the control shell is a blink deck (Alejandro,
    2026-09-13), which is what Fatal_Vlad's, toto_2295's and Valident's lists
    are: a value package with its own targets inside an intact control suite.
    The Blink midrange deck's own marker stays Phelia, so the two name
    different decks on the same shell.
    """
    from tracker import classify

    shell = {"Teferi, Time Raveler": 3, "Wrath of the Skies": 3, "Narset, Parter of Veils": 4}
    assert classify.archetype(_control(shell)) == "jeskai"
    assert classify.archetype(_control(shell | {"Ephemerate": 4})) is None
    assert classify.fallout(_control(shell | {"Ephemerate": 4})) == [("jeskai", "ephemerate")]


def test_tron_s_versions_are_read_on_their_markers_and_never_on_a_splash():
    """The Tron lands are Tron; blue and green are versions and colourless is
    tracked (Alejandro, 2026-09-13). Blue Tron is the deck on Stock Up or Force
    of Negation and green Tron the deck on the Chromatic eggs or Sylvan
    Scrying; every other list is colourless whatever it casts. narca's Dress
    Down build is the case the splash line got wrong, reading a playset in the
    colourless Eldrazi shell's flex slot as the blue deck arriving.
    """
    from types import SimpleNamespace
    from tracker import classify

    lands = {"Urza's Tower": 4, "Urza's Mine": 4, "Urza's Power Plant": 4}
    colours = {"Stock Up": frozenset("U"), "Dress Down": frozenset("U"), "Dismember": frozenset("B"),
               "Sylvan Scrying": frozenset("G"), "Ancient Stirrings": frozenset("G")}

    def tron(spells):
        return SimpleNamespace(mainboard=lands | spells, colours=colours, land_names=frozenset(lands))

    for spells, version in [
        ({"Karn, the Great Creator": 4, "Dismember": 4}, "colourless"),
        ({"Karn, the Great Creator": 4, "Dress Down": 4}, "colourless"),
        ({"Ancient Stirrings": 4}, "colourless"),
        ({"Stock Up": 4}, "blue"),
        ({"Force of Negation": 2}, "blue"),
        ({"Sylvan Scrying": 4, "Ancient Stirrings": 4}, "green"),
    ]:
        assert classify.archetype(tron(spells)) == "tron", spells
        assert classify.variant("tron", tron(spells)) == version, spells


def test_the_boundary_day_is_not_in_the_store(tmp_path):
    """The events published on 2026-05-18, the announcement date, were played
    under the old rules (Alejandro, 2026-09-13): the history opens the day after.
    """
    db = _built(tmp_path, [_lists("2026-05-18", 1), _lists("2026-05-19", 1)])
    with duckdb.connect(db, read_only=True) as con:
        assert con.execute("SELECT DISTINCT date FROM decklists").fetchall() == [("2026-05-19",)]


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


def test_the_opening_fortnight_names_no_fortnight_before_it(tmp_path):
    """The history opens the day after the boundary, so nothing sits behind its
    first fortnight. A row saying it was read against the fortnight to 17 May
    names a fortnight the store does not hold and a date before the bans."""
    db = _built(tmp_path, [_lists(FIRST, 8)])
    opening = timeline.findings(db, config.REPORTS["blink"])[0]
    assert "2026-05-17" not in opening["against"]
    assert config.HISTORY_START in opening["against"]


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

    The two fortnights of the gap are sized past `TRACK_RETURN_ABSENCE_LISTS`
    between them, or neither card counts as having been gone from anything.
    """
    vacuum, emrakul = {"Ghost Vacuum": (0, 3)}, {"Emrakul, the Aeons Torn": (0, 3)}
    db = _built(tmp_path, [
        # Before the gap: the vacuum is a two-list one-off, Emrakul is in every list.
        _mixed(FIRST, [vacuum | emrakul] * 2 + [emrakul] * 6, "e0"),
        _lists(SECOND, 13),
        _lists("2026-06-17", 13),
        # After it, they swap: the deck turned to one and remembered the other.
        _mixed("2026-07-01", [vacuum] * 8 + [emrakul] * 4, "e3"),
    ])
    returns = {
        row["card"]
        for entry_ in timeline.findings(db, config.REPORTS["blink"])
        for row in entry_["found"]
        if row["kind"] == "return"
    }
    assert "Ghost Vacuum" in returns
    assert "Emrakul, the Aeons Torn" not in returns


def test_a_return_needs_enough_lists_behind_it_to_have_been_absent_from(tmp_path):
    """A thin fortnight is the deck having been small, not the card having been gone.

    The same card, the same appearance, and the only difference is how many
    lists it was missing from. Read against a fortnight of five it is the deck's
    opening weeks reporting themselves as an innovation burst, which is what the
    live history did: Devoted Combo's bin to 2026-06-14 called 16 cards new off
    a two-list baseline, Craterhoof Behemoth among them.
    """
    arrival = {"Ghost Vacuum": (0, 3)}
    thin = _built(tmp_path / "thin", [_lists(FIRST, 5), _lists(SECOND, 10, cards=arrival)])
    read = _built(tmp_path / "read", [_lists(FIRST, 30), _lists(SECOND, 10, cards=arrival)])

    def returns(db):
        return [
            row["card"]
            for row in timeline.findings(db, config.REPORTS["blink"])[1]["found"]
            if row["kind"] == "return"
        ]

    assert returns(thin) == []
    assert returns(read) == ["Ghost Vacuum"]


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
    """Membership is every signature card, so two of three is another deck."""
    short = blink("nearly", placement=1, points=15, cards={"Witch Enchanter": (0, 0)})
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
    # The first fortnight carries `TRACK_RETURN_ABSENCE_LISTS`, so that the card
    # the second one sideboards reads as new to the deck rather than as new to
    # a population too thin to have shown it.
    db = _built(tmp_path, [_lists(FIRST, 25), _lists(SECOND, 10, cards=adopted)])
    spot, payload = _paper_event("2026-06-06", [blink(f"pt{i}", cards=adopted) for i in range(10)])
    spotlight.cached(spot, tmp_path).write_text(json.dumps(payload), encoding="utf-8")

    plain = timeline.findings(db, config.REPORTS["blink"], spotlights=())[1]
    assert plain["against"] == "the fortnight to 2026-05-31"
    assert [row["card"] for row in plain["found"] if row["kind"] == "return"] == ["Clarion Conqueror"]

    # The bin the event fell in now carries a row per baseline: its own previous
    # fortnight, then the event. The event's row is picked by name rather than
    # by position, the position being a fact about how many events fell in it.
    rows = timeline.findings(db, config.REPORTS["blink"], spotlights=(spot,), directory=tmp_path)
    chained = next(row for row in rows if row["against"] == "Pro Tour Test")
    assert chained["cross_population"] is True
    assert not [row for row in chained["found"] if row["card"] == "Clarion Conqueror"]
    # And the fortnight reading is not discarded to make room for it.
    own = next(row for row in rows if row["start"] == chained["start"] and row is not chained)
    assert own["against"] == "the fortnight to 2026-05-31"
    assert own["cross_population"] is False

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
    rows = timeline.findings(db, _report(manabase=True), spotlights=(spot,), directory=tmp_path)
    after = next(row for row in rows if row["against"] == spot["label"])
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


def test_presence_is_the_whole_deck_and_conversion_is_the_version(tmp_path, monkeypatch):
    """A metagame share is the whole deck's; a finish is the version's.

    Read on one version of two, presence answers half the question. Read pooled,
    conversion credits the tracked version with the other version's finishes.
    So the two are frozen as two populations in two files, and the summary's
    volume clause and conversion clause come from different rows.
    """
    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    both = challenge(FIRST, [
        blink("esper_pilot", variant="esper", placement=9, points=12),
        blink("orzhov_pilot", variant="orzhov", placement=1, points=15),
    ], "e1")
    db = _built(tmp_path, [both])
    weekly.freeze(db, "blink", through="2026-05-18")

    reading = weekly.facts(db, "blink", "2026-05-18")
    assert reading["challenge"]["lists"] == 2
    assert (reading["conversion"]["lists"], reading["conversion"]["top8"]) == (1, 0)
    assert reading["versions"] == {"Orzhov": {"lists": 1, "challenge": 1, "trophies": 0}}
    assert [row["chal"] for row in weekly.version_weeks_through(db, "blink", config.REPORTS["blink"], "2026-05-18")] == [1]


@pytest.mark.parametrize("mainboard,expected", [
    ({"Unholy Heat": 2, "Ugin's Labyrinth": 2}, "gruul"),
    ({"Writhing Chrysalis": 3}, "gruul"),
    ({"Lightning Bolt": 2, "Grove of the Burnwillows": 4}, "gruul"),
    ({"Ugin's Labyrinth": 4, "Devourer of Destiny": 3}, "lab"),
    ({"Grove of the Burnwillows": 4}, "mono-green"),
])
def test_a_three_way_variant_rule_reads_in_order(mainboard, expected):
    """The first version whose cards the list holds names it; none is the default.

    A Gruul list on a couple of Labyrinths is a Gruul list, so the red spells
    are tested before the Labyrinth. A red source is not the line: Grove of the
    Burnwillows sits in nine of ten mono-green lists, which is why BenT's and
    Lostwanderer's Pro Tour lists are read on the Bolts they cast off it.
    """
    from types import SimpleNamespace
    from tracker import classify

    assert classify.variant("broodscale", SimpleNamespace(mainboard=mainboard)) == expected


def test_blink_s_esper_version_is_the_grave_or_a_blue_spell():
    """A version read on a colour is read on the spells the list casts and never
    on the splash line (Alejandro, 2026-09-13).

    Watery Grave named the Esper half until SuperCow12653 registered 2 Teferi
    off Hallowed Fountain and Meticulous Archive twice, with no Grave: the card
    and the colour together name the version whichever way a pilot builds the
    mana. A list casting nothing blue off a fetchable Grave is still Esper, the
    card being tested first.
    """
    from types import SimpleNamespace
    from tracker import classify

    creatures = {card: 2 for card in config.TRACKED_DECKS["blink"]["signature"]}
    lands = {"Marsh Flats": 4, "Godless Shrine": 2, "Hallowed Fountain": 2, "Watery Grave": 2}
    colours = {"Teferi, Time Raveler": frozenset("WU"), "Solitude": frozenset("W")}

    def blink_list(spells, mana):
        main = creatures | spells | {land: count for land, count in lands.items() if land in mana}
        return SimpleNamespace(mainboard=main, colours=colours, land_names=frozenset(lands))

    orzhov_mana = ("Marsh Flats", "Godless Shrine")
    esper_mana = (*orzhov_mana, "Watery Grave")
    assert classify.variant("blink", blink_list({"Solitude": 4}, orzhov_mana)) == "orzhov"
    assert classify.variant("blink", blink_list({"Teferi, Time Raveler": 2}, orzhov_mana)) == "esper"
    assert classify.variant("blink", blink_list({"Solitude": 4}, esper_mana)) == "esper"


def test_a_version_read_by_colour_is_one_the_report_names(tmp_path, monkeypatch):
    """Blue and green Tron are read in the report as versions (Alejandro,
    2026-09-13), so the report has to know they exist: the presence panel and
    the bare counts list every version the rule names, colour ones included."""
    assert config.versions("tron") == ("blue", "green", "colourless")
    assert weekly._others(config.REPORTS["tron"]) == ["blue", "green"]


def test_broodscale_s_golgari_version_is_the_black_cards_and_never_dismember():
    """Black and green is a fourth version, read after red and the Labyrinth
    (Alejandro, 2026-09-13). The build is Sephiroth with Fatal Push on
    Overgrown Tomb, Swamp and Underground Mortuary, and it took a challenge-64
    on 6 July. Dismember is the card the version cannot be read on: Phyrexian
    mana casts it in 419 members that hold no black source at all, the same
    reason Prowess draws no colour rule off Mutagenic Growth. A list on a red
    spell is still Gruul, which is what keeps the versions a partition.
    """
    from types import SimpleNamespace
    from tracker import classify

    core = {"Basking Broodscale": 4, "Blade of the Bloodchief": 4, "Eldrazi Temple": 4}
    colours = {"Dismember": frozenset("B"), "Sephiroth, Fabled SOLDIER": frozenset("B"),
               "Fatal Push": frozenset("B"), "Thoughtseize": frozenset("B"),
               "Unholy Heat": frozenset("R"), "Kozilek's Command": frozenset("G")}
    lands = frozenset({"Eldrazi Temple", "Ugin's Labyrinth", "Overgrown Tomb"})

    def brood(spells):
        return SimpleNamespace(mainboard=core | spells, colours=colours, land_names=lands)

    for spells, version in [
        ({"Kozilek's Command": 4}, "mono-green"),
        ({"Dismember": 2}, "mono-green"),
        ({"Sephiroth, Fabled SOLDIER": 3, "Fatal Push": 2}, "golgari"),
        ({"Thoughtseize": 4, "Fatal Push": 3}, "golgari"),
        ({"Sephiroth, Fabled SOLDIER": 3, "Unholy Heat": 4}, "gruul"),
        ({"Sephiroth, Fabled SOLDIER": 3, "Ugin's Labyrinth": 4}, "lab"),
    ]:
        assert classify.archetype(brood(spells)) == "broodscale", spells
        assert classify.variant("broodscale", brood(spells)) == version, spells


def test_a_fortnight_too_thin_to_read_says_so_instead_of_printing_its_rows(tmp_path):
    """A bin of eight lists prints the same kind of claim as a bin of a hundred
    and thirty, and the reader has only the counts beside the row to tell them
    apart (Alejandro, 2026-09-13). Grinding Station's fortnight to 2026-08-23
    printed 21 rows off 8 lists, its own namesake among them at "Oswald
    Fiddlebender fell in the mainboard, 21/23 to 5/8 lists".

    The same move across the same two fortnights, and the only difference is how
    many lists the thinner of them holds.
    """
    took_up = {"Ghost Vacuum": (3, 0)}
    thin = _built(tmp_path / "thin", [_lists(FIRST, 20), _lists(SECOND, 8, cards=took_up)])
    read = _built(tmp_path / "read", [_lists(FIRST, 20), _lists(SECOND, 10, cards=took_up)])

    def rows(db):
        found = timeline.findings(db, config.REPORTS["blink"])[1]["found"]
        return [row for row in found if row["kind"] != "event"]

    assert [row["kind"] for row in rows(thin)] == ["thin"]
    assert "8 lists, the smaller of the two" in rows(thin)[0]["text"]
    assert [row["card"] for row in rows(read)] == ["Ghost Vacuum"]


def test_the_floor_reads_the_smaller_fortnight_whichever_side_it_is_on(tmp_path):
    """The evidence for a move is the thinner of the two populations, so a thick
    fortnight read against a thin one is no better off than the reverse. Devoted
    Combo's bin to 2026-06-14 printed 14 rows against a 2-list history."""
    took_up = {"Ghost Vacuum": (3, 0)}
    db = _built(tmp_path, [_lists(FIRST, 8), _lists(SECOND, 20, cards=took_up)])

    found = [row for row in timeline.findings(db, config.REPORTS["blink"])[1]["found"]]
    assert [row["kind"] for row in found if row["kind"] != "event"] == ["thin"]


def test_a_return_is_read_off_the_absence_behind_it_and_not_across_the_two(tmp_path):
    """The floor is on the move, so it leaves the return reading alone.

    A return says the deck had stopped playing a card and took it up again,
    which rests on the lists it was missing from rather than on the two
    populations either side of the line. That absence has a floor of its own
    (`TRACK_RETURN_ABSENCE_LISTS`), given to it on 2026-09-13, so a thin bin is
    already refused there when the history behind it is thin too.
    """
    db = _built(tmp_path, [_lists(FIRST, 30), _lists(SECOND, 8, cards={"Ghost Vacuum": (3, 0)})])

    found = timeline.findings(db, config.REPORTS["blink"])[1]["found"]
    assert [row["kind"] for row in found if row["kind"] != "event"] == ["return", "thin"]
    assert "Ghost Vacuum appears for the first time" in found[0]["text"]


def test_a_paper_events_watchlist_is_rendered_and_never_frozen(tmp_path, monkeypatch):
    """A novelty is a claim about an event, not about a fortnight.

    The frozen timeline is the deck's committed history and is written once: a
    row in it is a fortnight's finding, phrased under the rule that was in force
    when it was frozen. A watchlist is neither. It is read off one room against
    the deck's own history, it carries no baseline, and it is recomputed on every
    render like the rest of the paper section, so it has no business in the file
    that must not be rebuilt.
    """
    from tracker import spotlight

    monkeypatch.setattr(config, "TRACKING_DIR", tmp_path / "tracking")
    monkeypatch.setattr(config, "REPORT_DIR", tmp_path / "reports")
    monkeypatch.setattr(config, "MELEE_DIR", tmp_path / "melee")
    # A fortnight of MTGO that never registered the card, and an event whose
    # good finishers did.
    db = _built(tmp_path, [_lists(FIRST, 25), _lists(SECOND, 25)])
    finishers = [blink(f"pt{i}", cards={"Ghost Vacuum": (0, 2)}) for i in range(4)]
    spot, payload = _paper_event("2026-06-06", finishers + [blink(f"pt{i}") for i in range(4, 100)])
    monkeypatch.setattr(config, "MAJOR_EVENTS", (spot,))
    spotlight.cached(spot).parent.mkdir(parents=True, exist_ok=True)
    spotlight.cached(spot).write_text(json.dumps(payload), encoding="utf-8")

    week = spotlight.week(spot)
    weekly.freeze(db, "blink", through=week)
    page = weekly.render(db, "blink", week).read_text(encoding="utf-8")

    frozen = weekly._read(weekly.deck_dir("blink") / "timeline.csv")
    assert "Ghost Vacuum" not in {row["card"] for row in frozen}
    assert '<span class="tag">novelty</span>Ghost Vacuum to watch in the sideboard' in page
    # Under the event it was read off, and said to have been read against no
    # baseline, so a reader never takes it for a move between two populations.
    assert "against its own field and the deck's MTGO history" in page


def test_the_summary_reads_as_a_lead_and_a_list_of_facts():
    """The summary is scanned before it is read, so the facts are bullets.

    A reader meets the lead first and the figures under it, one per line. The
    two shapes the file uses are a paragraph and a `- ` block, and a bold label
    opens each bullet so the eye can find the reading it wants.
    """
    written = (
        "Broodscale won RC Baltimore. SolomonGrundy took it on 15-2-1.\n\n"
        "- **MTGO** 11.2% of the top 32, from 10.5%.\n"
        "- **Conversion** the Lab version is over-converting.\n"
    )
    markup = weekly.summary_html(written)

    assert markup.startswith("<p>Broodscale won RC Baltimore.")
    assert markup.count("<li>") == 2
    assert "<li><b>MTGO</b> 11.2% of the top 32, from 10.5%.</li>" in markup
    # One list, not one per bullet.
    assert markup.count("<ul>") == 1


def test_a_summary_of_paragraphs_alone_still_renders():
    """Weeks before the bullets, and any week with nothing to itemise."""
    markup = weekly.summary_html("First paragraph.\n\nSecond paragraph.")

    assert markup == "<p>First paragraph.</p><p>Second paragraph.</p>"
