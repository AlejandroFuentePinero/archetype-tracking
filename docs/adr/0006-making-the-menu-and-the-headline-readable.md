# ADR 0006: Making the menu and the headline readable

Status: accepted (2026-09-14)

## Context

A reader meets this project through two surfaces before they meet a number: the
index the Space opens on, and the headline at the top of whichever report they
picked. Both were failing the same job, which is telling a reader what is in
front of them.

The index was seventeen cards, each carrying a deck name and nothing else. The
week is in the header, so every card on the page says the same thing about the
same week, and a reader choosing one is choosing on the deck name and on what
they already knew before they arrived. Nothing the week produced reaches the
page that exists to hand the week out.

The headline was the opposite failure, too much rather than too little. The
skill said to name who finished, from `top`, which is every list that made the
cut. Broodscale put eleven in Baltimore's top 32 and three in China's, so its
headline ran to 71 words and fourteen pilots in one sentence, under a rule two
paragraphs further down the same skill that says the summary is read aloud in a
meeting and that six numbers in one sentence is a table.

## Decision

**Three names per event in the headline, and no more.** Where an event put more
than three lists in the cut, the clause leads with `cut_lists` and names the
best three: "RC Baltimore put eleven lists in the top 32, led by" and then the
three. The count is not optional. Naming three of eleven without saying eleven
reports the deck's event as smaller than it was, which is the opposite of the
failure being fixed, and the other eight are what the positional figure and the
numbers table are for.

**Each card on the index carries two figures**, both read off the facts file the
report was rendered from: the deck's MTGO top-32 share against the week before,
and its best paper finish named with the event it was made in. They are the two
halves of the report itself, one number each, which is what a card has room for.

Two things about the card are choices rather than consequences:

- **Neither figure gets a direction word.** Both shares are printed and a reader
  can see which way they went. "Down from" is a verdict, and the summary's
  clause 1 is where this project gives verdicts, under a rule about what counts
  as level that a menu card has no room to carry.
- **The paper finish is one event's and never the week's.** Where a week seats
  two regions the better finish is named with its own room, because two events
  on one weekend are two fields and a finish pooled across them is a finish in a
  room nobody played in. That is clause 5's rule, applied one surface up.

## Consequences

Three already-written headlines were rewritten: Broodscale from 71 words to 42,
Goryo's and Izzet Prowess from five names at RC China to three and the count.
No figure moved, no other clause changed, and the four names that stopped
printing are on the positional figure and in the numbers table of the same page.
This is a change of method on a written summary, which is what ADR 0002 governs,
and it is taken for the same reason ADR 0005's extension was: the first sharing
is 2026-09-15 and this lands on 2026-09-14, inside the window where there is no
reader. After 2026-09-15 a headline rule adopted changes the weeks ahead of it
and leaves the written summaries standing.

The deploy gains a third refusal. `site.build` already refuses a report still on
the pending line and reports that disagree on the week; it now also refuses a
report whose facts file is not beside it, because a card that cannot read its
figures would ship as a card that says less without saying why. The facts file
is written by the same `weekly` run that renders the HTML, so this only fires on
a `reports/` directory assembled by hand or left over from an older version.
