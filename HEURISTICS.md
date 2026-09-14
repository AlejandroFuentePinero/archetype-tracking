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

**A challenge that did not fire is not a missing challenge, and a major paper
weekend is the usual reason** (2026-09-14):
MTGO's Sunday schedule thins when the format's players are in a tournament hall.
A Sunday short of its usual challenges reads exactly like a fetch that dropped
an event, and the two have to be told apart before a week's field is doubted.
*Applies*: a Sunday under two challenge-class events on a weekend carrying an
RC, a Pro Tour or a Spotlight is the calendar and not a gap. Do not re-fetch it,
do not doubt the week, and do not say anything about it in the report: a
paragraph explaining why a field was small is a caveat on a number that is
correct. A short Sunday with no major event behind it is still a gap and is
chased. Sunday 2026-09-13, the day of RC Baltimore and RC China, ran one
challenge-class event where the other sixteen Sundays since the bans ran two to
four, and was twice mistaken for an ingestion gap before this was ruled.

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

**A splash is under five off-colour cards, lands excluded, and never a
playset** (2026-09-13):
A light splash does not move a list out of its deck: Dimir on a Steam Vents
for sideboard Meltdown is very common and still Dimir, and lands say nothing
on their own. The line is the count of off-colour nonland cards in the
mainboard: four or fewer is a splash, five or more is another deck that goes
deeper into the third colour, and a full playset of one off-colour card is the
other deck's card whatever the total, so 4 Quantum Riddler makes Jeskai Energy
and 4 Flame of Anor makes Grixis Frog.
*Applies*: every colour rule reads the mainboard spells this way and never the
sources; the `off_colour` land lists go. Measured on 2026-09-13 over the store
and the paper lists with 0 members leaving anywhere: Blink admits 6, Boros
Energy 14, Dimir 57 and Boros Ponza 2 of the full-signature lists the source
rule turned away, and haoqinglangou's Ponza on 4 Teferi and the 82 Jeskai
Energy lists on 4 Riddler stay outside.

**A deck is its shell, and a card every list plays can still be supporting
rather than core** (2026-09-13):
Membership is the combination that makes the shell, and a staple the shell
can test without is supporting evidence rather than a core card: Dragon's Rage
Channeler in Prowess, Weapons Manufacturing in Affinity, Erode in Ponza, Karn
in Tron. A list that cuts one of those is the same deck in a different build.
The opposite holds for Blink, where the four creatures are the deck only
together.
*Applies*: a rule has core cards, all required, and a supporting tier read as
a count. Prowess is Steam Vents and Lava Dart with four of six staples;
Affinity is Kappa, Pinnacle and Explosives with Manufacturing supporting;
Ponza is Cleansing Wildfire with four of six land-destruction staples; Tron is
the three lands. Each is measured under its own entry below.

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

**Grinding Station is the deck, and Oswald and Loki are its two builds**
(2026-09-13):
The tracked deck is the Grinding Station engine on Emry, Sewer-veillance Cam
and Mox Amber, which no other deck runs together. Oswald Fiddlebender appears
in this deck alone, but the mono-blue build on Loki, God of Mischief has no
Fiddlebender, and forcing the card would leave half the deck outside. The
Tezzeret and Krang build shares Oswald, Emry and the Saga shell without the
Station and is a different deck; the Kethis combo and the Song of Creation
deck run the Station trio, and the Kethis deck is a different deck whether
or not it adds Loki for Plaza of Heroes (pass three, 2026-09-13): Kethis,
the Hidden Hand is its engine and puts a list outside, which moves
J4K3ST3R02's 4 July challenge and Rexplosion's 10 July league. A green
source is a splash, usually for Haywire Mite. This replaces the UW Oswald
reading of 2026-09-12.
*Applies*: membership is Grinding Station, Emry and Sewer-veillance Cam in the
mainboard with either Oswald Fiddlebender or Loki, God of Mischief, no colour
rule; 94 lists since the bans (83 MTGO, 11 paper), the 61 UW Oswald members
and 33 more, 27 of them with no white land, IainB7's 28th at Spotlight Dallas
among them. The report is renamed Grinding Station, and every frozen row under
`data/tracking/oswald/` reads the old population.

**Domain Zoo forks on Psychic Frog, the traditional version is the one we
track, and a Kavu-less Frog list is still Zoo** (2026-09-13):
Two versions: the bluer build on Psychic Frog and the traditional one on
Territorial Kavu. Being five colours the deck moves a lot, and that is expected
rather than a finding. Frog was first chosen on the perception that Frog with
Quantum Riddler had become the popular build; the data said otherwise (Frog 13
of 85 MTGO lists and 6 of 22 at Spotlight Dallas since 10 August, every list
since 7 September traditional), so the tracked version moved to traditional on
2026-09-12. A list on Leyline of the Guildpact, Scion, Leyline Binding, Frog
and Ragavan with no Kavu is still Domain Zoo and lands in the Frog version;
the Shardless Agent cascade decks on the same two leylines are not.
*Applies*: membership is Territorial Kavu and Scion of Draco, or Scion, Leyline
of the Guildpact and Psychic Frog with no mainboard Shardless Agent or Crashing
Footfalls, which admits exactly Argentorum's 8 June league, Jselzo's 22 July
league and izzetrycal's Pro Tour list, and moves no member. The version rule
is mainboard Psychic Frog. The report reads the traditional version for
conversion, goldfishing and the storyline; the Frog version is a bare count
and a line on the presence figure's version panel.

**Broodscale has four versions, and the most popular one is tracked**
(2026-09-13):
Mono-green; Gruul, on red cards like Unholy Heat and Writhing Chrysalis; Lab,
on Devourer of Destiny and Ugin's Labyrinth over the mono-green shell; and
Golgari, black and green on Sephiroth with Fatal Push. Which to track was
left to the data: in the week to 13 September the Lab version was 73 of 84
lists and 33 of 37 swiss-like finishes, having been level with Gruul over the
regime as a whole. Golgari is its own build and not a splash: its manabase is
Llanowar Wastes, Overgrown Tomb, Swamp and Underground Mortuary where the
mono-green shell runs Grove of the Burnwillows and Yavimaya, and it converts
above its weight, 6 of its 13 lists being swiss-like finishes with
YungDingo's 6 July challenge-64 win and Owllicious's 4th of 21 June among
them.
*Applies*: the version rule reads the red spells first, then Ugin's
Labyrinth, then the black cards, and a list on none of them is mono-green.
A list on both red and the Labyrinth is Gruul. The Gruul markers are Unholy
Heat, Writhing Chrysalis and Lightning Bolt (pass three, 2026-09-13), which
moves BenT's and Lostwanderer's Pro Tour lists and nothing on MTGO. The
Golgari markers are Sephiroth, Fatal Push and Thoughtseize (2026-09-13) and
never Dismember, which Phyrexian mana casts in 419 members holding no black
source at all, the same reason Prowess draws no colour rule off Mutagenic
Growth. Read last, it takes 13 lists from mono-green and none from Gruul or
Lab, so Jack-Z's 21 August league on Fatal Push and Writhing Chrysalis stays
Gruul and no frozen row moves. The report reads the Lab version, and moving
it to another version is Alejandro's call, since it invalidates every frozen
row under `data/tracking/broodscale/`.
*Watch*: whether Golgari consolidates or fades. It peaked at 7 lists in July,
took 5 in August and has 1 so far in September, and its two most recent lists
are two builds rather than one: Napoleon_I's Sephiroth of 29 August and
gpowerone's Thoughtseize and Inquisition discard build of 7 September. Read
the fortnight to 20 September for which way it went, and say so in that
week's clause 6. A version that thins to nothing is worth dropping again, the
same call in reverse.

**Devoted Combo is Devoted Druid with either Tyvar, and the Nantuko cards are
its own** (2026-09-13):
Tyvar, Jubilant Brawler and Tyvar, the Pummeler are both unique to Druid
combo, as are Springheart Nantuko and Quirion Ranger; a list swapping one
Tyvar for the other or adding the Nantuko half is a version of the same deck,
same game plan and play style, not a hybrid. The Druid-less mono-green Nantuko
deck on Ouroboroid, Leyline of Abundance and Quirion is a different deck, and
Druid without any Tyvar is the Vizier of Remedies elves build.
*Applies*: membership is Devoted Druid with Tyvar, Jubilant Brawler or Tyvar,
the Pummeler in the mainboard, no colour rule. That admits exactly noah212's
Dallas list and Dennison's Brisbane list (431 lists, no MTGO change); the 29
Nantuko lists without Druid stay outside. One population, no versions.

**Affinity is the Kappa and Pinnacle shell, and Explosives, Weapons
Manufacturing and Krang support it** (2026-09-13):
The deck runs Kappa Cannoneer and Pinnacle Emissary as four-ofs with
Engineered Explosives and Weapons Manufacturing in nearly every list; some
lists test without Manufacturing and stay within the shell, and a list
without Explosives is Affinity too, an innovation worth flagging rather than
another deck (Kaoanchun's Izzet build at RC China, the Explosives slot given
to Thoughtcast and countermagic). Krang is supporting too. Basim Ibn Ishaq
decks and Sewer-veillance Cam decks are not Affinity, Tamiyo with Mox Amber
is the Tamiyo artifact deck unless Manufacturing sits beside them, and Song
of Creation has nothing to do with Affinity. The report is called Affinity,
not Grixis Affinity. This replaces the three-card reading of 2026-09-13.
*Applies*: Kappa and Pinnacle in the mainboard with any one of Explosives,
Manufacturing or Krang (the supporting tier), which keeps the Frogmite and
Ravenous Robots aggro lists on neither outside. A mainboard Song of Creation,
Basim Ibn Ishaq or Sewer-veillance Cam puts a list outside, and so does Tamiyo
beside Mox Amber with no Manufacturing (the rule's `excluded` cards, the last
one weighed). Measured on 2026-09-13 over the store and the paper lists: the
tier admits exactly Kaoanchun's RC China list and Yojak3's 5 September league
(Krang and Cranial Plating, no Explosives) and no member leaves; read on the
two core cards alone it would also admit ChewDawg's two Robots lists and
Costola91's two Frogmite lists, which stay outside. One population, no
versions.

**Izzet Prowess is the blue and red prowess shell, and Channeler supports it**
(2026-09-13):
The deck is Izzet: Steam Vents and Lava Dart under Cori-Steel Cutter, Monastery
Swiftspear, Dragon's Rage Channeler, Slickshot Show-Off, Mutagenic Growth and
Stormchaser's Talent, and a list that cuts Channeler, or Swiftspear, or sides
its Cutters is still Prowess, a different build inside the shell. The red and
Boros prowess lists on Lava Spike and Skewer the Critics share the creatures
and are a different deck. So is Izzet Phoenix, and the prowess core with
Phoenix and Looting grafted on is a hybrid brew, out for now. A Gruul list
holds one Vents for its sideboard Consign; every Izzet list holds two or more.
This replaces the four-card reading of 2026-09-12.
*Applies*: Steam Vents at two or more and Lava Dart in the mainboard with four
of the six staples; a mainboard Arclight Phoenix puts a list outside. That
admits exactly Certified_Noob's 2 and 5 September and DelverOfBolts's 3 June
challenges and the leagues of kyrre2013 on 9 June, Eason271 on 21 July,
lilcreacher on 25 July and TuckerMTG on 5 August, and no member leaves;
Bosseidon's Talent decks on three staples stay outside. One population, no
versions. No colour rule, confirmed on the Thoughtseize
playset (pass three, 2026-09-13): a playset outside blue and red on an
intact Izzet shell is an innovation attempt and stays Prowess, Suechtler's
23 August and FraCante's 24 May challenges with it. A colour rule cannot be
drawn here because of one card: Mutagenic Growth is green on record and
castable through Phyrexian mana, and it alone accounts for 603 of the 605
members the
splash line on blue and red would throw out.

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
outside Goryo's (`EXCLUDED_CARDS`). That moves GabbaAndrewTeam's 14 July and
chapaking8's 17 July leagues and the Dallas Spotlight list registered as
Esper Goryo's; ador's 20 July challenge with Phelia and Overlord stays.
Frozen Goryo's rows for the weeks of 14 and 17 July counted the two league
lists.

**Esper Blink is the three creatures together on their own colours, and not the
decks built around them** (2026-09-14):
Phelia, Overlord of the Balemurk and Witch Enchanter are the deck as a
combination, not a signal from one card: a list that cuts any one of them is
not Blink, whatever the rest of the 75 looks like. Flickerwisp was the fourth
until 2026-09-14 and is a slot rather than the deck: a list on the three that
gives the Flickerwisp seat to Psychic Frog is the same deck innovating. RC
Baltimore is where that build arrived in numbers, six lists whose pilots all
typed `Esper Blink` and five of them running Frog as a four-of, four of those
beside four Quantum Riddler. The Guide of Souls and
Ocelot Pride energy engine on the blink creatures is energy, a different deck;
so are the Estrid's Invocation Overlords deck, the Stoneforge Mystic Stoneblade
build and the Tidehollow Sculler Vial taxes deck, the last a hybrid whose taxes
package displaces the interaction suite. The Orzhov Aether Vial lists on
Ephemerate are a version of Blink, so Vial on its own says nothing.
*Applies*: all three in the mainboard, which against the four-card rule moves 8
MTGO lists since the bans and 7 paper lists in (the six Baltimore lists and
CruzH at Dallas) and nothing out. The lists that cut Phelia or the Enchanter
are still outside, three on Emperor of Bones without Phelia and one without the
Enchanter. A mainboard Guide of Souls, Ocelot Pride,
Estrid's Invocation, Stoneforge Mystic or Tidehollow Sculler puts a list
outside (the rule's `excluded` cards): the leagues of dabigatran on 1 March,
Jeppebc on 29 March and 10 April, TOP_AI (his second) on 22 May and taku123
on 25 July, and the challenges of JJ on 2 March and UomoComune26490 on
5 September. Colour is the splash line, which admits the six lists on one
Sacred Foundry or Temple Garden with nothing off-colour cast (JJ's 24 July
challenge and the leagues of Outsid3r on 24 June, koskadelli on 29 July,
meanfannypack on 31 July, TheRealStormCrow on 8 August and SuperCow12653 on
1 September) and keeps the Mardu and Abzan builds outside. The Esper
version is read on Watery Grave or a blue spell (pass three, 2026-09-13),
which moves SuperCow12653's two lists, the only two between the halves, and
makes the versions a partition again.

**Oswald with Kappa Cannoneer in the mainboard is the Kappa artifact deck**
(2026-09-13):
The Kappa Cannoneer, Pinnacle Emissary, Welding Jar and Krang deck bolted two
Oswald and a Grinding Station on for a fortnight and then cut them again; it
was never the Oswald deck. Oswald lists side Kappa, so the card is read in the
mainboard only.
*Applies*: a mainboard Kappa Cannoneer puts a list outside Grinding Station (the rule's
`excluded` cards). That moves exactly chinotron23's leagues of 27 August and
4 September, whose frozen Oswald rows counted them.

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
under Dredger's Insight is a hybrid brew, and the ruling for now is that
hybrid brews leave the population rather than being read as a pilot's
version. A Mystic Forge inside the intact Gruul shell is an innovation and
the list is Broodscale (godseerker at RC China, one Forge as a Saga target
with no Karn and no Mox Opal); the Karn, Mox Opal, Mystic Forge package the
earlier reading named as a brew holds nothing in the history since the bans,
so Forge is no longer an excluded card.
*Applies*: Eldrazi Temple joins the mainboard signature, which moves exactly
RandomGameActions's 25 February league, Bmadman's 2 March challenge,
ArsonBjork's 13 May league and Dimmer's Spotlight Brisbane list; a mainboard
Dredger's Insight puts a list outside (the rule's `excluded` card). Dropping
Forge on 2026-09-13 moves exactly godseerker's list in and nothing else.

**Trudge is the Eldrazi ramp shell** (2026-09-14):
The mono-green Springheart Nantuko decks on Quirion Ranger, Badgermole Cub and
Summoner's Pact run Slumbering Trudge and Fanatic of Rhonas as mana dorks and
none of the Labyrinth, Temple, Kozilek's Command or Fight Rigging shell; they
are a different deck. Ugin's Labyrinth stood in for that shell while every list
in the history held it, and RC Baltimore ended that: TheJV's list (rank 735,
4-5-0) is the shell whole, Fight Rigging, Kozilek's Command, Sowing Mycospawn,
Malevolent Rumble, Emrakul and Ulamog, on a manabase with no Labyrinth. The
rule reads the shell rather than any one of its cards.
*Applies*: Slumbering Trudge and Fanatic of Rhonas in the mainboard with any
one of Ugin's Labyrinth, Eldrazi Temple, Kozilek's Command or Fight Rigging.
Every member holds all four and the Nantuko decks hold none, so Taurum's
23 April and Gormatron's 2 May challenges and the leagues of wasatchwarrior on
3 May, Gormatron on 7 May and Dooter611 on 9 June stay outside as before.
Against the Labyrinth clause this moves exactly TheJV's Baltimore list in and
no MTGO list. A clean 60 with an unpublished sideboard (AoFTW's 26 July
league) stays.

**Tron is the Tron lands, and colourless is the version we track**
(2026-09-13):
A list on Urza's Tower, Mine and Power Plant is Tron. Colourless Tron on Karn,
Ugin's Labyrinth and the Eldrazi is the tracked version; blue Tron on Stock Up
and Force of Negation and green Tron on Chromatic Sphere, Star and Sylvan
Scrying are versions of the same deck, read in the report as versions and
tracked for performance through colourless. Ancient Stirrings on a green
splash inside the Eldrazi engine is colourless with a splash. A combo brew in
the flex slots, such as Devoted Druid with Luxior, stays a hybrid brew, out
for now. This replaces the Eldrazi Tron reading of 2026-09-13 that put the
other Tron decks outside.
*Applies*: the three lands in the mainboard, Karn supporting, which admits
416FrowningTable's 29 August challenge and the leagues of inf1nitus on
1 September and Argtigg on 3 September (Eldrazi Tron with Karn cut). The
version rule is markers and never the splash line (pass three, 2026-09-13):
blue is Stock Up
or Force of Negation in the mainboard, green is Chromatic Sphere, Chromatic
Star or Sylvan Scrying, and every other list is colourless whatever it
splashes, so a playset of Dress Down, Portent of Calamity, Malevolent Rumble
or Ancient Stirrings inside the Eldrazi shell is a build reading and not a
version change, and so is Emrakul, the Aeons Torn: blue Tron is a version of
the colourless deck that plays more Emrakul, not a deck the card names
(Alejandro, 2026-09-13). The card sits in 46 of the 50 blue lists and 18 of the
669 colourless, which is a build the version leans on and not a marker, so a
colourless list holding it is colourless and the version boundary is not to
raise it. Measured: blue 78 to 53, green 5 to 3, colourless 745 to
772, no list changing deck, and AlimTheBackpack's 4 Rumble Brisbane list
moving from green to colourless, which reverses the splash-line reading of
that one list. Since the bans that is 822 lists (713 MTGO, 109
paper): 740 colourless, 77 blue, 5 green. Sphere, Star, Stock Up and Rumble
stop being exclusions and become version markers; Devoted Druid stays
excluded. Every frozen row under `data/tracking/tron/` reads the old
population. Applied on 2026-09-13 (issue #3), with the boundary at
2026-05-19: 821 lists (712 MTGO, 109 paper), 739 colourless, 77 blue, 5 green.

**Boros Energy is the red and white deck on Guide, Ocelot, Ajani and
Bombardment** (2026-09-13):
Drawn from Alejandro's example list and the data. Guide of Souls and Ocelot
Pride are the engine of every energy deck, and the Azorius blink and Selesnya
Birthing Ritual lists on them run neither Ajani nor Goblin Bombardment. Mardu
and Jeskai energy run all four and are different decks: Jeskai on a playset of
Quantum Riddler, Mardu on five or more black cards. A Godless Shrine held for
sideboard Thoughtseize is a splash.
*Applies*: the four in the mainboard and the splash line on blue, black and
green. That admits 14 lists the source rule turned away (13 MTGO, Lindenk's
Pro Tour list), no member leaves, and 234 Mardu and Jeskai lists stay
outside. A mainboard Eldrazi Temple, Cori-Steel Cutter or Agatha's Soul
Cauldron puts a list outside (the rule's `excluded` cards): the Boros Eldrazi,
Cutter prowess and Leonardo Cauldron hybrid brews, out for now, exactly
Cantergiani's and EDHplayer's 21 March leagues and Zorro7x4's 28 June
challenge. One population, no versions.

**Boros Ponza is the Cleansing Wildfire land-destruction suite, and Erode
supports it** (2026-09-13):
Boros land destruction is obvious on sight: Cleansing Wildfire with Erode,
Field of Ruin, Demolition Field, Price of Freedom, Wrath of the Skies and
Solitude. Erode is in almost every list but is supporting, since the plan is
the suite and not the card. The Pinnacle Monk red decks on Wildfire and Price
run nothing else of it. The Jeskai and Azorius control lists that splash
Erode are control decks, and a Ponza list on a playset of Teferi is the
Jeskai deck. This replaces the Erode-with-Wildfire reading of 2026-09-13.
*Applies*: Cleansing Wildfire in the mainboard with four of the six staples,
and the splash line on blue, black and green. That admits exactly EDHplayer's
21 May league, JTKR's Dallas list and -=Alfa=-'s 21 August challenge and
26 August league (three Riddler and a Shark Typhoon is a splash), no member
leaves, and haoqinglangou's 9 July challenge and 13 July league on 4 Teferi
stay outside. A mainboard Boom/Bust puts a list outside (the rule's
`excluded` cards): EDHplayer's pre-ban Boom/Bust and Magmatic Hellkite lists
are a hybrid brew, out for now. One population, no versions.

**Dimir Midrange is Frog with Riddler, and a light splash is still Dimir**
(2026-09-13):
Drawn from Alejandro's example list and the data. Frog alone admits the Dimir
Oculus lists on Unearth, and a third of those run Quantum Riddler too, so the
pair is not enough on its own: Oculus, the Necrodominance deck on Soul Spike,
Persist reanimator, Dimir Goryo's without Ephemerate and Death's Shadow all
sit on Frog and Riddler in blue and black and are different decks. Meltdown in
the sideboard off one Steam Vents is very common and the list is still Dimir;
Grixis Frog on a playset of Flame of Anor, Unholy Heat or Ragavan, and Esper
Frog on five or more white cards, go deeper and are different decks. Goryo's,
Blink and Domain Zoo share the pair and are tested first. The Moonshadow and
Street Wraith aggro build stays in.
*Applies*: both cards in the mainboard, the splash line on white, red and
green, and no mainboard Necrodominance, Persist, Unearth, Goryo's Vengeance,
Death's Shadow or Namor the Sub-Mariner (the rule's `excluded` cards). The
Oculus deck is named by Unearth and not by Abhorrent Oculus (pass three,
2026-09-13), every other Oculus list running four of each where a one-of in
the stock shell is a threat slot, which admits dzk's 14th; the mono-blue
Namor, Archmage's Charm and Disrupting Shoal tempo shell on a black splash
is its own deck, which takes Andeloth's 9 September challenge out; and the
Street Wraith, Nethergoyf and Stubborn Denial shell stays the Death's Shadow
deck's, so
ipadkid's 28th is correctly outside. That admits 57
lists the source rule turned away (51 MTGO, 6 paper; ipadkid's 3rd and
Hedron's 53rd at Dallas among them), no member leaves, and 197 lists on a
deeper splash stay outside. One population, no versions.

**UWr Control is the blue and white control shell, and Discharge makes a list
Jeskai without making it a different deck** (2026-09-13):
We track the blue-white control shell as one deck: Teferi, Time Raveler and
Wrath of the Skies over a draw engine, whether Consult the Star Charts, the
Orim's Chant and Isochron Scepter lock, Narset, Day's Undoing, Thundertrap
Trainer or Flow State. Control is extremely flexible and adapts its
interaction to the meta, so a variety of interaction is expected, and Galvanic
Discharge is a build reading, not a membership rule; Jeskai and Azorius are
the same deck tracked together. The sweeper is a slot and not a card (pass
three, 2026-09-13): a list that fills it with Supreme Verdict, Terminus or
Temporary Lockdown instead of Wrath is the same deck, and an off-colour
removal playset is interaction rather than another deck's card. Ephemerate
is the exception, pointing at Blink and not at control, and so is a playset
of Price of Freedom: a control shell on the Ponza land-destruction suite with
Loki on top (oko333 at RC China, Price, Erode, Field of Ruin and Demolition
Field as four-ofs with no Cleansing Wildfire) is a brew that is part of no
deck. Loki itself is not the line: the Azorius Loki control lists (JakeTMS,
2 July; Grevv at Dallas) carry no land destruction and are control. This
replaces the Consult-with-Discharge reading of 2026-09-13.
*Applies*: Teferi in the mainboard with any one of Wrath of the Skies,
Supreme Verdict, Terminus or Temporary Lockdown, and any one of the engines,
now ten with Wan Shi Tong, Librarian, Stock Up and Brainsurge added (each
more common among members, at 15%, 14% and 17%, than Flow State and
Thundertrap Trainer, which the tier already named); the splash line on black
and green, which ignores an off-colour removal playset while the rest of the
mainboard stays under the line; a mainboard Ephemerate, Wrenn and Six,
Indomitable Creativity, Saheeli Rai, Cleansing Wildfire, Phelia, Ragavan,
Territorial Kavu, Guide of Souls or Ocelot Pride putting a list outside (the
Omnath, Creativity and Saheeli hybrids, out for now, and the Ponza, Blink
midrange, Zoo and energy decks that carry the two cards), and Price of
Freedom joining the Ponza line on 2026-09-13, which moves exactly oko333's
list out and nothing else. Since the bans that
is 486 lists (436 MTGO, 50 paper), the 179 Jeskai members and 307 more, 205
on Discharge. The report is renamed UWr Control, one population, no versions,
and every frozen row under `data/tracking/jeskai/` reads the old population.
Applied on 2026-09-13 (issue #3), with the boundary at 2026-05-19 and the
two oversize lists out, the store holds 476 (427 MTGO, 49 paper). The
pass-three rules were applied the same day (issue #5): 32 lists in and 4
out, 477 members to 505.

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
Outburst on black sources (the leagues of Cagalli123 on 19 May and RNicoF on
19 June, Hravv's 4 July challenge and marknorton at Brisbane) are Living End
builds and stay (2026-09-13). One population, no versions.

## Data interpretation

**The history opens the day after the announcement, since the boundary day was
played under the old rules** (2026-09-13):
What was played under the old rules is a different era, and a list from it
should not be in the database at all rather than merely outside every window.
The events published on 2026-05-18, the announcement date, were played before
the bans took effect: 25 of that day's lists mainboard Phlage, 17 of its 18
Boros Energy lists among them.
*Applies*: `HISTORY_START` is 2026-05-19, the store build skips lists dated
before it, and the index records only what the store holds. `REGIME_BOUNDARY`
stays the announcement Monday, being the calendar every fortnight bin and
window is anchored on: anchored on the Tuesday the bins would close on a
Monday and the storyline would freeze each fortnight a week late, and no list
on the boundary day is in the store for a window to read. The raw cache
keeps the earlier payloads. The 60 boundary-day lists that sat in post-ban
populations leave them, and every frozen row that read them is invalidated. A
storyline return can only remember as far back as the boundary.

**A 75-card mainboard is a list published with its boards merged, and no
member** (2026-09-13):
Some lists arrive as 75 mainboard cards and an empty sideboard. The deck is
ordinary, but its boards cannot be told apart, so reading it would count
fifteen sideboard cards into a build. A 60 with an unpublished sideboard is
still a list.
*Applies*: a mainboard over `MAINBOARD_MAX` (62) answers to no membership rule,
an oversize registration with a full sideboard included, since it distorts a
copies reading the same way. That moves EvoPride's Prowess list of 20 June,
tao_bye_bye's 65-card Storm list of 8 March and the Dallas Storm list;
AoFTW's Trudge list of 26 July, a clean 60 with no sideboard, stays.

**A paper list published with its boards merged is dropped, and the reason
recorded** (2026-09-13):
Melee publishes these with no sideboard heading at all, only type headings,
confirmed by refetching all three pages on 2026-09-13. The failure is at the
source and not in the fetch, so there is nothing to fix and nothing to
recover by hand. The sample is small and it is corrupted or meme
registrations rather than decks: 146 Plains at 0-1, a 76-card five-colour
pile of one-ofs at 0-5, and one genuine 60 and 15 run together. Recovering
the one real list by hand would put a hand-split 75 in a population every
other list of which the fetch split, which is a worse thing to carry than one
missing Storm list.
*Applies*: they are dropped, not classified and not recovered, which
`MAINBOARD_MAX` already does. The report keeps printing the count with the
reason beside it, as a note on what the field published and not as an alarm
about the fetch: the count climbing means melee published another merged
registration, which says nothing about this engine. Three at Brisbane and
Dallas as of 2026-09-13: lnget's 146 Plains and EntreriArtemis's Storm at
Brisbane, AK47100's Boros pile at Dallas.

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

**Top 32 is the window the site publishes, not a cut, so every challenge class
is one population** (2026-09-13):
Top 32 means nothing beyond being the only data we get. Conversion is top 8
anyway, and that is where a finish is read. MTGO added challenge-16 on
2026-08-22, seating 29 to 50 players and publishing its whole field, records
included, so its lists are nearer a census than a challenge-64's top 32 of 82:
better metagame data rather than worse. Measured on the store, its conversion
deviates from each deck's other challenge lists by a median of 11.4 points
against the 11.1 points expected from sample size alone (13 decks, 5 to 25
challenge-16 lists each), and the classes already pooled differ by as much on
far larger samples: Blink converts 35.2% of its 54 challenge-32 lists against
15.4% of its 39 challenge-96 lists. The weekly challenge field ran 288 to 512
before challenge-16 existed and 384 to 480 since, so nothing about the
denominator moved either.
*Applies*: `_CHALLENGE` is every event class except league, challenge-16
included; no class is split out of the top-32 denominator, and no page carries
a note about the stratum. A later review proposing to drop or split a class on
its size is answered here rather than re-measured.

**A fortnight of fewer than ten lists is too thin to read a card-level row off**
(2026-09-13):
The storyline reads each fortnight against the one before it whatever either
holds, so a bin of 8 lists prints the same kind of claim as a bin of 130 and the
reader has only the counts beside the row to tell them apart. The return reading
was given this floor on 2026-09-13, having read a return off an absence its
history was too thin to evidence; the adoption and copies rows answer to the
same rule. Measured on the frozen files, 66 of the 597 comparison rows read
across such a bin and 55 of those fail a two-sided Fisher test at p<0.05.
Devoted Combo's fortnight to 2026-06-14 prints 14 rows against a 2-list history,
"Craterhoof Behemoth climbed in the mainboard, 0/2 to 8/9 lists" among them
(p=0.06), and Grinding Station's fortnight to 2026-08-23 prints 21 rows off 8
lists, its own namesake at "Oswald Fiddlebender fell in the mainboard, 21/23 to
5/8 lists" (p=0.09) and Damping Sphere at "19/23 to 5/8" (p=0.34).
*Applies*: a floor of ten lists on the smaller of the two populations in
`timeline.moved`, the shape the absence window already has, printing the bin as
too thin to read rather than printing its rows. Ten and not `TRACK_MIN_LISTS`:
the rows this is for cluster at 8 and 9 lists, so a floor of five leaves the
mass of them standing. Swapping `moved` for `shifted` is not the fix, being not
uniformly stricter and adding about 30 rows across storm, livingend, tron,
ponza, dimir, jeskai, prowess and devoted. Devoted Combo and Grinding Station
hold most of the suppressed rows and will read as too thin for stretches, which
is the reading those fortnights can carry.

## Proposed, awaiting pilot verdict

Heuristic candidates, held here until Alejandro rules on them. Nothing in this
section is adopted knowledge and nothing here may steer an analysis. Each entry
cites the evidence that raised it and counts the sessions it has been put to
him in. See `.claude/skills/mtg-heuristics/SKILL.md`.

**The novelty bars are the top fifth of the field, three lists, a 10% MTGO peak
and 1.5x concentration** (raised 2026-09-14, surfaced 0×):
The paper novelty reading shipped on these four numbers. Each was measured, but
measured is not ruled on: the reading prints a handful of rows a season and a
bar moved one notch either way roughly halves or doubles that, so what the
reading is worth is a pilot's call rather than a knee in a curve.
*Evidence*: over the five cached events and all seventeen tracked decks the
settled bars print 7 rows, every one of them a finding no other reading makes.
The strongest is Jennifer Walters in Devoted Combo sideboards, 3 of 7 good
finishers at Spotlight Brisbane and 5 of 14 at RC Baltimore, against no MTGO
fortnight above 7%. The cut: a fixed top 64 gives non-Fallaji Goryo's 7 lists at
Amsterdam, 1 at Brisbane, 1 at Dallas and 5 at Baltimore, where the top fifth
gives 8, 6, 12 and 12. The list floor: 3 prints 7 rows over the five events,
2 prints about 35. The peak bar: 5% prints 4 rows, 10% prints 12 before
duplicate suppression, 15% prints 20, 20% prints 31, 30% prints 47. The
concentration bar: 1.25x prints 16, 1.5x prints 12, 2x prints 4, 3x prints none.
Two of the seven rows are worth a second look on their own terms: Sacred Foundry
in Izzet Prowess mainboards at 3 of 30, a land rather than a card choice, and
Grafdigger's Cage in Boros Energy sideboards at 3 of 16 against an MTGO peak of
9%, which is a card that deck plainly knows.
*Applies if adopted*: the four `TRACK_NOVELTY_*` constants stand as shipped.
Two questions stay open either way. A floor on the cut population: the
prototype produced two rows that were the sample size talking, Tron 3 of a
4-list cut at Amsterdam and Simic Neoform 3 of 6 at Baltimore, and a floor of 10
lists drops both but also drops the Brisbane half of Jennifer Walters, where
raising concentration may drop them on their merits instead. And a floor on the
fortnights the MTGO peak is read over: a closed bin of two lists holding a card
once is a 50% peak that silently kills the card as a novelty for good, which is
the shape `TRACK_RETURN_ABSENCE_LISTS` exists to refuse elsewhere. A floor of 10
lists there changes exactly one row today, so it is cheap either way and has not
been taken.
