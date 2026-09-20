# ADR 0008: Counting returns in pilots, and what ADR 0002 protects

Status: accepted (2026-09-21)

## Context

Two readings changed method on 2026-09-21, both by pilot verdict, six days into
having a reader. ADR 0002 says a change of method under a reader changes the
fortnights ahead of it and leaves the frozen ones standing, so both were put to
Alejandro against that rule before either was built.

**The return gates counted lists.** A return row needed 2 lists in the mainboard
or 3 in the sideboard, the lowest list floor in the project. A league publishes
every 5-0, so a grinder entering with a brew is several lists of it in one
fortnight, and read as lists that is the deck picking a card up when one player
did. Four of the 20 return rows frozen in the Izzet Prowess timeline were one
pilot, SightWinner, across three league lists on 15, 19 and 25 June: Jeskai
Ascendancy, Legion Leadership, Light Up the Stage and Murktide Regent. Jeskai
Ascendancy has never been registered by another Prowess pilot, before or since.
This is the inversion `goldfishing` already reads per pilot per 60 for, and the
league stratum heuristic already keeps a per-pilot cap for, and the return
reading was the one place with neither.

**A thin fortnight could set the novelty bar.** The paper watchlist refuses a
card the deck's MTGO history has held above 10% of a fortnight in that zone.
`mtgo_peaks` already passes over the open bin an event falls in, because one
list of two registering a card reads as half the deck playing it and silences
the row. A closed bin of two lists does exactly the same thing and was not
covered.

## Decision

**ADR 0002 protects a stable system, not a system still being built**
(Alejandro, 2026-09-21). Its rule exists so that the metrics do not move with
every build once they are settled. Six days in, with the readings still being
calibrated against their first real use, a frozen row computed under a method
since ruled wrong is not a record worth protecting. The append-only rule holds
for numbers that genuinely moved, which is what it was written for, and a method
ruled out by the pilot may be withdrawn from the frozen files with the pass
recorded here. When the readings stop moving, ADR 0002 reads as written.

**The return gates count distinct pilots, at 2 and 2.** The sideboard's 3 did
not carry over. It was calibrated on list volume, so read in pilots it tightens
the bar rather than restating it: over the 289 frozen return rows, 2 and 2
withdraws the 63 that rest on a single pilot, where carrying the 3 across
withdraws 96 and takes 33 rows that two or more pilots registered. Jeskai's
Counterspell in the bin to 14 June is one of the 33, Valident on 8 and 10 June
and iSteze on the 13th. The row still names its lists, which is what every other
row here counts; the pilots decide whether it prints.

**A fortnight under `TRACK_NOVELTY_PEAK_LISTS` cannot set the novelty peak**,
at 10 lists, the floor the storyline's own card-level rows already answer to. A
card held only in such bins has no peak and reads as one the deck has not been
playing.

**No floor on the cut a novelty is read over.** Proposed beside the peak floor
and refused: a flat floor of ten good finishers silences whole decks at whole
events rather than bad rows. The top fifth gives non-Fallaji Goryo's 8 lists at
Amsterdam, 6 at Brisbane, 12 at Dallas and 12 at Baltimore, so the deck the
reading was built for would carry no watchlist row at two of the four events
cached. A row off a small cut is refused on concentration or it is not refused.

## Consequences

`timeline.csv` alone, 63 rows withdrawn across 14 of the 17 reports: storm 8,
tron 7, energy 6, jeskai 6, blink 5, oswald 5, ponza 5, livingend 5, dimir 4,
prowess 4, zoo 4, affinity 2, broodscale 1, devoted 1. Goryo's, Simic Neoform
and Trudge hold no row that rests on a single pilot and were not touched. No bin
was left without a row, so none had to fall back to `stable`. No weekly figure
answers to either change and none moved.

The withdrawal was computed as a difference on today's engine: the same
storyline built twice, once gated on lists and once on pilots, and only rows in
the difference were removed. A row that has moved since it was frozen for any
other reason cannot have been caught by it, and no row was rewritten or
reordered.

The novelty rows were never frozen. They are recomputed from the cached event
JSON on every render, so the paper storyline on the five published event pages
moves under the peak floor whether or not a file is touched. That is a change a
reader can see and this week's summaries say so.

Both changes are announced in the summaries for the week to 2026-09-20, which is
the remedy ADR 0002 names for a frozen row that was wrong.
