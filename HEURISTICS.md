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
Affinity, not Grixis Affinity. A list holding the full Affinity four under the
Song engine is a hybrid brew, and out for now (2026-09-13).
*Applies*: Weapons Manufacturing and Engineered Explosives join the two
creatures in the mainboard signature. The 34 lists since the bans without both,
16 of them in the fortnight to 6 September, leave the population; that rise is
what put Song of Creation and Undercity Sewers in the storyline as arrivals.
A mainboard Song of Creation puts a list outside (the rule's `excluded`
cards), which moves exactly GinkoHS's 10673 of 5 September. One population, no
versions.

**Izzet Prowess is only the blue and red deck** (2026-09-12):
The deck is Izzet: Cori-Steel Cutter, Dragon's Rage Channeler, Mutagenic
Growth, Slickshot Show-Off and the rest of the blue and red shell. The red and
Boros prowess lists on Lava Spike and Skewer the Critics share the creatures
and are a different deck. So is Izzet Phoenix, which answers the rule through
Cutter, Swiftspear, DRC and Vents, and the prowess core with Phoenix and
Looting grafted on is a hybrid brew, out for now (2026-09-13). A Gruul list
holds one Vents for its sideboard Consign; every Izzet list holds two or more.
*Applies*: Steam Vents joins the three creatures in the mainboard signature.
Every Izzet list since the bans runs it, and the 32 lists with no blue card,
19 of them with white, leave the population. A mainboard Arclight Phoenix
puts a list outside (the rule's `excluded` cards), 9 lists, 8 of them pre-ban,
and Steam Vents has a floor of 2 copies, which moves Duduk123's 18177 alone.
One population, no versions.

**Ephemerate is part of what makes the deck Esper** (2026-08-07):
The trio alone (Goryo's Vengeance, Atraxa, Psychic Frog) admits Grixis
reanimator builds, which are a different deck with a different manabase, a
different gameplan and no bearing on this 75. Ephemerate is the blink half of
the Esper shell and the line the two versions fall either side of.
*Applies*: Ephemerate joins the mainboard signature cards, so membership is the
four and not the three. Grixis lists leave the archetype's population entirely;
those that keep Goryo's Vengeance land on the near-miss watchlist, which is
where a different construction direction belongs.

**Persist reanimator is its own deck, not a Goryo's version** (2026-09-13):
Goryo's is Goryo's Vengeance and the legendary Atraxa it pairs with. Persist
runs a different package (Persist, Archon of Cruelty, Emeritus of Ideation,
Dina's Guidance), so a list holding both is the Persist deck with Goryo's as a
second angle, not a Goryo's build. The Shifting Woodland Omniscience combo
wearing the Goryo's core is read the same way. A Goryo's list carrying Blink's
creatures is different: it is a hybrid whose engine is still the Goryo's
package, so it stays Goryo's.
*Applies*: a mainboard Persist, Omniscience or Shifting Woodland puts a list
outside Goryo's (`EXCLUDED_CARDS`). That moves the two July league lists
19894 and 20074 and the Dallas Spotlight list registered as Esper Goryo's;
ador's 9004 with Phelia and Overlord stays. Frozen Goryo's rows for the weeks
of 14 and 17 July counted the two league lists.

**Esper Blink is the four creatures on their own colours, and not the decks
built around them** (2026-09-13):
The Guide of Souls and Ocelot Pride energy engine on the blink creatures is
energy, a different deck; so are the Estrid's Invocation Overlords deck, the
Stoneforge Mystic Stoneblade build and the Tidehollow Sculler Vial taxes deck.
The Orzhov Aether Vial lists on Ephemerate are a version of Blink, so Vial on
its own says nothing.
*Applies*: a mainboard Guide of Souls, Ocelot Pride, Estrid's Invocation,
Stoneforge Mystic or Tidehollow Sculler puts a list outside Blink (the rule's
`excluded` cards). That moves exactly seven lists: 12705, 13848, 14405, 16492,
20578, 1376 and 177, the last two challenge lists of 2 March and 5 September.
Frozen Blink rows for the weeks holding 16492 (22 May), 20578 (25 July) and
177 (5 September) counted them.

**Oswald with Kappa Cannoneer in the mainboard is the Kappa artifact deck**
(2026-09-13):
The Kappa Cannoneer, Pinnacle Emissary, Welding Jar and Krang deck bolted two
Oswald and a Grinding Station on for a fortnight and then cut them again; it
was never the Oswald deck. Oswald lists side Kappa, so the card is read in the
mainboard only.
*Applies*: a mainboard Kappa Cannoneer puts a list outside Oswald (the rule's
`excluded` cards). That moves exactly chinotron23's 22362 and 22763, the
leagues of 27 August and 4 September, whose frozen Oswald rows counted them.

**Domain Zoo is Kavu and Scion as the deck, not as domain bodies in another**
(2026-09-13):
Persist reanimator (Persist, Archon of Cruelty, Faithless Looting), the
five-colour Living End build (Living End, Bloodbraid Marauder, Malevolent
Rumble) and the five-colour energy build (Guide of Souls, Ocelot Pride, Ajani,
Goblin Bombardment) each run Kavu and Scion as bodies and are their own decks.
The Persist lists were 22 of the 25 pre-ban Frog camp lists, so that camp's
pre-ban consensus was never Zoo's.
*Applies*: a mainboard Persist, Living End, Guide of Souls or Ocelot Pride puts
a list outside Zoo (the rule's `excluded` cards). That moves 39 lists: 24
Persist (21 pre-ban), 8 Living End (Katla's build, one of them gyurme's
Spotlight Brisbane list) and the 7 energy lists of 26 May to 6 June, which sat
in the traditional camp's opening two post-ban bins. Frozen Zoo rows across
those weeks counted them.

**Broodscale is the combo on the Eldrazi Temple shell, and a hybrid brew on
that shell is out for now** (2026-09-13):
The Golgari Yawgmoth and Cauldron decks run Broodscale and the Blade as one
combo among theirs, with no Temple, Kozilek's Command or Fleshraker, and are
different decks. On the intact shell, the Cauldron and Young Wolf package
under Dredger's Insight and the Karn, Mox Opal, Mystic Forge package are
hybrid brews, and the ruling for now is that hybrid brews leave the population
rather than being read as a pilot's version.
*Applies*: Eldrazi Temple joins the mainboard signature, which moves exactly
12560, 1350, 15946 and Dimmer's Spotlight Brisbane list; a mainboard Dredger's
Insight or Mystic Forge puts a list outside (the rule's `excluded` cards),
which moves exactly 13274, 14207, 9360, 1541 and 12945. Only 9360 (31 July)
is post-ban, so one frozen Broodscale row counted a moved list.

**Trudge is the Eldrazi ramp shell on Ugin's Labyrinth** (2026-09-13):
The mono-green Springheart Nantuko decks on Quirion Ranger, Badgermole Cub and
Summoner's Pact run Slumbering Trudge and Fanatic of Rhonas as mana dorks and
none of the Labyrinth, Temple, Kozilek's Command or Fight Rigging shell; they
are a different deck.
*Applies*: Ugin's Labyrinth joins the two creatures in the mainboard
signature. Every other list in the history holds it, so that moves exactly
6626, 6833, 15495, 15694 and 17784, four of them pre-ban. A clean 60 with an
unpublished sideboard (AoFTW's 20592) stays.

**Tron is Eldrazi Tron, and the other Tron decks on the lands and Karn are out**
(2026-09-13):
Mono-Green Tron proper digs with Chromatic Sphere, Chromatic Star and Sylvan
Scrying and runs neither Temple nor Labyrinth; blue Tron is the Force of
Negation and Stock Up control deck; the Malevolent Rumble green ramp build on
the Tron lands is the neighbour shell; and a combo brew in the flex slots, such
as Devoted Druid with Luxior, is a hybrid brew, out for now. Ancient Stirrings
on a green splash inside the full Eldrazi engine is the same deck.
*Applies*: a mainboard Chromatic Sphere, Chromatic Star, Stock Up, Malevolent
Rumble or Devoted Druid puts a list outside Tron (the rule's `excluded`
cards). That moves 11 lists: 13510, 11590, 2254, 14892, 15208, 11955, 2036,
22941 and the Dallas lists of ClintonWillesen1 and simmmins and Brisbane's
AlimTheBackpack. Only 22941 (7 September) is post-ban in the store, so one
frozen Tron row counted a moved list; the paper readings for Dallas and
Brisbane change by one and two lists.

**Boros Energy is the red and white deck on Guide, Ocelot, Ajani and
Bombardment** (2026-09-13):
Drawn from Alejandro's example list and the data. Guide of Souls and Ocelot
Pride are the engine of every energy deck, and the Azorius blink and Selesnya
Birthing Ritual lists on them run neither Ajani nor Goblin Bombardment. Mardu
and Jeskai energy run all four and are different decks, the way a Mardu Blink
list is.
*Applies*: the four in the mainboard and no blue, black or green source, read
on sources and never fetchlands, since Marsh Flats fetches Sacred Foundry in
nearly every Boros list. Since the bans that is 1033 lists, with 117 Mardu and
134 Jeskai lists outside. A mainboard Eldrazi Temple, Cori-Steel Cutter or
Agatha's Soul Cauldron puts a list outside (the rule's `excluded` cards): the
Boros Eldrazi, Cutter prowess and Leonardo Cauldron hybrid brews, out for now
(2026-09-13), exactly 13463, 13489 and 8284, the last post-ban (28 June).
One population, no versions.

**Boros Ponza is Erode with Cleansing Wildfire** (2026-09-13):
Drawn from Alejandro's example list and the data. Erode is the deck's card, in
611 of the 620 land-destruction lists since the bans, and the Wildfire is the
red half of the plan: the five mono-white lists on Crucible of Worlds hold
Erode alone, and the Boros energy lists that splash Erode hold neither. The
Jeskai and Azorius control lists that splash Erode are control decks.
*Applies*: both cards in the mainboard and no blue, black or green source,
466 lists since the bans. A mainboard Boom/Bust puts a list outside (the
rule's `excluded` cards): EDHplayer's four pre-ban Boom/Bust and Magmatic
Hellkite lists are a hybrid brew, out for now (2026-09-13). One population,
no versions.

**Dimir Midrange is Frog with Riddler, and only the blue and black deck**
(2026-09-13):
Drawn from Alejandro's example list and the data. Frog alone admits the Dimir
Oculus lists on Unearth, and a third of those run Quantum Riddler too, so the
pair is not enough on its own: Oculus, the Necrodominance deck on Soul Spike,
Persist reanimator, Dimir Goryo's without Ephemerate and Death's Shadow all
sit on Frog and Riddler in blue and black and are different decks. The Esper
Frog decks on Plains and the Grixis ones on Steam Vents share the pair and are
different decks; Goryo's, Blink and Domain Zoo share it too and are tested
first. The Moonshadow and Street Wraith aggro build stays in: no single card
names it without moving clean lists.
*Applies*: both cards in the mainboard and no white, red or green source, and
no mainboard Necrodominance, Persist, Abhorrent Oculus, Goryo's Vengeance or
Death's Shadow (the rule's `excluded` cards). Since the bans that moves 24
lists, 405 remaining, plus three of the Dallas and Brisbane paper lists. Every
frozen row under `data/tracking/dimir/` counted them. One population, no
versions.

**Jeskai Control is the Consult shell with Galvanic Discharge, and the colour
is read on the spell** (2026-09-13):
Drawn from Alejandro's example list and the data. Consult the Star Charts,
Teferi and Wrath of the Skies are the control shell. A colour rule on sources
fails it: the Azorius control lists run Steam Vents, Watery Grave and Breeding
Pool as extra colours for Prismatic Ending and cast no red spell off them, 120
of the 123 shell lists on a black source holding none. Galvanic Discharge is
the red card the Jeskai lists actually play, in 137 of the 162 red-white-blue
shell lists.
*Applies*: the four in the mainboard and no colour rule, 155 lists since the
bans; a Breeding Pool beside the Discharge is a splash inside the deck. The 25
red-white-blue shell lists with no red spell are Azorius control on a Steam
Vents and stay outside. A mainboard Wrenn and Six, Indomitable Creativity or
Saheeli Rai puts a list outside (the rule's `excluded` cards): the four-colour
Omnath control lists, the Creativity combo and the Saheeli combo inside the
shell, a hybrid brew, out for now (2026-09-13); 7 store lists and Nicklinger's
Dallas list, 148 remaining. One population, no versions.

**Storm is Ral, Ruby Medallion and Past in Flames** (2026-09-13):
Drawn from Alejandro's example list and the data. Ruby alone admits the Belcher
lists on Pinnacle Monk, which never run Ral or Past in Flames; Ral alone admits
an Izzet storm on Stormcatch Mentor with no Medallion. The sideboard colours
are the Wish targets and every list is the same red deck under them.
*Applies*: the three in the mainboard, no colour rule, 472 lists since the
bans. The Izzet Stormcatch shell carrying the three on an Island (Nilsfit,
3 September) is a Storm build and stays (2026-09-13). One population, no
versions.

**Temur Living End is Living End with both cascade spells** (2026-09-13):
Drawn from Alejandro's example list and the data. The Sultai build on
Formidable Speaker and Overlord of the Balemurk shares Living End and Shardless
Agent and never runs Violent Outburst, and it is a different deck. Temple
Garden sits in 187 of the 326 lists beside no white spell, a fetchable land of
the Temur shell and not a colour, and Alejandro's own list runs one.
*Applies*: the three in the mainboard, no colour rule, 326 lists since the
bans. The four lists carrying the Sultai build's black suite beside Violent
Outburst on black sources (16270, 18438, 8502 and marknorton at Brisbane) are
Living End builds and stay (2026-09-13). One population, no versions.

## Data interpretation

**The history opens on the regime boundary; pre-ban lists are not in the
store** (2026-09-13):
What was played under the old rules is a different era, and a list from it
should not be in the database at all rather than merely outside every window.
*Applies*: `HISTORY_START` is the boundary, the store build skips lists dated
before it, and the index records only what the store holds. The raw cache keeps
the earlier payloads. A storyline return can only remember as far back as the
boundary.

**A 75-card mainboard is a list published with its boards merged, and no
member** (2026-09-13):
Some lists arrive as 75 mainboard cards and an empty sideboard. The deck is
ordinary, but its boards cannot be told apart, so reading it would count
fifteen sideboard cards into a build. A 60 with an unpublished sideboard is
still a list.
*Applies*: a mainboard over `MAINBOARD_MAX` (62) answers to no membership rule,
an oversize registration with a full sideboard included, since it distorts a
copies reading the same way. That moves EvoPride's Prowess 4396 of 20 June,
tao_bye_bye's 65-card Storm 1589 of 8 March and the Dallas Storm list;
AoFTW's Trudge 20592, a clean 60 with no sideboard, stays.

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

**Jeskai Control is read on a red spell and not a red source** (raised
2026-09-13, surfaced 1×):
The rule above keys Jeskai on Galvanic Discharge because a source rule cannot
tell it from Azorius control. Whether the team calls the four-colour control
lists on Watery Grave and Breeding Pool a different deck, and whether the Boros
energy rule should keep Mardu and Jeskai energy outside, were decided from the
deck names alone.
*Evidence*: since the bans, 123 Consult shell lists on a black source and 74 on
a green one, of which 3 and 15 cast Galvanic Discharge; 25 red-white-blue
shell lists cast no red spell at all. Energy: 1033 Boros lists against 117
Mardu and 134 Jeskai.
*Applies if adopted*: the rules stand. If rejected, Jeskai drops the Discharge
and reads the whole Consult shell, or Energy folds Mardu and Jeskai in as
versions; either invalidates every frozen row under that deck's directory.

**The regime boundary day was played under the old rules** (raised
2026-09-13, surfaced 1×):
`REGIME_BOUNDARY` is 2026-05-18, the announcement date, and the window reads
that day as post-ban. The events published that day were played before the
bans took effect.
*Evidence*: 25 lists dated 2026-05-18 mainboard Phlage, Titan of Fire's Fury
(17 of 18 Boros Energy lists, 3 Boros Ponza challenge lists) and none after;
60 of the day's 112 lists are members of a tracked deck and sit in every
post-ban population, where a banned card reads as the deck's own variation.
*Applies if adopted*: the boundary moves to 2026-05-19, or the boundary day is
read as pre-ban; either moves those lists out of every post-ban population and
every frozen row that read them is invalidated.
