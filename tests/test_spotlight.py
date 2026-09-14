"""The paper Spotlight readings: membership, position, record, and the chain.

Same seam as the rest of the suite: payloads shaped as melee publishes them in
one end, and the verdict a reader would act on out the other. What is asserted
here is never a query or an intermediate, it is whether the deck reads as
present, as having finished well, and as having changed something.

The payloads are written rather than captured because every claim below is about
two events of deliberately different size, or about a name disagreeing with the
cards under it, and no fetched event holds one of those disentangled from the
rest of what a nine-hundred-player field was doing.
"""

import json

import pytest

from tracker import config, melee, spotlight, store, weekly
from tests import synthetic

SIGNATURE = {card: 4 for card in config.TRACKED_DECKS["blink"]["signature"]}
ESPER = {"Watery Grave": 1}
FILLER = {"Thoughtseize": 4, "Solitude": 4, "Flooded Strand": 4, "Plains": 2}

BRISBANE = {"id": 441441, "label": "Spotlight Brisbane", "date": "2026-08-29", "region": "australia"}
DALLAS = {"id": 405590, "label": "Spotlight Dallas", "date": "2026-09-05", "region": "usa"}


def _list(rank, main=None, side=None, name="Esper Blink", wins=8, losses=4, draws=0, points=None):
    return {
        "decklist_id": f"d{rank}",
        "rank": rank,
        "pilot": f"pilot{rank}",
        "name": name,
        "record": f"{wins}-{losses}-{draws}",
        "wins": wins,
        "losses": losses,
        "draws": draws,
        # Swiss points, which is a separate figure from the record and not
        # derivable from it: a playoff match is a win that earns none.
        "points": wins * 3 if points is None else points,
        "main": {**SIGNATURE, **ESPER, **FILLER, **(main or {})},
        "side": side or {},
    }


def _payload(spot, lists, players=None):
    return {
        "tournament": {
            "id": spot["id"],
            "name": spot["label"],
            "organiser": "test",
            "start": f"{spot['date']}T00:00:00Z",
            "round": "Finals",
            "players": players or len(lists),
        },
        "lists": lists,
    }


def _cache(tmp_path, spot, payload):
    tmp_path.mkdir(parents=True, exist_ok=True)
    spotlight.cached(spot, tmp_path).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_a_double_faced_card_is_folded_to_the_face_mtgo_publishes():
    """The fold is what makes a paper list of this deck classify at all.

    Melee writes a modal double-faced card as `Front // Back` and MTGO writes
    the front face, and one of this deck's four signature cards is one. Left
    unfolded the name never matches, every Blink list in the field fails
    membership on it, and the deck reads as absent from paper entirely, which is
    a far worse failure than a missing card because nothing about it looks wrong.
    """
    markup = (
        '<div class="decklist-category-title">Creature (4)</div>'
        '<div class="decklist-record"><span class="decklist-record-quantity">4</span>'
        '<a class="decklist-record-name" href="/Card/View/x">'
        "Witch Enchanter // Witch-Blessed Meadow</a></div>"
    )
    main, _ = melee.boards(markup)
    assert main == {"Witch Enchanter": 4}


def test_a_split_card_keeps_both_halves_because_mtgo_publishes_both():
    """Melee writes a split card the way it writes a double-faced one, and MTGO does not.

    MTGO publishes both halves under one name, `Wear/Tear`, so folded to its
    front face the card becomes `Wear`, which no MTGO list has ever registered.
    Every paper row for it then reads as the event adopting a card the deck has
    never played, and the fortnight after reads as the deck dropping it again.
    The live cache carries 2,511 registrations of `Wear/Tear` and not one of
    `Wear`.
    """
    markup = (
        '<div class="decklist-category-title">Instant (3)</div>'
        '<div class="decklist-record"><span class="decklist-record-quantity">3</span>'
        '<a class="decklist-record-name" href="/Card/View/x">Wear // Tear</a></div>'
    )
    main, _side = melee.boards(markup)
    assert main == {"Wear/Tear": 3}


def test_the_sideboard_is_split_on_its_heading_and_not_on_a_count():
    """A companion sits under its own heading and is not a 61st mainboard card."""
    markup = (
        '<div class="decklist-category-title">Instant (2)</div>'
        '<div class="decklist-record"><span class="decklist-record-quantity">2</span>'
        '<a class="decklist-record-name" href="/x">Ephemerate</a></div>'
        '<div class="decklist-category">'
        '<div class="decklist-category-title">Sideboard (1)</div>'
        '<div class="decklist-record"><span class="decklist-record-quantity">1</span>'
        '<a class="decklist-record-name" href="/x">Clarion Conqueror</a></div>'
    )
    main, side = melee.boards(markup)
    assert main == {"Ephemerate": 2}
    assert side == {"Clarion Conqueror": 1}


def test_membership_is_the_cards_and_never_the_name_the_pilot_typed():
    """A decklist name on melee is free text and cannot decide an archetype.

    The same seventy-five was registered as "Esper Blink", "Azorius Blink" and a
    bare "Esper" at one event, and lists that are not the deck were registered
    as "Esper Blink". Counting by name would put both errors into every share.
    """
    # Named for another deck and holding the rule, against named for this one
    # and one signature card short of it.
    impostor = _list(3, name="Esper Blink")
    del impostor["main"]["Witch Enchanter"]
    payload = _payload(
        BRISBANE,
        [_list(1, name="Azorius Blink"), _list(2, name="Mono-Green Eldrazi"), impostor],
    )
    assert [row["rank"] for row in spotlight.members(payload)] == [1, 2]


def test_a_spotlight_sits_on_the_week_it_was_played_in():
    """Keyed by that week's Monday and read by its Sunday, like every other week.

    A Spotlight is a Saturday, and the report's calendar is weeks. Brisbane on
    29 August is the week ending 30 August and Dallas on 5 September is the week
    ending 6 September, which is what puts the two in different weeks rather
    than in the one fortnight bin that happens to contain both.
    """
    assert spotlight.week(BRISBANE) == "2026-08-24"
    assert spotlight.week(DALLAS) == "2026-08-31"
    assert weekly.week_label(spotlight.week(BRISBANE)) == "2026-08-30"
    assert weekly.week_label(spotlight.week(DALLAS)) == "2026-09-06"


def test_position_is_read_against_the_field_and_not_as_a_rank():
    """Rank 100 is a different result at 932 seats than at 574.

    This is the whole reason the positional axis is a share. Two lists that
    finished in the same tenth of two differently sized rooms have to read as
    the same result, and two lists on the same rank must not.
    """
    small = _payload(BRISBANE, [_list(rank) for rank in range(1, 101)])
    big = _payload(DALLAS, [_list(rank) for rank in range(1, 1001)])
    # One list at a tenth of the way down each field.
    tenth_of_small = spotlight.reading(small)["placings"][10]
    tenth_of_big = spotlight.reading(big)["placings"][100]
    assert tenth_of_small == pytest.approx(tenth_of_big)


def test_a_seat_that_registered_no_decklist_still_counts_under_the_field():
    """The field a position is read against is the seats, not the decklists.

    An entrant can be ranked and publish nothing, so ranks run past the number
    of lists: Dallas ranked 932 over 928 published and Brisbane 573 over 571.
    Read against the lists, the bottom of such a field lands past 1.0, which is
    where the diagonal the panel is drawn against closes.
    """
    # 100 seats, of which the four who registered nothing are the four ranks
    # missing from the published lists.
    published = [_list(rank) for rank in range(1, 101) if rank not in (40, 60, 80, 100)]
    reading = spotlight.reading(_payload(BRISBANE, published, players=100))
    assert reading["lists"] == 96
    assert max(reading["placings"]) < 1.0
    # Rank 99 is the last seat but one, and reads as that rather than as the
    # 96 lists it would be a fraction of.
    assert reading["placings"][-1] == pytest.approx(98 / 100)


def test_the_win_rate_counts_matches_and_never_points():
    """Points stop accruing at the top cut and the record does not.

    The pilot who wins the event plays three more matches than the Swiss leader
    and earns no points for them, so a rate read off points scores the winner
    below somebody they beat.
    """
    # Won the event: 12-3 through the Swiss for 36 points, then three playoff
    # wins that earn none. Against the pilot who topped the Swiss and lost in
    # the quarter-final, on more points and fewer wins.
    winner = _list(1, wins=15, losses=3, points=36)
    swiss_leader = _list(2, wins=13, losses=2, points=39)
    reading = spotlight.reading(_payload(DALLAS, [winner, swiss_leader]))
    assert reading["wins"] == 28
    assert reading["losses"] == 5
    assert reading["win_rate"] == pytest.approx(28 / 33)
    # The two figures disagree about which pilot had the better tournament, and
    # the record is the one that gets it right.
    assert winner["wins"] > swiss_leader["wins"]
    assert winner["points"] < swiss_leader["points"]


def test_conversion_is_the_cut_against_the_whole_room():
    """A deck that held more of the top 32 than of the field converted.

    The reading MTGO cannot make, its challenge data being a top 32 with no
    field under it to divide by. Above 1.00 the deck finished above its numbers.
    """
    # Six of 320 lists, and three of them in the top 32: a tenth of the cut
    # against a fiftieth of the room.
    ours = [_list(rank) for rank in (1, 5, 20)]
    theirs = [_list(rank, name="Other") for rank in range(33, 350)]
    for row in theirs:
        row["main"] = {"Lightning Bolt": 4}
    reading = spotlight.reading(_payload(DALLAS, ours + theirs))
    assert reading["cut_lists"] == 3
    assert reading["conversion"] > 1
    assert reading["best"] == 1


def test_the_second_spotlight_is_read_against_the_first_and_not_against_mtgo(tmp_path):
    """Paper to paper is the only clean comparison the two events allow.

    Both fell inside one MTGO fortnight, so a bin lookup would read each against
    the same rows and call the second one's change a repeat of the first's. The
    chain reads Dallas against Brisbane, which is one week apart with the format
    and the medium held constant.
    """
    plain = [_list(rank) for rank in range(1, 21)]
    adopted = [_list(rank, side={"Clarion Conqueror": 3}) for rank in range(1, 21)]
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, plain))
    _cache(tmp_path, DALLAS, _payload(DALLAS, adopted))

    chain = spotlight.chain(config.DB_PATH, spotlights=(BRISBANE, DALLAS), directory=tmp_path)
    assert chain[1]["against"] == "Spotlight Brisbane"
    # Marked, the two being an Australian field and an American one. The medium
    # is held constant and the room is not, and the room is what the flag says.
    assert chain[1]["cross_population"] is True
    climbed = [row for row in chain[1]["found"] if row["card"] == "Clarion Conqueror"]
    assert climbed and "climbed" in climbed[0]["text"]


def test_the_first_spotlight_is_marked_as_crossing_populations(tmp_path):
    """Its baseline is MTGO, which is a different room and says so.

    An Australian paper field and the MTGO field are two populations, so a card
    at nine tenths of one and half of the other is not the deck changing its
    mind. The row carries the flag rather than the reader being expected to
    remember which side of the chain it came from.
    """
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 21)]))
    chain = spotlight.chain(config.DB_PATH, spotlights=(BRISBANE,), directory=tmp_path)
    assert chain[0]["cross_population"] is True
    assert chain[0]["against"].startswith("the fortnight to ")


def test_a_thin_spotlight_does_not_earn_rows_off_the_size_difference(tmp_path):
    """The fortnight's count gate inverts when the two populations differ tenfold.

    It asks the number of lists to move by five, which holds the evidence
    constant only while both sides are about the same size. Eleven paper lists
    against a hundred and twelve MTGO ones is not that: a card at a seventh of
    the big population and a third of the small one differs by thirteen lists on
    the denominators alone, and every moderately played card would earn a row.

    So a small real move is suppressed and a large one is not, at a size ratio
    that would pass both under the fortnight's own gate.
    """
    baseline = [_list(rank) for rank in range(1, 113)]
    for row in baseline[:16]:
        row["side"] = {"Nihil Spellbomb": 2}
    for row in baseline[:85]:
        row["side"] = {**row["side"], "Damping Sphere": 2}

    thin = [_list(rank) for rank in range(1, 12)]
    # A seventh of the big field to a third of the small one: a real-looking
    # jump that eleven lists cannot actually evidence.
    for row in thin[:4]:
        row["side"] = {"Nihil Spellbomb": 2}
    # And a card most of the baseline ran that almost none of these do.
    for row in thin[:3]:
        row["side"] = {**row["side"], "Damping Sphere": 2}

    found = {row["card"] for row in spotlight.findings(thin, baseline)}
    assert "Nihil Spellbomb" not in found
    assert "Damping Sphere" in found


def test_a_card_in_both_boards_counts_once_as_the_store_counts_it():
    """Melee publishes the two boards apart and the store does not.

    A list running three in the mainboard and two in the side is one mainboard
    registration to the store, so counting it in both zones here would make every
    split card read as a sideboard adoption the moment paper met MTGO.
    """
    split = [
        _list(rank, main={"Ghost Vacuum": 3}, side={"Ghost Vacuum": 2}) for rank in range(1, 12)
    ]
    plain = [_list(rank) for rank in range(1, 12)]
    # Nothing about the sideboard moved, so nothing about it is a finding.
    found = spotlight.findings(split, plain)
    assert not [row for row in found if row["zone"] == "side"]
    assert [row["zone"] for row in found] == ["main"]


def test_a_card_changing_zone_is_one_row_and_not_two():
    """Promoting a sideboard card is a decision about what it is for.

    Read one board at a time it is a card the deck took up and a card the deck
    put down, in the same week, which is two findings about one move and reads
    as the deck contradicting itself.
    """
    before = [_list(rank, side={"Consign to Memory": 3}) for rank in range(1, 12)]
    after = [_list(rank, main={"Consign to Memory": 3}) for rank in range(1, 12)]
    found = spotlight.findings(after, before)
    assert [row["kind"] for row in found] == ["migration"]
    assert "moves to the mainboard" in found[0]["text"]


def test_a_week_never_reports_a_spotlight_it_had_not_seen_yet(tmp_path, monkeypatch):
    """Rebuilt in October, the August report has to say what it said in August.

    Every other part of the report is cut off at the week being rendered, the
    weekly rows and the timeline included, because a report whose past changes
    under it is a report nobody can cite. A Spotlight cache is the one input
    that arrives for all events at once, so without this the week before
    Brisbane would show Dallas, an event a fortnight in its own future.
    """
    monkeypatch.setattr(config, "MELEE_DIR", tmp_path)
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 12)]))
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 12)]))

    def shown(week):
        return [entry["label"] for entry in weekly.spotlights_through(week)]

    assert shown("2026-08-17") == []
    assert shown(spotlight.week(BRISBANE)) == ["Spotlight Brisbane"]
    assert shown(spotlight.week(DALLAS)) == ["Spotlight Brisbane", "Spotlight Dallas"]


def test_a_spotlight_never_reports_a_returning_card(tmp_path):
    """A card absent from MTGO and present in paper is a different field building.

    The return reading is a claim about one population's history over months.
    Pointed at a paper event it would announce a card the Australian field simply
    plays as the deck rediscovering it, every time.
    """
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 21)]))
    exotic = [_list(rank, main={"Karakas": 2}) for rank in range(1, 21)]
    _cache(tmp_path, DALLAS, _payload(DALLAS, exotic))
    chain = spotlight.chain(config.DB_PATH, spotlights=(BRISBANE, DALLAS), directory=tmp_path)
    assert not [row for row in chain[1]["found"] if row["kind"] == "return"]


def _sized(main: dict, total: int) -> dict:
    """`main` padded with basics to exactly `total` cards, the guard being a count."""
    return {**main, "Wastes": total - sum(main.values())}


def test_a_list_whose_boards_did_not_separate_is_not_read_as_a_member():
    """A parse failure may not add lists to the archetype.

    Melee groups a decklist page under type headings and the split is the
    heading, so a sideboard filed under one the fetch does not know puts the
    whole 75 in the mainboard. Membership is a mainboard test, so a list that
    only sideboarded a signature card would join the deck on that failure.
    Melee's own history carries three such lists, at 75, 76 and 146 cards.
    """
    # A non-member whose sideboarded signature cards landed in the mainboard.
    leaked = _list(5)
    leaked["main"] = _sized({**FILLER, "Broadside Bombardiers": 4, **SIGNATURE, **ESPER}, 75)
    leaked["side"] = {}
    assert spotlight.unread(leaked)

    payload = _payload(BRISBANE, [_list(1), leaked])
    assert [row["rank"] for row in spotlight.members(payload, "blink", "esper")] == [1]
    reading = spotlight.reading(payload, "blink", "esper")
    # Published and in the field, so still in every denominator; just not ours.
    assert (reading["field"], reading["lists"], reading["unread"]) == (2, 1, 1)


def test_a_pilot_who_registered_no_sideboard_is_read_normally():
    """Sixty cards and an empty sideboard is a legal registration, not a failure.

    The signature of the failure is the pair: a mainboard past 60 *and* nothing
    in the sideboard. Melee's history has three lists on 60 with no sideboard,
    and turning those away would be the guard costing real lists.
    """
    bare = _list(2)
    bare["main"] = _sized(bare["main"], 60)
    bare["side"] = {}
    assert not spotlight.unread(bare)
    assert len(spotlight.members(_payload(BRISBANE, [_list(1), bare]), "blink", "esper")) == 2


def _other(rank):
    """A finisher of some other deck: the shape of a row, none of the signature."""
    return {**_list(rank, name="Other"), "main": {"Lightning Bolt": 4, "Mountain": 56}}


def test_the_reading_names_who_finished():
    """The finishes, with pilots and records, not just the best rank.

    A Spotlight is the biggest tournament of its era and the paper paragraph
    leads with who finished. Left out of the reading, those names come off the
    standings page by hand, which is the one part of the report written from
    whatever the writer happened to scroll past.
    """
    field = [_other(rank) for rank in range(1, 101)]
    field[0] = _list(1, wins=13, losses=1)
    field[39] = _list(40, wins=11, losses=4)
    top = spotlight.reading(_payload(DALLAS, field))["top"]
    assert [(row["rank"], row["pilot"], row["record"]) for row in top] == [
        (1, "pilot1", "13-1-0")
    ]


def test_a_deck_that_missed_the_cut_still_reports_its_best_finish():
    """Nothing in the top 32 is a finding, not a blank: the best list is named."""
    field = [_other(rank) for rank in range(1, 101)]
    field[39] = _list(40, wins=11, losses=4)
    assert spotlight.reading(_payload(DALLAS, field))["top"] == [
        {"rank": 40, "pilot": "pilot40", "record": "11-4-0"}
    ]


def test_the_weeks_spotlight_reaches_the_summary_writer(tmp_path):
    """The paper figures are in the JSON the summary is written from, or nowhere.

    Every other clause is written from that file. This one was written off the
    rendered page, and nothing in the file said an event had fallen in the week
    at all, so whether the report got a paper paragraph depended on the writer
    remembering it had.
    """
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 12)]))
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 21)]))
    chain = spotlight.chain(config.DB_PATH, spotlights=(BRISBANE, DALLAS), directory=tmp_path)

    reported = weekly._paper(chain, spotlight.week(DALLAS))
    assert [entry["label"] for entry in reported] == ["Spotlight Dallas"]
    assert reported[0]["top"][0]["pilot"] == "pilot1"
    # Both sides of the comparison, because the clause quotes both.
    assert reported[0]["against"] == "Spotlight Brisbane"
    assert reported[0]["against_row"]["lists"] == 11
    assert weekly._paper(chain, "2026-08-17") == []


BALTIMORE = {"id": 405588, "label": "RC Baltimore", "date": "2026-09-12", "region": "usa"}
CHINA = {"id": 451148, "label": "RC China", "date": "2026-09-12", "region": "china"}


def test_both_championships_of_one_weekend_reach_the_summary_writer(tmp_path):
    """A week can hold two major events, and the clause is written from both.

    The writer used to be handed the first event whose week matched the reported
    week, with nothing in the file saying a second had been played: the week
    ending 2026-09-13 ran Baltimore and China on one day, and the paper clause
    would have reported half the deck's paper week as the whole of it.

    Side by side and not in a sequence. `chain` reads no event against one
    played in its own week, so each of the two is read against the event behind
    the weekend and neither is the other's baseline.
    """
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 21)]))
    _cache(tmp_path, BALTIMORE, _payload(BALTIMORE, [_list(rank) for rank in range(1, 13)]))
    _cache(tmp_path, CHINA, _payload(CHINA, [_list(rank) for rank in range(1, 8)]))
    chain = spotlight.chain(
        config.DB_PATH, spotlights=(DALLAS, BALTIMORE, CHINA), directory=tmp_path
    )

    reported = weekly._paper(chain, spotlight.week(BALTIMORE))

    assert [entry["label"] for entry in reported] == ["RC Baltimore", "RC China"]
    assert [entry["lists"] for entry in reported] == [12, 7]
    assert [entry["against"] for entry in reported] == ["Spotlight Dallas", "Spotlight Dallas"]
    assert [entry["against_row"]["lists"] for entry in reported] == [20, 20]


AMSTERDAM = {
    "id": 434455, "label": "Pro Tour Amsterdam", "date": "2026-07-17",
    "format": "Modern", "region": "international",
}


def test_each_event_reads_against_whatever_the_storyline_said_last(tmp_path):
    """A major event is a storyline entry, not a thing only another event may follow.

    MTGO moves what pilots take to a Pro Tour and a Pro Tour moves what turns up
    on MTGO the fortnight after, so an event weeks from the nearest other one is
    read against the fortnight that closed before it rather than against
    nothing. Dallas is the other case: Brisbane was played after that fortnight
    closed, so Brisbane is the entry it follows.
    """
    field = [_list(rank) for rank in range(1, 4)] + [_other(rank) for rank in range(4, 6)]
    _cache(tmp_path, AMSTERDAM, _payload(AMSTERDAM, field))
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 12)]))
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 21)]))

    amsterdam, brisbane, dallas = spotlight.chain(
        config.DB_PATH, spotlights=(AMSTERDAM, BRISBANE, DALLAS), directory=tmp_path
    )
    assert amsterdam["lists"] == 3 and amsterdam["field"] == 5
    assert amsterdam["against"] == "the fortnight to 2026-07-12"
    assert brisbane["against"] == "the fortnight to 2026-08-23"
    assert (dallas["against"], dallas["cross_population"]) == ("Spotlight Brisbane", True)


def test_the_constructed_rounds_of_a_two_format_event_are_read_apart():
    """Which rounds a Pro Tour's record is taken over, and where each run opens.

    Melee publishes a running total over the whole event, so the Modern record is
    the difference across each Modern run: the standings at its last round, less
    the standings at the round before it started. Read whole instead, a Modern
    deck's win rate is six rounds of limited and the column means nothing.
    """
    played = [
        {"id": str(n), "name": name, "format": fmt}
        for n, (name, fmt) in enumerate(
            [(f"Round {r}", fmt) for r, fmt in enumerate(
                ["Draft"] * 3 + ["Modern"] * 5 + ["Draft2"] * 3 + ["Modern"] * 5, start=1
            )]
            + [("Quarterfinals", "Draft 3"), ("Semifinals", "Draft 3"), ("Finals", "Draft 3")],
            start=1,
        )
    ]
    # Rounds 4 to 8 opening off round 3, and 12 to 16 opening off round 11.
    assert melee._blocks(played, "Modern") == [("3", "8"), ("11", "16")]


def test_an_empty_paper_row_says_it_was_the_sample_and_not_the_fetch():
    """A bare "stable" on a thin event reads as data that failed to arrive.

    Esper Blink took eight lists to Amsterdam against a fortnight of twenty
    seven, and the gate wants the move worth five lists in the smaller of the
    two, so five of those eight have to change their mind about one card. The
    row says which entry it was read against and how much of the event a finding
    costs, because a reader cannot otherwise tell a quiet event from a broken
    fetch.

    Whichever of the two bars asks for more lists is the one quoted. Past
    twenty-five lists the count gate is no longer the binding one and the
    adoption share is, so a row there costs a fifth of the smaller side rather
    than a flat five.
    """
    thin = {"against": "the fortnight to 2026-07-12", "baseline_lists": 27}
    assert "the fortnight to 2026-07-12" in weekly._stable(8, thin)
    assert "at 8 lists" in weekly._stable(8, thin)
    assert f"worth {config.TRACK_MIN_LISTS} of them" in weekly._stable(8, thin)

    fat = {"against": "Spotlight Brisbane", "baseline_lists": 29}
    assert "at 29 lists" in weekly._stable(77, fat)
    assert "worth 6 of them" in weekly._stable(77, fat)


def test_a_paper_list_reads_its_splash_off_the_colours_mtgo_has_published(tmp_path):
    """Melee publishes a decklist's cards and nothing else, so the splash line
    on a paper list reads the colours MTGO has published for the same names,
    the way the land count reads MTGO's types. A Dimir list on a playset of
    Flame of Anor is Grixis Frog, on paper as on MTGO.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw", [synthetic.league("2026-07-14", [synthetic.entry("colours", cards={"Lightning Bolt": (1, 0)})])]
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    assert store.card_colours(db)["Lightning Bolt"] == frozenset("R")
    assert store.card_colours(db)["Psychic Frog"] == frozenset("UB")

    shell = {"Psychic Frog": 4, "Quantum Riddler": 4, "Thoughtseize": 4, "Island": 24, "Swamp": 24}
    dimir = {**_list(1, name="Dimir Midrange"), "main": shell}
    grixis = {**_list(2, name="Grixis Frog"), "main": {**shell, "Flame of Anor": 4}}
    colours = store.card_colours(db) | {"Flame of Anor": frozenset("UR")}
    members = spotlight.members(
        _payload(DALLAS, [dimir, grixis]), "dimir", None, colours=colours, land_names=store.land_names(db)
    )
    assert [row["rank"] for row in members] == [1]


# The Pro Tour, the event the paper boundary reading was raised on: two
# Broodscale lists casting red off a card the Gruul rule did not name, in a
# field the MTGO store never reads.
AMSTERDAM = {"id": 434455, "label": "Pro Tour Amsterdam", "date": "2026-07-17", "region": "international"}


def _registered(rank, entry, name="Broodscale"):
    """One synthetic 75, published the way melee publishes a paper list."""
    return {
        **_list(rank, name=name),
        "pilot": entry["pilot"],
        "main": entry["main"],
        "side": entry["side"],
    }


def test_a_paper_list_casting_a_named_versions_colour_is_a_boundary_case(tmp_path):
    """The reading the MTGO store cannot reach: a rule gap only paper shows.

    KarplusanKid's list is the shape the two Pro Tour Broodscale lists have: a
    paper list casting red off a card the Gruul rule does not name, so it reads
    mono-green. It sits in a melee payload, which the store never loads, so
    nothing computed from the store can see it, which is why the boundary
    shipped with this half of its fourth criterion unmet.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw",
        [
            synthetic.league(
                "2026-07-14",
                [
                    synthetic.broodscale("gruul0", "gruul", cards={"Galvanic Discharge": (2, 0)}),
                    *(synthetic.broodscale(f"gruul{n}", "gruul") for n in range(1, 5)),
                    *(synthetic.broodscale(f"green{n}") for n in range(10)),
                ],
            )
        ],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    melee_dir = _cache(
        tmp_path / "melee",
        AMSTERDAM,
        _payload(
            AMSTERDAM,
            [
                _registered(
                    1, synthetic.broodscale("KarplusanKid", cards={"Galvanic Discharge": (2, 0)})
                ),
                _registered(2, synthetic.broodscale("someone")),
            ],
        ),
    )

    rows = spotlight.version_boundary(db, (AMSTERDAM,), melee_dir)
    assert [
        (row["event"], row["pilot"], row["archetype"], row["version"], row["kind"], row["marker"])
        for row in rows
    ] == [("Pro Tour Amsterdam", "KarplusanKid", "broodscale", "gruul", "colour", "R")]


def test_a_card_marker_is_read_off_mtgo_and_put_to_a_field_too_thin_to_carry_it(tmp_path):
    """The whole reason the markers come off the store: a card is a marker
    because `VERSION_MARKER_SHARE` of a named version's lists hold it, and one
    paper event's field cannot carry that bar. Amsterdam's mono-green
    Broodscale population is nine lists, where two lists casting red read as a
    fifth of the version rather than as two lists. So the store says what a
    marker is, and the event says which of its lists carry one.

    The list already sitting in the named version is not a case: the default is
    the one version no list is ever read into, which is the whole asymmetry the
    boundary exists for.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw",
        [
            synthetic.league(
                "2026-07-14",
                [
                    *(synthetic.blink(f"esper{n}", cards={"Shadowspear": (2, 0)}) for n in range(5)),
                    *(synthetic.blink(f"orzhov{n}", "orzhov") for n in range(10)),
                ],
            )
        ],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    field = [
        _registered(1, synthetic.blink("SuperCow12653", "orzhov", cards={"Shadowspear": (2, 0)})),
        _registered(2, synthetic.blink("labelled", cards={"Shadowspear": (2, 0)})),
        _registered(3, synthetic.blink("plain", "orzhov")),
    ]
    melee_dir = _cache(tmp_path / "melee", AMSTERDAM, _payload(AMSTERDAM, field))

    rows = spotlight.version_boundary(db, (AMSTERDAM,), melee_dir)
    assert len(field) < config.TRACK_MIN_LISTS
    assert [(row["pilot"], row["version"], row["kind"], row["marker"]) for row in rows] == [
        ("SuperCow12653", "esper", "card", "Shadowspear")
    ]


def test_the_paper_field_is_no_part_of_what_makes_a_card_a_marker(tmp_path):
    """The separation `config.MELEE_DIR` exists for, read the one way it could
    have been broken here. A paper event and an MTGO event are not the same
    population, so a share read across both is meaningless and nothing may pool
    them by accident.

    MTGO's Esper population is a list short of `TRACK_MIN_LISTS` here, so it has
    no cards to read, and the paper field holds ten Esper lists on Shadowspear.
    Pooled, the two would clear the bar between them and the paper Orzhov list
    would be named on a marker half of whose population never played MTGO.
    """
    raw = synthetic.write_cache(
        tmp_path / "raw",
        [
            synthetic.league(
                "2026-07-14",
                [
                    *(
                        synthetic.blink(f"esper{n}", cards={"Shadowspear": (2, 0)})
                        for n in range(config.TRACK_MIN_LISTS - 1)
                    ),
                    *(synthetic.blink(f"orzhov{n}", "orzhov") for n in range(10)),
                ],
            )
        ],
    )
    db = tmp_path / "engine.duckdb"
    store.build(raw, db)
    field = [
        _registered(1, synthetic.blink("SuperCow12653", "orzhov", cards={"Shadowspear": (2, 0)})),
        *(
            _registered(n, synthetic.blink(f"paper{n}", cards={"Shadowspear": (2, 0)}))
            for n in range(2, 12)
        ),
    ]
    melee_dir = _cache(tmp_path / "melee", AMSTERDAM, _payload(AMSTERDAM, field))

    assert spotlight.version_boundary(db, (AMSTERDAM,), melee_dir) == []


CHINA = {"id": 451148, "label": "RC China", "date": "2026-09-12", "region": "china"}
BALTIMORE = {"id": 405588, "label": "RC Baltimore", "date": "2026-09-12", "region": "usa"}


def test_an_event_is_read_against_both_the_paper_event_and_the_fortnight(tmp_path):
    """Two baselines, because they answer two different questions.

    The paper row holds the medium constant and is the stronger of the two; the
    MTGO row says whether the field the deck came from had already moved. The
    earlier rule kept whichever was later and dropped the other, so an event
    that followed another paper event lost its MTGO baseline with nothing
    saying so.
    """
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 12)]))
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 21)]))

    _, dallas = spotlight.chain(
        config.DB_PATH, spotlights=(BRISBANE, DALLAS), directory=tmp_path
    )
    assert [row["against"] for row in dallas["comparisons"]] == [
        "Spotlight Brisbane",
        "the fortnight to 2026-08-23",
    ]
    # The strongest is the one the paper section and the summary clause quote,
    # so it is the entry's own reading and not a third copy of a comparison.
    assert (dallas["against"], dallas["cross_population"]) == ("Spotlight Brisbane", True)
    assert dallas["comparisons"][0]["found"] == dallas["found"]


def test_two_events_on_one_weekend_are_read_against_the_same_two_entries(tmp_path):
    """Neither Regional Championship is the other's baseline.

    Baltimore and China were played on one weekend in two rooms, so a row
    between them would report the distance between an American field and a
    Chinese one as a fortnight's worth of change. Both are read against the
    paper event before that weekend and against the last closed fortnight, and
    Dallas qualifies as the paper one though it fell inside that fortnight: its
    lists are never folded into a fortnight's own numbers, so the two baselines
    share no list.
    """
    _cache(tmp_path, DALLAS, _payload(DALLAS, [_list(rank) for rank in range(1, 21)]))
    _cache(tmp_path, CHINA, _payload(CHINA, [_list(rank) for rank in range(1, 16)]))
    _cache(tmp_path, BALTIMORE, _payload(BALTIMORE, [_list(rank) for rank in range(1, 26)]))

    chain = spotlight.chain(
        config.DB_PATH, spotlights=(DALLAS, CHINA, BALTIMORE), directory=tmp_path
    )
    read = {entry["label"]: [row["against"] for row in entry["comparisons"]] for entry in chain}
    assert read["RC Baltimore"] == ["Spotlight Dallas", "the fortnight to 2026-09-06"]
    assert read["RC China"] == ["Spotlight Dallas", "the fortnight to 2026-09-06"]
    # One baseline, two readings of it: Baltimore and Dallas are both American
    # fields and the row holds the room, where China against the same event is
    # two metagames a week apart. The medium cannot tell the two rows apart.
    crossed = {entry["label"]: entry["cross_population"] for entry in chain}
    assert crossed["RC Baltimore"] is False and crossed["RC China"] is True
    # Order of configuration must not decide which of the two is the baseline.
    flipped = spotlight.chain(
        config.DB_PATH, spotlights=(BALTIMORE, CHINA, DALLAS), directory=tmp_path
    )
    assert [entry["label"] for entry in flipped] == [entry["label"] for entry in chain]
    assert all(
        "RC " not in row["against"] for entry in flipped for row in entry["comparisons"]
    )


def test_a_paper_event_seasons_back_is_not_a_baseline(tmp_path):
    """The paper row is the entry before, not the last one however far back.

    Amsterdam is six weeks and two closed fortnights before Brisbane. Read
    against it, the row would report a season's drift as one event's, and the
    fortnights in between would be the evidence it skipped over.
    """
    field = [_list(rank) for rank in range(1, 4)] + [_other(rank) for rank in range(4, 6)]
    _cache(tmp_path, AMSTERDAM, _payload(AMSTERDAM, field))
    _cache(tmp_path, BRISBANE, _payload(BRISBANE, [_list(rank) for rank in range(1, 12)]))

    _, brisbane = spotlight.chain(
        config.DB_PATH, spotlights=(AMSTERDAM, BRISBANE), directory=tmp_path
    )
    assert [row["against"] for row in brisbane["comparisons"]] == ["the fortnight to 2026-08-23"]


def test_a_round_with_no_standings_is_a_wait_rather_than_an_empty_event(monkeypatch):
    """Nought of nought rows pages to completion and caches an event of no lists.

    The site lists a round it has published no standings for and answers with an
    empty set rather than an error, which the paging arithmetic reads as a
    complete field. Left to it the fetch overwrites a good cache with an empty
    one and reports it in the same line it would report a real event.
    """
    monkeypatch.setattr(
        melee, "_standings_page", lambda *a, **k: {"recordsTotal": 0, "data": []}
    )
    with pytest.raises(melee.Unavailable, match="no standings"):
        melee.standings(405588, "1425471")


def _round_row(team, rank, wins, losses, draws, points, deck):
    """One standings row in the shape melee serves it, cut to what the fetch reads."""
    return {
        "TeamId": team,
        "Rank": rank,
        "MatchWins": wins,
        "MatchLosses": losses,
        "MatchDraws": draws,
        "Points": points,
        "Team": {"Players": [{"Username": f"player{team}"}]},
        "Decklists": [{"DecklistId": f"d{team}", "DecklistName": deck}],
    }


@pytest.fixture
def baltimore(monkeypatch):
    """An event whose last round was played and whose last standings never came.

    RC Baltimore's shape, cut to the two players it turns on: eighteen rounds
    listed, standings published through the Semifinals in one bulk write, and a
    Finals the page marks completed, carrying its match and no standings at all.
    """
    monkeypatch.setattr(melee.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        melee,
        "details",
        lambda _: {"Name": "RC Baltimore", "OrganizationName": "SCG", "StartDate": "2026-09-12"},
    )
    monkeypatch.setattr(melee, "decklist", lambda _: ({"Forest": 60}, {"Pithing Needle": 15}))
    monkeypatch.setattr(
        melee, "_listed", lambda _: [("1", "Round 15"), ("2", "Semifinals"), ("3", "Finals")]
    )
    semifinals = [
        _round_row(4357397, 1, 15, 1, 1, 40, "Devoted Druid Combo"),
        _round_row(4318405, 2, 14, 2, 1, 37, "Mono-Green Broodscale"),
    ]
    monkeypatch.setattr(
        melee,
        "_standings_page",
        lambda _t, round_id, *a, **k: (
            {"recordsTotal": 0, "data": []}
            if round_id == "3"
            else {"recordsTotal": len(semifinals), "data": semifinals}
        ),
    )
    monkeypatch.setattr(
        melee,
        "_matches_page",
        lambda _t, round_id, *a, **k: {
            "recordsTotal": 1,
            "data": [
                {
                    "HasResult": True,
                    "ResultString": "Pete Ingram won 2-1-0",
                    "Competitors": [
                        {"TeamId": 4357397, "GameWinsAndGameByes": 1},
                        {"TeamId": 4318405, "GameWinsAndGameByes": 2},
                    ],
                }
            ],
        }
        if round_id == "3"
        else {"recordsTotal": 0, "data": []},
    )
    return semifinals


def test_an_event_is_read_at_the_last_round_that_published_a_field(baltimore):
    """A listed round with no standings is read past rather than waited on.

    The old rule took the last round the page listed, so an organiser who
    published everything but the Finals blocked the fetch on an empty field.
    The field it wanted was already published one round back.
    """
    assert melee.final_round(405588) == ("2", "Semifinals", [("3", "Finals")])


def test_the_round_after_the_last_standings_is_folded_in_from_its_match(baltimore):
    """The finals was played and melee served the match; only the standings are missing.

    Read at the Semifinals alone the event says the deck that won came second,
    which is the one number a reader checks. The pairings grid carries who won,
    so the ranking is carried forward off the source rather than typed in: the
    winner takes the win and the better of the two ranks, and both finish 15-2-1.
    """
    payload = melee.tournament(405588)
    read = {row["pilot"]: (row["rank"], row["record"], row["points"]) for row in payload["lists"]}
    assert read["player4318405"] == (1, "15-2-1", 37)
    assert read["player4357397"] == (2, "15-2-1", 40)
    # Points stop at the end of the Swiss, so a playoff match moves the record
    # and the rank and nothing else. Said by the file, not only by the code.
    assert payload["tournament"]["round"] == "Semifinals"
    assert payload["tournament"]["advanced"] == ["Finals"]
    # Ranked order, the swap at the top having reordered the standings.
    assert [row["rank"] for row in payload["lists"]] == [1, 2]


def test_an_event_whose_last_round_published_its_standings_carries_nothing_forward(baltimore, monkeypatch):
    """The ordinary case, where the walk stops at the first round it looks at.

    Every event before Baltimore published the standings of its last round, and
    for those the match reader never runs: there is nothing after the round the
    field was read at.
    """
    monkeypatch.setattr(
        melee, "_standings_page", lambda _t, _r, *a, **k: {"recordsTotal": 2, "data": baltimore}
    )
    payload = melee.tournament(405588)
    assert payload["tournament"]["round"] == "Finals"
    assert payload["tournament"]["advanced"] == []
    assert [(row["rank"], row["record"]) for row in payload["lists"]] == [
        (1, "15-1-1"),
        (2, "14-2-1"),
    ]


def test_a_fortnight_holding_two_events_is_read_against_both_and_its_own_past(tmp_path):
    """The other direction of the chain, under the rule the event side reads by.

    A bin that held an event used to keep the event and drop the fortnight
    before it, so the fortnight to 2026-09-06 never said whether the MTGO field
    had moved on its own terms, and a bin holding two events kept one of them on
    a sort order. Both readings are kept, and the two rooms stay apart: pooled
    into a single baseline an American field and a Chinese one are a share
    neither of them reported.
    """
    _cache(tmp_path, CHINA, _payload(CHINA, [_list(rank) for rank in range(1, 16)]))
    _cache(tmp_path, BALTIMORE, _payload(BALTIMORE, [_list(rank) for rank in range(1, 26)]))

    from tracker import timeline

    rows = [
        row
        for row in timeline.findings(
            config.DB_PATH, config.REPORTS["blink"], spotlights=(CHINA, BALTIMORE), directory=tmp_path
        )
        if row["start"] == "2026-09-07"
    ]
    assert [row["against"] for row in rows] == [
        "the fortnight to 2026-09-06",
        "RC Baltimore",
        "RC China",
    ]
    # The fortnight reading is the one with no caveat on it, and it leads.
    assert [row["cross_population"] for row in rows] == [False, True, True]
    # Each row is the bin's own MTGO lists, never the bin pooled with an event.
    assert len({row["lists"] for row in rows}) == 1


def test_the_marks_inside_a_fortnight_are_not_repeated_under_every_baseline(tmp_path):
    """A mark says what happened in the bin, not what the bin was read against.

    Printed under all three rows, one ban enters the storyline three times and
    reads as three bans.
    """
    _cache(tmp_path, CHINA, _payload(CHINA, [_list(rank) for rank in range(1, 16)]))
    _cache(tmp_path, BALTIMORE, _payload(BALTIMORE, [_list(rank) for rank in range(1, 26)]))

    from tracker import timeline

    marks = [
        (row["against"], finding["text"])
        for row in timeline.findings(
            config.DB_PATH, config.REPORTS["blink"], spotlights=(CHINA, BALTIMORE), directory=tmp_path
        )
        if row["start"] == "2026-09-07"
        for finding in row["found"]
        if finding["kind"] == "event"
    ]
    assert len(marks) == len({text for _against, text in marks})


def test_a_retried_request_goes_up_shaped_like_the_first_one(monkeypatch):
    """A retry has to be the same call, or it is not a retry.

    The standings endpoint answers on `X-Requested-With` and `Referer`, and a
    retry that drops them is a differently shaped request asking a different
    question. It reached that state once by reading the headers inside the
    attempt loop, where the first attempt consumed them.
    """
    sent = []

    class _Response:
        status_code = 200

        def __init__(self, body):
            self.body = body

        def raise_for_status(self):
            pass

        def json(self):
            return self.body

    def _send(method, url, **kwargs):
        sent.append(kwargs.get("headers"))
        # Short on the first attempt, whole on the second: the shape `usable`
        # exists to retry through.
        return _Response({"data": []} if len(sent) == 1 else {"data": ["a row"]})

    monkeypatch.setattr(melee.SESSION, "request", _send)
    monkeypatch.setattr(melee.time, "sleep", lambda _: None)

    asked = {"X-Requested-With": "XMLHttpRequest", "Referer": "/Tournament/View/405588"}
    melee._request("POST", "/anything", lambda r: bool(r.json()["data"]), headers=asked)

    assert len(sent) == 2, "the short first answer was retried"
    assert sent[0] == asked
    assert sent[1] == asked, "the retry carried the headers the endpoint answers on"


# The novelty watchlist: cards the event's good finishers registered that the
# deck's own MTGO history has not been playing. Driven on a synthetic store
# rather than the live one, the reading resting on what MTGO never published and
# no captured history holding an absence disentangled from everything else the
# archetype was doing.


def _mtgo(day, pilots=20, cards=None):
    """One day's MTGO publication of the deck, as a league dump."""
    return synthetic.league(day, [synthetic.blink(f"p{day}{n}", cards=cards) for n in range(pilots)])


def _store(tmp_path, *days):
    """An MTGO store of the deck: the history a peak is read over."""
    db = tmp_path / "engine.duckdb"
    events = [_mtgo(day) for day in days or ("2026-07-14",)]
    store.build(synthetic.write_cache(tmp_path / "raw", events), db)
    return db


def _field(count):
    """A paper field of the deck, ranked 1 to `count`."""
    return [_list(rank) for rank in range(1, count + 1)]


def test_a_card_the_good_finishers_play_and_the_deck_does_not_is_a_watchlist_row(tmp_path):
    """The reading the project had no shape for: a card is concentrated in the
    lists that finished well, and the deck it belongs to has not been playing it.

    No existing gate can reach it. Adoption wants a fifth of the population to
    move, which by the time it fires makes the card established rather than new;
    the return gates want the card to have been absent from MTGO entirely. A
    card four of the twenty good finishers registered and almost nobody else did
    is neither, and it is the thing a pilot reads off a standings page by eye.
    """
    db = _store(tmp_path)
    field = _field(100)
    for row in field[:4]:
        row["side"] = {"Ghost Vacuum": 2}
    melee_dir = _cache(tmp_path / "melee", BRISBANE, _payload(BRISBANE, field))

    entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=melee_dir)

    assert [(row["kind"], row["card"], row["zone"]) for row in entry["novelties"]] == [
        ("novelty", "Ghost Vacuum", "side")
    ]


def test_a_card_the_whole_room_is_playing_is_not_a_novelty(tmp_path):
    """Most of the good finishers playing a card is mostly the deck playing it.

    Without the concentration bar the reading reports the deck's own staples
    every time, a card in half the field being in about half of any slice of it.
    What earns a row is the card that sits with the good finishers and not with
    the rest, which is a smaller number on a far smaller denominator.
    """
    db = _store(tmp_path)
    field = _field(100)
    # Over half the room, and so over half the cut: a staple of this field.
    for row in field[:12] + field[20:63]:
        row["side"] = {"Damping Sphere": 2}
    # And a card only the good finishers registered.
    for row in field[:4]:
        row["side"] = {**row["side"], "Ghost Vacuum": 2}
    melee_dir = _cache(tmp_path / "melee", BRISBANE, _payload(BRISBANE, field))

    entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=melee_dir)

    # The staple is 12 of the 20 good finishers, a bigger number than the card
    # that prints, and it is the one the reading refuses.
    assert [row["card"] for row in entry["novelties"]] == ["Ghost Vacuum"]


def test_the_mtgo_bar_is_read_in_the_zone_the_event_played_the_card(tmp_path):
    """A sideboard staple turning up in mainboards is a decision somebody made.

    Read over both boards at once it is a card the deck plays, and the reading
    would never see the move. A sideboard churns far harder than a mainboard,
    which is why the return gates are per zone too: the same card sideboarded
    again is the deck doing what it does.
    """
    # Every MTGO list of the deck sideboards Consign to Memory, and none mains it.
    db = _store(tmp_path)

    mained = _field(100)
    for row in mained[:4]:
        row["main"] = {**row["main"], "Consign to Memory": 2}
    sided = _field(100)
    for row in sided[:4]:
        row["side"] = {"Consign to Memory": 2}

    def watchlist(field, where):
        directory = _cache(tmp_path / where, BRISBANE, _payload(BRISBANE, field))
        entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=directory)
        return [(row["card"], row["zone"]) for row in entry["novelties"]]

    assert watchlist(mained, "mained") == [("Consign to Memory", "main")]
    assert watchlist(sided, "sided") == []


def test_the_cut_is_a_share_of_the_field_and_never_a_rank(tmp_path):
    """Rank 30 is the top of a fifty-seat room and the middle of a two-fifty one.

    The objection this module raises against reading rank between events, put to
    the cut itself. A fixed top 64 is the top 17.7% of Pro Tour Amsterdam and
    the top 4.3% of RC Baltimore, so the same three lists would be good
    finishers at one event and unremarkable at the other, and the reading would
    print four times as readily at the small one.
    """
    db = _store(tmp_path)

    def watchlist(seats, where):
        field = _field(seats)
        # The same three ranks in both rooms, and nothing else about them differs.
        for row in field[29:32]:
            row["side"] = {"Ghost Vacuum": 2}
        directory = _cache(tmp_path / where, BRISBANE, _payload(BRISBANE, field))
        entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=directory)
        return [row["card"] for row in entry["novelties"]]

    # Ranks 30 to 32 of fifty seats are past the top fifth and are nobody's good
    # finish; of two hundred and fifty they are inside it.
    assert watchlist(50, "small") == []
    assert watchlist(250, "big") == ["Ghost Vacuum"]


def test_two_of_the_good_finishers_are_not_evidence_of_anything(tmp_path):
    """The floor that decides whether the reading is worth reading at all.

    At two lists it prints seven rows an event across the tracked decks against
    two at three, for a claim resting on two pilots. Ketramose, the New Dawn at
    RC Baltimore is 2 of that deck's 12 good finishers and is the case that
    raised this reading; it is refused here, and correctly (Alejandro,
    2026-09-14).
    """
    db = _store(tmp_path)

    def watchlist(pilots, where):
        field = _field(100)
        for row in field[:pilots]:
            row["side"] = {"Ghost Vacuum": 2}
        directory = _cache(tmp_path / where, BRISBANE, _payload(BRISBANE, field))
        entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=directory)
        return [row["card"] for row in entry["novelties"]]

    assert watchlist(2, "two") == []
    assert watchlist(3, "three") == ["Ghost Vacuum"]


def test_a_card_the_adoption_reading_already_reports_does_not_print_twice(tmp_path):
    """One decision earns one row, which is why the migration fold exists too.

    A card that swung a fifth of the population is a move the field made, and
    that is the stronger claim of the two. Printed beside a watchlist row it
    reads as two findings about one card, and the weaker one says nothing the
    stronger did not.
    """
    # The fortnight Brisbane is read against, and it had never seen the card.
    db = _store(tmp_path, "2026-08-12")
    field = _field(100)
    # Three tenths of the event, and most of its good finishers: over the
    # adoption bar and over the concentration one at the same time.
    for row in field[:12] + field[40:58]:
        row["side"] = {"Ghost Vacuum": 2}
    melee_dir = _cache(tmp_path / "melee", BRISBANE, _payload(BRISBANE, field))

    entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=melee_dir)

    adopted = [row for row in entry["found"] if row["card"] == "Ghost Vacuum"]
    assert adopted and "climbed" in adopted[0]["text"]
    assert entry["novelties"] == []


def test_the_mtgo_bar_is_read_over_fortnights_that_closed(tmp_path):
    """The fortnight an event falls in has not finished, and is not a fortnight yet.

    `chain` already reads its MTGO baseline off the last bin that closed, for
    the reason every other reading here is cut off at a settled period: a bin
    part way through holds a few days of publication, and a share taken over it
    is a share of whatever happened to have been published by the Friday.

    Read into that open bin the novelty bar inverts. One list of two registering
    a card reads as half the deck playing it, so the card is refused as
    something the deck knows, and the thinner the open bin the more certainly it
    silences the row. Two of the six rows the reading found over the cached
    events were being lost exactly this way.
    """
    # A closed fortnight of twenty lists that never registered the card, and two
    # lists published after it closed, one of which did.
    db = tmp_path / "engine.duckdb"
    store.build(
        synthetic.write_cache(
            tmp_path / "raw",
            [
                _mtgo("2026-08-12"),
                _mtgo("2026-08-26", pilots=1, cards={"Ghost Vacuum": (0, 2)}),
                _mtgo("2026-08-27", pilots=1),
            ],
        ),
        db,
    )
    field = _field(100)
    for row in field[:4]:
        row["side"] = {"Ghost Vacuum": 2}
    melee_dir = _cache(tmp_path / "melee", BRISBANE, _payload(BRISBANE, field))

    entry, = spotlight.chain(db, spotlights=(BRISBANE,), directory=melee_dir)

    # Half of the open bin, and none of the fortnight that closed.
    assert [row["card"] for row in entry["novelties"]] == ["Ghost Vacuum"]
