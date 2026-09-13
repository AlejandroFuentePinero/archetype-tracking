"""The weekly readings of a tracked deck: presence, conversion, goldfishing.

A tracked deck gets a fixed set of numbers, computed the same way every week,
that say how much of the field it
holds, whether it converts that presence into finishes, and whether it is still
being built or merely copied.

Every reading here is a share of a published stratum rather than a bare count.
A week that ran three challenges publishes three times the top-32 slots of a week
that ran one, so a count rises with the calendar and a share does not. The counts
are carried beside the shares regardless, because a share off two lists is a
figure nobody should read without seeing the two.

Which camps a reading is taken over is the report's decision and is made once,
in `config.REPORTS`. Presence pools every camp, a metagame share being a share
of the whole archetype. Every other reading is the report's own camp: two camps
are different decks in the sense that matters to how a list is built and to
how it finishes, and pooled, a camp arriving reads as the deck changing its
mind.
"""

from collections import Counter
from pathlib import Path

import duckdb

from . import classify, config
from .store import _rows, population

# The week bucket. ISO weeks start Monday, and the report is generated Monday
# for the week that just closed, so a bucket is always a settled week.
_WEEK = "CAST(CAST(date_trunc('week', CAST(date AS DATE)) AS DATE) AS VARCHAR)"

# The challenge-class stratum: every event that publishes a placement. The event
# classes differ in size and in prestige and are pooled deliberately, since what
# the reading wants is the whole of the field that keeps standings.
_CHALLENGE = "event_class <> 'league'"


def weekly(
    db_path: Path = config.DB_PATH,
    archetype: str = "blink",
    camp: str | None = "esper",
    since: str = config.REGIME_BOUNDARY,
) -> list[dict]:
    """One row per week: the deck's presence and conversion against the field.

    Weeks come from the field rather than from the deck, so a week the deck
    published nothing in is a zero on the plot instead of a gap in it. The
    denominators are the whole published stratum that week: every challenge-class
    list for presence, every challenge-class list that placed top 8 for
    conversion, every league list for trophies.
    """
    where, args = population(archetype, camp)
    with duckdb.connect(db_path, read_only=True) as con:
        return _rows(
            con.execute(
                f"""
                WITH field AS (
                    SELECT {_WEEK} AS week,
                           count(*) FILTER ({_CHALLENGE}) AS chal_field,
                           count(*) FILTER ({_CHALLENGE} AND placement <= 8) AS top8_field,
                           count(*) FILTER (event_class = 'league') AS league_field
                    FROM decklists WHERE date >= ? GROUP BY week
                ),
                deck AS (
                    SELECT {_WEEK} AS week,
                           count(*) FILTER ({_CHALLENGE}) AS chal,
                           count(*) FILTER ({_CHALLENGE} AND placement <= 8) AS top8,
                           count(*) FILTER ({_CHALLENGE} AND placement <= 16) AS top16,
                           count(*) FILTER (event_class = 'league') AS trophies,
                           count(*) AS lists
                    FROM decklists
                    WHERE {where} AND date >= ? GROUP BY week
                )
                SELECT f.week,
                       coalesce(d.lists, 0) AS lists,
                       coalesce(d.chal, 0) AS chal,
                       f.chal_field,
                       coalesce(d.chal, 0) / f.chal_field AS chal_share,
                       coalesce(d.top8, 0) AS top8,
                       f.top8_field,
                       CASE WHEN f.top8_field > 0
                            THEN coalesce(d.top8, 0) / f.top8_field END AS top8_share,
                       coalesce(d.top16, 0) AS top16,
                       coalesce(d.trophies, 0) AS trophies,
                       f.league_field,
                       CASE WHEN f.league_field > 0
                            THEN coalesce(d.trophies, 0) / f.league_field END AS trophy_share
                FROM field f LEFT JOIN deck d USING (week)
                ORDER BY f.week
                """,
                [since, *args, since],
            )
        )


def signatures(
    db_path: Path = config.DB_PATH,
    archetype: str = "blink",
    camp: str | None = "esper",
    since: str = config.REGIME_BOUNDARY,
) -> list[dict]:
    """Every list's mainboard as one string, with the week it was published in.

    The unit a goldfishing reading needs: two lists are the same 75 or they are
    not, and a comparison card by card would call a one-card difference most of
    a match. Sideboards are left out because they are the part of a copied list
    a pilot changes first, so a goldfishing reading taken over all 75 would report
    the field's sideboarding as innovation.
    """
    where, args = population(archetype, camp, "d.")
    with duckdb.connect(db_path, read_only=True) as con:
        return _rows(
            con.execute(
                f"""
                SELECT d.list_id, d.pilot, {_WEEK} AS week,
                       string_agg(c.card || '#' || c.main, '|' ORDER BY c.card) AS mainboard
                FROM decklists d JOIN configurations c USING (list_id)
                WHERE {where} AND d.date >= ? AND c.main > 0
                GROUP BY d.list_id, d.pilot, week ORDER BY week
                """,
                [*args, since],
            )
        )


def _most_registered(mainboards: list[str]) -> str | None:
    """The 60 the most pilots registered that week, or nothing from no lists.

    Ties are broken on the mainboard itself rather than left to whichever the
    max happened to reach first. Two 75s tied for most-registered is common in a
    thin week, and resolved by iteration order the answer depends on the set's
    ordering, which for strings is the hash seed: the same store then reports
    different figures on different runs of the same code. Across this history
    six weeks are tied, and the worst of them moved a published bar from 0% to
    58%.
    """
    if not mainboards:
        return None
    counts = Counter(mainboards)
    return min(counts, key=lambda mainboard: (-counts[mainboard], mainboard))


def goldfishing(
    db_path: Path = config.DB_PATH,
    archetype: str = "blink",
    camp: str | None = "esper",
    since: str = config.REGIME_BOUNDARY,
) -> list[dict]:
    """Per week, how many pilots registered last week's most-registered 60 again.

    How much of the field is copying rather than building.

    The direct reading of whether a deck is still being built. Every other
    reading here answers it by absence: a week nothing moved in looks the same
    whether the field settled or the field was quiet. This one says which, and
    it is also the warning that a fat week is not the independent sample its
    list count claims, since a week most of which is one list copied carries
    about as much evidence as its distinct builds do.

    Read per pilot per 60 and never per publication, which is the one thing this
    reading cannot get wrong without inverting itself. A league dump publishes
    every 5-0, so one grinder on one list can appear five times in a week, and
    counted as five that is five lists the field failed to build. It is one
    pilot's deck registered five times. The week to 6 September is the case:
    Esper Blink published 69 lists on 27 distinct mainboards, which reads as a
    copied field, and those 69 lists are 57 distinct pilot builds of which only
    four mainboards have a second pilot behind them. `lists` stays beside the
    reading because a share off a handful of builds is a figure nobody should
    read without seeing what it came from.
    """
    by_week: dict[str, list[tuple[str, str]]] = {}
    for row in signatures(db_path, archetype, camp, since):
        by_week.setdefault(row["week"], []).append((row["pilot"], row["mainboard"]))

    readings, previous_top = [], None
    for week in sorted(by_week):
        published = by_week[week]
        # One entry per pilot per 60: the same pilot's repeats of one list are
        # one decision, and their separate lists are separate ones.
        builds = [mainboard for _, mainboard in sorted(set(published))]
        copied = sum(1 for m in builds if m == previous_top) if previous_top else 0
        readings.append(
            {
                "week": week,
                "lists": len(published),
                "builds": len(builds),
                "distinct": len(set(builds)),
                "copied": copied,
                "copied_share": copied / len(builds) if builds else None,
            }
        )
        previous_top = _most_registered(builds)
    return readings


def excluded(
    db_path: Path, deck: str, since: str = config.REGIME_BOUNDARY
) -> int | None:
    """How many lists holding the deck's signature its colour rule turned away.

    None for a deck with no colour rule, where colour is no part of
    membership, so there is nothing here for the report to keep an eye on.

    A list holding every signature card and five off-colour spells, or a
    playset of one, is a different deck. Printed every week because it is the
    one part of membership that can go stale silently: a card whose colour the
    site never published reads as colourless, and nothing else in the report
    would say so. Read off the fall-out, so only a list nothing else claimed
    counts, and the tested order is not something this count depends on
    noticing.
    """
    rule = config.TRACKED_DECKS.get(deck)
    if not rule or not rule.get("colours"):
        return None
    with duckdb.connect(db_path, read_only=True) as con:
        return con.execute(
            f"""
            SELECT count(*) FROM fallout JOIN decklists USING (list_id)
            WHERE fallout.archetype = ? AND reason IN ({",".join("?" * len(classify.COLOUR_REASONS))})
            AND date >= ?
            """,
            [deck, *classify.COLOUR_REASONS, since],
        ).fetchone()[0]
