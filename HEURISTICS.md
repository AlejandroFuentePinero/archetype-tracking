# MTG Heuristics

Pilot-supplied knowledge from long-term play, not derivable from the data.
Each entry: the heuristic, why it holds, and how it changes the analysis.
Source is Alejandro unless noted. Dates are when captured.

## Tournament structure

**Challenge participation is expensive** (2026-08-07):
A challenge is a ~10-hour tournament; availability caps how often even
dedicated pilots play. Frequency thresholds must stay modest.
*Applies*: proven pilot = 2+ challenge top-16 Goryo's finishes in the baseline
window, not more.

**One deck per pilot in a challenge; a league day can trophy the same pilot
twice** (2026-09-11):
A challenge-class event is one entry per player, so a pilot appears in its
standings once and his list is his whole showing. A league is continuous: a
pilot can run it repeatedly in a day and publish a 5-0 each time, so a league
dump can carry several lists from one name, and they may not be the same 75.
*Applies*: in the challenge stratum (event, pilot) identifies a list, so counting
lists is counting pilots and no de-duplication is owed. In the league stratum it
does not, so a rate reading there is counting a grinder's session: keep the
per-pilot cap on the conversion gap and on any share read as pilots holding a
configuration. Raw trophy volume per week is the deliberate exception and is
never capped, since what it measures is how much of the league stratum the deck
occupies and a grinder's repeat trophies are part of that occupancy. It is also
why the ingest index diffs as a multiset: two identical league rows are two
lists, not one filed twice.

**A lone dissenting regular beats herd convergence as evidence** (2026-08-07):
Mass adoption of a winner's 75 inflates belief in it (goldfish copying). A
single pilot who goes against the hype with a different configuration and does
well repeatedly is stronger grounds for a hypothesis than the herd's converged
numbers.
*Applies*: pet-tech flags classify rather than discount; dissenter patterns
auto-raise hypothesis candidates.

**Top-8 is mostly tiebreakers; top-16 is the real cut** (2026-08-07):
In MTGO challenges the top-8/9-16 boundary usually separates identical 4-2
records on breakers, not performance. Top-16 vs 17-32 is the meaningful
performance stratum.
*Applies*: normalized Swiss points are the primary performance lens; when a
placement band is needed, cut at top-16 / 17-32, never top-8 / rest.

## Card evaluation

**Cards are only evaluable in deck context** (2026-08-07):
In general, a card's value depends on the whole deck structure, so raw
single-card adoption stats mislead. They are acceptable for Goryo's right now
only because the shell is heavily optimised and just a few flex slots move.
*Applies*: single-card adoption tables are valid for this archetype this
season; re-examine before reusing the pipeline on another archetype. Card-pair
co-occurrence is tracked as a cheap partial guard.

## Archetype knowledge

**Goryo's forks on Fallaji Archaeologist, and non-Fallaji is the one we track**
(2026-09-11):
Current Goryo's builds split into a Fallaji Archaeologist camp (3-4 copies)
and a non-Fallaji camp (0 copies). These are divergent construction
directions, not flex-slot drift; the non-Fallaji build is the more stable of
the two and is the primary camp. Lists on 1-2 copies are hybrid experiments,
innovation probing in both directions, and belong to neither consensus.
*Applies*: consensus builds, novelty deltas, and slot comparisons are computed
within-camp; hybrids are flagged as innovation, excluded from camp consensus.
The camp ratio over time is a tracked signal. In the weekly report the camps are
pooled for volume and performance, a metagame share being a share of the whole
archetype, and every build reading is the non-Fallaji camp's.

**Goryo's argues about its manabase: 21 lands against 22, and Hedge Maze over
Breeding Pool** (2026-09-11):
The live construction questions in the deck are how much land it runs and which
dual fills the last land slot, not which spells it plays. Both are
one-card decisions that no adoption share and no mean copy count can see: the
land added is a different card in every list, and the duals are one-ofs swapping
places.
*Applies*: the weekly report reads the land count as a configuration of the whole
list, so a camp walking from 21 to 22 earns a timeline row. Hedge Maze and
Breeding Pool are watched slots, read at ten points rather than twenty, because
the move that matters is smaller than the ordinary bar: non-Fallaji Hedge Maze
went 11% to 30% in the fortnight to 6 September, which the twenty-point bar
missed by one point.

**Simic Neoform is four cards, and Planar Genesis is the one that names it**
(2026-09-12):
Membership is Neoform, Allosaurus Rider, Eldritch Evolution and Planar Genesis,
all four in the mainboard, with no count and no colour rule. The four-colour
Glittering Wish build on Gemstone Mine plays the first three and never Planar
Genesis, and it is a different deck. Raised from the data and adopted by
Alejandro on 2026-09-12: of the 471 MTGO lists since February mainboarding any
of Neoform, Allosaurus Rider or Planar Genesis, 439 answer to all four.
*Applies*: the rule stands as written in `config.TRACKED_DECKS`; the Glittering
Wish lists stay outside the population.

**UW Oswald is Oswald Fiddlebender with Grinding Station, and a green splash
is the same deck** (2026-09-12):
The deck to track is the blue-white build on Grinding Station and Oswald. The
Tezzeret and Krang build shares Oswald, Emry and the Saga shell without the
Station and is a different deck. A green source in an Oswald list is a splash,
usually for Haywire Mite, and does not make it another deck.
*Applies*: membership is the two cards in the mainboard with no colour rule, so
the 18 of 56 lists since the bans on one Breeding Pool stay in. One population,
no versions.

**Domain Zoo forks on Psychic Frog, and the traditional version is the one we
track** (2026-09-12):
Two versions: the bluer build on Psychic Frog and the traditional one. Being
five colours the deck moves a lot, and that is expected rather than a finding.
Frog was first chosen on the perception that Frog with Quantum Riddler had
become the popular build; the data said otherwise (Frog 13 of 85 MTGO lists
and 6 of 22 at Spotlight Dallas since 10 August, every list since 7 September
traditional, and Riddler in four fifths of traditional lists), so the tracked
version moved to traditional the same day.
*Applies*: membership is Territorial Kavu and Scion of Draco with no colour
rule. The version rule is mainboard Psychic Frog. The report reads the
traditional version for conversion, goldfishing and the storyline; the Frog
version is a bare count and a line on the presence figure's version panel.

**Broodscale has three versions, and the most popular one is tracked**
(2026-09-12):
Mono-green; Gruul, on red cards like Unholy Heat and Writhing Chrysalis; and
Lab, on Devourer of Destiny and Ugin's Labyrinth over the mono-green shell.
Which to track was left to the data: in the week to 13 September the Lab
version was 73 of 84 lists and 33 of 37 swiss-like finishes, having been level
with Gruul over the regime as a whole.
*Applies*: the version rule reads the red spells first, then Ugin's Labyrinth,
and a list on neither is mono-green. A list on both is Gruul. The report reads
the Lab version, and moving it to another version is Alejandro's call, since
it invalidates every frozen row under `data/tracking/broodscale/`.

**Affinity is Kappa Cannoneer with Weapons Manufacturing and Engineered
Explosives** (2026-09-12):
The deck runs Weapons Manufacturing, Kappa Cannoneer and Engineered Explosives
as four-ofs. The Krang, Tamiyo and Song of Creation artifact decks share Kappa,
Pinnacle Emissary and the Urza's Saga shell, and cards like Song of Creation
and Undercity Sewers have nothing to do with Affinity. The report is called
Affinity, not Grixis Affinity.
*Applies*: Weapons Manufacturing and Engineered Explosives join the two
creatures in the mainboard signature. The 34 lists since the bans without both,
16 of them in the fortnight to 6 September, leave the population; that rise is
what put Song of Creation and Undercity Sewers in the storyline as arrivals.
One population, no versions.

**Izzet Prowess is only the blue and red deck** (2026-09-12):
The deck is Izzet: Cori-Steel Cutter, Dragon's Rage Channeler, Mutagenic
Growth, Slickshot Show-Off and the rest of the blue and red shell. The red and
Boros prowess lists on Lava Spike and Skewer the Critics share the creatures
and are a different deck.
*Applies*: Steam Vents joins the three creatures in the mainboard signature.
Every Izzet list since the bans runs it, and the 32 lists with no blue card,
19 of them with white, leave the population. One population, no versions.

**Ephemerate is part of what makes the deck Esper** (2026-08-07):
The trio alone (Goryo's Vengeance, Atraxa, Psychic Frog) admits Grixis
reanimator builds, which are a different deck with a different manabase, a
different gameplan and no bearing on this 75. Ephemerate is the blink half of
the Esper shell and the line the two versions fall either side of.
*Applies*: Ephemerate joins the mainboard signature cards, so membership is the
four and not the three. Grixis lists leave the archetype's population entirely;
those that keep Goryo's Vengeance land on the near-miss watchlist, which is
where a different construction direction belongs.

## Data interpretation

**Presence is the whole deck; performance and builds are the tracked version**
(2026-09-12):
A metagame share is a share of the whole deck, versions included, so presence
is read pooled for every report. A finish, a copied list or a card moving is a
fact about one build, so conversion, goldfishing, the storyline and the numbers
table are read on the tracked version alone. A major paper event shows the deck
as a whole, its build rows on the tracked version like the storyline.
*Applies*: every subject in `config.REPORTS` freezes two populations, the
archetype in `weekly.csv` and its version in `version.csv`, and the summary's
volume clauses come from the first and its conversion clause from the second.
This replaced the earlier state where Esper Blink read everything on Esper and
Goryo's read everything pooled, so the frozen weekly rows of both were rebuilt
on 2026-09-12 and their summaries for the week to 6 September quote a Blink
volume and a Goryo's conversion the tables no longer show.

**Kavaero, Mind-Bitten and Superior Spider-Man are one card** (2026-08-07):
Superior Spider-Man is the Marvel printing of Kavaero; mechanically they are
the same card, and the IP is the whole of the difference. MTGO publishes each
list under whichever printing the pilot registered, and a pilot may register
both.
*Applies*: the two names merge at ingestion and their copies are summed, before
anything counts a configuration. Eight lists in the history register both, and
without the merge each reads as two separate one-ofs rather than the two-of it
is, splitting one card's adoption history down the middle.

**MTGGoldfish's Eldrazi and Gruul Basking Broodscale rows are one deck**
(2026-08-14):
The site's Eldrazi row is the Gruul build, and Gruul Basking Broodscale Combo is
the same 75 tabled a second time; Alejandro checked the cards. The site's own
split reports one deck at two shares, so the field's second-largest deck reads
as two mid-sized ones. Mono-Green Eldrazi, Eldrazi Tron and Eldrazi Ramp are
different shells that share a creature suite and stay their own rows.
*Applies*: the two names merge into one archetype, `Broodscale`, on the way out
of the transcriptions and across the whole snapshot history, so every reading
already taken is corrected too. Neither of the site's names survives the merge,
since a deck left at both would be counted twice by anything summing the field.
The committed transcriptions stay exactly what the screenshots showed. The
merged share sums two figures the site rounded to a tenth each, so it can sit a
tenth off; the deck counts are exact.

**A card can spread challenge-first, and league-only hype detection is blind to
it** (2026-09-10):
Copying usually shows in the league stratum first and hardest, which is why hype
is read there. It does not always. Clarion Conqueror saturated the challenge
stratum in the non-Fallaji camp while its league share stayed under the bar, so
the reading that exists to catch a copied configuration never saw the largest
one this regime has produced.
*Applies*: a spike is read in whichever stratum the configuration actually moved
in, not in the league stratum by rule, and lineage joins a departure to a hype
episode in either. A lineage row saying the field never piled in is not evidence
that it did not until the challenge stratum has been checked too.

**Hype corrects in about a week, and the weekend is the judge** (2026-08-07):
One week of play is usually enough for reality to hit misconfigured or
suboptimal hyped lists, but the heaviest tournament density is on weekends, so
the correction generally requires a weekend to land.
*Applies*: time bins align to the tournament week; a hype flag cannot resolve
until at least one post-spike weekend of challenge data exists; late spikes
(after the final pre-tournament weekend) are decided by pilot judgment alone.

**League 5-0s are soft evidence** (2026-08-07):
Leagues are casual; many opponents pilot weak decks, so 5-0 is attainable with
suboptimal builds ("free wins"). Leagues still matter: they reflect the
competitive field's assumptions and are where players (often the same ones who
play challenges) test innovations first.
*Applies*: league-derived stats are never blended with challenge stats;
leagues drive novelty detection, challenges drive performance evidence.

## Proposed, awaiting pilot verdict

Heuristic candidates, held here until Alejandro rules on them. Nothing in this
section is adopted knowledge and nothing here may steer an analysis. Each entry
cites the evidence that raised it and counts the sessions it has been put to
him in. See `.claude/skills/mtg-heuristics/SKILL.md`.
