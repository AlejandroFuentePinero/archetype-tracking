# ADR 0003: Reading a major event against both entries behind it

Status: accepted (2026-09-14)

## Context

The storyline is one chain. Every entry is read against whatever came
immediately before it, and a major paper event is an entry like a fortnight is.
`spotlight.chain` implemented "immediately before" as a choice of one: the paper
event before it where that event was played after the last fortnight closed, and
the last closed MTGO fortnight otherwise.

The weekend of 2026-09-12 broke the assumption the choice rests on. Two Regional
Championships were played on it, Baltimore and China, in two rooms on the same
day, and the paper event before them, Spotlight Dallas, fell in the last week of
the fortnight they are read back to rather than after it.

Three things followed, and each is a different fault:

- **An event that followed another paper event lost its MTGO baseline.** The
  rule kept whichever entry was later and discarded the other. Spotlight Dallas
  was read against Spotlight Brisbane alone, so nothing in its storyline said
  whether the MTGO field the deck came from had already moved the same way.
  The two baselines answer different questions and only one was ever asked.
- **Dallas did not qualify as the paper entry for either Championship.** Its
  week closed on 2026-09-06, the same day the fortnight it sits in closed, and
  the test was a strict `>`. So both Championships were read against the
  fortnight alone and the nearest paper event, one week earlier and the same
  medium, went unused.
- **The two Championships would have been read against each other.** Whichever
  was configured second took the first as the entry before it. An American field
  and a Chinese field played on one day are two rooms rather than a before and
  an after, and such a row reports the distance between them as a weekend's
  worth of change.

## Decision

An event is read against both entries behind it, and never against one played in
its own week.

- **The MTGO fortnight always.** Every event gets the last closed fortnight as a
  baseline. It is a cross-population reading and is marked as one, as before.
- **The paper event as well, where it is close enough to be the entry before.**
  The latest event of an earlier week qualifies when it was played no earlier
  than the baseline fortnight opened. Further back than that the two sides span
  different stretches of the season and the row would report a quarter's drift
  as an event's.
- **Never an event of the reading event's own week.** Two Championships on one
  weekend are each read against Dallas and the fortnight, and neither against
  the other. The chain sorts its events rather than trusting the configured
  order, so which of two same-day events is listed first decides nothing.
- **Ordered strongest first.** The paper row holds the format and the medium
  constant and is the stronger of the two, so it leads, and the entry's own
  `against` is that comparison rather than a third copy of one. The storyline
  prints one row per comparison, each saying what it read against.

Dallas falling inside the fortnight it is a baseline beside is not a double
count. A major event's lists are never folded into a fortnight's own numbers and
never enter the store, so the two baselines share no list.

## Consequences

Paper rows were never frozen. `timeline.csv` holds fortnight rows alone, keyed
by the bin they cover, and the paper half of the storyline is recomputed from
the cache on every render. So no frozen row moves here and none was rewritten.

What does change is how an already-rendered report re-renders. Spotlight Dallas
gains a second storyline row, against the fortnight to 2026-08-23, which it
never carried. Under ADR 0002 that is a change of method, and a change of method
under a reader is the thing the append-only rule exists to prevent. The first
sharing is 2026-09-15. This lands on 2026-09-14, in the window where there is no
reader, and is the last such change that may be taken quietly.

## The same rule, the other direction

Taken the same day, on Alejandro's ruling, once the event side was working.

A fortnight had the mirror of the fault. `timeline.findings` read a bin holding
a major event against that event and dropped the fortnight before it entirely,
and where two events fell in one bin it kept the later of them. So the fortnight
to 2026-09-06 never said whether the MTGO field had moved on its own terms, and
the fortnight to 2026-09-20 would have been read against one Championship picked
by sort order.

A fortnight is now read against every entry behind it, one row each: the
fortnight before, then each event that fell inside it, in the order they were
played. The fortnight before leads, because it holds the medium and the room
constant and is the only reading of the set with no caveat on it at all, where
on an event the paper comparison leads. Two events in one bin stay two rows:
pooled into one baseline an American field and a Chinese one are a share neither
room reported, which is the rule that motivated this ADR in the first place.

The dated marks a bin carries ride on its first row alone. They say what
happened inside the fortnight rather than what it was read against, and repeated
under every baseline one ban would enter the storyline three times.

Frozen rows stand. `freeze` skips a bin already on file, so the fortnight to
2026-09-06 keeps its single comparison against Spotlight Dallas and does not
gain the two this rule would now give it. The storyline therefore shows one
comparison there and three below it, which is the append-only rule working
rather than an inconsistency to repair.

## Settled since (2026-09-14)

`weekly._paper` gave the summary the first event whose week was the reported
week. The week ending 2026-09-13 holds both Championships, so the paper clause
of that report would have named one of them and nothing in the file would have
said the other was played.

It now gives every event of the week, under `major_events` rather than
`major_event`, and the skill's clause 5 takes one sentence per entry. Side by
side and not pooled, for the reason this ADR already gives: two rooms on one day
are two fields, so a share across both is a share of a field nobody played in.

The comparison row moved with it. It used to be the chain entry before this one,
which for the second of a weekend's two events is the first of them, a row the
entry was never read against. It is now looked up by the label the entry's own
comparison names, so an event read against the MTGO fortnight carries no paper
row and says so with a null.
