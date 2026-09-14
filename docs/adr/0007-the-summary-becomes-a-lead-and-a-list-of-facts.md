# ADR 0007: The summary becomes a lead and a list of facts

Status: accepted (2026-09-14)

## Context

The summary is the part of the report that gets read. The Tuesday meeting reads
it aloud, and everyone who was not there reads it on a screen instead of
scrolling five thousand pixels of figures. Since ADR 0005 extended the order it
had been eight paragraphs of prose in a fixed sequence, and the sequence was the
point: a reader comparing two weeks was comparing the deck rather than comparing
two pieces of writing.

Eight paragraphs is the wrong shape for that job. Prose is read start to finish
or not at all, and a reader who wants the paper result is reading four
paragraphs of MTGO to reach it. Worse, the fixed order was being paid for twice.
It forced a paragraph for every reading whether or not the reading found
anything, so thirteen of seventeen decks carried "Nothing reached the watchlist
at RC Baltimore or RC China" and thirteen carried "The deck has one population,
so there are no other versions to report." Those are sentences whose content is
that nothing happened, and a reader who learns to skip one skims the rest.

The index was fixed for the same class of problem one day earlier (ADR 0006).
This is the surface behind it.

## Decision

The summary is a lead of one or two sentences, then the week's facts as bullets,
each opening with a bold label. The order of the bullets is fixed as the clause
order was: MTGO, conversion, build, one per paper event, watchlist, other
versions.

**A bullet only appears when it has something to say.** This is the part that
reverses a decision rather than reshaping one. ADR 0005 argued that every deck
should write the watchlist clause, empty or not, because "a clause that appears
only when it has something to say is a clause a reader cannot count on." That
reasoning holds for prose, where an absent paragraph is invisible. It does not
hold for a labelled list, where the labels present are themselves the index of
what the week produced, and where a bullet reporting that a reading found
nothing is the exact thing that teaches a reader to skim. The storyline further
down still renders the reading on every week it ran.

The two MTGO volume clauses merge into one bullet. They were always one reading
split across two paragraphs: the week against last week, and the week against
both its medians. A bullet can hold all three figures without becoming a table.

**The lead leads with the result, not the mechanics.** "Broodscale won RC
Baltimore" and "Nothing in paper" are leads. "RC Baltimore put eleven lists in
the top 32" is a figure, and figures now have somewhere to go. The three-name
cap from ADR 0006 is unchanged, and so is the rule that a count accompanies it
where more lists made the cut.

The renderer gains `weekly.summary_html`, which reads a `- ` block as a list and
anything else as a paragraph, with `**bold**` inside either. That is the whole
markdown it supports, and it is deliberately not more: the file's job is to be
read aloud in a meeting, not to be a formatting language.

Separately and for the same reader, the index dek loses its 560px cap. A 700px
sentence inside a 940px page was wrapping mid-phrase and reading as though it
had been cut off.

## Consequences

All seventeen summaries for the week to 2026-09-13 were rewritten. Every figure
was carried across unchanged and each was traced back to its facts JSON after
the rewrite; each page now round-trips to its summary file exactly. Grinding
Station goes from eight paragraphs to a lead and five bullets, Broodscale to a
lead and six. Ninety-four bullets render across the seventeen.

This is a rewrite of already-written summaries, which is what ADR 0002 forbids
once there is a reader. It lands on 2026-09-14 and the first sharing is
2026-09-15, so it is inside the same window ADR 0003, 0005 and 0006 were taken
in, and it is the last change that window will carry. From 2026-09-15 a change
to the summary's shape changes the weeks ahead of it, leaves the written
summaries standing, and is announced in that week's summary.

The `weekly-report` skill is rewritten to the new format, so this is what gets
written every Monday from here. The clause vocabulary is gone from it: what were
clauses 1 to 7 are now named bullets, and the handover checklist gained a line
saying no bullet may report that a reading found nothing.

What this gives up is countability. A reader who wants to know whether the
watchlist reading ran on a deck that produced no row now has to look at the
storyline rather than read it off the summary. That is the trade ADR 0005 called
the other way, and it is called this way here because the reader it was
protecting was hypothetical while the thirteen empty lines were on every page.
