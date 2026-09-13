"""The terminal surface, at the layer it decides what a reader is told.

The other surface has its own tests. This one is where the readings are turned
into the lines a pilot actually reads at the prompt, and a field the analysis
computed and this drops is a finding the engine took and never delivered. So
every test here is about what reaches the line, given a row the audit produced.

The rows are written rather than captured, because what is under test is the
display rule and not the arithmetic behind it: `store.arrivals` is tested on
the store it reads, and a row here is one of its answers held still.
"""

from tracker import cli, index


def _arrival(**over) -> dict:
    """One of the archetype's lists as `store.arrivals` returns it."""
    return {
        "pilot": "_must_be_nice",
        "event": "Modern League",
        "event_id": "modern-league-2026-08-0510847",
        "event_class": "league",
        "date": "2026-08-05",
        "placement": None,
        "swiss_points": None,
        "record": "5-0",
        "camp": "non-fallaji",
    } | over


def _row(**over) -> index.Row:
    return index.Row(
        date="2026-08-05",
        event_id="modern-league-2026-08-0510847",
        event_class="league",
        pilot="_must_be_nice",
        placement="",
        swiss_points="",
    )._replace(**over)


def test_an_ingest_counts_the_lists_it_brought_in_and_not_only_the_events():
    """The days hardest to speak about are the ones already cached.

    A league dump gains 5-0s through its own day, so the unsettled window
    overwrites captures the cache already held. Reporting events alone would say
    nothing arrived on exactly the day something did, which is the reading the
    index was kept for.
    """
    added = [_row(pilot=f"pilot{n}") for n in range(18)]
    line = cli._ingest_lines(index.Change(added, []), [_arrival()])[0]

    assert "18 new list(s)" in line
    assert "1 event(s)" in line, "one day, eighteen arrivals"
    assert "1 of them Goryo's" in line


def test_an_ingest_names_the_archetype_s_arrivals_and_leaves_the_field_a_number():
    """What the rest of the session is about is which Goryo's lists are new, so
    those are named. The field's hundreds are a count: naming them would bury
    the four lines that matter."""
    lines = cli._ingest_lines(
        index.Change([_row()], []),
        [_arrival(), _arrival(pilot="PTarts2win", event="Modern Challenge 64", placement=10)],
    )

    assert "5-0" in lines[1] and "_must_be_nice" in lines[1] and "non-fallaji" in lines[1]
    assert "#10" in lines[2] and "PTarts2win" in lines[2]


def test_a_run_that_brought_nothing_in_says_so_rather_than_printing_a_zero():
    assert cli._ingest_lines(index.Change([], []), []) == [
        "  no list published since the last run"
    ]


def test_lists_the_site_no_longer_publishes_are_said_out_loud():
    """A withdrawn event is not a gap and not an error, but lists leaving the
    history quietly is the same failure as lists arriving quietly."""
    lines = cli._ingest_lines(index.Change([], [_row(), _row(pilot="pepeteam")]), [])

    assert lines[-1] == "  2 list(s) the site no longer publishes"


def test_a_first_run_counts_the_history_it_filed_rather_than_reciting_it():
    """A first run's index was empty, so its arrivals are the whole history.

    That is not news and must not print as though it were. It is not nothing
    either, so what was dropped off the end is counted rather than left silent.
    """
    ours = [_arrival(pilot=f"pilot{n}") for n in range(cli.NAMED_ARRIVALS + 14)]
    lines = cli._ingest_lines(index.Change([_row()], []), ours)

    assert len(lines) == cli.NAMED_ARRIVALS + 2, "the count, the named, then the remainder"
    assert lines[-1] == "    and 14 more, further back"


def test_the_fall_out_prints_per_deck_and_per_reason_with_the_recent_count():
    """A deck adopting another deck's engine card shows up here as a count that
    grows week on week, so the line carries the fortnight's share of it."""
    rows = [
        {"archetype": "goryos", "reason": "persist", "pilot": "a", "event": "e", "date": "2026-09-10", "list_id": 1},
        {"archetype": "goryos", "reason": "persist", "pilot": "b", "event": "e", "date": "2026-07-01", "list_id": 2},
        {"archetype": "blink", "reason": "energy", "pilot": "c", "event": "e", "date": "2026-09-11", "list_id": 3},
    ]
    lines = cli._fallout_lines(rows, today="2026-09-13")

    assert lines[0] == "  3 list(s) holding a deck's core and turned away, 2 in the last 14 days"
    assert "  blink: energy 1 (1 recent)" in lines
    assert "  goryos: persist 2 (1 recent)" in lines


def test_no_fall_out_says_so():
    assert cli._fallout_lines([], today="2026-09-13") == ["  no list holding a deck's core was turned away"]


def _boundary(**over) -> dict:
    """One boundary case as `store.boundaries` returns it."""
    return {
        "archetype": "broodscale",
        "version": "gruul",
        "kind": "colour",
        "marker": "R",
        "pilot": "KarplusanKid",
        "event": "Modern Challenge 64",
        "date": "2026-09-11",
        "list_id": "modern-challenge-64-2026-09-1112849509#KarplusanKid",
    } | over


def test_the_version_boundary_names_the_lists_under_the_deck_and_version_they_disagree_with():
    """A count alone would say a rule has a gap without saying where to look.

    The boundary is read one list at a time, so the lists are named and each
    carries what says it is the other version: the colour its population is
    built in, or the card it holds.
    """
    lines = cli._version_boundary_lines(
        [
            _boundary(),
            _boundary(kind="card", marker="Devourer of Destiny", version="lab"),
            _boundary(pilot="ador", list_id="b", version="lab", kind="card", marker="Devourer of Destiny"),
        ]
    )

    assert lines[0] == "  2 list(s) sitting in a version their mainboard disagrees with"
    assert "  broodscale: 1 list(s) in mono-green that look gruul" in lines
    assert "  broodscale: 2 list(s) in mono-green that look lab" in lines
    assert "    2026-09-11  Modern Challenge 64        ador          on Devourer of Destiny" in lines
    assert "    2026-09-11  Modern Challenge 64        KarplusanKid  casts R" in lines


def test_a_deck_whose_versions_partition_cleanly_prints_a_zero_rather_than_going_unmentioned():
    """Absence and a clean reading are different answers, and a deck missing from
    the table is the first of them told as the second."""
    lines = cli._version_boundary_lines([_boundary()])

    assert "  blink: its versions partition cleanly" in lines
    assert "  zoo: its versions partition cleanly" in lines


def test_a_deck_the_boundary_does_not_read_is_not_reported_as_reading_clean():
    """The same confusion the other way up. Tron's versions are not read at all,
    every signal the check could raise there having been ruled a build, so
    calling it clean would report a deck nothing looked at as one nothing was
    found in."""
    assert not [line for line in cli._version_boundary_lines([_boundary()]) if "tron" in line]


def test_a_deck_of_one_population_has_no_boundary_to_print_and_is_left_out():
    """A deck with no versions has no default version to fall into, so there is
    nothing here to say about it either way."""
    lines = cli._version_boundary_lines([])

    assert not [line for line in lines if "affinity" in line or "neoform" in line]


# Two configured paper events, the shape `config.MAJOR_EVENTS` carries.
PAPER_EVENTS = (
    {"id": 434455, "label": "Pro Tour Amsterdam", "date": "2026-07-17"},
    {"id": 441441, "label": "Spotlight Brisbane", "date": "2026-08-29"},
)


def _paper(**over) -> dict:
    """One paper boundary case as `spotlight.version_boundary` returns it."""
    return {
        "event": "Pro Tour Amsterdam",
        "date": "2026-07-17",
        "rank": 12,
        "pilot": "KarplusanKid",
        "archetype": "broodscale",
        "version": "gruul",
        "kind": "colour",
        "marker": "R",
    } | over


def test_the_paper_boundary_names_the_lists_under_the_event_they_were_played_at():
    """A paper list is found on the standings page it finished in, so the event
    is what the lists are grouped under, and the rank is how one is looked up.

    The markers are the store's and the lists are the event's, so the count is
    the event's own and never a share: nothing here counts a paper list beside
    an MTGO one.
    """
    lines = cli._paper_boundary_lines(
        [
            _paper(),
            _paper(rank=44, pilot="ador"),
            _paper(rank=44, pilot="ador", version="lab", kind="card", marker="Devourer of Destiny"),
        ],
        PAPER_EVENTS,
    )

    assert "  Pro Tour Amsterdam: broodscale, 2 list(s) in mono-green that look gruul" in lines
    assert "  Pro Tour Amsterdam: broodscale, 1 list(s) in mono-green that look lab" in lines
    assert "    #12    KarplusanKid  casts R" in lines
    assert "    #44    ador          on Devourer of Destiny" in lines


def test_an_event_whose_lists_agree_with_their_versions_says_so_rather_than_going_unlisted():
    """The same distinction the MTGO table draws: an event missing from the
    reading is a clean event told as one nobody read, and the two are different
    answers. The events read are what this is handed, so an event among them
    that raised nothing is the first, and one nobody fetched is never passed."""
    lines = cli._paper_boundary_lines([_paper()], PAPER_EVENTS)

    assert "  Spotlight Brisbane: every list sits in a version its mainboard agrees with" in lines
