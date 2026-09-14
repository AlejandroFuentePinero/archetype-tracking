# ADR 0005: Adding a watchlist row to the paper half of the storyline

Status: accepted (2026-09-14, extended the same day)

## Context

Every card row this project prints answers one question: did the field move. A
card earns one by swinging `TRACK_ADOPTION_DELTA`, a fifth of the population, so
by the time it prints it is established rather than new. Nothing reported the
other thing a pilot reads off a standings page by eye, that the good finishers
are registering a card the field is not.

Ketramose, the New Dawn in non-Fallaji Goryo's at RC Baltimore is the case that
raised it, and every existing gate refused it correctly. Against Spotlight
Dallas the swing is 6.7 points where the bar is 20. Against the fortnight to
2026-09-06 it is 3.3 points and 2.9 lists of evidence where five are needed. It
is not a watched slot, so it answers to the coarse bar. And `spotlight.findings`
has no return branch at all, by the design its docstring gives: a card absent
from MTGO for a month and present at Brisbane is the Australian field building
differently, not the deck rediscovering anything. The card is also not new,
having sat between 0 and 7 percent of the mainboards of every fortnight since
mid-June.

So this is not a threshold to loosen. It is a second reading, making a weaker
claim, with a bar of its own. See issue #11, and `CONTEXT.md` under **Novelty,
at a major paper event**, for the rule.

## Decision

A major paper event carries a watchlist row, computed fresh on every render and
never frozen. It is not a finding that the field moved and is phrased so it
cannot be read as one.

The part that needs an ADR is not the rule. It is that an already-rendered
report gains a storyline row it never carried.

Paper rows were never frozen. `timeline.csv` holds fortnight rows alone, keyed
by the bin they cover, and the paper half of the storyline is recomputed from
the cache on every render (ADR 0003). So no frozen row moves here and none is
rewritten, and `weekly.freeze` is untouched.

What changes is how an already-rendered report re-renders. Under ADR 0002 that
is a change of method, and a change of method under a reader is the thing the
append-only rule exists to prevent. ADR 0003 made the same kind of change on
2026-09-14 and closed by saying it was the last such change that might be taken
quietly. This one lands the same day, still before the first sharing on
2026-09-15, so it is inside the window where there is no reader. It is written
down here rather than taken quietly, which is what that sentence asked for.

## Consequences

Over the five cached events and all seventeen tracked decks the reading prints
seven rows, every one of them something no existing reading reports: a card an
adoption or watched-slot row already names is suppressed rather than printed
twice. Five fall at RC Baltimore, one at Spotlight Dallas and one at Spotlight
Brisbane. The strongest is Jennifer Walters in Devoted Combo sideboards, 3 of 7
good finishers at Brisbane and 5 of 14 at Baltimore, against no MTGO fortnight
above 7 percent: two events, two rooms, two months apart, and the MTGO
population is not playing it.

Ketramose does not print, at 2 of Goryo's 12 good finishers against a floor of
3. That is the ruling of 2026-09-14 and not an accident of calibration: the case
that raised the reading is refused by it, and the floor is what makes the rest
of the rows worth reading.

The MTGO bar is read over the fortnights that closed before the event and never
the one it falls in, which is the baseline rule `spotlight.chain` already reads
its own comparison by. This was wrong in the first cut and the numbers show why:
a bin part way through holds a few days of publication, so one list of two
registering a card reads as half the deck playing it and the card is refused as
something the deck knows. Two rows were being lost that way, Salvage Titan in
Affinity and Sunbaked Canyon in Boros Energy, both at Spotlight Dallas.

The four `TRACK_NOVELTY_*` constants are measured but unratified. They are
raised in `HEURISTICS.md` under **Proposed, awaiting pilot verdict**, with the
sweeps behind each and two questions left open: a floor on the cut population,
and a floor on the fortnights the peak is read over. A verdict that moves any of
them moves the row count, and after 2026-09-15 that is a change of method under
a reader and answers to ADR 0002 rather than to this window.

## Extension: the summary gains a clause, the same day

The row above reaches the storyline and nothing else. A reader who reads only
the summary, which is what the Tuesday meeting reads, never learns the reading
ran. This week that hides the strongest thing the paper data says about Devoted
Combo: Jennifer Walters in 5 of the 14 lists it put in Baltimore's top fifth
against 8 of its 59 over the event. It sat five thousand pixels down the page
with nothing above pointing at it.

So the weekly-report skill gains a clause. The fixed order goes from six clauses
to seven, the watchlist taking sixth place and the versions clause moving to
seventh. It goes after the paper clause rather than beside the MTGO innovation
clause it resembles, so that the two paper clauses stay together and the reader
meets the event's numbers before the cards read off it. The versions clause was
the right one to displace, being observability with no verdict.

Three things about the clause are worth writing down, because each was a choice:

- **It reads `novelties` on `major_events` and nothing else.** The storyline
  renders every event ever cached, so it currently shows seven rows where the
  reported week produced five. Devoted Combo's Brisbane row belongs to the week
  Brisbane was played, which is the same rule clause 5 already keeps: an event a
  week outside the reported week is the comparison and never the subject.
- **Every deck writes the clause, including the thirteen with no row.** A clause
  that appears only when it has something to say is a clause a reader cannot
  count on, and the whole reason the order is fixed is that a reader comparing
  two weeks compares the deck. The empty form says what it is saying it of.
- **The MTGO bar is printed and the other two are not.** Without it a row reads
  as a concentration; with it, as a card the deck does not play. The cut share
  and the concentration multiple are already carried by the words "the top fifth
  of the field" and by the two counts beside the card.

Seventeen summaries already written for the week to 2026-09-13 were rewritten to
carry the clause. That is the thing ADR 0002 forbids once there is a reader, and
it is taken here for the same reason as the row above: the first sharing is
2026-09-15 and this lands on 2026-09-14. No figure in any of the seventeen
moved, and no clause already written changed a word. Each gained one paragraph
in sixth place. After 2026-09-15 a clause added to the order changes the weeks
ahead of it, leaves the written summaries standing, and is announced in that
week's summary.
