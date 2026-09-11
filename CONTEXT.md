# Archetype Tracking

A system that reads published MTGO and paper decklist data and reports named Modern archetypes fortnightly: how much of the field each holds, whether it converts that presence into finishes, and what its builds changed.

## Language

### Data source

**MTGO**:
Magic: The Gathering Online. The source of every weekly reading in this project. Melee is the only other source of decklist-level data and is never pooled with it.

**Melee**:
The tournament platform the major paper events publish on, and the second source of decklist-level data. It publishes what MTGO cannot: every finisher of an event rather than its top 32, with each player's match record. It also names modal double-faced cards `Front // Back` where MTGO names them by the front face, so the fold to the front face happens on fetch. Unfolded it is not a missing card but a missing archetype, every Blink list failing membership on Witch Enchanter with nothing about the result looking wrong.

**Spotlight**:
A paper tournament of several hundred players, entering the analysis by name in config rather than by a feed, the way `events.csv` works. Read entirely apart from the MTGO figures and never loaded into the store: the challenge-class readings are defined as every event class except league, so a Spotlight landing in `decklists` would be counted as challenge-class by default and nine hundred paper lists would swamp a weekly field of four hundred. It sits on the report's calendar as the week it was played in, keyed by that week's Monday and named by its Sunday, like every other week.

**Major paper event**:
Any paper tournament the pilot puts in `config.MAJOR_EVENTS`: a Spotlight, a Pro Tour, an RC. All are read the same way and share one section of the report and one figure. A storyline entry like any other, read against whatever came immediately before it, which is the paper event played since the last fortnight closed and the fortnight itself where there was none: MTGO moves what pilots take to a Pro Tour and a Pro Tour moves what turns up on MTGO the fortnight after. It gets its own row for the focus, not because it is a separate story. Its lists are never folded into a fortnight's own numbers: an event week sits inside a fortnight rather than beside one, so the two cannot be sequenced, and pooled it would be most of the bin. The MTGO response reaches the timeline by the calendar instead, the fortnight holding an event running on past it and the one after being read against that. It stays out of the store and out of the manabase reading.

**Constructed rounds**:
The rounds of a two-format event that were played in the format under analysis. A Pro Tour is six rounds of draft and ten of Modern under a single ranking, and its top 8 is a draft pod, so the deck is read at the end of the last Modern round: that is the last standing the Modern deck earned, and the playoff reorders the top 8 on limited results alone. The match record is those rounds alone, taken as the difference between the standings either side of each run, since melee publishes a running total. The finishing positions cannot be cleaned the same way and still carry the draft rounds, which is said wherever such a row is read.

**League**:
A continuous MTGO event. Only undefeated (5-0) lists are published, as trophy reports.

**Challenge**:
A scheduled MTGO tournament, often with hundreds of players. Only the top 32 lists are published.

**Event class**:
The kind of event a list was published under, kept exactly as the site publishes it: `league`, `challenge-32`, `challenge-64`, `challenge-96`, `showcase-challenge`, `showcase-qualifier`, `rc-qualifier`, `rc-super-qualifier`, `last-chance`.

**Challenge-class**:
Every event class except league: Swiss rounds, then publication of the top 32 with placement and Swiss points. The stratum that carries performance evidence.
_Avoid_: tournament (the payload's own word, which does not distinguish the strata)

**Swiss points**:
A pilot's points from the Swiss rounds of a challenge-class event, 3 per win, as published in the standings. Excludes the playoff entirely, so a winner may hold fewer Swiss points than someone who finished below them. See ADR 0001.

**Decklist**:
A single published list: mainboard plus sideboard, with pilot, date, and event attached.

**Pilot**:
The player who registered a decklist.

**Ingest index**:
The committed record of every published list the raw cache holds, one row each, kept at the list rather than at the event. The cache itself is too large to commit, so without this nothing in the repo says what the analysis history was built from and no run can tell its population from the last one's. The list is the grain because the unsettled days are the ones hardest to speak about: a league dump gains 5-0s through its own day, so a refresh overwrites captures it already held, and a record kept at the event would report those days unchanged while lists appeared inside them. Free of the archetype rule and of every other reading, since what membership makes of a list moves when the rule moves and what the site published does not: which arrivals are Goryo's is asked of the store afterwards, against the index rather than inside it. Withdrawals are reported beside arrivals, lists leaving the history quietly being the same failure as lists arriving quietly.

### Deck concepts

**Archetype**:
A family of decks recognised by its signature cards. Goryo's and Blink are the two here.

**Signature card**:
A card whose presence in a list identifies its archetype.

**Printing**:
One of the names the site publishes a single card under. Superior Spider-Man is the Marvel printing of Kavaero, Mind-Bitten, mechanically the same card, and a list is published under whichever its pilot registered. Printings merge to one card at ingestion and their copies are summed, before anything counts a configuration: a pilot registering both is playing a two-of, not two one-ofs.

**Goryo's**:
A Modern archetype: an Esper (WUB) list whose mainboard contains Goryo's Vengeance, Atraxa, Grand Unifier, Psychic Frog and Ephemerate, all four required. Ephemerate is in the rule because the other three are as at home in a Grixis reanimator deck as in this one: it is the blink half of the Esper shell, and the line the two versions fall either side of. Green sources for casting Atraxa do not change membership.
_Avoid_: Reanimator (broader family), Grixis Reanimator (a different archetype, and what the rule without Ephemerate lets in)

**Configuration**:
For a card in a list, the pair (mainboard copies, sideboard copies). The unit at which adoption is tracked: a main↔side migration is a configuration change even when total copies are constant. Deck-level counts (e.g. lands) are configurations of the list as a whole.

**Variant**:
A recognised camp within the archetype, defined by a divergence card. Currently: Fallaji camp (3-4 copies) vs non-Fallaji camp (0 copies); 1-2 copies is a hybrid experiment belonging to neither consensus. Consensus builds and novelty are computed per variant, never across camps. The weekly report calls a camp a **version of the deck**, that being the pilot's word for it, and prints the name in `config.VERSION_NAMES` where the rule's name is not the pilot's: the non-fallaji camp is the **Riddler** build. Display only. Everything else here, every identifier in the code and every stored record keys the camp by its rule name.

### Tracked decks

**Tracked deck**:
A deck the engine classifies and reports on weekly without optimising. It has no reference list, no hypotheses, no slot audit and no playtest queue: what it has is a fixed set of weekly figures and a change timeline, computed the same way every week for a team meeting to read. The tier is the point of the word. Goryo's answers to a pilot who plays it and to a submission date; a tracked deck answers to neither, and reading one with the other's instruments would put an engine's guesses where a pilot's knowledge belongs.
_Avoid_: archetype on its own (Goryo's is one too, and the difference between them is the whole distinction)

**Blink**:
The tracked Modern archetype: a mainboard holding Phelia, Exuberant Shepherd, Flickerwisp, Overlord of the Balemurk and Witch Enchanter, all four, and no source that produces red or green. The four are required together because no smaller set is the deck: Phelia alone admits a white energy build and a Boros build, and Ephemerate alone is half Goryo's. Membership is tested after Goryo's, so a list holding both signatures takes one name and it is Goryo's.

**Off-colour exclusion**:
The colour half of Blink's membership rule. A Mardu build shares all four signature cards and is a different deck, so a mainboard source that actually produces red or green puts a list outside the archetype rather than into a third variant. Read on sources and never on fetchlands, most of the Orzhov half fetching with Flooded Strand, which produces neither. The rule is a hand-written list of card names and is the one part of membership that can go stale silently, so the count it turned away is printed every week: a red build on a source nobody listed would otherwise read as a member and nothing would say so.

**Esper Blink / Orzhov Blink**:
Blink's two variants, split on mainboard Watery Grave. Presence and not a count, a variant here being which colours the deck is, which one copy settles. The card partitions the archetype exactly, where a rule drawn on blue sources throws away the Orzhov lists that fetch and one drawn on blue spells drops any Esper list that cut Teferi. Every reading in the weekly report is the Esper variant alone; Orzhov is carried as bare numbers in the summary, its challenge-class population being single figures over the whole post-regime history, which is enough to say it exists and nowhere near enough to read a build or a conversion rate off.

**Report subject**:
What one weekly report is computed over, named once in `config.REPORTS` rather than passed as a flag. It fixes the archetype, the camp the volume and performance figures are pooled over, the camp the build readings are taken on, and the slots it watches. One subject per directory under `data/tracking/`, because a pooled row and a one-camp row in the same `weekly.csv` are two measurements under one column heading and nothing in the file says which a row is. Kept apart from the membership rules: a rule says what a list is, a subject says which of those lists a report reads, and Goryo's has a rule already without being a tracked deck.
_Avoid_: deck, where the population is what matters (Blink is one deck and one subject; Goryo's is one deck read as two populations)

**Pooled camps**:
Every camp of an archetype counted as one population, which is what the volume and performance figures of the Goryo's report are taken over. A metagame share is a share of the whole deck, and read on one camp of three it answers a third of the question. Never the build readings: pooled, a card at nine tenths of one camp and none of another reads as the deck at half of it, and a camp arriving reads as the deck changing its mind. Goryo's pooled looks like it drifted a copy of Quantum Riddler over the regime, where inside the non-fallaji camp the card is flat at four.

**Build camp**:
The one camp a subject's storyline, goldfishing figure and Spotlight findings are read on, where its weekly figures may be pooled. The non-fallaji camp for Goryo's, the Esper variant for Blink. Labelled in the report wherever the two populations differ, because the figures above a storyline row would otherwise put a list count beside it that the row was never read against.

**Week**:
Monday to Sunday, the bucket every weekly reading groups on. Keyed by its Monday wherever it is stored, that being what the store's `date_trunc` returns and the name every frozen row and summary file carries. Named by its Sunday wherever it is read, on the report's header, its table and the x-axis of every figure, because a week labelled with the day it opened reads as the day the data stops and puts the reader a week behind the figures.

**Detection bin**:
The fortnight a change is read over, anchored at the regime boundary and never overlapping. A week of this deck runs from nine published lists to sixty-four, so a threshold set as a share of a week measures the sample size: at every bar from five points to twenty-five a weekly reading reverses in the next week about two times in five, and raising the bar loses findings without buying purity. Over a fortnight the same bars reverse between fifteen and twenty-two percent of the time and the rate falls as the bar rises. The plots stay weekly; only the detection is binned. Anchored rather than trailing, so the bin a date falls in never moves and a row written six weeks ago still describes the same fortnight.

**Returning card**:
A card appearing in a bin having been out of the deck for `RETURN_ABSENCE_DAYS`, at a share larger than it has ever held. Three conditions and each drops a different false one. The absence is a month rather than a fortnight because a staple running at a few lists a week misses a fortnight on chance alone: Orcish Bowmasters, a card of ninety-eight lifetime appearances, reads as a return at the shorter window. The gate is per zone because a sideboard churns far harder than a mainboard. And the share has to beat the card's own peak, which is what separates a card the field turned to from one that was always a one-off and is a one-off again. Read against the whole store rather than the post-regime window, since how long a card has been gone is a fact about the deck and not about the regime; a window starting at the boundary calls every card of the opening fortnight new.
_Avoid_: fringe card (the archetype-level reading, which is a share of a whole history rather than an absence)

**Board migration, as a timeline row**:
A returning card that was in the other zone the bin before. Read one zone at a time it is new to the mainboard, which is true and reads as novelty, so the row says which it is: a sideboard staple being promoted is a decision about what the card is for, not the deck discovering it.

**Copy drift**:
The mean copies of a named card, over the lists that register it, read fortnight to fortnight as a timeline row. The reading for the slots the deck argues about the number of rather than the presence of, which no adoption share can see because those cards sit at near-total adoption. Read on the mean and never the mode: on this deck's cards the modal count oscillates every other week and every oscillation reverses, a plurality one pilot can flip holding it. The cards are named in config rather than found by a scan, so the timeline reads the same slots every fortnight and a card arriving is a decision somebody made.

**Watched slot**:
A slot named in a subject's `watch`, read at ten points rather than twenty and by copy count rather than by presence. It answers the question a mean cannot: two copies going to three in a fifth of the camp moves a mean over eighty lists by three tenths of a copy, under any bar a copies reading can hold, where the same decision read as a distribution is a fifth of the lists moving from one row to another. The finer bar holds only because the list is short and every entry on it is a question the pilot asked: unfiltered at ten points this population gives 78 rows across eight fortnights against 41 at twenty, and 38% of them reverse in the next fortnight either way. Read here and nowhere else, the ordinary adoption reading skipping a watched slot, so one decision earns one row.
_Avoid_: copy drift (the mean reading, which a watched slot replaces rather than joins)

**Manabase reading**:
The land count read as a configuration of the whole list, fortnight to fortnight, at the standard bar. The reading no card-level one can stand in for: the land a camp adds is a different card in every list, so a camp walking from 21 lands to 22 moves no card's adoption and no card's copies, and read card by card the decision is invisible. MTGO only, a melee decklist page being fetched for its cards and not its type headings, so a paper list carries no land count to compare. Recoverable at the price of refetching every decklist page, the headings being on the page.

**Goldfishing**:
The share of a week's builds whose mainboard is identical to the previous week's most-registered mainboard, which is to say how much of the field is copying rather than building. A build is one pilot's one 60, counted once however many times they published it: a league dump publishes every 5-0, so read per publication one grinder entering a lot of leagues reads as the field copying, and the reading inverts. The week to 6 September is the case, Esper Blink publishing 69 lists on 27 distinct mainboards where those 69 are 57 distinct pilot builds and only four mainboards have a second pilot behind them. The direct reading of whether a deck is still being built, where every other reading answers it only by absence: a week nothing moved in looks the same whether the field stopped building or the field was quiet. High is neither good nor bad. It is also the warning that such a week is not the sample its list count claims, the evidence in it being closer to its distinct builds than to its lists. The reference is the most-played list of the week before and never the winning one: a week's best finish is one list, where what this counts is what the field converged on. Mainboards only, the sideboard being the part of a copied list a pilot changes first.

**Spike**:
A week's volume at twice both of the deck's own baselines: the median of the four weeks behind it, and the median week since the bans. A deck at several times its baseline is being copied, and a performance figure taken over it measures adoption density rather than the deck, which the report has to say in the week it happens. Both baselines, because either alone misreads a different week. Against the regime median alone a deck that moved to a new level never stops spiking, the median staying held down by the months before it got there: Esper Blink ran 27, 33, 36 and 43 finishes on four consecutive weeks against a median of 10 and flagged on all four. Against the trailing median alone a thin stretch turns one challenge weekend into a spike: Blink's four weeks to 3 August ran 2, 4, 8 and 6 lists, where a week of 10 is that deck's ordinary week and doubles the trailing median.
_Avoid_: elevated, of a level a deck has held for weeks (the banner's word, and it means the departure and not the height)

**Unread list**:
A published paper list whose boards did not separate, so membership cannot be tested on it. Melee groups a decklist page under type headings and the fetch splits on the heading, so a sideboard filed under one the fetch does not know puts the whole 75 in the mainboard. Membership being a mainboard test, such a list would join an archetype on a parse failure, on cards its pilot only sideboarded. Counted and reported rather than dropped silently, so a fetch that starts failing shows up as itself rather than as an archetype quietly gaining or shedding lists. Three exist across Brisbane and Dallas, at 75, 76 and 146 cards. A list on 60 with no sideboard is a pilot who registered none and is read normally.

**Field share, against cut share**:
The two shares a Spotlight yields, and the difference between them is why paper and MTGO figures never share an axis. A challenge publishes its top 32, so every MTGO share in this project is already a share of a cut. A Spotlight publishes every finisher, so its field share is a true metagame share and has no MTGO counterpart at all. Only a Spotlight's own top-32 share is the quantity `chal_share` carries, and it is printed with its count, thirty-two slots being a handful of lists.
_Avoid_: presence, on a Spotlight (the weekly word, which means the cut share and would read as the field one)

**Finishing share**:
Where a list placed, as the share of the field that finished above it: nought is the winner and a half is the middle of the room. The positional unit, because rank is not comparable between events of different size, rank 300 being the top third of a 932-seat event and past the halfway mark of a 574-seat one. In these units a deck whose lists are spread evenly through the standings reads as the diagonal, which is the null every positional figure is drawn against.

**Conversion, at a Spotlight**:
The deck's share of the top 32 over its share of the whole field. Above one it held more of the cut than of the room, which is the honest performance reading and is comparable between events of different size. The reading MTGO cannot make, its challenge data being a cut with no field under it to divide by.

**Cross-population reading**:
A comparison whose two sides are different rooms: an Australian paper field, an American one and the MTGO field are three populations. A card at nine tenths of one and half of another is not the deck changing its mind, so a row spanning two of them is marked as one. A paper event read against the fortnight before it is such a row; one read against the paper event a week earlier is not, holding the format and the medium constant, and it is the stronger of the two. Marked rather than suppressed: the rooms are not decoupled, and a reader told which room each side came from can weigh the row.

**Frozen row**:
A week's figures or a fortnight's findings, written once and never edited. The store is rebuilt from the cache on every run and a past week can genuinely move, a league dump gaining trophies through its own day being the usual reason, so the report renders what was reported rather than what the store now says. Appended and never rewritten: a history that can be rebuilt is a history that can come to disagree with itself, and a timeline nobody can cite is not a timeline.

### Pilot knowledge

**Heuristic**:
A piece of MTG expertise supplied by the user (gained from play, not derivable from data) that informs how the data is interpreted. Captured persistently so the co-intelligence improves across sessions. About how the numbers are read and never about what a card does: knowledge about a card steers one reading, and filed here it would steer every reading in the project.

**Heuristic candidate**:
A heuristic the agent inferred rather than the user stating it, including one raised against an adopted heuristic the evidence now contradicts. Staged with the evidence that raised it and never treated as knowledge; it becomes a heuristic only on an explicit verdict from the user, and expires unratified.

### Analytical concepts

**Regime change**:
A Modern B&R change or meta-warping set release that resets the relevance of prior lists. Lists on either side of a regime boundary belong to different eras and are not directly comparable.

**Meta share**:
The fraction of published winning lists an archetype occupies over a time window. A proxy for true field share, since only the winning portion of the field is visible.

**Adoption**:
For a configuration, the share of a population's lists that registered it. The population is one camp, in one stratum, over one window, and never a blend of them: the same configuration reads differently in each, and a share over two of anything is a number no population reported. Deck-level configurations, such as the land count, are read the same way.

**Top-32 truncation**:
The visibility bias: challenges publish only the top 32, leagues only 5-0s. Losing lists never appear, so all analysis is conditioned on success.

**Herd adoption**:
Many pilots converging on a recent winner's exact list. Looks like consensus; is largely copying, and inflates belief in that configuration's optimality.
