"""The analytical store: a DuckDB file rebuilt from the immutable raw cache."""

import csv
import tempfile
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

import duckdb

from . import config, index
from .classify import classify_cache, fallout as fallout_of, version_boundary as boundary_of
from .parse import Decklist

DECKLISTS_SCHEMA = """
CREATE OR REPLACE TABLE decklists (
    list_id VARCHAR,
    pilot VARCHAR,
    event VARCHAR,
    event_id VARCHAR,
    event_class VARCHAR,
    date VARCHAR,
    placement INTEGER,
    swiss_points INTEGER,
    record VARCHAR,
    archetype VARCHAR,
    camp VARCHAR,
    lands INTEGER
)
"""

# A card in a list, as the pair the domain calls a configuration. One pilot can
# publish two 5-0 lists in one league dump, so the list a card belongs to is
# `list_id`, which carries an ordinal for exactly that case.
CONFIGURATIONS_SCHEMA = """
CREATE OR REPLACE TABLE configurations (
    list_id VARCHAR,
    card VARCHAR,
    main INTEGER,
    side INTEGER
)
"""

# Every card the payloads have typed as a land, so a list fetched without types,
# which is what a melee decklist page yields, can be given the same land count
# the MTGO lists carry. A name and nothing else: the type is the fact kept.
LANDS_SCHEMA = """
CREATE OR REPLACE TABLE lands (
    card VARCHAR
)
"""

# Every card the payloads have published a colour for, with its colours as
# letters, so a paper list can be read on the splash line the way the MTGO
# lists are. Melee publishes names and nothing else, like the land count.
CARDS_SCHEMA = """
CREATE OR REPLACE TABLE cards (
    card VARCHAR,
    colours VARCHAR
)
"""

# Every list that holds a deck's core and belongs to nothing, with the deck and
# the reason its rule turned it away: an engine's name from `config.ENGINES`,
# the splash line, a floor or a supporting tier. One row per deck the list
# resembles. Kept so
# every exclusion is visible, and a deck adopting another deck's engine card
# reads as a growing count here rather than as a silent decline in its report.
FALLOUT_SCHEMA = """
CREATE OR REPLACE TABLE fallout (
    list_id VARCHAR,
    archetype VARCHAR,
    reason VARCHAR
)
"""


# Every member sitting in its deck's default version whose mainboard is a named
# version's, with that version and what says so: a colour its population is
# built in, or a card it holds. The default is the one version no list is read
# into, everything holding no marker falling to it, so a rule gap there is
# silent where every other misreading is loud. Kept so the gap is a printed
# count rather than a sweep somebody remembers to run.
VERSION_BOUNDARY_SCHEMA = """
CREATE OR REPLACE TABLE version_boundary (
    list_id VARCHAR,
    archetype VARCHAR,
    version VARCHAR,
    kind VARCHAR,
    marker VARCHAR
)
"""


def _identify(decklists: list[Decklist]) -> list[str]:
    """Each list's id: the event it was published in and the pilot who registered it.

    An id used to be the list's place in the cache, which is a fact about the
    order the files happened to sort in and not about the list. The 2026-09-13
    refresh cached 64 lists whose slugs sort early and moved every id from June
    on by about 32, so the ids quoted in the archived reviews, in `HEURISTICS.md`
    and in the rule comments came to name other lists with nothing saying so.
    The event and the pilot are what the site published, so an id minted from
    them is the same id on the next rebuild.

    One pilot can trophy twice in a league dump, so his second list takes the
    ordinal and his first keeps the bare key: an id does not move when a later
    list arrives. Two such lists exchange ids only where the dump republishes
    them in the other order, which is the unsettled window's own risk.
    """
    seen: Counter[str] = Counter()
    ids = []
    for decklist in decklists:
        key = f"{decklist.event_id}#{decklist.pilot}"
        seen[key] += 1
        ids.append(key if seen[key] == 1 else f"{key}#{seen[key]}")
    return ids


def _load(con: duckdb.DuckDBPyConnection, table: str, rows: Iterable[tuple]) -> None:
    """Bulk-load `rows` into `table`.

    DuckDB inserts a row at a time some four orders of magnitude slower than it
    reads a file, and a card row per card per list is around 600,000 of them, so
    the rows go via a CSV it reads in one pass. An unquoted empty field is the
    database's own spelling of NULL, which is what `csv` writes `None` as.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{table}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerows(rows)
        # A run the site served nothing to has an empty cache to rebuild from,
        # and an empty file has no dialect for the database to read.
        if path.stat().st_size:
            con.execute(f"COPY {table} FROM '{path}' (FORMAT CSV, HEADER false)")


def build(raw_dir: Path = config.RAW_DIR, db_path: Path = config.DB_PATH) -> Path:
    """Rebuild the store from the raw cache. Derived data is never authoritative.

    The tables are one picture of the cache, so they land together or not at
    all: a rebuild that died between them would leave lists whose cards had gone,
    and a card query would answer that nobody plays it rather than fail.

    The index is written from the same parse, after the tables land. It is the
    committed record of what the cache held, and the cache itself is not
    committed; written from a second read it could come to disagree with the
    store it is filed beside, and a record that disagrees with the thing it
    records is worse than none.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    parsed = classify_cache(raw_dir)
    # Identified over the whole cache, so a list keeps its id whatever the
    # history start is set to.
    lists = [
        (list_id, d)
        for list_id, d in zip(_identify(parsed), parsed)
        if d.date >= config.HISTORY_START
    ]
    with duckdb.connect(db_path) as con:
        con.execute("BEGIN TRANSACTION")
        con.execute(DECKLISTS_SCHEMA)
        con.execute(CONFIGURATIONS_SCHEMA)
        con.execute(LANDS_SCHEMA)
        con.execute(CARDS_SCHEMA)
        con.execute(FALLOUT_SCHEMA)
        con.execute(VERSION_BOUNDARY_SCHEMA)
        _load(
            con,
            "decklists",
            (
                (
                    list_id,
                    d.pilot,
                    d.event,
                    d.event_id,
                    d.event_class,
                    d.date,
                    d.placement,
                    d.swiss_points,
                    d.record,
                    d.archetype,
                    d.camp,
                    d.lands,
                )
                for list_id, d in lists
            ),
        )
        _load(
            con,
            "configurations",
            (
                (list_id, card, d.mainboard.get(card, 0), d.sideboard.get(card, 0))
                for list_id, d in lists
                for card in d.mainboard | d.sideboard
            ),
        )
        _load(con, "lands", ((card,) for card in sorted(set().union(*(d.land_names for _, d in lists)))))
        published = {}
        for _, d in lists:
            published.update(d.colours)
        _load(con, "cards", ((card, "".join(sorted(colours))) for card, colours in sorted(published.items())))
        _load(
            con,
            "fallout",
            ((list_id, deck, reason) for list_id, d in lists for deck, reason in fallout_of(d)),
        )
        _load(con, "version_boundary", boundary_of(lists))
        con.execute("COMMIT")
    index.write([d for _, d in lists], db_path)
    return db_path


def land_names(db_path: Path = config.DB_PATH) -> frozenset[str]:
    """Every card the MTGO payloads have typed as a land."""
    with duckdb.connect(db_path, read_only=True) as con:
        return frozenset(row[0] for row in con.execute("SELECT card FROM lands").fetchall())


def card_colours(db_path: Path = config.DB_PATH) -> dict[str, frozenset[str]]:
    """Every card's colours as the MTGO payloads have published them."""
    with duckdb.connect(db_path, read_only=True) as con:
        # A colourless card is an empty string, which the CSV load reads as NULL.
        return {
            card: frozenset(colours or "")
            for card, colours in con.execute("SELECT card, colours FROM cards").fetchall()
        }


def fallout(db_path: Path = config.DB_PATH) -> list[dict]:
    """Every list turned away by a rule whose core it holds, with the deck and the reason.

    Most recent first, then by deck, so a run's tail reads as what this week's
    lists did.
    """
    with duckdb.connect(db_path, read_only=True) as con:
        return _rows(
            con.execute(
                "SELECT f.archetype, f.reason, d.pilot, d.event, d.date, d.list_id"
                " FROM fallout f JOIN decklists d USING (list_id)"
                " ORDER BY d.date DESC, f.archetype, d.pilot"
            )
        )


def version_boundary(db_path: Path = config.DB_PATH) -> list[dict]:
    """Every member whose version label disagrees with its mainboard, with what says so.

    Most recent first, then by deck, the way the fall-out reads.
    """
    with duckdb.connect(db_path, read_only=True) as con:
        return _rows(
            con.execute(
                "SELECT b.archetype, b.version, b.kind, b.marker,"
                " d.pilot, d.event, d.date, d.list_id"
                " FROM version_boundary b JOIN decklists d USING (list_id)"
                " ORDER BY d.date DESC, b.archetype, b.version, d.pilot, b.marker"
            )
        )


def _rows(cursor: duckdb.DuckDBPyConnection) -> list[dict]:
    """An executed cursor's rows, each keyed by the column it selected."""
    names = [c[0] for c in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def population(archetype: str, camp: str | None, prefix: str = "") -> tuple[str, list]:
    """The predicate naming the lists a reading is taken over, and its parameters.

    `camp` of `None` pools every camp of the archetype, which is what a reading
    of the whole deck wants: a metagame share read on one camp of three is a
    third of the answer. A named camp is the reading the build questions want,
    where pooling would report a camp arriving as the deck changing its mind.
    """
    if camp is None:
        return f"{prefix}archetype = ?", [archetype]
    return f"{prefix}archetype = ? AND {prefix}camp = ?", [archetype, camp]



def _query(db_path: Path, columns: str, source: str, where: str, params: list) -> list[dict]:
    """The archetype's rows for one question, most recent and best finishes first."""
    with duckdb.connect(db_path, read_only=True) as con:
        return _rows(
            con.execute(
                f"SELECT {columns} FROM {source}"
                f" WHERE archetype = ?{f' AND {where}' if where else ''}"
                f" ORDER BY date DESC, placement NULLS LAST, pilot",
                [config.ARCHETYPE] + params,
            )
        )


def goryos_lists(
    db_path: Path = config.DB_PATH, day: str | None = None, camp: str | None = None
) -> list[dict]:
    """The archetype's lists, most recent and best finishes first.

    Naming a `camp` narrows to that camp's population, which is what consensus
    is computed over: hybrids are members of the archetype and of no camp, so
    they answer to neither.
    """
    filters = {"date": day, "camp": camp}
    return _query(
        db_path,
        "pilot, event, event_id, event_class, date, placement, swiss_points, record, camp",
        "decklists",
        " AND ".join(f"{column} = ?" for column, value in filters.items() if value),
        [value for value in filters.values() if value],
    )


def arrivals(added: list[index.Row], db_path: Path = config.DB_PATH) -> list[dict]:
    """The archetype's lists among what an ingest brought in.

    The index is kept free of the membership rule, so which of the new lists are
    Goryo's is a question asked here, of the store, against the keys the ingest
    reported. Filing the answer in the index instead would restate the whole
    file the day `config.SIGNATURE_CARDS` moved, and an ingest diff has to be
    the field's news rather than this engine's.

    In the challenge stratum this key is exact: an event is one entry per player,
    so a pilot appears in its standings once and his list is his whole showing.
    A league is continuous and can trophy the same pilot twice in a day, so the
    index files two rows there that this key cannot tell apart. The ambiguity is
    the league stratum's alone, and it over-reports only where such a pilot's day
    was already cached and has since gained another list. It under-reports never,
    which is the direction for a report of what is new to be wrong in.
    """
    keys = {(row.date, row.event_id, row.pilot) for row in added}
    return [
        row
        for row in goryos_lists(db_path)
        if (row["date"], row["event_id"], row["pilot"]) in keys
    ]

