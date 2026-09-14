# Classifier review, RC Baltimore (melee 405588)

**Reviewed:** 2026-09-14, the 1494 lists of the Regional Championship at SCG CON Baltimore (12 September, 15 Swiss rounds and a top 8, all Modern, 1 unread), fetched 2026-09-14. One angle over every list: the rules as adopted on 2026-09-13, read beside the deck name each pilot typed on melee. Every fall-out row read by hand, every list holding two thirds of a deck's core read by hand, and all 1202 members scanned for a typed name that names another tracked deck. Single finder, no independent verifier: the rows here are candidates for Alejandro's verdict, not rulings.
**Outcome:** resolved. 2 lists ruled by Alejandro on 2026-09-14, both in. The rulings are pilot entries in `HEURISTICS.md`, revising the Blink entry of 2026-09-13 and the Trudge entry of the same day, and were applied to `tracker/config.py` the same day; every measured effect below landed as ruled and the store was rebuilt. Every other fall-out row and near miss is an adopted ruling firing exactly as it was written, and is listed for the record. Nothing here blocks the 2026-09-13 reports.

The field reads 1202 members over 16 tracked decks and Goryo's, 56 lists holding a deck's core and turned away by a rule, 235 holding no tracked core at all, and 1 unread. The 235 are untracked decks and nothing is hiding in them: Amulet Titan 23, Tameshi Belcher 18, Golgari Yawgmoth 9, Hollow One 8, Birthing Ritual 15 across four colour pairs, Samwise 7, Eldrazi 14, Burn 4.

# Rulings

- **Blink without Flickerwisp: in, Psychic Frog in that seat is the same deck innovating.** The core is Phelia, Overlord of the Balemurk and Witch Enchanter; Flickerwisp is a slot. Measured: 8 MTGO lists since the bans and 7 paper lists move in, nothing out.
- **Trudge without Ugin's Labyrinth: in, the rule reads the Eldrazi shell and not the land.** Membership is Slumbering Trudge and Fanatic of Rhonas with any one of Ugin's Labyrinth, Eldrazi Temple, Kozilek's Command or Fight Rigging. Measured: exactly TheJV's list moves in, 0 MTGO lists, and the five Springheart Nantuko lists the 2026-09-13 clause excludes stay outside.

# What was put to him

| list | rank | pilot | name typed | record | reads | category | conf | reason |
|---|---|---|---|---|---|---|---|---|
| melee:46a290e0-5e09-473c-8778-b4c20161d8c3 and 5 more, below | 437, 491, 687, 773, 1067, 1194 | Jsnodgrass, carwolf, MylL, ViktorMaliuha, DiverseCurse, JonA26 | Esper Blink (all six) | 5-4-0 to 1-3-1 | none (blink turned away on the fourth core card) | false-negative | medium | Six pilots typed `Esper Blink` on a list holding Phelia, Overlord of the Balemurk and Witch Enchanter with Ephemerate in the mainboard, and cutting Flickerwisp for Psychic Frog: five of the six run Frog as a four-of, four of those alongside four Quantum Riddler. The 2026-08-07 ruling made membership the four cards and counted nine MTGO lists that had cut one; the whole MTGO cache now holds 12 without Flickerwisp, 8 of them since the bans, and this one event holds 6, against 112 Blink members here. Measured: dropping Flickerwisp from the signature moves 12 MTGO lists across the whole cache, 8 of them since the bans, and 7 paper lists in (these six and CruzH at Dallas), and nothing out. Is Blink-on-Frog a Blink build that swapped a slot, or the Dimir deck borrowing the Blink package? |
| melee:c0197412-3b0d-4062-8149-b4c20129b749 | 735 | TheJV | Mono-Green Eldrazi | 4-5-0 | none (trudge turned away on Ugin's Labyrinth) | false-negative | low | 4 Slumbering Trudge, 4 Fanatic of Rhonas, 4 Fight Rigging, 4 Kozilek's Command, 4 Sowing Mycospawn, 4 Malevolent Rumble, 4 Disciple of Freyalise, 4 Emrakul, 2 Ulamog: the Eldrazi shell whole, on a manabase with no Ugin's Labyrinth. The Labyrinth clause was written to exclude the Springheart Nantuko decks, which run Quirion Ranger and Summoner's Pact and none of the Command, Rigging or Mycospawn shell, and its five named exclusions are all that build. This list is the opposite case and the clause catches it anyway. Measured: dropping Labyrinth from the signature moves exactly those five MTGO lists in as well, so the clause cannot simply lose the card. Should the rule key on the Eldrazi shell rather than on the land? |

The six Blink lists in full: `46a290e0-5e09-473c-8778-b4c20161d8c3` (437 Jsnodgrass, no Frog, 3 Ephemerate), `8c03ee75-56e3-4b62-bfe8-b4c1004bb14a` (491 carwolf), `41c74578-a8f6-4984-8b9b-b4c20141cdb8` (687 MylL), `f7370c77-0c93-4e9d-ad7a-b4c2013a9203` (773 ViktorMaliuha), `540ab8cb-4e2d-4e8b-9442-b4c2014e3d51` (1067 DiverseCurse), `f7d5c81e-706f-4ea3-ac04-b4c100312d8f` (1194 JonA26).

# For the record

Every fall-out row, grouped by the card that fired it and settled by an adopted ruling. The 56 rows carry 59 reasons between them, three lists being turned away by two rules each, and the five that also feed the Blink question above are counted here as well. The best finish in each group is named so the size of what a rule turns away is on file.

| n | deck / reason | fired on | best finish |
|---|---|---|---|
| 23 | energy / playset | Quantum Riddler x4 | 109 RyaN4, 10-5-0, `Jeskai Energy` |
| 5 | jeskai / blink | Phelia x4 | 17 ncowden, 11-3-1, `Jeskai Blink` |
| 5 | dimir / persist | Persist | 304 KingSolomon42, 7-5-0, `Esper Reanimator` |
| 7 | dimir / playset | Phelia, Solitude, Ephemerate or Ragavan as a four-of | 409 Jee33, 5-4-0, `Grixis Midrange` |
| 3 | energy / splash | five or more black cards | 309 MarcelineOrion, 7-6-0, `Mardu Energy` |
| 4 | affinity / basim, affinity / cam | Basim Ibn Ishaq, Sewer-veillance Cam | 56 Arcbound_Papi, 11-4-0, `Izzet Affinity` |
| 2 | jeskai / omnath | Wrenn and Six x4 | 802 Lexton, 3-4-0, `Four-Color Control` |
| 2 | jeskai / playset | Wilderness Reclamation and Planar Genesis x4 | 430 Spys212, 5-4-0, `Bant Control (Kaheera)` |
| 1 each | dimir / goryos, dimir / namor, dimir / shadow, dimir / splash, jeskai / splash, blink / playset, oswald / kappa, prowess / phoenix | Goryo's Vengeance, Namor, Death's Shadow, a seven-card red splash, a five-card black splash, Bolt and Ragavan x4, Kappa Cannoneer x4, Arclight Phoenix x4 | 513 Andeloth, 5-4-0, `Dimir Midrange` |

The 13 remaining near misses, each holding two thirds of a core and each named by the ruling that excludes it: 5 `Grixis Goryo's` on Goryo's Vengeance, Atraxa and Faithless Looting with no Ephemerate (386 MatW18 best at 5-4-0), the near-miss watchlist the 2026-08-07 ruling created; 4 `Living End` on Formidable Speaker, Overlord of the Balemurk and Shardless Agent with no Violent Outburst (234 BranniganLaw, 8-6-0), the Sultai build; 2 cascade decks holding Shardless Agent without Living End itself (`Temur Combo`, `Four-Color Rhinos`); 798 poxromana `Izzet Storm`, the Stormcatch Mentor shell on Ral and Past in Flames without Ruby Medallion, which the Storm ruling names; and 517 Zozbie `Orzhov Blink`, three of four core cards but out on a mainboard Guide of Souls, which the Blink ruling names.

Mislabels, the classifier right and the typed name wrong, 9 of 1202 members: 34 Milesw `Esper Goryo's` is Domain Zoo on 4 Scion of Draco, 4 Leyline of the Guildpact and 4 Territorial Kavu, and it finished 11-3-1; 152 ctreu01 `Izzet Prowess` is Boros Energy on the full Guide, Ocelot, Ajani and Bombardment core, 10-5-0; 485 Benjipug and 579 Skip2Combat `Esper Midrange`, 487 SomethingNormal `Esper Goryo's` and 654 Rabadon123 `Mono-Green Broodscale` are all Esper Blink holding the whole four-card core; 531 bresett123 `Domain Zoo` is Dimir Frog; 1037 Vinylpenguin `Esper Goryo's` is Devoted Druid combo; 1352 RonaldCherrycoke `Dimir Midrange` is Izzet Prowess. As at China, the typed name is weak evidence and `Mono-Green Broodscale` on an Esper Blink 75 is the plainest case of it this project has seen.

One unread: 1454 colorblindkevin, 69 Swamps and no sideboard under the name `Living End`, dropped by the rule of 2026-09-13 and counted here rather than read by hand. Four more lists run a legal mainboard over 60 and are read normally: 519 Laxboy1983 at 65, 858 Mooch at 76 and 1429 SkyB1 at 250 are past `MAINBOARD_MAX` and answer to no rule, and 1402 Mihicular's 40 Rat Colony on a clean 60 with an empty sideboard is read as registered.

# Population note, not a classifier question

The Goryo's hybrid spike at China does not repeat here. Baltimore is 122 Goryo's lists: 105 non-fallaji, 10 hybrid and 7 fallaji, so the hybrid camp is 8% of the event where at China it was 20 of 40. Across the five fetched events the shares are Amsterdam 15%, Brisbane 28%, Dallas 7%, Baltimore 8% and China 50%, and Baltimore is the largest field of the five. Read together, the two rooms of one weekend say the China field was the outlier and not the turn in the deck, which is the question the China review left open before the Goryo's report calls the non-fallaji camp the deck.
