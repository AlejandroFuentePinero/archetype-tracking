# Archetype Tracking

Reads published Magic: The Gathering decklists and reports named Modern
archetypes fortnightly. It caches every published MTGO event and every
configured paper event from Melee, curates them into a DuckDB store, and freezes
a fixed set of readings per tracked archetype: how much of the field it holds,
whether it converts that presence into finishes, whether it is still being built
or merely copied, and which slots of its build moved. The readings render as a
weekly HTML report with a hand-written summary at the top.

It is a working tool built for one team meeting, not a product. It grew out of
an earlier attempt to optimise one deck's 75 from the same data. That attempt
failed honestly and its record stays in
[deck-optimisation-engine](https://github.com/AlejandroFuentePinero/deck-optimisation-engine);
the tracking half is what moved here.

## Read this before you trust a number

Published decklists are conditioned on winning. A challenge publishes its top
32, a league publishes only 5-0s, and a losing list never appears. The audit of
the earlier attempt found its statistics honest and its premise unachievable:
every performance instrument it built ran at a few percent of statistical
power against effects smaller than its own detection floor. So this engine
measures adoption and never performance. What it reports is what pilots
registered, how that moved from one fortnight to the next, and how much of a
published cut a deck held. Where a figure looks like performance, the Spotlight
conversion rate for instance, it is a share of a cut over a share of a field
and is printed with both counts.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). The report renders
its figures with matplotlib, which `uv sync` installs.

```bash
git clone https://github.com/AlejandroFuentePinero/archetype-tracking.git
cd archetype-tracking
uv sync
```

## Quickstart

The store and the raw cache are not committed, so a fresh clone builds them:

```bash
# Fetch every published Modern event since HISTORY_START and rebuild the store.
# The first run is a six-month backfill: hundreds of events, expect it to be slow.
uv run tracker refresh

# Freeze the closed weeks and render last week's report for each tracked deck.
uv run tracker weekly --deck blink
uv run tracker weekly --deck goryos
```

Later runs are cheap: `refresh` refetches only the unsettled window, the last
few days that are still gaining lists, plus anything new.

## Commands

| Command | What it does |
| --- | --- |
| `refresh [--since D] [--until D]` | Cache published MTGO events into `data/raw/`, rebuild the store, update the ingest index |
| `weekly [--deck D] [--week D]` | Freeze the closed weeks and fortnights of a tracked deck, write the week's numbers as JSON, render the HTML |
| `event-fetch [--id N]` | Cache a major paper event's standings and decklists from Melee into `data/raw-melee/` |

`weekly` defaults to Esper Blink and to the last complete week; run it on a
Monday for the week that closed on Sunday. It prints the numbers, where they
landed as JSON, and where the HTML landed. The summary at the top of that HTML
is written by hand into `data/tracking/<deck>/summary/<week>.md`, and
`.claude/skills/weekly-report/` fixes the clause order it goes in. Everything
under `data/tracking/` is committed and append-only, because the report's own
history cannot be rebuilt from a cache: a past week genuinely moves when a
league dump fills in, and the frozen row is what was reported.

`event-fetch` reads `config.MAJOR_EVENTS`, skips every list already cached, and
writes one JSON per event. A played-out event does not change, so it runs once
the week an event lands and never again. Paper lists never enter the store and
never share an axis with MTGO figures: a Spotlight publishes every finisher
where a challenge publishes a cut, so the two are different populations.

Which lists a report reads is not a flag. It is the report's own entry in
`config.REPORTS`: the archetype, the camp its volume figures are pooled over,
the camp its build readings are taken on, and the slots it watches. Adding a
subject is an entry there and a first run.

## Documentation

| File | What it holds |
| --- | --- |
| [`CONTEXT.md`](CONTEXT.md) | The glossary. Every term the code and the report use, defined once. Read this first |
| [`HEURISTICS.md`](HEURISTICS.md) | Pilot knowledge from play that decides how the numbers are read, and which is not derivable from the data |
| [`docs/adr/`](docs/adr/) | Architecture decisions. ADR 0001 is what four days of backfill established about the MTGO stream |
| [`docs/agents/`](docs/agents/) | Conventions for the coding agents that work on this repo |

`CONTEXT.md` is not optional reading. The vocabulary is load-bearing: "detection
bin", "watched slot", "build camp" and "frozen row" all mean one specific thing
here, and several terms carry an explicit `_Avoid_` line naming the near-synonym
that would blur a real distinction.

## Layout

```
tracker/            the package
  mtgo.py           network: discover and fetch MTGO event payloads
  melee.py          network: fetch a paper event's standings and decklists
  parse.py          payloads to decklist records
  classify.py       archetype membership, then the variant within it
  refresh.py        cache a range of days, then rebuild the store
  store.py          the DuckDB store, rebuilt from the cache every run
  index.py          the committed record of what the cache holds
  tracking.py       the weekly readings: presence, conversion, goldfishing
  timeline.py       the fortnightly change detection
  spotlight.py      a paper event read as a storyline entry
  weekly.py         freeze the closed weeks, then render the report
  plots.py          the report's figures, as inline SVG
  config.py         every named threshold, in one file
data/               index.csv, events.csv, raw-melee/ and tracking/ are committed
tests/              78 tests over committed MTGO payload fixtures
```

## Data

**Committed:** the ingest index (`data/index.csv`, one row per published list
the cache holds), the major-event marks (`data/events.csv`), the Melee payloads
(`data/raw-melee/`), and the frozen tracking rows and summaries
(`data/tracking/`). Each of these is either the engine's own memory, which no
cache can rebuild, or a capture that should not be fetched twice: a paper event
is fifteen hundred decklist pages scraped from a third-party site.

**Not committed:** the raw MTGO payload cache (`data/raw/`, hundreds of
megabytes), the DuckDB store, and the rendered reports. All three are derived
and rebuildable from `refresh`.

The committed index does carry MTGO pilot logins, because a list without the
pilot who registered it cannot support the readings that count builds per
pilot. Those logins are exactly as MTGO publishes them on its own public
decklist pages.

### Fetching etiquette

`refresh` reads public event pages from `mtgo.com` and parses the JSON payload
each page embeds. There is no API and no key. It retries a page up to five times
with lengthening backoff, because the site intermittently serves a 200 whose
content is missing, and a stub taken at face value silently drops published
lists from the cache. It is a sequential scraper with no parallelism, so a
backfill is slow by construction. Please keep it that way.

## Tests

```bash
uv run pytest
```

78 tests over committed MTGO payload fixtures. The network layer is excluded
from the test seam by design and is verified by spot-checking fetched counts
against the live site; the calendar rule deciding which month may legitimately
have no index yet is not network, and is tested.

## Licence

[MIT](LICENSE).

Not affiliated with or endorsed by Wizards of the Coast. Magic: The Gathering
and MTGO are trademarks of Wizards of the Coast LLC. Card names and decklist
data are the property of their respective owners.
