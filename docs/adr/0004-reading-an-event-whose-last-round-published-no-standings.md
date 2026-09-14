# ADR 0004: Reading an event whose last round published matches and no standings

Status: accepted (2026-09-14)

## Context

`melee.final_round` took the last round the tournament page listed and read the
event's final ranking from that round's standings. It rests on an assumption the
page does not guarantee: that a round appearing in the selector has published a
field.

RC Baltimore broke it. The organiser bulk-published every round through the
Semifinals in a single second, 2026-09-13T23:43:36Z to 23:43:38Z, and never
published the Finals. The page still lists a Finals button, marks it
`data-is-completed="True"`, and serves the match from `/Match/GetRoundMatches`:
Curtis Lam on Devoted Druid Combo against Pete Ingram on Mono-Green Broodscale,
`HasResult` true, Ingram taking it two games to one. Only the standings grid is
empty, and `standings` refuses an empty field as data that has not arrived
rather than as a deck nobody played, which is right and is what blocked the
fetch.

So the fetch was blocked on a published event, by a round whose result is
published, in a grid the fetch did not read.

Three readings were available and two of them are wrong.

- **Wait for the organiser.** Publishing standings is a separate action from
  entering a result, and this organiser took it once across seventeen rounds and
  not again. Nothing is scheduled to arrive.
- **Fill the two rows in by hand.** The result is certain and public, and
  `spotlight.unread`'s refusal to recover a list by hand does not govern here:
  that rule exists because a hand-split 75 would enter a population every other
  member of which was machine-split, where a rank is recorded rather than
  derived and no method differs. The objection that does hold is narrower.
  `known` caches decklists by id, but rank and record are read fresh from the
  standings on every run, so a rerun of `event-fetch` reverts a hand-typed row
  in silence and a report's headline changes back with nobody having touched it.
- **Read the match.** The result is in the source. It costs one more endpoint
  and two rules.

## Decision

An event is read at the last round whose standings it published, and carried
forward by the matches of the rounds after it.

- **`final_round` walks back.** It returns the last round carrying a field, and
  the rounds the page lists after it.
- **`results` reads the pairings grid** for each of those, taking the winner
  from the games each competitor holds and not from `ResultString`, which is
  prose the site assembles for a reader. A match with no result, without two
  sides, or with the games level is not a before and an after and is left out.
- **`_advance` folds a decided match in.** The winner takes the win and the
  better of the two competitors' ranks, the loser the loss and the worse. That
  is exact for a playoff match, whose two players always hold two adjacent
  ranks, and the walk stops at the first later round that decided nothing, an
  event being read forward rather than in pieces.
- **Points, tiebreakers and game records are left alone.** Points stop at the
  end of the Swiss, which the standings confirm rather than assume: Lam's Swiss
  13-1-1 is exactly his 40 and Ingram's 12-2-1 exactly his 37, so three playoff
  wins each carried none. The other two are published and never persisted.
- **The payload says what it is.** `tournament.round` names the round the field
  was read at and `tournament.advanced` the rounds carried forward, so a file
  read short of its last round says so instead of passing as complete.

## Consequences

For every field the cache persists this is identical to what the organiser's
Finals standings would carry if they ever arrive: Ingram first at 15-2-1, Lam
second at 15-2-1, both on unchanged points. Ranks 3 through 1494 were already
settled at the Semifinals, checked by diffing that round against Round 15, where
the playoff had moved exactly eight teams. A later refetch is therefore a no-op
on every number rather than a correction, and nothing here has to be unwound.

It matters because both finalists are on tracked decks. `spotlight.reading` puts
rank and record in `top`, and the weekly summary leads its paper clause with
them, so read at the Semifinals alone the Broodscale report would have said the
deck that won the event came second.

No frozen row moves. Baltimore had never been fetched, and paper rows are never
frozen in the first place: `timeline.csv` holds fortnight rows alone and the
paper half of the storyline is recomputed on every render (ADR 0003). This is
new data arriving rather than a method rewriting a reading a reader was given,
so the append-only rule of ADR 0002 is not in play.

One hazard is opened that was closed before. An event fetched while its Swiss is
still running now caches as a complete event read at Round 7, where previously
it was refused outright. `standings` still raises where no round has published a
field at all, and the round read at is both printed by `event-fetch` and kept in
the payload, so the case is loud rather than silent. It is not prevented.
