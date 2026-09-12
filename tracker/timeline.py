"""What changed in a tracked deck, fortnight by fortnight.

The plots are weekly and this is not, for one reason. A week of this deck runs
from nine published lists to sixty-four, so a threshold set as a share of the
week is measuring the sample size: at every bar from five points to twenty-five,
a change detected weekly reverses in the next week about two times in five, and
raising the bar loses findings without buying purity. Over a fortnight the same
bars reverse between fifteen and twenty-two percent of the time, and the rate
falls as the bar rises, which is what a threshold is supposed to do.

So a timeline row is a fortnight's row. The bins do not overlap, because
overlapping ones would report the same change twice and a reader cannot tell a
repeated finding from a continuing one. They are anchored at the regime boundary
rather than at today, so the bin a date falls in never moves and a row written
six weeks ago still describes the same fortnight. Bins before the boundary carry
negative indices and are never reported: they exist so that a card's history
reaches back past the boundary, which is what tells a return from a cold start.

Each row is read against the entry before it in the storyline, and a major paper
event is an entry. The fortnight an event falls in is therefore read against the
event's own lists and not against the fortnight before, and the event is read
against that fortnight (see `spotlight.chain`). MTGO moves what pilots take to a
Pro Tour and a Pro Tour moves what turns up on MTGO after it, and a chain that
skipped the event on the way back would report the response without the thing
it responded to.

Findings are written mechanically, from the numbers, in fixed forms. The
interpretation layer is the weekly summary written over the top of this; a row
that phrased itself differently on a later run would make the committed history
disagree with itself for no reason.
"""

import csv
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import duckdb

from . import config
from .store import _rows, land_names, population


def bin_of(day: str, since: str = config.REGIME_BOUNDARY) -> int:
    """The bin a day falls in. Negative before the boundary, by design."""
    offset = (date.fromisoformat(day) - date.fromisoformat(since)).days
    return offset // config.TRACK_BIN_DAYS


def bin_start(index: int, since: str = config.REGIME_BOUNDARY) -> str:
    """The first day of bin `index`."""
    return (date.fromisoformat(since) + timedelta(days=index * config.TRACK_BIN_DAYS)).isoformat()


def bin_end(index: int, since: str = config.REGIME_BOUNDARY) -> str:
    """The last day of bin `index`."""
    return (date.fromisoformat(bin_start(index + 1, since)) - timedelta(days=1)).isoformat()


def _history(db_path: Path, archetype: str, camp: str | None) -> tuple[list[dict], list[dict]]:
    """Every registration and every list of the population, over the whole store.

    The whole store and not the post-regime window, because whether a card has
    been out of the deck for a month is a fact about the deck rather than about
    the regime. Read over the window alone, every card of the opening fortnight
    reads as new and the timeline opens on an innovation burst that is really a
    cold start.
    """
    joined, args = population(archetype, camp, "d.")
    where, plain = population(archetype, camp)
    with duckdb.connect(db_path, read_only=True) as con:
        registered = _rows(
            con.execute(
                f"""
                SELECT c.list_id, c.card, c.main,
                       CASE WHEN c.main > 0 THEN 'main' ELSE 'side' END AS zone, d.date
                FROM decklists d JOIN configurations c USING (list_id)
                WHERE {joined} AND (c.main > 0 OR c.side > 0)
                """,
                args,
            )
        )
        lists = _rows(
            con.execute(f"SELECT list_id, date, lands FROM decklists WHERE {where}", plain)
        )
    return registered, lists


def events(path: Path = config.EVENTS_PATH) -> list[dict]:
    """The dated events a plot marks and a row names. Empty when none are kept."""
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return sorted(csv.DictReader(handle), key=lambda row: row["date"])


def adoption_row(card: str, zone: str, n: int, size: int, was: int, was_size: int) -> dict:
    """The deck took a card up or put it down, phrased once.

    Shared with the Spotlight readings rather than written twice, so a paper row
    and a fortnight row that found the same thing say it the same way.
    """
    share = n / size
    was_share = was / was_size if was_size else 0.0
    return {
        "kind": "adoption",
        "zone": zone,
        "card": card,
        "text": f"{card} {'climbed' if share > was_share else 'fell'} in the "
        f"{zone}board, {was}/{was_size} to {n}/{size} lists "
        f"({was_share:.0%} to {share:.0%})",
    }


def copies_row(card: str, zone: str, now: float, before: float) -> dict:
    """The deck kept a card and changed its mind about how many."""
    return {
        "kind": "copies",
        "zone": zone,
        "card": card,
        "text": f"{card} {'up' if now > before else 'down'} from "
        f"{before:.1f} to {now:.1f} copies on average",
    }


def copies_at_row(card: str, count: int, n: int, size: int, was: int, was_size: int) -> dict:
    """A watched slot at one copy count, as the share of lists registering it.

    The mean cannot answer the question a watched slot asks. Two copies going to
    three in a quarter of the camp moves a mean over eighty lists by a fifth of
    a copy, which no copies bar can see without seeing everything; the same
    decision read as a distribution is a fifth of the lists moving from one row
    to another, which is plainly a decision somebody made.
    """
    share = n / size
    was_share = was / was_size if was_size else 0.0
    return {
        "kind": "copies",
        "zone": "main",
        "card": card,
        "text": f"{card} at {count} cop{'y' if count == 1 else 'ies'} "
        f"{'climbed' if share > was_share else 'fell'}, {was}/{was_size} to "
        f"{n}/{size} lists ({was_share:.0%} to {share:.0%})",
    }


def lands_row(count: int, n: int, size: int, was: int, was_size: int) -> dict:
    """The camp moved its manabase, read at one land count."""
    share = n / size
    was_share = was / was_size if was_size else 0.0
    return {
        "kind": "manabase",
        "zone": "main",
        "card": f"{count} lands",
        "text": f"{count} lands {'climbed' if share > was_share else 'fell'}, "
        f"{was}/{was_size} to {n}/{size} lists ({was_share:.0%} to {share:.0%})",
    }


def moved(
    n: int, size: int, was: int, was_size: int, bar: float = config.TRACK_ADOPTION_DELTA
) -> bool:
    """Whether a share moved far enough, in both units, to be a row.

    The share is what makes a move large and the count is what makes it
    evidence, so a thin population cannot clear the bar on one pilot.

    `bar` is the share, and only a watched slot lowers it. See TRACK_WATCH_DELTA.
    """
    share = n / size
    was_share = was / was_size if was_size else 0.0
    return abs(share - was_share) >= bar and abs(n - was) >= config.TRACK_MIN_LISTS


def shifted(
    n: int, size: int, was: int, was_size: int, bar: float = config.TRACK_ADOPTION_DELTA
) -> bool:
    """Whether a share moved far enough to be a row, at two unequal sizes.

    `moved` above holds the evidence constant only while the two populations are
    about the same size. Two closed fortnights are; a closed fortnight and the
    one still filling are not, and neither is a Spotlight against a fortnight.
    There the difference in raw counts is mostly the difference in population,
    and a fortnight three days old clears a five-list gate on its denominator
    alone.

    So the gate is the same quantity read the way it was meant: the move has to
    be worth `TRACK_MIN_LISTS` in the smaller of the two populations, which is
    all the evidence there actually is.
    """
    share = n / size
    was_share = was / was_size if was_size else 0.0
    return abs(share - was_share) >= bar and (
        min(size, was_size) * abs(share - was_share) >= config.TRACK_MIN_LISTS
    )


def watched_rows(
    cards: set[str], held: dict, was_held: dict, size: int, was_size: int
) -> list[dict]:
    """What the camp did with the slots the report watches, by copy count.

    Both sides are `{(card, zone): [mainboard copies, one per list]}`, which is
    the shape a fortnight's own registrations and a Spotlight's lists both
    reduce to, so paper and MTGO ask this question once and phrase the answer
    the same way.

    Watched slots are read here and nowhere else, the ordinary adoption reading
    skipping them, so one decision earns one row. Two shapes, because two kinds
    of slot are watched. A card the camp only ever runs one number of is a
    presence decision and is phrased as one: saying "at 1 copy" about a card
    nobody runs two of is noise in the sentence. Anything else is phrased per
    count, that being the whole of what the pilot is asking.
    """
    rows = []
    for card in sorted(cards):
        now = Counter(held.get((card, "main"), []))
        was = Counter(was_held.get((card, "main"), []))
        if not now and not was:
            continue
        counts = sorted(set(now) | set(was))
        if len(counts) == 1:
            count = counts[0]
            n, before = now.get(count, 0), was.get(count, 0)
            if shifted(n, size, before, was_size, config.TRACK_WATCH_DELTA):
                rows.append(adoption_row(card, "main", n, size, before, was_size))
            continue
        for count in counts:
            n, before = now.get(count, 0), was.get(count, 0)
            if shifted(n, size, before, was_size, config.TRACK_WATCH_DELTA):
                rows.append(copies_at_row(card, count, n, size, before, was_size))
    return rows


def copies_rows(
    held: dict, was_held: dict, size: int, was_size: int, watched: set[str]
) -> list[dict]:
    """The staples whose mean copies moved, in the shape `watched_rows` reads.

    A staple is a mainboard card held by TRACK_STAPLE_SHARE of both sides, which
    is the slot the deck argues about the number of rather than the presence of
    and the only one a mean can answer for. Under that bar the mean moves when
    a different set of pilots arrives, and adoption already reports the
    arrival. Every staple, lands included: a change in any card of the deck is
    what the timeline is for. Watched slots are read by count elsewhere.
    """
    rows = []
    for (card, zone), copies in sorted(held.items()):
        before = was_held.get((card, zone), [])
        if zone != "main" or card in watched:
            continue
        if not (_staple(len(copies), size) and _staple(len(before), was_size)):
            continue
        now, was = sum(copies) / len(copies), sum(before) / len(before)
        if abs(now - was) >= config.TRACK_COPY_DELTA:
            rows.append(copies_row(card, zone, now, was))
    return rows


def _staple(n: int, size: int) -> bool:
    return n >= config.TRACK_MIN_LISTS and n / size >= config.TRACK_STAPLE_SHARE


def manabase_rows(now: dict, was: dict, size: int, was_size: int) -> list[dict]:
    """Whether the camp moved its manabase, land count by land count.

    Both sides are `{land count: lists on it}`, which a fortnight and a paper
    event both reduce to. A land count is a configuration of the list as a whole
    rather than of a card in it. Nothing in the weekly report read it that way,
    so a camp walking from 21 lands to 22 over a regime was invisible to it: the
    land added is a different card in every list, so no card's adoption moves
    and no card's copies move either.

    Read at the standard bar rather than the watched one. The values are few,
    a camp registering three or four land counts in a fortnight, so this is not
    the scan over a hundred cards that the finer bar exists to refuse.
    """
    rows = []
    for count in sorted(set(now) | set(was)):
        n, before = now.get(count, 0), was.get(count, 0)
        if shifted(n, size, before, was_size):
            rows.append(lands_row(count, n, size, before, was_size))
    return rows


def findings(
    db_path: Path = config.DB_PATH,
    report: dict | None = None,
    since: str = config.REGIME_BOUNDARY,
    spotlights: tuple[dict, ...] = config.MAJOR_EVENTS,
    directory: Path | None = None,
) -> list[dict]:
    """One row per fortnight from `since`: what moved, phrased in fixed forms.

    Five readings, answering different questions. Adoption says the deck took a
    card up or put it down. Copies says it kept a staple and changed its mind
    about how many, which no adoption reading can see, because the cards that
    happens to sit at total adoption and never move a share. Returns say a card
    the deck had stopped playing came back, and came back larger than it has
    ever been, which is the only version of that worth a row: a card that was
    always a one-off being a one-off again is not news. Watched slots say what
    the camp did with the few slots the pilot argues about, at a finer bar and
    by copy count. Manabase says the camp moved its land count, which is a
    configuration of the whole list and which no card-level reading can see.

    Read on the report's build camp and never on its pooled population: pooled,
    a camp arriving reads as the deck changing its mind about every card the two
    camps disagree on.

    Each fortnight is read against the entry before it in the storyline. That is
    the fortnight before, unless a major paper event in `spotlights` fell inside
    this one, in which case it is the event: the latest one where two did. A
    fortnight read against paper is a cross-population reading and the entry
    says so. The event's own lists are never folded into the fortnight's
    numbers, each entry being one room, and the gate on a paper baseline is
    `shifted` rather than `moved`, the two populations being nowhere near one
    size. A card the event played is not a return when MTGO takes it up after,
    the entry before having held it; one the event did not play is read as a
    return off the deck's own MTGO history, how long a card has been gone being
    a fact about the deck.
    """
    from . import spotlight  # noqa: PLC0415, spotlight reads this module's rows

    report = report or config.REPORTS["blink"]
    registered, lists = _history(db_path, report["archetype"], report["build_camp"])
    sizes: dict[int, int] = {}
    lands: dict[int, dict[int, int]] = {}
    for row in lists:
        index = bin_of(row["date"], since)
        sizes[index] = sizes.get(index, 0) + 1
        if row["lands"]:
            per = lands.setdefault(index, {})
            per[row["lands"]] = per.get(row["lands"], 0) + 1

    held: dict[tuple[str, str], dict[int, list[int]]] = {}
    copies: dict[tuple[str, str], dict[int, list[int]]] = {}
    for row in registered:
        key, index = (row["card"], row["zone"]), bin_of(row["date"], since)
        held.setdefault(key, {}).setdefault(index, []).append(row["list_id"])
        copies.setdefault(key, {}).setdefault(index, []).append(row["main"])

    paper = _paper(spotlights, directory, report, since)
    typed = land_names(db_path) if paper and report["manabase"] else frozenset()
    watched = set(report["watch"])
    first = bin_of(since, since)
    timeline = []
    for index in sorted(i for i in sizes if i >= first):
        size = sizes[index]
        start, end = bin_start(index, since), bin_end(index, since)
        if index in paper:
            label, rows = paper[index]
            against, crossed, comparable, gate = label, True, True, shifted
            was_held = spotlight._held(rows)
            was_size, was_lands = len(rows), spotlight.lands(rows, typed)
        else:
            # A delta may not cross the regime boundary: the fortnight before
            # the first post-regime bin belongs to a different era, so what it
            # played is not what this deck put down. Returns still read past it,
            # since how long a card has been gone is a fact about the deck and
            # not the regime.
            against, crossed, comparable, gate = (
                f"the fortnight to {bin_end(index - 1, since)}", False, index - 1 >= first, moved
            )
            was_held = {key: bins[index - 1] for key, bins in copies.items() if index - 1 in bins}
            was_size, was_lands = sizes.get(index - 1, 0), lands.get(index - 1, {})
        found = []

        for (card, zone), bins in sorted(held.items()):
            if index not in bins:
                continue
            n, was = len(bins[index]), len(was_held.get((card, zone), []))
            share = n / size

            other = held.get((card, "side" if zone == "main" else "main"), {})
            if not was and _is_return(bins, index, sizes, zone, share):
                phrase = (
                    f"moves to the {zone}board"
                    if index - 1 in other
                    else _return_phrase(bins, index)
                )
                found.append(
                    {
                        "kind": "return",
                        "zone": zone,
                        "card": card,
                        "text": f"{card} {phrase}, {n} of {size} lists ({share:.0%})",
                    }
                )
            elif (
                comparable
                and not (zone == "main" and card in watched)
                and gate(n, size, was, was_size)
            ):
                found.append(adoption_row(card, zone, n, size, was, was_size))

        # A card the bin dropped entirely has no row of its own above, so it is
        # read from the baseline's side. Watched slots are read by copy count
        # below, where zero copies is a row like any other.
        for (card, zone), before_copies in sorted(was_held.items()):
            if index in held.get((card, zone), {}) or (zone == "main" and card in watched):
                continue
            if comparable and gate(0, size, len(before_copies), was_size):
                found.append(adoption_row(card, zone, 0, size, len(before_copies), was_size))

        if comparable:
            now_held = {key: bins[index] for key, bins in copies.items() if index in bins}
            found += watched_rows(watched, now_held, was_held, size, was_size)
            found += copies_rows(now_held, was_held, size, was_size, watched)
            if report["manabase"]:
                found += manabase_rows(lands.get(index, {}), was_lands, size, was_size)

        for event in events():
            if start <= event["date"] <= end:
                found.append({"kind": "event", "zone": None, "card": None, "text": event["label"]})

        timeline.append(
            {
                "bin": index,
                "start": start,
                "end": end,
                "lists": size,
                "against": against,
                "cross_population": crossed,
                "found": found,
            }
        )
    return timeline


def _paper(
    spotlights: tuple[dict, ...], directory: Path | None, report: dict, since: str
) -> dict[int, tuple[str, list[dict]]]:
    """The major event each bin is read against: the latest one inside it.

    The build camp's lists at the event, shaped as `spotlight.findings` reads
    them. Only events fetched by now count, a report having to render on a
    machine that has never pulled a paper event.
    """
    from . import spotlight  # noqa: PLC0415

    latest = {}
    for spot in sorted(spotlights, key=lambda s: s["date"]):
        if not spotlight.cached(spot, directory).exists():
            continue
        payload = spotlight.load(spot, directory)
        rows = spotlight.members(payload, report["archetype"], report["build_camp"])
        latest[bin_of(spot["date"], since)] = (spot["label"], rows)
    return latest


def _is_return(
    bins: dict[int, list[int]], index: int, sizes: dict[int, int], zone: str, share: float
) -> bool:
    """Whether an appearance with no bin behind it is a return worth a row.

    Three conditions, each dropping a different false one. The absence has to
    cover `RETURN_ABSENCE_DAYS`, because a staple running at a few lists a week
    misses a fortnight on chance alone and reads as having left. The gate is per
    zone, because a sideboard churns far harder than a mainboard: two thirds of
    the sideboard names this deck has registered appear in two weeks or fewer,
    and between them they carry four percent of its volume. And the appearance
    has to be a larger share than the card has ever held, which is what
    separates a card the field turned to from one that was always a one-off.
    """
    gate = config.TRACK_RETURN_MAIN_LISTS if zone == "main" else config.TRACK_RETURN_SIDE_LISTS
    if len(bins[index]) < gate:
        return False
    absence = config.RETURN_ABSENCE_DAYS // config.TRACK_BIN_DAYS
    if any(index - back in bins for back in range(1, absence + 1)):
        return False
    if not config.TRACK_RETURN_BEATS_PEAK:
        return True
    peak = max(
        (len(held) / sizes[i] for i, held in bins.items() if i < index and sizes.get(i)),
        default=0.0,
    )
    return share > peak


def _return_phrase(bins: dict[int, list[int]], index: int) -> str:
    """How the row says the card came back, or that it never went away first."""
    prior = [i for i in bins if i < index]
    if not prior:
        return "appears for the first time"
    weeks = (index - max(prior)) * config.TRACK_BIN_DAYS // 7
    return f"returns after {weeks} weeks away"
