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
Any paper tournament the pilot puts in `config.MAJOR_EVENTS`: a Spotlight, a Pro Tour, an RC. All are read the same way and share one section of the report and one figure. A storyline entry like any other: read against whatever came immediately before it, and read against by whatever comes after. The event is read against both entries behind it, the last fortnight that closed before it and the paper event before it where that event was played no earlier than the fortnight opened, and the fortnight the event fell in is read against every event inside it and against the fortnight before it. Both directions take every entry behind them and never a choice of one, the paper row holding the medium constant and the MTGO row saying whether the field the deck came from had already moved; ordered strongest first, which is the paper one. Never an event of its own week: two Regional Championships on one weekend are two rooms rather than a before and an after, so each is read against the entries behind the weekend and neither against the other. A baseline event falling inside the baseline fortnight is no double count, an event's lists never entering the store. See ADR 0003. MTGO moves what pilots take to a Pro Tour and a Pro Tour moves what turns up on MTGO after it, so the chain runs through the event in both directions; a fortnight read against the fortnight before alone would report the response without the thing it responded to, and one read against the event alone would report the response without saying whether the field moved on its own terms. On a fortnight the strongest reading is the fortnight before, holding the medium and the room constant, so that one leads and the events follow in the order they were played; two events in one bin stay two rows, pooled being a share neither room reported. It gets its own row for the focus, not because it is a separate story. Its lists are never folded into a fortnight's own numbers: an event week sits inside a fortnight rather than beside one, and pooled it would be most of the bin. It stays out of the store.

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

**List id**:
A list's name in the store: the event it was published in and the pilot who registered it, as `modern-challenge-64-2026-07-0412846489#J4K3ST3R02`. One pilot can trophy twice in a league dump, so his second list takes an ordinal and his first keeps the bare key, and an id does not move when a later list arrives. It was the list's position in the raw cache until 2026-09-13, which is a fact about the order files sort in and not about the list: a refresh that cached 64 lists slugged early moved every id from June on, and the ids quoted across two archived reviews came to name other lists with nothing saying so.

**Ingest index**:
The committed record of every published list the raw cache holds, one row each, kept at the list rather than at the event. The cache itself is too large to commit, so without this nothing in the repo says what the analysis history was built from and no run can tell its population from the last one's. The list is the grain because the unsettled days are the ones hardest to speak about: a league dump gains 5-0s through its own day, so a refresh overwrites captures it already held, and a record kept at the event would report those days unchanged while lists appeared inside them. Free of the archetype rule and of every other reading, since what membership makes of a list moves when the rule moves and what the site published does not: which arrivals are Goryo's is asked of the store afterwards, against the index rather than inside it. Withdrawals are reported beside arrivals, lists leaving the history quietly being the same failure as lists arriving quietly.

### Deck concepts

**Archetype**:
A family of decks recognised by its signature cards. Goryo's, Blink and Neoform are the three here.

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
A recognised camp within the archetype, defined by a divergence card. Currently: Fallaji camp (3-4 copies) vs non-Fallaji camp (0 copies); 1-2 copies is a hybrid experiment belonging to neither consensus. A tracked deck's rule is ordered instead: each version names the cards that commit a list to it, the first version the mainboard holds any card of takes the list, and a list holding none is the default version. Presence and never a count, except where a version is a colour, which Blink's Esper half also is: a version read on a colour is read on any spell of it the mainboard casts and never on the splash line, a playset naming a build and not a version. Consensus builds and novelty are computed per variant, never across camps. The weekly report calls a camp a **version of the deck**, that being the pilot's word for it, and prints the name in `config.VERSION_NAMES` where the rule's name is not the pilot's: the non-fallaji camp is the **Riddler** build. Display only. Everything else here, every identifier in the code and every stored record keys the camp by its rule name.

### Tracked decks

**Tracked deck**:
A deck the engine classifies and reports on weekly without optimising. It has no reference list, no hypotheses, no slot audit and no playtest queue: what it has is a fixed set of weekly figures and a change timeline, computed the same way every week for a team meeting to read. The tier is the point of the word. Goryo's answers to a pilot who plays it and to a submission date; a tracked deck answers to neither, and reading one with the other's instruments would put an engine's guesses where a pilot's knowledge belongs.
_Avoid_: archetype on its own (Goryo's is one too, and the difference between them is the whole distinction)

**Blink**:
The first tracked Modern archetype: a mainboard holding Phelia, Exuberant Shepherd, Flickerwisp, Overlord of the Balemurk and Witch Enchanter, all four, cast on white, blue and black by the splash line. The four are required together because no smaller set is the deck: Phelia alone admits a white energy build and a Boros build, and Ephemerate alone is half Goryo's. A Mardu build shares all four and is a different deck, and the splash line is what says so. Membership is tested after Goryo's, so a list holding both signatures takes one name and it is Goryo's.

**Splash line**:
The colour half of a membership rule, and Tron's version rule. Read on the spells the mainboard casts and never on its sources, a Sacred Foundry held for a sideboard card saying nothing: under five off-colour nonland cards is a splash inside the deck, five or more is a deck that goes deeper into the colour, and a full playset of one off-colour card is the other deck's card whatever the total, so 4 Quantum Riddler is Jeskai Energy and 4 Flame of Anor is Grixis Frog. Blink, Boros Energy, Boros Ponza, Dimir Midrange and UWr Control read it; Tron reads it the other way round, a list deeper than a splash into blue or green being that colour's version. A card the site published no colour for reads as colourless, which is the one way the line can go stale silently, so the count it turned away is printed every week and every list it turned away is in the fall-out.
_Avoid_: off-colour exclusion (the earlier rule, read on sources, which turned away six Blink lists on one land)

**Engine**:
A deck a membership rule has to turn away, named once in `config.ENGINES` with the mainboard cards that mark it. A list answering to a deck's core and carrying an engine its rule names as another deck's carries more than one engine and belongs to nothing; variation inside an intact engine stays, and a hybrid brew on an intact shell is out for now. Which engines count as another deck's is the rule's to say, deck by deck, because a marker names a deck only beside a shell it does not belong to: Eldrazi Temple names the Boros Eldrazi brew beside the energy four and sits in every Trudge and Tron list.

**Core and supporting**:
A rule's core is the cards every list of the deck holds. A staple the shell can test without is supporting rather than core, Channeler in Prowess, Manufacturing in Affinity, Erode in Ponza, Karn in Tron, and a list that cuts one of those is the same deck in a different build. A rule reads its supporting tier as a count where the count is what says which deck, four of six in Prowess and Ponza and one of two in Grinding Station and Devoted Combo, and otherwise reads nothing of it: Karn and Manufacturing are no part of their rules. Blink is the opposite case, its four creatures being the deck only together.

**Fall-out**:
Every list that holds a deck's core and belongs to nothing, with the deck and the reason its rule turned it away: an engine's name, the splash line, a floor, a supporting tier. Written to the store on every rebuild and printed by `tracker refresh` per deck and reason with the fortnight's count beside the total, so a deck adopting another deck's engine card shows up as a growing count rather than as a silent decline in its storyline.

**Version boundary**:
Every member of a deck's default version whose mainboard is a named version's, with the version it looks like and what says so. A version rule reads its markers in order and drops every list holding none into the default, so the default is the one version no list is ever read into: a list that is a named version on every other reading takes it silently and its storyline is read as the default's, and nothing else in the build would say it happened. Two shapes are read, being the two pass three's sweep used. A colour comes off the rule, which names the cards a version is drawn on and sometimes the colour itself, because a version can be drawn on a colour without its whole population casting it, 48 of the 387 Gruul Broodscale lists being on colourless Writhing Chrysalis alone. A card comes off the population, `config.VERSION_MARKER_SHARE` of the named version's lists holding it, and a version under `config.TRACK_MIN_LISTS` has no population to read that off, nine tenths of a one-list version being every card in one decklist. Either way the default version has to do without it, under one list in ten, or a version's own colours read as its neighbour's: black sits in three quarters of mono-green Broodscale off Dismember, which Phyrexian mana casts, and every traditional Zoo list casts blue and black. Sources say nothing, the way they say nothing to the splash line. Written to the store on every rebuild and printed by `tracker refresh` per deck and version with the lists named, a boundary being settled one list at a time where the fall-out is watched as a count. A deck of one population has no default to fall into and is no part of it, and a deck whose versions partition cleanly prints a zero rather than going unlisted. A deck whose rule says `version_boundary` is false is left out whole and prints nothing at all, every signal the check could raise there having been ruled a build already: Tron is the one, its splash line and Portent of Calamity ruled builds by its version rule and Emrakul, the Aeons Torn ruled one on 2026-09-13, blue Tron being a version of the colourless deck that plays more of it rather than a deck the card names. Saying such a deck partitions cleanly would be the same confusion the other way up, a deck nothing looked at reported as a deck nothing was found in. What counts as a marker is read over the MTGO store alone and written to it on every rebuild, the paper lists in `data/raw-melee` being a population it never pools. Which lists carry one is read over both: `tracker event-fetch` reads each configured event in `config.MAJOR_EVENTS` against those markers, the store saying what a marker is and the event saying which of its lists hold one, so no denominator counts a paper list beside an MTGO one. That split is what lets a paper field be read at all, one event's nine-list version being far too thin for the one-in-ten bar: two lists of it casting red read as a fifth of the version rather than as two lists, and run over that field alone the check finds nothing. Run over the cached events today it names no list, the Lightning Bolt ruling of 2026-09-13 having closed the gap the two Pro Tour Broodscale lists showed: reverted, it names both on the colour, which is the reading that would have raised them. An event whose lists all sit in versions their mainboards agree with says so, and an event nobody has fetched is not read at all and says nothing either way.

**Esper Blink / Orzhov Blink**:
Blink's two variants, split on mainboard Watery Grave or any blue spell the list casts. Presence and not a count, a variant here being which colours the deck is, which one copy settles. A rule drawn on blue sources throws away the Orzhov lists that fetch; the Grave alone partitioned the archetype until SuperCow12653 registered 2 Teferi off Hallowed Fountain and Meticulous Archive twice, and the card and the colour together name the version whichever way a pilot builds the mana. Presence is the whole deck's and every other reading in the weekly report is the Esper variant's; Orzhov is carried as bare numbers in the summary, its challenge-class population being single figures over the whole post-regime history, which is enough to say it exists and nowhere near enough to read a build or a conversion rate off.

**Neoform**:
The second tracked Modern archetype: a mainboard holding Neoform, Allosaurus Rider, Eldritch Evolution and Planar Genesis, all four. Planar Genesis is the card that says which deck: the other three are the engine of the four-colour Glittering Wish build on Gemstone Mine as well, and that is a different deck. No colour rule, nothing sharing the four being another colour of this one, and no variant, nothing in the history forking it: its members carry no camp and every reading in its report is the whole archetype's. Tested after Goryo's and Blink, like every tracked rule. The report calls it **Simic Neoform**, the pilots' name for it.

**Grinding Station**:
A mainboard holding Grinding Station, Emry, Lurker of the Loch and Sewer-veillance Cam, with Oswald Fiddlebender or Loki, God of Mischief over them. The trio is what no other deck runs together; Oswald appears in this deck alone, but the mono-blue build on Loki has no Fiddlebender, and forcing the card would leave half the deck outside. The Song of Creation deck runs the trio and neither, and the Kappa Cannoneer artifact deck that bolted Oswald on is a different one. So is the Kethis combo, whether or not it adds Loki for Plaza of Heroes: Kethis, the Hidden Hand is its engine. No colour rule, a green source being a splash for Haywire Mite inside the same deck. One population. Keyed `oswald` in the store and under `data/tracking/`, the name it was tracked under first.

**Domain Zoo**:
A mainboard holding Scion of Draco with Territorial Kavu, or with Leyline of the Guildpact and Psychic Frog, a Kavu-less Frog list being the deck's Frog version and not another deck. No colour rule: the deck is five colours and its manabase is the part that moves. Two versions, split on mainboard Psychic Frog: **Frog**, the bluer build, and **Traditional**, the tracked version.

**Broodscale**:
A mainboard holding Basking Broodscale and Blade of the Bloodchief, the combo. Mono-Green Eldrazi and Eldrazi Tron share the shell and neither card. Three versions, read in order: **Gruul** on Unholy Heat, Writhing Chrysalis or Lightning Bolt, **Lab** on Ugin's Labyrinth, and **mono-green** on neither. Red is read on spells and not sources, Grove of the Burnwillows sitting in nine of ten mono-green lists; a list on both red spells and the Labyrinth is Gruul, and a list on neither marker is mono-green whatever else it splashes. The Lab version is tracked, chosen from the data on 2026-09-12 when it had become most of the deck.

**Devoted Combo**:
A mainboard holding Devoted Druid with Tyvar, Jubilant Brawler or Tyvar, the Pummeler, both unique to the deck; Springheart Nantuko and Quirion Ranger are its own cards too, and the Druid-less Nantuko deck is a different one. One population.

**Affinity**:
A mainboard holding Kappa Cannoneer and Pinnacle Emissary, the shell, with any one of Engineered Explosives, Weapons Manufacturing or Krang; the Cannoneer alone admits the Hammer build. Explosives and Manufacturing are in nearly every list and are supporting, some lists testing without either, and a list on none of the three is the Frogmite or Ravenous Robots aggro deck. Basim Ibn Ishaq, Sewer-veillance Cam and Song of Creation each name a different deck, and Tamiyo beside Mox Amber is the Tamiyo artifact deck unless Manufacturing sits beside them. One population.

**Izzet Prowess**:
A mainboard holding at least two Steam Vents and Lava Dart with four of the six staples, Cori-Steel Cutter, Monastery Swiftspear, Dragon's Rage Channeler, Slickshot Show-Off, Mutagenic Growth and Stormchaser's Talent: a list that cuts Channeler is the same deck in a different build. The Cutter alone admits the artifact decks on Emry and Tamiyo, the land keeps out the red and Boros prowess lists, and Arclight Phoenix names another deck. One population.

**Eldrazi Trudge**:
A mainboard holding Slumbering Trudge and Fanatic of Rhonas. The report calls it **Trudge**. One population.

**Tron**:
A mainboard holding Urza's Tower, Urza's Mine and Urza's Power Plant; Karn is supporting. Three versions by their markers: **Blue** on Stock Up or Force of Negation, **Green** on Chromatic Sphere, Chromatic Star or Sylvan Scrying, and **Colourless**, the tracked version, on neither. The splash line names membership and never a version here: a playset of Dress Down, Portent of Calamity, Malevolent Rumble or Ancient Stirrings inside the colourless Eldrazi shell is a build reading.

**Boros Energy**:
A mainboard holding Guide of Souls, Ocelot Pride, Ajani, Nacatl Pariah and Goblin Bombardment, cast on red and white by the splash line. The two creatures alone admit the Azorius blink and Selesnya Birthing Ritual decks; Mardu and Jeskai energy share all four and are different decks, Jeskai on a playset of Quantum Riddler and Mardu on five or more black cards. One population.

**Boros Ponza**:
A mainboard holding Cleansing Wildfire with four of the six land-destruction staples, Erode, Field of Ruin, Demolition Field, Price of Freedom, Wrath of the Skies and Solitude, cast on red and white by the splash line. Erode is in almost every list and is supporting, the plan being the suite and not the card; the Pinnacle Monk red decks on Wildfire and Price run nothing else of it, and a list on a playset of Teferi is the Jeskai deck. One population.

**Dimir Midrange**:
A mainboard holding Psychic Frog and Quantum Riddler, cast on blue and black by the splash line: Meltdown in the sideboard off one Steam Vents is still Dimir, a playset of Flame of Anor is Grixis Frog. Frog alone admits Dimir Oculus, which the Unearth it reanimates with names rather than the Oculus itself, a one-of Oculus in the stock shell being a threat slot. The mono-blue Namor, Archmage's Charm and Disrupting Shoal tempo shell on a black splash is another deck again. Tested after Goryo's, Blink and Domain Zoo, which share the pair too. One population.

**UWr Control**:
A mainboard holding Teferi, Time Raveler with any one sweeper, Wrath of the Skies, Supreme Verdict, Terminus or Temporary Lockdown, and any of the ten draw engines, Consult the Star Charts, Isochron Scepter, Narset, Day's Undoing, Orim's Chant, Thundertrap Trainer, Flow State, Wan Shi Tong, Stock Up or Brainsurge, cast on blue, white and red by the splash line. The blue and white control shell tracked as one deck: control adapts its interaction to the meta, so the sweeper is a slot and not a card and Galvanic Discharge is a build reading, and Jeskai and Azorius are the same deck. Removal is a slot too, so a playset of Fatal Push off colour does not name another deck while the rest stays under the line; Ephemerate does name one, a blink package inside an intact control suite not being control. One population. Keyed `jeskai` in the store and under `data/tracking/`, the name it was tracked under first.

**Storm**:
A mainboard holding Ral, Monsoon Mage, Ruby Medallion and Past in Flames. Ruby alone admits Belcher and Ral alone an Izzet storm on Stormcatch Mentor. No colour rule, the sideboard colours being the Wish targets. One population.

**Temur Living End**:
A mainboard holding Living End, Shardless Agent and Violent Outburst. The Sultai build on Formidable Speaker shares the first two and never the Outburst. No colour rule: Temple Garden sits in most lists beside no white spell. One population.

**Report subject**:
What one weekly report is computed over, named once in `config.REPORTS` rather than passed as a flag. It fixes the archetype, the version its performance and build readings are taken on, and the slots it watches; presence is always the whole archetype's. One subject per directory under `data/tracking/`, and one population per file in it, `weekly.csv` for the archetype and `version.csv` for its tracked version, because a pooled row and a one-camp row in one file are two measurements under one column heading and nothing in the file says which a row is. Kept apart from the membership rules: a rule says what a list is, a subject says which of those lists a report reads, and Goryo's has a rule already without being a tracked deck.
_Avoid_: deck, where the population is what matters (Blink is one deck and one subject; Goryo's is one deck read as two populations)

**Pooled camps**:
Every camp of an archetype counted as one population, which is what every report's presence figures are taken over. A metagame share is a share of the whole deck, and read on one camp of three it answers a third of the question. Never the performance or build readings, a finish being one build's: pooled, a card at nine tenths of one camp and none of another reads as the deck at half of it, and a camp arriving reads as the deck changing its mind. Goryo's pooled looks like it drifted a copy of Quantum Riddler over the regime, where inside the non-fallaji camp the card is flat at four.

**Tracked version**:
The one camp a subject's conversion, goldfishing figure, numbers table, storyline and Spotlight findings are read on, where its presence figures are pooled. The non-fallaji camp for Goryo's, the Esper variant for Blink, the Traditional version for Domain Zoo, the Lab version for Broodscale, the Colourless version for Tron. Labelled in the report wherever it is read, because the presence figures above would otherwise put a list count beside a row it was never read against.
_Avoid_: build camp (the earlier name, from when only the build readings were read on it)

**Week**:
Monday to Sunday, the bucket every weekly reading groups on. Keyed by its Monday wherever it is stored, that being what the store's `date_trunc` returns and the name every frozen row and summary file carries. Named by its Sunday wherever it is read, on the report's header, its table and the x-axis of every figure, because a week labelled with the day it opened reads as the day the data stops and puts the reader a week behind the figures.

**Detection bin**:
The fortnight a change is read over, anchored at the regime boundary and never overlapping. A week of this deck runs from nine published lists to sixty-four, so a threshold set as a share of a week measures the sample size: at every bar from five points to twenty-five a weekly reading reverses in the next week about two times in five, and raising the bar loses findings without buying purity. Over a fortnight the same bars reverse between fifteen and twenty-two percent of the time and the rate falls as the bar rises. The plots stay weekly; only the detection is binned. Anchored rather than trailing, so the bin a date falls in never moves and a row written six weeks ago still describes the same fortnight. A bin of fewer than `config.TRACK_ROW_MIN_LISTS` lists, or one read against a bin that holds fewer, is too thin to read a move across and prints a row saying so in place of its comparison rows (Alejandro, 2026-09-13). The floor is on the smaller of the two populations, that being all the evidence there is: read without it a bin of 8 lists prints the same kind of claim as a bin of 130 and only the counts beside the row tell them apart, and 66 of the 597 rows frozen before it read across such a bin. Returns are no part of it, resting on the absence behind the bin and answering to `TRACK_RETURN_ABSENCE_LISTS` instead, and a fortnight read against a paper event answers to `timeline.shifted`, the two populations there being nowhere near one size.

**Returning card**:
A card appearing in a bin having been out of the deck for `RETURN_ABSENCE_DAYS`, at a share larger than it has ever held. Three conditions and each drops a different false one. The absence is a month rather than a fortnight because a staple running at a few lists a week misses a fortnight on chance alone: Orcish Bowmasters, a card of ninety-eight lifetime appearances, reads as a return at the shorter window. The gate is per zone because a sideboard churns far harder than a mainboard. And the share has to beat the card's own peak, which is what separates a card the field turned to from one that was always a one-off and is a one-off again. Read against the whole store rather than the post-regime window, since how long a card has been gone is a fact about the deck and not about the regime; a window starting at the boundary calls every card of the opening fortnight new.
_Avoid_: fringe card (the archetype-level reading, which is a share of a whole history rather than an absence)

**Board migration, as a timeline row**:
A returning card that was in the other zone the bin before. Read one zone at a time it is new to the mainboard, which is true and reads as novelty, so the row says which it is: a sideboard staple being promoted is a decision about what the card is for, not the deck discovering it.

**Copy drift**:
The mean copies of a staple, over the lists that register it, read entry to entry as a timeline row. The reading for the slots the deck argues about the number of rather than the presence of, which no adoption share can see because those cards sit at near-total adoption. Read on the mean and never the mode: on this deck's cards the modal count oscillates every other week and every oscillation reverses, a plurality one pilot can flip holding it. The staples are found and not named: a card held by seven lists in ten on both sides of the comparison. Under that bar the mean moves when a different set of pilots arrives, and the adoption reading is already reporting the arrival; read unfiltered the scan doubles as fetchland tuning and five-list means, and a quarter of its rows reverse the fortnight after. Every staple reads here, lands included, a change in any card of the deck being what the timeline is for; a watched slot reads by count instead.

**Watched slot**:
A slot named in a subject's `watch`, read at ten points rather than twenty and by copy count rather than by presence. It answers the question a mean cannot: two copies going to three in a fifth of the camp moves a mean over eighty lists by three tenths of a copy, under any bar a copies reading can hold, where the same decision read as a distribution is a fifth of the lists moving from one row to another. The finer bar holds only because the list is short and every entry on it is a question the pilot asked: unfiltered at ten points this population gives 78 rows across eight fortnights against 41 at twenty, and 38% of them reverse in the next fortnight either way. Read here and nowhere else, the ordinary adoption reading skipping a watched slot, so one decision earns one row.
_Avoid_: copy drift (the mean reading, which a watched slot replaces rather than joins)

**Manabase reading**:
The land count read as a configuration of the whole list, fortnight to fortnight, at the standard bar. The reading no card-level one can stand in for: the land a camp adds is a different card in every list, so a camp walking from 21 lands to 22 moves no card's adoption and no card's copies, and read card by card the decision is invisible. A paper list's count is read off the names MTGO has typed as lands, a melee decklist page being fetched for its cards and not its type headings; a land no MTGO list has ever registered goes uncounted, which at a tracked deck's manabase is no land at all.

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

**Novelty, at a major paper event**:
A card `config.TRACK_NOVELTY_MIN_LISTS` or more of an event's good finishers registered, which the deck has not been playing and which the rest of its own field at that event is not. A watchlist entry and never a finding that the field moved: it is the thing a pilot reads off a standings page by eye, and no other reading here reaches it. Adoption wants a fifth of the population to swing, so a card it reports is established rather than new, and the return reading is a claim about one population's history over months that a paper field cannot carry. The good finishers are the top `TRACK_NOVELTY_CUT_SHARE` of the field, by the same finishing share every positional reading uses and never a rank: a fixed top 64 is the top 17.7% of Pro Tour Amsterdam's 362 seats and the top 4.3% of RC Baltimore's 1494, and at Dallas it leaves non-Fallaji Goryo's one list to read a novelty off. The denominator a row counts over is the deck's own lists inside that cut and never the cut itself: Baltimore seats 1494, so its top fifth is the top 299 finishers, Devoted Combo put 14 of its 59 lists there, and a row reads 5 of 14. So the list floor bites unevenly and the counts beside the row are what say how hard. Three lists is a tenth of the 30 Izzet Prowess put in Baltimore's top fifth and half of the 6 non-Fallaji Goryo's put in Brisbane's, so a popular deck at a large event is read at a tenth of its good finishers and a thin deck at a small one at a majority of them. Novel is read per zone off MTGO, no fortnight of the deck's history having held the card above `TRACK_NOVELTY_PEAK` in that zone, a sideboard churning far harder than a mainboard. Over the fortnights that closed before the event and never the one it falls in, which is the baseline rule the event's own comparison already reads by: a bin part way through is a few days of publication rather than a fortnight, and a card in one list of two there reads as half the deck playing it and silences the row. Concentrated is read against the deck's own lists at the same event, `TRACK_NOVELTY_CONCENTRATION` times its share of them, so no row crosses two populations: one room, two slices of it. A card an adoption or watched-slot row already reports in the same entry prints no novelty row, the move being the stronger of the two claims. Computed fresh on every render and never frozen, a novelty being a claim about an event rather than about a fortnight. There is no MTGO counterpart to this reading and there cannot be one. It is a contrast between a cut and the field under it, and MTGO publishes no field: a challenge publishes its top 32 and a league its 5-0s, so every MTGO list this project holds is already a good finish. Read there, the group a card would be concentrated against is itself the top 32 of several hundred, everyone in it having finished well, and the contrast collapses into the sample. MTGO carries the other half instead, its history being what says the card is new, which is the bar `TRACK_NOVELTY_PEAK` sits on: the two mediums do different jobs here, MTGO saying what the deck normally plays and paper saying what its good finishers did differently.
_Avoid_: returning card (the MTGO reading, which is an absence over months rather than a concentration in one room)

**Cross-population reading**:
A comparison whose two sides are different rooms: an Australian paper field, an American one, a Chinese one and the MTGO field are four populations. A card at nine tenths of one and half of another is not the deck changing its mind, so a row spanning two of them is marked as one. The room a paper event drew from is its configured `region`, and the medium is not a proxy for it: paper against paper is one room only where the regions match, so Baltimore against Dallas is not a cross-population row and China against Dallas is, though both are paper a week apart. Marked on the medium alone until 2026-09-14, which read every paper pair as one field. A row against MTGO crosses whatever the regions say. The paper row is still the stronger of the two an event carries and still leads: it crosses at most the room, where the MTGO row crosses the room and the medium both. A Pro Tour is its own region and matches nothing, its field being invited worldwide rather than drawn from one metagame. Marked rather than suppressed: the rooms are not decoupled, and a reader told which room each side came from can weigh the row.

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
