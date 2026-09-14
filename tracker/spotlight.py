"""The paper Spotlight readings: where the deck finished, and how it won.

A Spotlight is not a big challenge and is not read as one. Two differences drive
everything here.

The first is the denominator. A challenge publishes its top 32, so every MTGO
share in this project is a share of a cut and is already performance-weighted. A
Spotlight publishes every finisher, so a share of its field is a true metagame
share and its top 32 is a separate, smaller reading. The two quantities are not
interchangeable and never share an axis: the only number that can sit beside a
weekly figure is the Spotlight's own top-32 share, and it carries an n of a
handful.

The second is that rank is not comparable between events. Dallas seated 932 and
Brisbane 574, so rank 300 is the top third of one and past the halfway mark of
the other. Every positional reading here is therefore a share of the field the
list actually beat, which is the same quantity at both events, and the null is
explicit: a deck that performed exactly like the field is the diagonal.

Match record is read from the wins and losses melee publishes and never from
points, because points stop accruing at the top cut. A pilot who won the event
holds fewer points than the Swiss leader and three more match wins, and points
would score that as the worse tournament.

Lists here are classified by the same `classify` rule the MTGO path uses, on
mainboards normalised by `melee.front_face`. They are never loaded into the
store: the challenge-class readings are defined as every event class except
league, so a Spotlight landing in `decklists` would be counted as challenge-class
by default and nine hundred paper lists would swamp a weekly field of four
hundred.
"""

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

from . import classify, config, store, timeline

# The band a Spotlight is read against the weekly report on. Thirty-two because
# that is what a challenge publishes, so it is the one slice of a paper event
# whose share means the same thing as `chal_share` does.
CUT = 32


def placing(rank: int, seats: int) -> float:
    """A finish as the share of the field that placed above it: 0 is the winner.

    The positional unit, written once and read twice: the series the positional
    panel plots, and the cut a novelty is read over. Two call sites computing it
    apart is one refactor away from a cut that no longer means what the panel
    shows. Over the seats rather than the published lists, for the reason
    `reading` gives where it takes the series.
    """
    return (rank - 1) / seats


def cached(spotlight: dict, directory: Path | None = None) -> Path:
    """Where a Spotlight's fetched payload lives."""
    return (directory or config.MELEE_DIR) / f"{spotlight['id']}.json"


def load(spotlight: dict, directory: Path | None = None) -> dict:
    """A Spotlight's payload, as fetched."""
    return json.loads(cached(spotlight, directory).read_text(encoding="utf-8"))


def week(spotlight: dict) -> str:
    """The Monday keying the week the Spotlight fell in.

    Keyed by its Monday and shown by its Sunday, exactly as every other weekly
    reading is, so a Spotlight sits on the report's own calendar rather than
    beside it. Brisbane on Saturday 29 August is the week ending 30 August.
    """
    day = date.fromisoformat(spotlight["date"])
    return (day - timedelta(days=day.weekday())).isoformat()


def closed(spotlight: dict) -> str:
    """The Sunday the event's week ended: where it sits among the fortnights.

    The storyline is ordered on the day each period closed, so an event has to
    carry one, and a paper event's period is its week.
    """
    return (date.fromisoformat(week(spotlight)) + timedelta(days=6)).isoformat()


def unread(entry: dict) -> bool:
    """Whether a published list's boards plainly failed to separate.

    Melee groups a decklist page under type headings and `melee.boards` splits
    on the heading, so a sideboard filed under one the fetch does not know puts
    the whole 75 in the mainboard. Read that way a list gains every card it
    only sideboarded, and membership is a mainboard test: a list sideboarding
    Ephemerate would join the archetype on a parse failure.

    A mainboard past 60 with no sideboard at all is that failure and not a legal
    registration. Melee's own history has four, at 69, 75, 76 and 146 cards, none
    of them near membership; a list on 60 with an empty sideboard is a pilot who
    registered no sideboard and is read normally.

    Those four are dropped and the reason recorded, never recovered by hand
    (Alejandro, 2026-09-13). Refetching the three known that day returned type
    headings and no sideboard heading, so the merge is how melee published them
    and not something this fetch can fix. Two of them are a meme or a
    corrupt registration (146 Plains, a 76-card five-colour pile) and splitting
    the rest by hand would put a hand-read 75 in a population every other list
    of which the fetch split.

    Counted rather than dropped silently, so the report says what the field
    published rather than an archetype quietly shedding lists. A rising count
    means melee merged another registration, which says nothing about this
    engine.
    """
    return not entry["side"] and sum(entry["main"].values()) > 60


def _decklist(
    entry: dict, colours: dict[str, frozenset[str]] | None, land_names: frozenset[str]
) -> SimpleNamespace:
    """One published paper list in the shape the membership rules read.

    Melee publishes a list's cards and nothing else, so the colours and the land
    types come off the store, which is MTGO's reading of the same names.
    """
    return SimpleNamespace(
        mainboard=entry["main"], colours=colours or {}, land_names=land_names
    )


def members(
    payload: dict,
    archetype: str = "blink",
    camp: str | None = "esper",
    colours: dict[str, frozenset[str]] | None = None,
    land_names: frozenset[str] = frozenset(),
) -> list[dict]:
    """The Spotlight's lists that answer to the deck's rule, in finishing order.

    `camp` of None pools every camp, which is what the presence and paper
    figures want. The build readings pass the report's camp, for the reason
    `store.population` gives.

    `colours` and `land_names` are what MTGO has published for the same names,
    read off the store, because melee publishes a list's cards and nothing
    else and the splash line has to read a paper list as it reads an MTGO one.

    The rule and not the name melee publishes. A decklist name is typed by its
    pilot: this field carried "Esper Blink", "Azorius Blink" and a bare "Esper"
    for the same seventy-five, and carried "Esper Blink" for lists that are not
    the deck. Membership is the mainboard, tested by `classify`, or the paper
    numbers would answer to a different question from the MTGO ones.
    """
    found = []
    for entry in payload["lists"]:
        if unread(entry):
            continue
        decklist = _decklist(entry, colours, land_names)
        name = classify.archetype(decklist)
        if name != archetype:
            continue
        if camp is not None and classify.variant(name, decklist) != camp:
            continue
        found.append(entry)
    return sorted(found, key=lambda row: row["rank"])


def version_boundary(
    db_path: Path = config.DB_PATH,
    spotlights: tuple[dict, ...] | None = None,
    directory: Path | None = None,
) -> list[dict]:
    """Every paper list sitting in its deck's default version whose mainboard is a named version's.

    The boundary the store prints, read where the store cannot see: a rule gap
    only paper shows is invisible to anything computed from MTGO. The two Pro
    Tour Broodscale lists that raised the reading are the case. They cast red off
    Lightning Bolt, which their Grove of the Burnwillows and Karplusan Forest
    paid for, where the Gruul rule of the day named only Unholy Heat and
    Writhing Chrysalis; they sit in `data/raw-melee`, which `store.build` never
    reads, and no MTGO Broodscale list has ever registered Lightning Bolt, so
    nothing computed from the store could reach them. The ruling of 2026-09-13
    named the card and closed that gap: this is the reading that would have
    raised it.

    Markers off MTGO and lists off the event, which pools no population. A card
    is a marker because `config.VERSION_MARKER_SHARE` of a named version's
    lists hold it, and one event's field cannot carry that bar: Pro Tour
    Amsterdam's mono-green Broodscale population is 9 lists, so its two lists
    casting red read as a fifth of the version rather than as two lists, which
    is over the bar that disqualifies a marker. So MTGO says what a marker is
    and the event says which of its lists carry one, and no denominator here
    counts a paper list beside an MTGO one.

    Read as `members` reads: the cards melee publishes, given the colours and
    the land types MTGO has published for the same names, because a paper list
    has to answer to the rule an MTGO list answers to.
    """
    markers = store.version_markers(db_path)
    colours, typed = store.card_colours(db_path), store.land_names(db_path)
    rows = []
    for spot in spotlights or config.MAJOR_EVENTS:
        if not cached(spot, directory).exists():
            continue
        for entry in load(spot, directory)["lists"]:
            if unread(entry):
                continue
            decklist = _decklist(entry, colours, typed)
            deck = classify.archetype(decklist)
            if deck not in markers:
                continue
            if classify.variant(deck, decklist) != config.TRACKED_DECKS[deck]["variant_default"]:
                continue
            rows += [
                {
                    "event": spot["label"],
                    "date": spot["date"],
                    "rank": entry["rank"],
                    "pilot": entry["pilot"],
                    "archetype": deck,
                    "version": version,
                    "kind": kind,
                    "marker": marker,
                }
                for version, kind, marker in classify.markers_held(markers[deck], decklist)
            ]
    return rows


def _rate(rows: list[dict]) -> tuple[float | None, int, int, int]:
    """Pooled match win rate over the lists given, and the record it came from."""
    wins = sum(row["wins"] for row in rows)
    losses = sum(row["losses"] for row in rows)
    draws = sum(row["draws"] for row in rows)
    played = wins + losses + draws
    return (wins / played if played else None), wins, losses, draws


def reading(
    payload: dict,
    archetype: str = "blink",
    camp: str | None = "esper",
    colours: dict[str, frozenset[str]] | None = None,
    land_names: frozenset[str] = frozenset(),
) -> dict:
    """Everything the report says about one Spotlight.

    `field_share` is the true metagame share the MTGO data cannot produce, and
    `cut_share` is the like-for-like one it can. `conversion` is the ratio of the
    two: above one, the deck held more of the top 32 than of the field, which is
    the honest performance number and is comparable between events of different
    size. `placings` is each list's finish as the share of the field above it,
    which is what makes two fields of different size one axis.
    """
    lists = payload["lists"]
    field = len(lists)
    seats = payload["tournament"]["players"]
    ours = members(payload, archetype, camp, colours, land_names)
    cut = [row for row in ours if row["rank"] <= CUT]
    rate, wins, losses, draws = _rate(ours)
    field_rate, *_ = _rate(lists)
    return {
        "id": payload["tournament"]["id"],
        "name": payload["tournament"]["name"],
        "players": payload["tournament"]["players"],
        "field": field,
        "lists": len(ours),
        "field_share": len(ours) / field if field else 0.0,
        "cut_lists": len(cut),
        "cut_share": len(cut) / CUT,
        "conversion": (len(cut) / CUT) / (len(ours) / field) if ours and field else None,
        "best": ours[0]["rank"] if ours else None,
        # The event's own headline: who finished, named, in finishing order. A
        # Spotlight is the biggest tournament of its era and the summary leads
        # its paper paragraph with the finishes rather than with a share, so the
        # names and records belong in the reading instead of being read off the
        # standings by hand. The lists that made the cut, or the best one where
        # none did.
        "top": [
            {"rank": row["rank"], "pilot": row["pilot"], "record": row["record"]}
            for row in (cut or ours[:1])
        ],
        "win_rate": rate,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "field_win_rate": field_rate,
        # Published, in the field and in every denominator here, but not testable
        # for membership. See `unread`.
        "unread": sum(1 for row in lists if unread(row)),
        # Each finish as the share of the field that placed above it: 0 is the
        # winner, 0.5 the middle of the room. In these units a field of 932 and a
        # field of 574 are one axis, and a deck whose lists are spread evenly
        # through the standings plots as the diagonal, which is the null every
        # positional reading here is against.
        #
        # Over the seats and not over the published lists, which are the
        # denominator every other figure here uses. A rank is a position among
        # entrants and an entrant can register no decklist, so Dallas ranks to
        # 932 over 928 lists and Brisbane to 573 over 571. Divided by the lists
        # the bottom of those two fields plots past 1.0, which is where the
        # diagonal closes and past which the panel has no room.
        "placings": sorted(placing(row["rank"], seats) for row in ours),
    }


def mtgo_lists(db_path: Path, archetype: str, camp: str | None, start: str, end: str) -> list[dict]:
    """The MTGO lists of the population published between two days, boards apart.

    Shaped like a Spotlight's own lists so one comparison serves both sides of
    the chain: the first Spotlight is read against MTGO and the next against the
    Spotlight before it.
    """
    registered, _ = timeline._history(db_path, archetype, camp)
    boards: dict[int, dict] = {}
    for row in registered:
        if not start <= row["date"] <= end:
            continue
        entry = boards.setdefault(row["list_id"], {"main": {}, "side": {}})
        zone = "main" if row["main"] > 0 else "side"
        entry[zone][row["card"]] = row["main"] if zone == "main" else 1
    return list(boards.values())


def mtgo_peaks(
    db_path: Path, archetype: str, camp: str | None, before: str
) -> dict[tuple[str, str], float]:
    """Per card and zone, the largest share of any MTGO fortnight ever to hold it.

    What tells a card the deck has not been playing from one it has, and the one
    bar in the novelty reading that is not read off the event. The whole store
    and not the post-regime window, for the reason `timeline._history` gives:
    how much of the deck a card has ever been is a fact about the deck rather
    than about the regime.

    Per zone, because a sideboard churns far harder than a mainboard, which is
    the same reason the return gates are per zone. A sideboard staple turning up
    in mainboards is a decision somebody made; the same card sideboarded again
    is the deck doing what it does.

    Over the fortnights that closed before the event and never the one it falls
    in, which is the baseline rule `chain` already reads its MTGO comparison by.
    A bin part way through holds a few days of publication, and a share taken
    over it is a share of whatever happened to have been published by the
    Friday. Read into it the bar inverts: one list of two registering a card
    reads as half the deck playing it, so the card is refused as something the
    deck knows, and the thinner the open bin the more certainly it silences the
    row. Two of the rows the reading finds over the cached events were lost this
    way, Salvage Titan in Affinity and Sunbaked Canyon in Boros Energy, both at
    Spotlight Dallas.

    Cutting at a closed bin also fixes the row: what an event earned does not
    change as the fortnight it fell in fills up. A report whose past changes
    under it is a report nobody can cite.
    """
    registered, lists = timeline._history(db_path, archetype, camp)
    last = timeline.bin_of(before) - 1
    sizes = Counter(
        index for index in (timeline.bin_of(row["date"]) for row in lists) if index <= last
    )
    held: dict[tuple[str, str], Counter] = {}
    for row in registered:
        index = timeline.bin_of(row["date"])
        if index <= last:
            held.setdefault((row["card"], row["zone"]), Counter())[index] += 1
    return {key: max(n / sizes[i] for i, n in bins.items()) for key, bins in held.items()}


def novelty_row(
    card: str, zone: str, n: int, cut_size: int, over: int, size: int, peak: float
) -> dict:
    """A card concentrated in the event's good finishers, phrased as a watchlist.

    Not a finding that the field moved, and worded so it cannot be read as one:
    every other card row in this project names a change, and this one names a
    question for the pilot. It carries both slices of the room it was read over
    and the MTGO bar it cleared, a share off a handful of good finishers being a
    figure nobody should read without seeing the handful.
    """
    return {
        "kind": "novelty",
        "zone": zone,
        "card": card,
        "text": f"{card} to watch in the {zone}board: {n} of the {cut_size} lists in the top "
        f"{config.TRACK_NOVELTY_CUT_SHARE:.0%} ({n / cut_size:.0%}), against {over} of {size} "
        f"over the event ({over / size:.0%}), and no MTGO fortnight above {peak:.0%}",
    }


def novelties(payload: dict, ours: list[dict], peaks: dict[tuple[str, str], float]) -> list[dict]:
    """Cards the event's good finishers registered that the deck has not been playing.

    The reading no other one here makes. Adoption wants a fifth of the
    population to move, so a card it reports is established rather than new, and
    the return reading is a claim about one population's history that a paper
    field cannot carry. What a pilot actually reads off a standings page is
    neither: a card sitting with the lists that finished well and not with the
    rest of the deck.

    Three conditions, each dropping a different false one. The card is held by
    `TRACK_NOVELTY_MIN_LISTS` of the cut, so the row does not rest on two
    pilots. No fortnight of the deck's MTGO history has held it above
    `TRACK_NOVELTY_PEAK` in that zone, which is what makes it novel rather than
    merely present. And it holds `TRACK_NOVELTY_CONCENTRATION` times as much of
    the cut as of the deck's own field at the event, without which the row
    reports whatever the whole room is playing.

    The cut is a share of the field and never a rank, read by the same quantity
    `reading`'s `placings` takes: a fixed rank is a four times different quality
    bar across the events already configured. The concentration baseline is the
    deck's own lists at this event and nothing else, so the row never crosses
    two populations: one room, two slices of it.
    """
    seats = payload["tournament"]["players"]
    cut = [row for row in ours if placing(row["rank"], seats) < config.TRACK_NOVELTY_CUT_SHARE]
    among, over = _held(cut), _held(ours)
    rows = []
    for (card, zone), copies in sorted(among.items()):
        n, peak = len(copies), peaks.get((card, zone), 0.0)
        event_wide = len(over.get((card, zone), []))
        if n < config.TRACK_NOVELTY_MIN_LISTS or peak > config.TRACK_NOVELTY_PEAK:
            continue
        if n / len(cut) < (event_wide / len(ours)) * config.TRACK_NOVELTY_CONCENTRATION:
            continue
        rows.append(novelty_row(card, zone, n, len(cut), event_wide, len(ours), peak))
    return rows


def chain(
    db_path: Path,
    report: dict | None = None,
    spotlights: tuple[dict, ...] | None = None,
    directory: Path | None = None,
) -> list[dict]:
    """Each Spotlight's reading and findings, in the order they were played.

    Two populations, as everywhere else in the report. The numbers are the whole
    archetype's, a metagame share of a paper field being the one quantity MTGO
    cannot produce and no use read on a third of the deck. The findings are the
    report's camp's, and the chain they are read along is that camp's too.

    Every event is read against the last closed MTGO fortnight, and against the
    paper event before it where one was played no earlier than that fortnight
    opened. Both and not one of the two: they answer different questions over
    the same stretch of time, and the earlier rule kept only the paper one where
    it existed, so an event that followed another lost its MTGO baseline
    entirely. The paper row holds the medium constant and is the stronger of the
    two; the MTGO row is the one that says whether the field the deck came from
    had already moved. They are ordered strongest first and each says what it
    read against, because a reader given one number cannot tell which it was.

    No event is read against one played in its own week. Two Regional
    Championships on one weekend are two rooms rather than a before and an
    after, and reading either against the other would report the distance
    between two fields as a fortnight's worth of change.

    A major event is not a separate story that may only be compared with other
    major events: MTGO moves what pilots take to a Pro Tour and a Pro Tour moves
    what turns up on MTGO after it. So the chain runs through the event in both
    directions: the event is read against what came before it here, and the
    fortnight it fell in is read against the event in `timeline.findings`.

    Each entry is one room and never a blend of two. A paper event is never
    folded into a fortnight's own numbers: its week sits inside a fortnight
    rather than beside one, and pooled it would be most of the bin.

    A row spanning two rooms is a cross-population reading and says so. The
    Australian field, the American field, the Chinese field and the MTGO field
    are four populations, so a card at nine tenths of one and half of another is
    not the deck changing its mind. Which room an event drew from is its
    configured `region`, and a row against MTGO crosses regardless. Paper
    against paper was taken as one room on the medium alone until 2026-09-14,
    which marked China against Dallas as the same field.

    The paper row still leads. It crosses at most one of the two things that
    make a reading weaker, the room, where the MTGO row crosses both the room
    and the medium, so it remains the stronger of the two whether or not the
    regions match.
    """
    report = report or config.REPORTS["blink"]
    archetype, build = report["archetype"], report["camp"]
    # Sorted rather than taken as configured, because which event precedes which
    # is what the chain is, and two played on one day need a settled order.
    played = sorted(spotlights or config.MAJOR_EVENTS, key=lambda s: (s["date"], s["label"]))
    typed = store.land_names(db_path)
    colours = store.card_colours(db_path)
    entries = []
    ours_of: dict[int, list[dict]] = {}
    for position, spot in enumerate(played):
        payload = load(spot, directory)
        ours = ours_of[spot["id"]] = members(payload, archetype, build, colours, typed)
        index = timeline.bin_of(spot["date"]) - 1
        start = timeline.bin_start(index)
        end = (
            date.fromisoformat(start) + timedelta(days=config.TRACK_BIN_DAYS - 1)
        ).isoformat()
        comparisons = []
        # The paper entry before this one: the latest event of an earlier week,
        # and only where it was played no earlier than the fortnight below it
        # opened. Further back than that the two sides span different stretches
        # of the season, and the row would report a quarter's drift as an
        # event's. An event of this event's own week is no part of it.
        earlier = [s for s in played[:position] if week(s) < week(spot)]
        if earlier and closed(earlier[-1]) >= start:
            prior = earlier[-1]
            comparisons.append(
                {
                    "against": prior["label"],
                    "cross_population": prior["region"] != spot["region"],
                    "baseline_lists": len(ours_of[prior["id"]]),
                    "found": findings(ours, ours_of[prior["id"]], report, typed),
                }
            )
        fortnight = mtgo_lists(db_path, archetype, build, start, end)
        comparisons.append(
            {
                "against": f"the fortnight to {end}",
                "cross_population": True,
                "baseline_lists": len(fortnight),
                "found": findings(ours, fortnight, report, typed),
            }
        )
        # Suppressed where an ordinary reading already reports the card in this
        # entry. A card the adoption or watched-slot reading caught is a move the
        # field made, which is the stronger claim, and printed twice it reads as
        # two findings about one card.
        reported = {row["card"] for comparison in comparisons for row in comparison["found"]}
        watchlist = [
            row
            for row in novelties(
                payload, ours, mtgo_peaks(db_path, archetype, build, spot["date"])
            )
            if row["card"] not in reported
        ]
        entries.append(
            {
                **reading(payload, archetype, None, colours, typed),
                "label": spot["label"],
                "date": spot["date"],
                "week": week(spot),
                # The constructed format, where the event played more than one.
                # Everything positional on such a row carries the rounds it was
                # not played in.
                "constructed": payload["tournament"].get("format"),
                "build_lists": len(ours),
                # Strongest first, and the strongest is also what the summary
                # clause and the paper section quote, so it is spread here
                # rather than copied: one comparison, not two that can drift.
                **comparisons[0],
                "comparisons": comparisons,
                # Read against no baseline at all, so it is no part of the
                # comparisons above: a watchlist is a claim about this room
                # against the deck's own history, not about a move between two.
                "novelties": watchlist,
            }
        )
    return entries


def _held(rows: list[dict]) -> dict[tuple[str, str], list[int]]:
    """Card and zone to the mainboard copies of the lists registering it.

    A card in the mainboard counts as mainboard and not as both, even where the
    list also sideboards it. That is the store's own rule, and the two sides of
    a comparison have to answer to one: melee publishes the boards separately,
    so a card split three and two across them would count once on the MTGO side
    and twice here, and every split card would read as a sideboard adoption.
    """
    held: dict[tuple[str, str], list[int]] = {}
    for row in rows:
        for card, copies in row["main"].items():
            held.setdefault((card, "main"), []).append(copies)
        for card in row["side"]:
            if card not in row["main"]:
                held.setdefault((card, "side"), []).append(0)
    return held


def _moved(n: int, size: int, was: int, was_size: int) -> bool:
    """Whether a share moved far enough to be a row, at two unequal sizes.

    The fortnight's own count gate does not transfer here and quietly inverts. A
    Spotlight of eleven lists against a fortnight of a hundred and twelve is a
    tenfold difference in population, and there the difference in raw counts is
    mostly that: eleven lists holding a card at a third and a hundred and twelve
    holding it at a seventh clears a five-list gate on the denominators alone,
    and every moderately played card in the field earns a row.

    `timeline.shifted` is that gate read the way it was meant, against the
    smaller population, and a thin Spotlight then reports little. Eleven lists
    cannot evidence a five-list change at anything under a forty-five point
    swing, and saying so beats printing three rows that are the sample size
    talking.
    """
    return timeline.shifted(n, size, was, was_size)


def findings(
    current: list[dict],
    baseline: list[dict],
    report: dict | None = None,
    land_names: frozenset[str] = frozenset(),
) -> list[dict]:
    """What the Spotlight's lists changed against the reading before it.

    Adoption, copies and the manabase. A return says a card the deck had stopped playing
    came back, which is a claim about one population's history over months, and a
    paper field is not that population: a card absent from MTGO for a month and
    present at Brisbane is the Australian field building differently, not the
    deck rediscovering anything.

    The thresholds are the fortnight's own, unchanged. They were calibrated on
    MTGO fortnights, so a Spotlight thin enough to clear the count gate on two
    pilots will produce noisy rows, and the caller says so rather than this
    silently raising the bar for paper.

    The manabase is read off `land_names`, the cards MTGO has typed as lands,
    because melee's fetch keeps the cards and not the type headings. A land no
    MTGO list has ever registered is therefore not counted, which at this
    deck's manabase is no land at all.
    """
    report = report or config.REPORTS["blink"]
    size, was_size = len(current), len(baseline)
    if not size or not was_size:
        return []
    held, was_held = _held(current), _held(baseline)
    watched = set(report["watch"])
    found = timeline.watched_rows(watched, held, was_held, size, was_size)
    found += timeline.copies_rows(held, was_held, size, was_size, watched)
    for (card, zone), copies in sorted(held.items()):
        n, was = len(copies), len(was_held.get((card, zone), []))
        if not (zone == "main" and card in watched) and _moved(n, size, was, was_size):
            found.append(timeline.adoption_row(card, zone, n, size, was, was_size))
    # A card the deck dropped entirely shows up in neither loop above, having no
    # row of its own in the current bin, so it is read from the baseline's side.
    for (card, zone), copies in sorted(was_held.items()):
        if (card, zone) in held or (zone == "main" and card in watched):
            continue
        if _moved(0, size, len(copies), was_size):
            found.append(timeline.adoption_row(card, zone, 0, size, len(copies), was_size))
    if report["manabase"] and land_names:
        found += timeline.manabase_rows(
            lands(current, land_names), lands(baseline, land_names), size, was_size
        )
    return _migrations(found, held, size)


def lands(rows: list[dict], land_names: frozenset[str]) -> dict[int, int]:
    """Lists by mainboard land count, the shape `timeline.manabase_rows` reads."""
    counts: dict[int, int] = {}
    for row in rows:
        count = sum(copies for card, copies in row["main"].items() if card in land_names)
        counts[count] = counts.get(count, 0) + 1
    return counts


def _migrations(found: list[dict], held: dict, size: int) -> list[dict]:
    """One card climbing in a board and falling in the other is one decision.

    It changed zone. Left as two rows it reads as the deck adopting a card and
    abandoning the same card in the same week, where promoting a sideboard
    staple is a decision about what the card is for and not the deck discovering
    it.

    The fortnight timeline does not fold these, and deliberately: its rows are
    frozen, so folding them now would leave one history phrased two ways with
    nothing in the file to say which rule a row answered to. A Spotlight is read
    fresh on every render and has no such history to contradict.
    """
    climbed = {row["card"] for row in found if row["zone"] == "main" and "climbed" in row["text"]}
    fell = {row["card"] for row in found if row["zone"] == "side" and "fell" in row["text"]}
    moved_zone = climbed & fell
    if not moved_zone:
        return found
    rows = [row for row in found if row["card"] not in moved_zone]
    for card in sorted(moved_zone):
        n = len(held[(card, "main")])
        rows.append(
            {
                "kind": "migration",
                "zone": "main",
                "card": card,
                "text": f"{card} moves to the mainboard, {n} of {size} lists ({n / size:.0%})",
            }
        )
    return rows
