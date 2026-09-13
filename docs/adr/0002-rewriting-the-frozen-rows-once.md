# ADR 0002: Rewriting the frozen rows once, before the reports were shared

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

## Decision

Recompute every frozen row under the corrected engine, once, on 2026-09-13, and
rewrite both files in place. Specifically:

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

## Why this is not a precedent

The rule protects a record of what a reader was told. These reports had not been
shared with anyone: the first sharing is 2026-09-15. There was no record to
protect, and from 2026-09-15 there is one.

The three cases are also not the case the rule was written for, which is a number
that genuinely moved. A split card folded in half never measured anything, `Wear`
not being a card anyone registered. A return read off four lists of history was
a claim with no evidence behind it, not a measurement that later changed. And the
thin league days are the inverse of a dump filling in late: the dump filled in
normally and the capture was taken too early, which is a fault in the reading and
not news about the week.

A number that moves because the source published more is still frozen where it
stands, and this ADR does not license rewriting one. If a frozen row is wrong,
the next week's summary says so.
