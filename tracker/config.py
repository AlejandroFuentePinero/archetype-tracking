"""Named configuration values. v2 repoints the engine by editing these."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = REPO_ROOT / "data" / "raw"
DB_PATH = REPO_ROOT / "data" / "engine.duckdb"


FORMAT = "modern"

# Printings the site publishes as separate cards that are one card. Superior
# Spider-Man is Kavaero, Mind-Bitten with the Marvel IP on it; a list is
# published under whichever printing its pilot registered, and a pilot may
# register both. The Magic name is the canonical one, being what most of the
# history is already published under.
# Elesh Norn is the same card again: the site publishes the March of the
# Machine legend under its full name almost everywhere and under the bare one
# twice, and the pilot confirmed they are one card. Left unmerged it reads as a
# card the archetype had never played, which is exactly the finding a returning-
# card reading exists to make and exactly the wrong one.
CARD_ALIASES = {
    "Superior Spider-Man": "Kavaero, Mind-Bitten",
    "Elesh Norn": "Elesh Norn, Mother of Machines",
}


# How far back the analysis history reaches. The history opens on the regime
# boundary: what was played under the old rules is a different era and is not
# in the store (Alejandro, 2026-09-13). The boundary is the day after the
# announcement, the events published on the announcement date having been
# played under the old rules. The raw cache keeps whatever was fetched before it.
HISTORY_START = "2026-05-19"

# The regime boundary the history spans (see ADR 0001). Lists either side of it
# belong to different eras, so every window is bounded by it. The announcement
# Monday, a day before the history opens: it is the calendar every fortnight
# bin and window is anchored on, and anchored on the Tuesday the bins would
# close on a Monday and the storyline would freeze each fortnight a week late.
# No list on the boundary day is in the store, so nothing reads across it.
REGIME_BOUNDARY = "2026-05-18"


# The baseline window: how far back the comparison reaches behind the fresh one.
# Fixed rather than running to the regime boundary, so a delta means the same
# thing on every run. Left open, the baseline lengthens by a day per day and a
# configuration that has not moved reports a shrinking delta as its denominator
# grows; two runs a fortnight apart would then disagree about a slot nothing
# happened to. It is also a comparison against the camp rather than against the
# format: a card adopted mid-regime is diluted across the weeks before it
# existed, so a long baseline reports a settled configuration as still climbing.
# The regime boundary still bounds it, since a window may never cross one.
BASELINE_WINDOW_DAYS = 28

# How long an event's publication can still change. A league dump gains 5-0s
# through its own day, and the site publishes on US time while we run on
# Australian time, so the last few days are refetched rather than trusted.
UNSETTLED_DAYS = 3

# The colours of the split cards the history has played. The site publishes a
# split card with no colour and no type, where every other card carries both,
# so the splash line would read a Fire/Ice as colourless and count nothing. The
# front-face reading Scryfall gives; a split card outside this table is read as
# colourless, which is the one way the line can go stale silently.
SPLIT_COLOURS = {
    "Fire/Ice": "UR",
    "Dead/Gone": "R",
    "Repudiate/Replicate": "GU",
    "Boom/Bust": "R",
    "Incubation/Incongruity": "GU",
    "Claim/Fame": "BR",
    "Spring/Mind": "GU",
    "Cease/Desist": "WBG",
    "Wear/Tear": "RW",
    "Rough/Tumble": "R",
    "Crime/Punishment": "BR",
}

# A mainboard over this many cards is a list published with its sideboard in
# the main (75 and 0), and no rule reads it (Alejandro, 2026-09-13). A 60 with
# an unpublished sideboard is still a list.
MAINBOARD_MAX = 62

# Membership rule: every signature card, in the mainboard.
ARCHETYPE = "goryos"
# Ephemerate is in the rule because the other three are as at home in a Grixis
# reanimator deck as in this one. It is the blink half of the Esper shell, and
# the line the two versions of the deck fall either side of.
SIGNATURE_CARDS = (
    "Goryo's Vengeance",
    "Atraxa, Grand Unifier",
    "Psychic Frog",
    "Ephemerate",
)
# The engines that move a list out of Goryo's, by name in `ENGINES`. Goryo's is
# Goryo's Vengeance and the legendary Atraxa it pairs with; Persist reanimator
# runs a different package and a list holding both is the Persist deck with
# Goryo's as a second angle (Alejandro, 2026-09-13). The Shifting Woodland
# Omniscience combo wears the Goryo's core the same way. A Goryo's list carrying
# Blink's creatures is not this: its engine is still the Goryo's package, so it
# stays.
EXCLUDED_ENGINES = ("persist", "omniscience")

# The engine registry: every deck a membership rule has had to turn away, named
# once, with the mainboard cards that mark it. A list answering to a deck's core
# and carrying an engine the deck names as another deck's carries more than one
# engine and belongs to nothing (Alejandro, 2026-09-13: an engine moves a list,
# variation inside an intact engine stays, and hybrid brews are out for now).
#
# Which engines count as another deck's is the rule's to say, deck by deck, and
# not the registry's: a marker names a deck only beside a shell it does not
# belong to. Eldrazi Temple names the Boros Eldrazi brew beside the energy four
# and sits in every Trudge and Tron list; Ragavan sits in every Boros Energy
# list and names a tempo deck beside the control shell. Measured over the store
# on 2026-09-13: read globally, the markers below would empty Trudge, Tron and
# Broodscale.
ENGINES = {
    "persist": ("Persist",),
    "omniscience": ("Omniscience", "Shifting Woodland"),
    "energy": ("Guide of Souls", "Ocelot Pride"),
    "overlords": ("Estrid's Invocation",),
    "stoneblade": ("Stoneforge Mystic",),
    "taxes": ("Tidehollow Sculler",),
    "kappa": ("Kappa Cannoneer",),
    "livingend": ("Living End",),
    "cascade": ("Shardless Agent", "Crashing Footfalls"),
    "dredger": ("Dredger's Insight",),
    "song": ("Song of Creation",),
    "basim": ("Basim Ibn Ishaq",),
    "cam": ("Sewer-veillance Cam",),
    "phoenix": ("Arclight Phoenix",),
    "devoted": ("Devoted Druid",),
    "eldrazi": ("Eldrazi Temple",),
    "prowess": ("Cori-Steel Cutter",),
    "cauldron": ("Agatha's Soul Cauldron",),
    "boombust": ("Boom/Bust",),
    "necro": ("Necrodominance",),
    # The Dimir Oculus deck is named by Unearth and not by the card it is
    # called after (Alejandro, 2026-09-13): a one-of Oculus in the stock Frog
    # and Riddler shell is a threat slot, where every Oculus list proper
    # reanimates with Unearth.
    "oculus": ("Unearth",),
    "goryos": ("Goryo's Vengeance",),
    "shadow": ("Death's Shadow",),
    "omnath": ("Wrenn and Six",),
    "creativity": ("Indomitable Creativity",),
    "saheeli": ("Saheeli Rai",),
    # Price of Freedom beside it: a control shell on a playset of it is the
    # land-destruction brew and not control (Alejandro, 2026-09-13).
    "ponza": ("Cleansing Wildfire", "Price of Freedom"),
    # Phelia beside the control shell is the Blink midrange deck; on its own
    # she names nothing, a Goryo's list carrying Blink's creatures staying.
    "blink": ("Phelia, Exuberant Shepherd",),
    "ragavan": ("Ragavan, Nimble Pilferer",),
    "zoo": ("Territorial Kavu",),
    "kethis": ("Kethis, the Hidden Hand",),
    "namor": ("Namor the Sub-Mariner",),
    # Ephemerate beside the control shell is a blink deck, not control filling
    # a slot (Alejandro, 2026-09-13). Phelia stays the Blink midrange deck's
    # marker: the two name different decks on the same shell.
    "ephemerate": ("Ephemerate",),
}

# Variant rule: the camps a member belongs to, by mainboard copies of the card
# the archetype forks on. No list in the history sideboards it, so the mainboard
# count is the whole commitment. A count between the camps is a hybrid
# experiment: it belongs to neither consensus.
DIVERGENCE_CARD = "Fallaji Archaeologist"
CAMPS = {"fallaji": (3, 4), "non-fallaji": (0,)}
HYBRID_CAMP = "hybrid"

# What the weekly report calls a camp, where the pilot's name for it is not the
# rule's. The rule is drawn on Fallaji Archaeologist and names both halves after
# it, which says what the rule tests and not what the deck is: the half on none
# of them is the Riddler build to everybody who plays it. Display only. The camp
# is keyed by its rule name in the store and in every reading, so renaming this
# moves a label and invalidates nothing. The tracked decks' versions are keyed
# lowercase and printed capitalised.
VERSION_NAMES = {
    "non-fallaji": "Riddler",
    "fallaji": "Fallaji",
    "hybrid": "Hybrid",
    "esper": "Esper",
    "orzhov": "Orzhov",
    "frog": "Frog",
    "traditional": "Traditional",
    "lab": "Lab",
    "gruul": "Gruul",
    "golgari": "Golgari",
    "mono-green": "Mono-green",
    "colourless": "Colourless",
    "blue": "Blue",
    "green": "Green",
}


def version_name(camp: str) -> str:
    """The name the report prints for a camp."""
    return VERSION_NAMES.get(camp, camp)

# Tracked decks: archetypes the engine classifies by signature and colour and
# reports on weekly. Goryo's above has its own rule and is tested first, these in
# turn, so a list takes the first name that claims it and is never two decks.
TRACKED_DECKS = {
    "blink": {
        # The three together are the deck. Phelia alone is not enough: a white
        # energy build and a Boros build both play her, and the Ephemerate pool
        # on its own is half Goryo's.
        #
        # Flickerwisp was the fourth until 2026-09-14. It is a slot and not the
        # deck (Alejandro, 2026-09-14): a list on the three that runs Psychic
        # Frog in the Flickerwisp seat is the same deck innovating, and RC
        # Baltimore is where that build arrived in numbers, six lists whose
        # pilots all typed `Esper Blink` and five of them on Frog as a four-of.
        # The 2026-08-07 ruling set the four-card core against nine MTGO lists
        # that had cut one; one event now holds most of that again.
        "signature": (
            "Phelia, Exuberant Shepherd",
            "Overlord of the Balemurk",
            "Witch Enchanter",
        ),
        # The deck is Esper or Orzhov and nothing else. A Mardu build shares all
        # three signature cards and is a different deck, and the line between
        # them is the splash line (Alejandro, 2026-09-13): the off-colour
        # spells the mainboard casts, never its sources. Six lists on one
        # Sacred Foundry or Temple Garden with nothing red or green cast are
        # Blink; five red cards, or a playset of one, are Mardu.
        "colours": frozenset("WUB"),
        # Variant rule: the blue half against the two-colour half, read on
        # mainboard Watery Grave or any blue spell the list casts (Alejandro,
        # 2026-09-13). The Grave alone partitioned the archetype until
        # SuperCow12653 registered 2 Teferi off Hallowed Fountain and
        # Meticulous Archive twice; the card and the colour together name the
        # version whichever way a pilot builds the mana. Presence and not a
        # count: a variant here is which colours the deck is, which one copy
        # settles.
        "variants": (("esper", ("Watery Grave",)),),
        "colour_variants": (("esper", "U"),),
        "variant_default": "orzhov",
        # The engines that name another deck built on the four creatures
        # (Alejandro, 2026-09-13): the Guide of Souls and Ocelot Pride energy
        # engine, the Estrid's Invocation Overlords deck, Stoneblade, and the
        # Tidehollow Sculler taxes deck. Aether Vial is not one: the Orzhov Vial
        # lists on Ephemerate are a version of this deck.
        "excluded_engines": ("energy", "overlords", "stoneblade", "taxes"),
    },
    "neoform": {
        # The four together are the deck, and Planar Genesis is the one that
        # says which deck. Rider, Neoform and Eldritch Evolution alone admit the
        # four-colour Glittering Wish build on Gemstone Mine, a different deck
        # that shares the engine; every Simic list in the history runs all four
        # at four copies, so the count is not in the rule.
        "signature": (
            "Neoform",
            "Allosaurus Rider",
            "Eldritch Evolution",
            "Planar Genesis",
        ),
        # No colour rule: nothing sharing the four is another colour of this
        # deck, so there is nothing for a source list to turn away.
        # No variant rule either. Nothing in the history forks the deck: the
        # only mid-adoption mainboard cards are which basics and fetches fill
        # the manabase. One population, so the camp is unset and every reading
        # pools it.
    },
    "oswald": {
        # Grinding Station on Emry, Sewer-veillance Cam and Mox Amber is the
        # deck, which no other deck runs together, with either Oswald
        # Fiddlebender or Loki, God of Mischief over it (Alejandro,
        # 2026-09-13). Oswald appears in this deck alone, but the mono-blue
        # build on Loki has no Fiddlebender, and forcing the card would leave
        # half the deck outside. The Kethis combo and the Song of Creation
        # deck run the trio and neither. No colour rule: a green source is a
        # splash, usually for Haywire Mite. The key is the report's directory
        # under `data/tracking/` and stays; the name moved.
        "signature": ("Grinding Station", "Emry, Lurker of the Loch", "Sewer-veillance Cam"),
        "supporting": (1, ("Oswald Fiddlebender", "Loki, God of Mischief")),
        # The Kappa Cannoneer and Pinnacle Emissary artifact deck bolted two
        # Oswald and a Station on for a fortnight and is a different deck
        # (Alejandro, 2026-09-13). Mainboard only: Station lists side Kappa.
        # The Kethis combo is a different deck too, whether or not it adds Loki
        # for Plaza of Heroes (Alejandro, 2026-09-13): the premise above, that
        # it runs neither Oswald nor Loki, is not what makes it another deck.
        "excluded_engines": ("kappa", "kethis"),
    },
    "zoo": {
        # Kavu and Scion together are the deck, and a Kavu-less list on Scion,
        # Leyline of the Guildpact and Psychic Frog is its Frog version
        # (Alejandro, 2026-09-13), exactly three lists since the bans. Five
        # colours, so no colour rule: the manabase is the part of this deck
        # that moves most.
        "signature": ("Scion of Draco",),
        "either": (("Territorial Kavu",), ("Leyline of the Guildpact", "Psychic Frog")),
        # Four other decks put the domain bodies in and are not this one
        # (Alejandro, 2026-09-13): Persist reanimator on Archon of Cruelty and
        # Faithless Looting, the five-colour Living End build on Bloodbraid
        # Marauder and Malevolent Rumble, the five-colour energy build on the
        # Guide of Souls and Ocelot Pride engine, and the Shardless Agent
        # cascade decks on the two leylines.
        "excluded_engines": ("persist", "livingend", "energy", "cascade"),
        # The Frog version is the bluer build; the traditional one is read.
        "variants": (("frog", ("Psychic Frog",)),),
        "variant_default": "traditional",
    },
    "broodscale": {
        # Basking Broodscale and the Blade are the combo and the deck. Mono-Green
        # Eldrazi shares the Eldrazi shell and neither card; Eldrazi Tron shares
        # Devourer of Destiny and Ugin's Labyrinth and neither card.
        # Eldrazi Temple names the shell: the Golgari Yawgmoth and Cauldron
        # decks carry the combo without it and are different decks (Alejandro,
        # 2026-09-13). Every other list in the history holds it.
        "signature": ("Basking Broodscale", "Blade of the Bloodchief", "Eldrazi Temple"),
        # A hybrid brew on the intact shell is out too, for now: Dredger's
        # Insight names the Yawgmoth-style Cauldron package, and nothing else
        # in the history holds it. A Mystic Forge inside the intact shell is an
        # innovation and not a brew (Alejandro, 2026-09-13).
        "excluded_engines": ("dredger",),
        # Four versions, read in this order. The red spells name the Gruul
        # build: Stomping Ground would too, but Grove of the Burnwillows sits
        # in nine of ten mono-green lists, so a source is not the line.
        # Lightning Bolt is the third marker (Alejandro, 2026-09-13), the two
        # Pro Tour lists on Bolt off Grove and Karplusan Forest being the Gruul
        # deck. Ugin's Labyrinth names the Lab build, every Devourer of Destiny
        # list running it and nine in ten of its lists running Devourer. A list
        # holding both is a Gruul list on a couple of Labyrinths, 27 of 1000
        # since the bans, and reads as Gruul. Golgari is read last, so a black
        # list on a red spell is still Gruul and the versions stay a partition
        # (Alejandro, 2026-09-13): the black cards are the marker and never
        # Dismember, which Phyrexian mana casts in 419 members holding no black
        # source, the reason Prowess draws no colour rule off Mutagenic Growth.
        # A list on none of the markers is mono-green whatever it splashes.
        "variants": (
            ("gruul", ("Unholy Heat", "Writhing Chrysalis", "Lightning Bolt")),
            ("lab", ("Ugin's Labyrinth",)),
            ("golgari", ("Sephiroth, Fabled SOLDIER", "Fatal Push", "Thoughtseize")),
        ),
        "variant_default": "mono-green",
    },
    "devoted": {
        # Devoted Druid with either Tyvar (Alejandro, 2026-09-13): both are
        # unique to Druid combo, as are Springheart Nantuko and Quirion Ranger,
        # and a list swapping one Tyvar for the other is a version of the same
        # deck. Druid without a Tyvar is the Vizier of Remedies elves build,
        # and the Druid-less Nantuko deck is a different deck.
        "signature": ("Devoted Druid",),
        "supporting": (1, ("Tyvar, Jubilant Brawler", "Tyvar, the Pummeler")),
    },
    "affinity": {
        # Kappa Cannoneer and Pinnacle Emissary are the shell, and Engineered
        # Explosives, Weapons Manufacturing and Krang support it: a list tests
        # without any one of them and stays within the shell, Explosives
        # included (Alejandro, 2026-09-13). One of the three keeps the Frogmite
        # and Ravenous Robots aggro lists, which run none, outside. Kappa alone
        # admits the Hammer build.
        "signature": ("Kappa Cannoneer", "Pinnacle Emissary"),
        "supporting": (
            1, ("Engineered Explosives", "Weapons Manufacturing", "Krang, Master Mind")
        ),
        # The Song of Creation deck, the Basim Ibn Ishaq aggro decks and the
        # Sewer-veillance Cam decks are not Affinity (Alejandro, 2026-09-13).
        "excluded_engines": ("song", "basim", "cam"),
        # Tamiyo beside Mox Amber is the Tamiyo artifact deck unless
        # Manufacturing sits beside them, when Manufacturing outweighs it
        # (Alejandro, 2026-09-13): the name the fall-out reports, the pair,
        # and the card that outweighs it.
        "outweighed": ("tamiyo", ("Tamiyo, Inquisitive Student", "Mox Amber"), "Weapons Manufacturing"),
    },
    "prowess": {
        # The deck is Izzet: Steam Vents and Lava Dart under the prowess
        # staples, and a list that cuts Channeler, or Swiftspear, or sides its
        # Cutters is the same deck in a different build (Alejandro,
        # 2026-09-13). The red and Boros prowess lists on Lava Spike and Skewer
        # share the creatures and never the land; Cori-Steel Cutter alone
        # admits the artifact decks on Emry and Tamiyo.
        "signature": ("Steam Vents", "Lava Dart"),
        # Four of the six staples: Bosseidon's Talent decks on three stay out.
        "supporting": (4, (
            "Cori-Steel Cutter", "Monastery Swiftspear", "Dragon's Rage Channeler",
            "Slickshot Show-Off", "Mutagenic Growth", "Stormchaser's Talent",
        )),
        # Izzet Phoenix answers the rule and is another deck, and the prowess
        # core with Phoenix grafted on is a hybrid brew (Alejandro, 2026-09-13).
        "excluded_engines": ("phoenix",),
        # One Vents is a Gruul list fetching for its sideboard: every Izzet list
        # runs two or more.
        "floor": {"Steam Vents": 2},
    },
    "trudge": {
        # The Eldrazi ramp shell, which the mono-green Nantuko decks run none of
        # while running Trudge and Fanatic as mana dorks (Alejandro,
        # 2026-09-13). Named by the shell itself rather than by Ugin's
        # Labyrinth alone (Alejandro, 2026-09-14): the Labyrinth stood in for
        # the shell while every list in the history held it, and TheJV's RC
        # Baltimore list is the shell whole on a manabase without the land,
        # which is the Nantuko clause catching the case it was written to
        # admit. Any one of these four is the shell; the Nantuko decks hold
        # none of them.
        "signature": ("Slumbering Trudge", "Fanatic of Rhonas"),
        "either": (
            ("Ugin's Labyrinth",),
            ("Eldrazi Temple",),
            ("Kozilek's Command",),
            ("Fight Rigging",),
        ),
    },
    "tron": {
        # The three lands are Tron, and Karn is supporting (Alejandro,
        # 2026-09-13): colourless Tron on Karn, Ugin's Labyrinth and the
        # Eldrazi is the tracked version, and blue Tron on Stock Up and green
        # Tron on the Chromatic eggs are versions of the same deck.
        "signature": ("Urza's Tower", "Urza's Mine", "Urza's Power Plant"),
        # A combo brew in the flex slots, Devoted Druid with Luxior, is a
        # hybrid brew and out for now (Alejandro, 2026-09-13).
        "excluded_engines": ("devoted",),
        # Versions by marker and never by the splash line (Alejandro,
        # 2026-09-13): blue Tron is the deck on Stock Up or Force of Negation,
        # green Tron the deck on the Chromatic eggs or Sylvan Scrying, and
        # every other list is colourless whatever it casts. The splash line
        # read the colourless Eldrazi shell's own flex slots as versions, a
        # playset of Dress Down or Portent of Calamity as blue and 4 Malevolent
        # Rumble or Ancient Stirrings as green, so narca's Dress Down build was
        # arriving in the blue version's storyline as a version change when it
        # is a build change.
        "variants": (
            ("blue", ("Stock Up", "Force of Negation")),
            ("green", ("Chromatic Sphere", "Chromatic Star", "Sylvan Scrying")),
        ),
        "variant_default": "colourless",
        # And the version boundary reads nothing here (Alejandro, 2026-09-13).
        # Blue Tron is a version of the colourless deck that plays more Emrakul,
        # not a deck the card names: Emrakul sits in 46 of the 50 blue lists and
        # 18 of the 669 colourless, which is a build the version leans on. With
        # the splash line and Portent of Calamity already ruled builds above,
        # every signal the boundary could raise here is one, so the deck is left
        # out rather than raised and dismissed once a week.
        "version_boundary": False,
    },
    "energy": {
        # Guide of Souls and Ocelot Pride are the engine of every energy deck,
        # and Ajani and Goblin Bombardment are what the Boros build does with
        # it. The Azorius and Selesnya lists on the two creatures are blink and
        # Birthing Ritual decks and hold neither. Mardu and Jeskai energy share
        # all four and are different decks, told apart on the splash line
        # (Alejandro, 2026-09-13): Jeskai on a playset of Quantum Riddler,
        # Mardu on five or more black cards, where a Godless Shrine held for
        # sideboard Thoughtseize is a splash.
        "signature": ("Guide of Souls", "Ocelot Pride", "Ajani, Nacatl Pariah",
                      "Goblin Bombardment"),
        "colours": frozenset("RW"),
        # Hybrid brews on the energy four, out for now (Alejandro, 2026-09-13):
        # the Boros Eldrazi build on the Temple, the Cutter prowess build and
        # the Leonardo Cauldron combo. Nothing else in the history holds them.
        "excluded_engines": ("eldrazi", "prowess", "cauldron"),
    },
    "ponza": {
        # Boros land destruction is Cleansing Wildfire with the suite around
        # it, and Erode supports it though nearly every list holds it
        # (Alejandro, 2026-09-13): the plan is the suite and not the card. The
        # Pinnacle Monk red decks on Wildfire and Price run nothing else of
        # it. The Jeskai and Azorius control lists that splash Erode are
        # control decks, told apart on the splash line, and a Ponza list on a
        # playset of Teferi is the Jeskai deck.
        "signature": ("Cleansing Wildfire",),
        "supporting": (4, (
            "Erode", "Field of Ruin", "Demolition Field", "Price of Freedom",
            "Wrath of the Skies", "Solitude",
        )),
        "colours": frozenset("RW"),
        # The Boom/Bust and Magmatic Hellkite build in place of Field of Ruin
        # and Demolition Field is a hybrid brew, out for now (Alejandro,
        # 2026-09-13). Flagstones is not the marker: clean lists run it.
        "excluded_engines": ("boombust",),
    },
    "dimir": {
        # Psychic Frog and Quantum Riddler together are the midrange deck. Frog
        # alone admits the Dimir Oculus lists on Unearth, which never run
        # Riddler; Goryo's, Blink and Domain Zoo share the pair and are tested
        # first. The Esper and Grixis Frog decks share the pair too and are
        # told apart on the splash line (Alejandro, 2026-09-13): Meltdown in
        # the sideboard off one Steam Vents is still Dimir, a playset of Flame
        # of Anor is Grixis Frog and five white cards are Esper Frog.
        "signature": ("Psychic Frog", "Quantum Riddler"),
        "colours": frozenset("UB"),
        # The other Dimir decks on the pair (Alejandro, 2026-09-13): Necro on
        # Soul Spike, Persist reanimator, Oculus on Unearth (which does run
        # Riddler, in a third of its lists), Goryo's without Ephemerate,
        # Death's Shadow, and the mono-blue Namor, Archmage's Charm and
        # Disrupting Shoal tempo shell on a black splash, which is twenty lists
        # of its own (Alejandro, 2026-09-13). The Moonshadow aggro build is
        # left in: no one card names it without moving clean lists.
        "excluded_engines": ("necro", "persist", "oculus", "goryos", "shadow", "namor"),
    },
    "jeskai": {
        # The blue and white control shell as one deck (Alejandro,
        # 2026-09-13): Teferi and a sweeper over a draw engine, whichever of
        # the ten it is. Control adapts its interaction to the meta, so
        # Galvanic Discharge is a build reading and not a membership rule:
        # Jeskai and Azorius are the same deck tracked together. The splash
        # line on black and green. The key is the report's directory under
        # `data/tracking/` and stays; the name moved.
        #
        # The sweeper is a slot and not a card (Alejandro, 2026-09-13). Wrath
        # of the Skies in the signature hid 23 control lists from every report:
        # a list on Supreme Verdict, Terminus or Temporary Lockdown fails the
        # core, so it never reached the fall-out table either. Dropping the
        # sweeper outright is the rule that does not work, admitting nine lists
        # that are not control.
        "signature": ("Teferi, Time Raveler",),
        "either": (
            ("Wrath of the Skies",), ("Supreme Verdict",),
            ("Terminus",), ("Temporary Lockdown",),
        ),
        # The draw engines, ten since Wan Shi Tong, Stock Up and Brainsurge
        # were added (Alejandro, 2026-09-13), each of the three already more
        # common among members (15%, 14%, 17%) than Flow State and Thundertrap
        # Trainer (10%, 3%), which the tier already named.
        "supporting": (1, (
            "Consult the Star Charts", "Isochron Scepter", "Narset, Parter of Veils",
            "Day's Undoing", "Orim's Chant", "Thundertrap Trainer", "Flow State",
            "Wan Shi Tong, Librarian", "Stock Up", "Brainsurge",
        )),
        "colours": frozenset("UWR"),
        # Removal is a slot control fills to the meta, so a playset of it off
        # colour does not name another deck while the rest of the mainboard
        # stays under the five-card line (Alejandro, 2026-09-13). Fatal Push is
        # the one such card the history holds; the tier grows as the meta names
        # another.
        "playset_exempt": ("Fatal Push",),
        # Decks built on the two cards that are not this one (Alejandro,
        # 2026-09-13): the four-colour Omnath, Creativity and Saheeli hybrids,
        # out for now, and the Ponza, Blink midrange, Ragavan, Zoo and energy
        # decks that carry the two cards. Ephemerate is the sixth such deck: a
        # blink value package inside an intact control suite is not control
        # (Alejandro, 2026-09-13).
        "excluded_engines": (
            "omnath", "creativity", "saheeli", "ponza", "blink", "ragavan", "zoo", "energy",
            "ephemerate",
        ),
    },
    "storm": {
        # Ral, Ruby Medallion and Past in Flames together. Ruby alone admits
        # the Belcher lists on Pinnacle Monk, which never run Ral or Past in
        # Flames; Ral alone admits an Izzet storm on Stormcatch Mentor with no
        # Medallion. No colour rule: the sideboard colours are the Wish
        # targets, and every list is the same red deck under them.
        "signature": ("Ral, Monsoon Mage", "Ruby Medallion", "Past in Flames"),
    },
    "livingend": {
        # Living End with the two cascade spells. The Sultai build on
        # Formidable Speaker and Overlord of the Balemurk shares Living End
        # and Shardless Agent and never runs Violent Outburst, and it is a
        # different deck. No colour rule: Temple Garden sits in 187 of the 326
        # lists beside no white spell, a fetchable land of the Temur shell.
        "signature": ("Living End", "Shardless Agent", "Violent Outburst"),
    },
}


def versions(archetype: str) -> tuple[str, ...]:
    """Every camp of an archetype in rule order, or nothing for one population.

    A version named by both a card and a colour, as Blink's Esper half is, is
    one version and is listed once.
    """
    if archetype == ARCHETYPE:
        return (*CAMPS, HYBRID_CAMP)
    rule = TRACKED_DECKS[archetype]
    if "variants" not in rule and "colour_variants" not in rule:
        return ()
    named = (*rule.get("variants", ()), *rule.get("colour_variants", ()))
    return (*dict.fromkeys(name for name, _ in named), rule["variant_default"])


# What makes a card or a colour a version's marker rather than a card the deck
# happens to play: the share of that version's lists holding it. The same bar
# read the other way is what disqualifies it, the default version having to
# hold it in under one list in ten, and the two are one number because they are
# one question asked of both populations. The bar has to sit below three
# quarters and above a twentieth on today's store: 166 of 221 mono-green
# Broodscale lists cast black off Dismember and every one of the 261 traditional
# Zoo lists casts blue and black, neither of which tells a version from a
# version, and 28 of the 669 colourless Tron lists cast blue, which is the
# reading this is for.
VERSION_MARKER_SHARE = 0.9

# The weekly report's subjects: which lists a report is computed over, what it
# calls itself, and which slots it watches. Kept apart from the membership rules
# above because the two answer different questions. A rule says what a list is,
# and Goryo's has one already, drawn on copy counts where a tracked deck's is
# drawn on presence, so it stays above `TRACKED_DECKS` and is tested first. A
# report says which of those lists it reads, and that is a separate decision
# made once per report.
#
# Two populations, and the split is fixed rather than a field. Presence is the
# whole archetype, every version pooled: a metagame share is a share of the
# whole deck, and read on one version of three it is a third of the answer.
# `camp` is the version everything else is read on, conversion and goldfishing
# and the storyline and the numbers table, and `None` where the deck has one
# population. Pooled, Goryo's looks like it drifted a copy of Quantum Riddler
# over the regime; inside the non-fallaji camp the card is flat at four, and
# the drift is the fallaji camp arriving rather than anybody changing their
# mind. The versions the report does not read are printed as bare counts and on
# the presence figure's third panel, and are every other camp the rule names.
REPORTS = {
    "blink": {
        "name": "Esper Blink",
        "archetype": "blink",
        "camp": "esper",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Phelia, Exuberant Shepherd, Overlord of the Balemurk and Witch "
            "Enchanter, casts under five spells outside white, blue and black and no "
            "playset of one, and carries none of the energy, Overlords, Stoneblade or taxes "
            "engines. The esper version mainboards Watery Grave or casts a blue spell; the "
            "orzhov version does neither."
        ),
    },
    "goryos": {
        "name": "Goryo's",
        "archetype": ARCHETYPE,
        "camp": "non-fallaji",
        # The slots the pilot argues about, read at the finer bar below and by
        # copy count rather than by presence. Both halves of the land swap are
        # here because a slot lost is the other half of a slot won, and a
        # reading that names only the winner leaves the reader to guess what it
        # came out of.
        "watch": ("Hedge Maze", "Breeding Pool", "Prismatic Ending", "Faithful Mending"),
        "manabase": True,
        "membership": (
            "mainboard holds all four of Goryo's Vengeance, Atraxa, Grand Unifier, Psychic Frog "
            "and Ephemerate, and neither the Persist nor the Omniscience engine. Green sources "
            "for casting Atraxa do not change membership, and there is no colour rule. The "
            "non-fallaji version is the one read."
        ),
    },
    "neoform": {
        "name": "Simic Neoform",
        "archetype": "neoform",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds all four of Neoform, Allosaurus Rider, Eldritch Evolution and Planar "
            "Genesis. No colour rule and no versions: every reading is the whole archetype's."
        ),
    },
    "oswald": {
        "name": "Grinding Station",
        "archetype": "oswald",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Grinding Station, Emry, Lurker of the Loch and Sewer-veillance Cam "
            "with Oswald Fiddlebender or Loki, God of Mischief, and neither Kappa Cannoneer nor "
            "Kethis, the Hidden Hand. No colour rule: a green splash is the same deck. No "
            "versions."
        ),
    },
    "zoo": {
        "name": "Domain Zoo",
        "archetype": "zoo",
        "camp": "traditional",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Scion of Draco with Territorial Kavu, or with Leyline of the "
            "Guildpact and Psychic Frog, and none of the Persist, Living End, energy or cascade "
            "engines. No colour rule. The frog version mainboards Psychic Frog; the traditional "
            "version does not and is the one read."
        ),
    },
    "broodscale": {
        "name": "Broodscale",
        "archetype": "broodscale",
        "camp": "lab",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Basking Broodscale, Blade of the Bloodchief and Eldrazi Temple, and "
            "neither the Dredger's Insight nor the Mystic Forge engine. No colour rule. The gruul "
            "version mainboards Unholy Heat, Writhing Chrysalis or Lightning Bolt, the lab "
            "version mainboards Ugin's Labyrinth and is the one read, the golgari version "
            "mainboards Sephiroth, Fatal Push or Thoughtseize, and the mono-green version "
            "holds none of them whatever it splashes."
        ),
    },
    "devoted": {
        "name": "Devoted Combo",
        "archetype": "devoted",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Devoted Druid with Tyvar, Jubilant Brawler or Tyvar, the Pummeler. "
            "No colour rule and no versions."
        ),
    },
    "affinity": {
        "name": "Affinity",
        "archetype": "affinity",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Kappa Cannoneer and Pinnacle Emissary with any one of Engineered "
            "Explosives, Weapons Manufacturing or Krang, Master Mind, none "
            "of Song of Creation, Basim Ibn Ishaq or Sewer-veillance Cam, and not Tamiyo, "
            "Inquisitive Student beside Mox Amber unless Weapons Manufacturing sits beside them. "
            "No colour rule and no versions."
        ),
    },
    "prowess": {
        "name": "Izzet Prowess",
        "archetype": "prowess",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds at least two Steam Vents and Lava Dart with four of Cori-Steel "
            "Cutter, Monastery Swiftspear, Dragon's Rage Channeler, Slickshot Show-Off, Mutagenic "
            "Growth and Stormchaser's Talent, and no Arclight Phoenix. No colour rule and no "
            "versions."
        ),
    },
    "trudge": {
        "name": "Trudge",
        "archetype": "trudge",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Slumbering Trudge and Fanatic of Rhonas with any one of Ugin's "
            "Labyrinth, Eldrazi Temple, Kozilek's Command or Fight Rigging. No colour rule and no "
            "versions."
        ),
    },
    "tron": {
        "name": "Tron",
        "archetype": "tron",
        "camp": "colourless",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Urza's Tower, Urza's Mine and Urza's Power Plant, and no Devoted "
            "Druid. The blue version mainboards Stock Up or Force of Negation, the green version "
            "mainboards Chromatic Sphere, Chromatic Star or Sylvan Scrying, and the colourless "
            "version holds neither whatever it casts and is the one read."
        ),
    },
    "energy": {
        "name": "Boros Energy",
        "archetype": "energy",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Guide of Souls, Ocelot Pride, Ajani, Nacatl Pariah and Goblin "
            "Bombardment, casts under five spells outside red and white and no playset of one, "
            "and none of Eldrazi Temple, Cori-Steel Cutter or Agatha's Soul Cauldron. No "
            "versions."
        ),
    },
    "ponza": {
        "name": "Boros Ponza",
        "archetype": "ponza",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Cleansing Wildfire with four of Erode, Field of Ruin, Demolition "
            "Field, Price of Freedom, Wrath of the Skies and Solitude, casts under five spells "
            "outside red and white and no playset of one, and no Boom/Bust. No versions."
        ),
    },
    "dimir": {
        "name": "Dimir Midrange",
        "archetype": "dimir",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Psychic Frog and Quantum Riddler, casts under five spells outside "
            "blue and black and no playset of one, and none of the Necrodominance, Persist, "
            "Unearth, Goryo's, Death's Shadow or Namor engines. No versions."
        ),
    },
    "jeskai": {
        "name": "UWr Control",
        "archetype": "jeskai",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Teferi, Time Raveler with one of Wrath of the Skies, Supreme "
            "Verdict, Terminus or Temporary Lockdown, and any of Consult the Star Charts, "
            "Isochron Scepter, Narset, Parter of Veils, Day's Undoing, Orim's Chant, Thundertrap "
            "Trainer, Flow State, Wan Shi Tong, Librarian, Stock Up or Brainsurge, casts under "
            "five spells outside blue, white and red and no playset of one other than Fatal Push, "
            "and none of Wrenn and Six, Indomitable Creativity, Saheeli Rai, Cleansing Wildfire, "
            "Phelia, Exuberant Shepherd, Ragavan, Nimble Pilferer, Territorial Kavu, Guide of "
            "Souls, Ocelot Pride or Ephemerate. No versions."
        ),
    },
    "storm": {
        "name": "Storm",
        "archetype": "storm",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Ral, Monsoon Mage, Ruby Medallion and Past in Flames. No colour rule "
            "and no versions."
        ),
    },
    "livingend": {
        "name": "Temur Living End",
        "archetype": "livingend",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Living End, Shardless Agent and Violent Outburst. No colour rule and "
            "no versions."
        ),
    },
}

# How far a watched slot's share has to move to earn a row, against the twenty
# points an unwatched one answers to. The finer bar is only ever applied to the
# named slots, and that is the whole of why it holds: over this deck's
# post-regime history an unfiltered scan at ten points produces 78 rows across
# eight fortnights against 41 at twenty, and 38% of them reverse in the next
# fortnight either way. Twice the volume for no more signal, which is what the
# twenty-point bar exists to refuse. A named slot is a question the pilot
# asked, so a ten-point move on it is worth printing knowing it may reverse,
# and the slot list is short enough that the reader can hold what was asked.
TRACK_WATCH_DELTA = 0.10

# Tracking rule: what counts as a change worth a timeline row, read over a
# fortnight rather than a week. A week of this deck runs from nine lists to
# sixty-four, a seven-fold swing, so a threshold set as a share is measuring the
# sample size and not the deckbuilding: across every bar from five points to
# twenty-five, a weekly reading reverses in the next bin about two times in
# five, and no threshold escapes it. Over a fortnight the same bars reverse
# between fifteen and twenty-two percent of the time and fall as the bar rises,
# which is what a threshold is supposed to do. The plots stay weekly; only the
# detection is binned.
TRACK_BIN_DAYS = 14

# And the bar itself, in both units. The share is what makes a move large; the
# list count is what makes it evidence. The count does the real work, being a
# fifty-six percent swing in the thinnest fortnight and eight percent in the
# fattest, which is the right behaviour when the denominator moves that far: it
# holds the evidence constant rather than the effect size.
TRACK_ADOPTION_DELTA = 0.20
TRACK_MIN_LISTS = 5

# How far a staple's mean copy count has to move to be the camp changing its
# mind rather than the week's lists differing. Read on the mean and never the
# mode: the modal count of the cards that actually move oscillates every other
# week and every oscillation reverses, because the mode is held by a plurality
# one pilot can flip.
TRACK_COPY_DELTA = 0.4

# What makes a card a staple, the share of lists holding it on both sides of a
# comparison, and so a card whose copies are read. The reading is for the slots
# the deck argues about the number of rather than the presence of, and a card
# under the bar is one the adoption reading is already answering for: its mean
# moves when different pilots arrive, not when the same pilots change a count.
# Found and not named, so a deck's staples are whatever it is playing at four
# this month. Seven in ten is where the scan stops being sensitive to the bar:
# on the three tracked decks it returns the same rows at eight, and five adds
# one marginal row.
TRACK_STAPLE_SHARE = 0.7

# Returning-card gates, per zone. A sideboard churns about seven times harder
# than a mainboard, so one gate cannot serve both: two thirds of the sideboard
# names this deck has ever registered appear in two weeks or fewer, and they
# carry four percent of the volume. Both sit on RETURN_ABSENCE_DAYS above, which
# a fortnight is too short for: a staple running at three to six lists a week
# misses two thin weeks on chance alone and reads as a return.
TRACK_RETURN_MAIN_LISTS = 2
TRACK_RETURN_SIDE_LISTS = 3

# And how many lists the absence itself has to be read over. A return claims the
# deck was not playing the card, and the claim needs a window big enough to have
# shown it: a deck's opening fortnights are thin because the deck was thin, not
# because the cards were absent. Read against a two-list window, Devoted Combo's
# fortnight to 2026-06-14 reported 16 cards as appearing for the first time,
# Craterhoof Behemoth among them, a card the deck has never been without; Simic
# Neoform reported Forest and Island, Oswald reported Hallowed Fountain and
# Trudge reported Primeval Titan. Set in the gap the history leaves between the
# two kinds of row: every window at or under 22 lists named the deck's own
# staples, and every window at or above 29 read as a change somebody made.
TRACK_RETURN_ABSENCE_LISTS = 25


# The floor a fortnight has to clear before a card-level move is read across it,
# on the smaller of the two populations, which is all the evidence there
# actually is. A fortnight of fewer than ten lists is too thin to read a row off
# (Alejandro, 2026-09-13): the storyline reads each fortnight against the one
# before it whatever either holds, so a bin of 8 lists prints the same kind of
# claim as a bin of 130 and only the counts beside the row tell them apart. Of
# the 597 comparison rows frozen before the floor, 66 read across such a bin and
# 55 of those fail a two-sided Fisher test at p<0.05. Ten and not
# `TRACK_MIN_LISTS`: those rows cluster at 8 and 9 lists, so a floor of five
# leaves the mass of them standing. The return reading answers to
# `TRACK_RETURN_ABSENCE_LISTS` above instead, its claim resting on the absence
# behind it rather than on the move across the two.
TRACK_ROW_MIN_LISTS = 10

# A return also has to be bigger than the card has ever been, which is what
# separates a card the field has turned to from a card that was always a
# one-off and is a one-off again. Without it the gates admit both and the
# timeline cannot tell the reader which it is looking at.
TRACK_RETURN_BEATS_PEAK = True

# Spike rule: how far this week's volume has to clear the level the deck was
# just at before the summary says so. A deck at several times its own baseline
# is being copied, and every performance figure taken over the spike measures
# adoption density rather than the deck. The report has to say that in the week
# it happens, not in the retrospective.
TRACK_SPIKE_MULTIPLE = 2.0

# And the two levels it is read against, both of which it has to clear.
#
# The first is the median of the weeks immediately behind it. Against the
# post-regime history alone a deck that has moved to a new level never stops
# spiking, because that median stays held down by the months before it got
# there: Esper Blink published 27, 33, 36 and 43 finishes on four consecutive
# weeks against a post-regime median of 10, and the banner fired on all four.
# Four weeks at a level is the level. Four weeks because that is
# BASELINE_WINDOW_DAYS, already this project's answer to how far back a
# comparison reaches before it stops describing the deck as it stands.
#
# The second is that same post-regime median, because the trailing one alone
# measures the calendar in a thin stretch: Blink's four weeks to 3 August ran 2,
# 4, 8 and 6 lists, where one challenge weekend doubles the median and a week of
# 10 reads as a spike. Ten lists is that deck's ordinary week. A spike has to be
# a departure from where the deck has just been and from where it has been all
# regime, which is the same shape as every other floor here: the effect size
# says the move is large and the second reading says it is not the sample.
TRACK_SPIKE_WEEKS = BASELINE_WINDOW_DAYS // 7

# The dated events a plot marks and the timeline names, one per line as
# `date,label`. Committed and hand-maintained: what counts as a major event is
# the pilot's call, and no feed serves it.
EVENTS_PATH = REPO_ROOT / "data" / "events.csv"

# The major paper events, by their melee tournament id, in the order they were
# played. The id is the one in the event's page, https://melee.gg/Tournament/View/<id>,
# and `melee.tournament` builds every request from it. One-off events rather than a feed, so they are named here rather than
# discovered: an event enters the analysis because the pilot says it matters,
# the same way `events.csv` works. The date is the local day the event started,
# which is the day `events.csv` marks it on and the day its week is taken from;
# melee publishes a UTC start, and Brisbane's is the evening before.
#
# `format` names the constructed format, and only at an event that played more
# than one. A Pro Tour is six rounds of draft and ten of Modern under a single
# ranking, so it is read at the end of its last Modern round and its record is
# the Modern rounds alone. See `melee.tournament`.
#
# `region` names the room the event drew its field from, and is what decides
# whether a comparison between two events is cross-population. Paper against
# paper used to be taken as one room on the medium alone, which read an
# Australian field against an American one as the deck changing its mind. A Pro
# Tour is its own room and matches nothing: its field is invited worldwide, so
# it is no more the American metagame than the Australian one.
MAJOR_EVENTS = (
    {
        "id": 434455, "label": "Pro Tour Amsterdam", "date": "2026-07-17",
        "format": "Modern", "region": "international",
    },
    {"id": 441441, "label": "Spotlight Brisbane", "date": "2026-08-29", "region": "australia"},
    {"id": 405590, "label": "Spotlight Dallas", "date": "2026-09-05", "region": "usa"},
    # Two Regional Championships on one weekend, in two rooms. Neither is read
    # against the other: `spotlight.chain` skips an event of the reading event's
    # own week, so both are read against Spotlight Dallas and the fortnight to
    # 2026-09-06. Baltimore is configured ahead of its cache, the organiser not
    # having published the finals standings when it was added on 2026-09-14; an
    # event with no cache is skipped by every reader until it is fetched.
    {"id": 405588, "label": "RC Baltimore", "date": "2026-09-12", "region": "usa"},
    {"id": 451148, "label": "RC China", "date": "2026-09-12", "region": "china"},
)

# One JSON per Spotlight, fetched once and kept. The melee equivalent of RAW_DIR
# and separate from it, because a paper event and an MTGO event are not the same
# population and nothing downstream may pool them by accident.
MELEE_DIR = REPO_ROOT / "data" / "raw-melee"

# What the weekly report is built from and cannot rebuild: the frozen weekly
# figures, the frozen timeline rows, and the summary written over them. Committed
# for the reason the ingest index is, one directory per tracked deck. The
# rendered page itself is derived and stays out, like every other report.
TRACKING_DIR = REPO_ROOT / "data" / "tracking"

# Returning-card rule: how long a card has to have been out of the pool for its
# reappearance to be a return rather than a gap.
RETURN_ABSENCE_DAYS = 28

# The rendered reports. Derived from the cache and the frozen rows, and so
# rebuildable: kept out of the repository like the store.
REPORT_DIR = REPO_ROOT / "reports"

# The Space's staging directory: the index and one report per deck, built by
# `tracker site` from REPORT_DIR and pushed as-is. Derived, so not committed.
SITE_DIR = REPO_ROOT / "site"
SITE_TITLE = "MTG Archetype Tracking"
