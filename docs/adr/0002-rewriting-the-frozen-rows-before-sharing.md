# ADR 0002: Rewriting the frozen rows before the reports were shared

Status: accepted (2026-09-13)

## Context

`timeline.csv` and `weekly.csv` are append-only. The weekly-report skill states
it as a hard rule: a past week's numbers can genuinely move when a league dump
fills in, and the frozen row is what was reported. A report whose past changes
under it is a report nobody can cite.

On 2026-09-13, four defects were fixed in the engine, and each of them had
already written rows into those files:

- **Split cards were folded in half across the paper boundary.** Melee publishes
  `Wear // Tear`; the fetch kept the front face alone, so the paper population
  held `Wear` and the MTGO population held `Wear/Tear`. The storyline then read
  one card vanishing and another arriving, in the same board, in the same
  fortnight. Fourteen such rows were frozen across Boros Energy, Boros Ponza,
  Storm and Domain Zoo.
- **A capture taken inside its own day's unsettled window was trusted.** The gate
  was a fact about the calendar alone, so a same-day capture froze whatever the
  day had published so far. 2026-08-23 was held at 7 lists and 2026-08-28 at 25,
  against a median league day of 60 across the days either side.
- **A return was read off an absence the fortnights behind it were too thin to
  evidence.** Sixty-seven rows, 66 of them phrased "appears for the first time",
  named cards that were simply core to the deck in bins whose history ran to a
  handful of lists.

Later the same day a fifth change landed, and it is not a defect fix. The floor
that had just been given to the return reading was adopted for the comparison
readings too, by pilot verdict, and is written up in `HEURISTICS.md`: a
fortnight of fewer than `config.TRACK_ROW_MIN_LISTS` lists, or one read against
a bin holding fewer, is too thin to read a card-level move across, and prints a
row saying so in place of its comparison rows. The rows it refuses are not bad
arithmetic. They are claims phrased exactly like a claim read off a hundred and
thirty lists, with only the counts beside them to tell a reader which is which,
and 66 of the 597 comparison rows then frozen read across such a bin.

## Decision

Recompute every frozen row under the corrected engine, and again under the
floor, both on 2026-09-13 and both before the first sharing, rewriting the files
in place each time.

### The defect pass, c5a3d0f

- `refresh --since 2026-08-23` repaired the two thin league days (7 to 53 lists
  and 25 to 56), which the new settle gate now refetches on any normal run.
- Both files were rebuilt for all seventeen reports through 2026-08-31, the last
  complete week, leaving the 2026-09-07 week to the ordinary Monday run.

What moved: in `weekly.csv`, 146 cells across the weeks to 2026-08-17 and
2026-08-24 and no other week, all of them `league_field`, `trophies`, `lists`
and `trophy_share`. No challenge-class figure moved anywhere. In `timeline.csv`,
84 findings went (67 thin returns, 14 split-card ghosts, 3 adoption rows that a
fuller population put under the bar), 24 arrived, and 136 rows kept their finding
and restated its numbers on the repaired population.

### The floor pass, 2fb5764

`timeline.csv` alone. No weekly figure answers to the floor and none moved.

84 rows went and 9 arrived, across four reports: Devoted Combo 48 out and 3 in,
Grinding Station 24 and 3, Simic Neoform 8 and 2, Trudge 4 and 1. The other
thirteen were rebuilt and did not move. Of the 84, 66 were adoption rows and 16
copies rows, each read across a bin under the floor, and 2 were Grinding Station
bins that had printed `stable`, which told a reader nothing moved where in truth
nothing could be read. The 965 rows that remain kept their phrasing to the byte.

Eight of the nine bins that now read thin fall in the ten weeks after the bans,
when these decks ran to between three and nine lists a fortnight. The ninth is
Grinding Station's fortnight to 2026-08-23, 8 lists read against 8.

The floor stops at a fortnight read against another fortnight. A fortnight read
against a paper event is a cross-population reading gated by `timeline.shifted`,
whose own floor is the move being worth `TRACK_MIN_LISTS` in the smaller room,
so no row of that kind was withdrawn here.

## Why this is not a precedent

The rule protects a record of what a reader was told. These reports had not been
shared with anyone: the first sharing is 2026-09-15. There was no record to
protect, and from 2026-09-15 there is one.

The three defect cases are also not the case the rule was written for, which is
a number that genuinely moved. A split card folded in half never measured
anything, `Wear` not being a card anyone registered. A return read off four
lists of history was a claim with no evidence behind it, not a measurement that
later changed. And the thin league days are the inverse of a dump filling in
late: the dump filled in normally and the capture was taken too early, which is
a fault in the reading and not news about the week.

The floor pass shares the window and not the reasoning. A defect had written
rows that measured nothing; the floor withdraws rows that measured something on
evidence too slight to carry the phrasing they were given. That is a change of
method, and a change of method under a reader is the thing the append-only rule
exists to prevent, which is why it was taken in the window where there was no
reader and not a week into one. A floor adopted after 2026-09-15 changes the
fortnights ahead of it, leaves the frozen ones standing, and is announced in
that week's summary.

A number that moves because the source published more is still frozen where it
stands, and this ADR does not license rewriting one. If a frozen row is wrong,
the next week's summary says so.
