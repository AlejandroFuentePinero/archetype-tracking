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


# How far back the analysis history reaches. The history opens on the regime boundary: what was played under the old rules
# is a different era and is not in the store (Alejandro, 2026-09-13). The raw
# cache keeps whatever was fetched before it.
HISTORY_START = "2026-05-18"

# The regime boundary the history spans (see ADR 0001). Lists either side of it
# belong to different eras, so every window is bounded by it.
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
# A mainboard card that names another deck. Goryo's is Goryo's Vengeance and the
# legendary Atraxa it pairs with; Persist reanimator runs a different package
# and a list holding both is the Persist deck with Goryo's as a second angle
# (Alejandro, 2026-09-13). The Shifting Woodland Omniscience combo wears the
# Goryo's core the same way. A Goryo's list carrying Blink's creatures is not
# this: its engine is still the Goryo's package, so it stays.
EXCLUDED_CARDS = ("Persist", "Omniscience", "Shifting Woodland")

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
    "esper": "Esper",
    "orzhov": "Orzhov",
    "frog": "Frog",
    "traditional": "Traditional",
    "lab": "Lab",
    "gruul": "Gruul",
    "mono-green": "Mono-green",
}


def version_name(camp: str) -> str:
    """The name the report prints for a camp."""
    return VERSION_NAMES.get(camp, camp)

# Tracked decks: archetypes the engine classifies by signature and colour and
# reports on weekly. Goryo's above has its own rule and is tested first, these in
# turn, so a list takes the first name that claims it and is never two decks.
TRACKED_DECKS = {
    "blink": {
        # The four together are the deck. Phelia alone is not enough: a white
        # energy build and a Boros build both play her, and the Ephemerate pool
        # on its own is half Goryo's.
        "signature": (
            "Phelia, Exuberant Shepherd",
            "Flickerwisp",
            "Overlord of the Balemurk",
            "Witch Enchanter",
        ),
        # The deck is Esper or Orzhov and nothing else. A Mardu build shares all
        # four signature cards and is a different deck, so a mainboard source
        # that actually produces red or green puts a list outside the archetype.
        # Fetchlands are not colour evidence here: most of the Orzhov half
        # fetches with Flooded Strand, which produces neither.
        "off_colour": (
            "Sacred Foundry",
            "Blood Crypt",
            "Raucous Theater",
            "Elegant Parlor",
            "Mountain",
            "Snow-Covered Mountain",
            "Arena of Glory",
            "Overgrown Tomb",
            "Temple Garden",
            "Lush Portico",
        ),
        # Variant rule: the blue half against the two-colour half. Mainboard
        # Watery Grave partitions the archetype exactly, with no list between
        # the two, where a rule drawn on blue sources throws away the Orzhov
        # lists that fetch and a rule drawn on blue spells drops any Esper list
        # that cut Teferi. Presence and not a count: a variant here is which
        # colours the deck is, which one copy settles.
        "variants": (("esper", ("Watery Grave",)),),
        "variant_default": "orzhov",
        # A mainboard card that names another deck built on the four creatures
        # (Alejandro, 2026-09-13): the Guide of Souls and Ocelot Pride energy
        # engine, the Estrid's Invocation Overlords deck, Stoneblade, and the
        # Tidehollow Sculler taxes deck. Aether Vial is not one: the Orzhov Vial
        # lists on Ephemerate are a version of this deck.
        "excluded": (
            "Guide of Souls",
            "Ocelot Pride",
            "Estrid's Invocation",
            "Stoneforge Mystic",
            "Tidehollow Sculler",
        ),
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
        "off_colour": (),
        # No variant rule either. Nothing in the history forks the deck: the
        # only mid-adoption mainboard cards are which basics and fetches fill
        # the manabase. One population, so the camp is unset and every reading
        # pools it.
    },
    "oswald": {
        # Grinding Station is what makes an Oswald list this deck: the Tezzeret
        # and Krang build shares Oswald, Emry and the Saga shell and is a
        # different deck. No colour rule. A green source is a splash, usually
        # for Haywire Mite, and the pilot reads it as the same deck.
        "signature": ("Oswald Fiddlebender", "Grinding Station"),
        "off_colour": (),
        # The Kappa Cannoneer and Pinnacle Emissary artifact deck bolted two
        # Oswald and a Station on for a fortnight and is a different deck
        # (Alejandro, 2026-09-13). Mainboard only: Oswald lists side Kappa.
        "excluded": ("Kappa Cannoneer",),
    },
    "zoo": {
        # The two together are the deck and nothing else in the history shares
        # them. Five colours, so no colour rule: the manabase is the part of
        # this deck that moves most.
        "signature": ("Territorial Kavu", "Scion of Draco"),
        "off_colour": (),
        # Three other decks put Kavu and Scion in as domain bodies and are not
        # this one (Alejandro, 2026-09-13): Persist reanimator on Archon of
        # Cruelty and Faithless Looting, the five-colour Living End build on
        # Bloodbraid Marauder and Malevolent Rumble, and the five-colour energy
        # build on the Guide of Souls and Ocelot Pride engine.
        "excluded": ("Persist", "Living End", "Guide of Souls", "Ocelot Pride"),
        # The Frog version is the bluer build and the one the report reads.
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
        "off_colour": (),
        # A hybrid brew on the intact shell is out too, for now: Dredger's
        # Insight names the Yawgmoth-style Cauldron package and Mystic Forge the
        # Karn Forge package, and nothing else in the history holds either.
        "excluded": ("Dredger's Insight", "Mystic Forge"),
        # Three versions, read in this order. The red spells name the Gruul
        # build: Stomping Ground would too, but Grove of the Burnwillows sits
        # in nine of ten mono-green lists, so a source is not the line. Ugin's
        # Labyrinth names the Lab build, every Devourer of Destiny list running
        # it and nine in ten of its lists running Devourer. A list holding both
        # is a Gruul list on a couple of Labyrinths, 27 of 1000 since the bans,
        # and reads as Gruul.
        "variants": (
            ("gruul", ("Unholy Heat", "Writhing Chrysalis")),
            ("lab", ("Ugin's Labyrinth",)),
        ),
        "variant_default": "mono-green",
    },
    "devoted": {
        # Devoted Druid alone admits a handful of lists on Quirion Ranger and
        # Eladamri; Tyvar is the combo the deck is built around.
        "signature": ("Devoted Druid", "Tyvar, Jubilant Brawler"),
        "off_colour": (),
    },
    "affinity": {
        # Kappa Cannoneer alone admits the Hammer build; Pinnacle Emissary is
        # what the affinity deck plays and Hammer does not. Weapons Manufacturing
        # and Engineered Explosives keep out the Krang, Tamiyo and Song of
        # Creation artifact decks, which share the two creatures and the Saga
        # shell and are a different deck.
        "signature": ("Kappa Cannoneer", "Pinnacle Emissary", "Weapons Manufacturing",
                      "Engineered Explosives"),
        "off_colour": (),
        # The Song of Creation deck on the full Affinity four is a hybrid brew
        # and out (Alejandro, 2026-09-13).
        "excluded": ("Song of Creation",),
    },
    "prowess": {
        # Cori-Steel Cutter alone admits the artifact decks on Emry and Tamiyo,
        # 121 lists since the bans; the two creatures are what make it prowess.
        # Steam Vents is what makes it Izzet: the red and Boros prowess lists on
        # Lava Spike and Skewer share the three creatures and never the land.
        "signature": ("Cori-Steel Cutter", "Monastery Swiftspear", "Dragon's Rage Channeler",
                      "Steam Vents"),
        "off_colour": (),
        # Izzet Phoenix answers the rule through Cutter, Swiftspear, DRC and
        # Vents and is another deck, and the prowess core with Phoenix grafted on
        # is a hybrid brew (Alejandro, 2026-09-13).
        "excluded": ("Arclight Phoenix",),
        # One Vents is a Gruul list fetching for its sideboard: every Izzet list
        # runs two or more.
        "floor": {"Steam Vents": 2},
    },
    "trudge": {
        # Ugin's Labyrinth names the Eldrazi ramp shell: the mono-green Nantuko
        # decks run Trudge and Fanatic as mana dorks and none of the shell
        # (Alejandro, 2026-09-13). Every other list in the history holds it.
        "signature": ("Slumbering Trudge", "Fanatic of Rhonas", "Ugin's Labyrinth"),
        "off_colour": (),
    },
    "tron": {
        # The three lands and Karn. The lands alone admit a blue Tron on Force
        # of Negation and Stock Up, 53 lists since the bans, which is a
        # different deck; every list with Karn is the Eldrazi build.
        "signature": ("Urza's Tower", "Urza's Mine", "Urza's Power Plant", "Karn, the Great Creator"),
        "off_colour": (),
        # Cards that name another Tron deck (Alejandro, 2026-09-13): the
        # Chromatic eggs are Mono-Green Tron proper, Stock Up the blue control
        # build, Malevolent Rumble the green ramp build on the Tron lands, and
        # Devoted Druid a combo brew in the flex slots. Ancient Stirrings is not
        # one: clean Eldrazi Tron lists run it on a green splash.
        "excluded": (
            "Chromatic Sphere",
            "Chromatic Star",
            "Stock Up",
            "Malevolent Rumble",
            "Devoted Druid",
        ),
    },
    "energy": {
        # Guide of Souls and Ocelot Pride are the engine of every energy deck,
        # and Ajani and Goblin Bombardment are what the Boros build does with
        # it. The Azorius and Selesnya lists on the two creatures are blink and
        # Birthing Ritual decks and hold neither. Mardu and Jeskai energy share
        # all four and are different decks, so a source that produces blue,
        # black or green puts a list outside, read on sources and never on
        # fetchlands: Marsh Flats fetches Sacred Foundry in nearly every Boros
        # list. Since the bans the four with no such source are 1036 lists,
        # against 117 Mardu and 134 Jeskai.
        "signature": ("Guide of Souls", "Ocelot Pride", "Ajani, Nacatl Pariah",
                      "Goblin Bombardment"),
        # Hybrid brews on the energy four, out for now (Alejandro, 2026-09-13):
        # the Boros Eldrazi build on the Temple, the Cutter prowess build and
        # the Leonardo Cauldron combo. Nothing else in the history holds them.
        "excluded": ("Eldrazi Temple", "Cori-Steel Cutter", "Agatha's Soul Cauldron"),
        "off_colour": (
            "Island", "Snow-Covered Island", "Swamp", "Snow-Covered Swamp",
            "Forest", "Snow-Covered Forest",
            "Hallowed Fountain", "Meticulous Archive", "Mystic Gate", "Floodfarm Verge",
            "Seachrome Coast", "Godless Shrine", "Shadowy Backstreet", "Bleachbone Verge",
            "Concealed Courtyard", "Blood Crypt", "Raucous Theater", "Blazemire Verge",
            "Blackcleave Cliffs", "Steam Vents", "Thundering Falls", "Riverpyre Verge",
            "Spirebluff Canal", "Watery Grave", "Undercity Sewers", "Gloomlake Verge",
            "Darkslick Shores", "Temple Garden", "Lush Portico", "Hushwood Verge",
            "Razorverge Thicket", "Stomping Ground", "Commercial District", "Thornspire Verge",
            "Copperline Gorge", "Breeding Pool", "Hedge Maze", "Willowrush Verge",
            "Botanical Sanctum", "Overgrown Tomb", "Underground Mortuary", "Wastewood Verge",
            "Blooming Marsh", "Boseiju, Who Endures", "Otawara, Soaring City",
            "Takenuma, Abandoned Mire",
        ),
    },
    "ponza": {
        # Erode is in nearly every land-destruction list, and Cleansing
        # Wildfire is the red half of the plan: the five mono-white lists on
        # Crucible of Worlds and Ghost Quarter hold Erode and not the Wildfire,
        # and the Boros energy lists that splash Erode hold neither Wildfire
        # nor the rest. The control decks on Erode, Jeskai and Azorius, are
        # different decks, so a blue, black or green source puts a list
        # outside, like energy. Since the bans that is 466 lists of the 474
        # on both cards.
        "signature": ("Erode", "Cleansing Wildfire"),
        # The Boom/Bust and Magmatic Hellkite build in place of Field of Ruin
        # and Demolition Field is a hybrid brew, out for now (Alejandro,
        # 2026-09-13). Flagstones is not the marker: clean lists run it.
        "excluded": ("Boom/Bust",),
        "off_colour": (
            "Island", "Snow-Covered Island", "Swamp", "Snow-Covered Swamp",
            "Forest", "Snow-Covered Forest",
            "Hallowed Fountain", "Meticulous Archive", "Mystic Gate", "Floodfarm Verge",
            "Seachrome Coast", "Godless Shrine", "Shadowy Backstreet", "Bleachbone Verge",
            "Concealed Courtyard", "Blood Crypt", "Raucous Theater", "Blazemire Verge",
            "Blackcleave Cliffs", "Steam Vents", "Thundering Falls", "Riverpyre Verge",
            "Spirebluff Canal", "Watery Grave", "Undercity Sewers", "Gloomlake Verge",
            "Darkslick Shores", "Temple Garden", "Lush Portico", "Hushwood Verge",
            "Razorverge Thicket", "Stomping Ground", "Commercial District", "Thornspire Verge",
            "Copperline Gorge", "Breeding Pool", "Hedge Maze", "Willowrush Verge",
            "Botanical Sanctum", "Overgrown Tomb", "Underground Mortuary", "Wastewood Verge",
            "Blooming Marsh", "Boseiju, Who Endures", "Otawara, Soaring City",
            "Takenuma, Abandoned Mire",
        ),
    },
    "dimir": {
        # Psychic Frog and Quantum Riddler together are the midrange deck. Frog
        # alone admits the Dimir Oculus lists on Unearth, 60 since the bans,
        # which never run Riddler; Goryo's, Blink and Domain Zoo share the pair
        # and are tested first. The Esper and Grixis Frog decks share the pair
        # too and are different decks, so a source that produces white, red or
        # green puts a list outside: Plains sits in 127 of the Esper lists and
        # Steam Vents in every Grixis one. Since the bans that is 394 lists.
        "signature": ("Psychic Frog", "Quantum Riddler"),
        # The other Dimir decks on the pair (Alejandro, 2026-09-13): Necro on
        # Soul Spike, Persist reanimator, Oculus on Unearth (which does run
        # Riddler, in a third of its lists), Goryo's without Ephemerate, and
        # Death's Shadow. The Moonshadow aggro build is left in: no one card
        # names it without moving clean lists.
        "excluded": (
            "Necrodominance",
            "Persist",
            "Abhorrent Oculus",
            "Goryo's Vengeance",
            "Death's Shadow",
        ),
        "off_colour": (
            "Plains", "Snow-Covered Plains", "Mountain", "Snow-Covered Mountain",
            "Forest", "Snow-Covered Forest",
            "Hallowed Fountain", "Meticulous Archive", "Mystic Gate", "Floodfarm Verge",
            "Seachrome Coast", "Godless Shrine", "Shadowy Backstreet", "Bleachbone Verge",
            "Concealed Courtyard", "Sacred Foundry", "Elegant Parlor", "Sunbillow Verge",
            "Inspiring Vantage", "Arena of Glory", "Steam Vents", "Thundering Falls",
            "Riverpyre Verge", "Spirebluff Canal", "Blood Crypt", "Raucous Theater",
            "Blazemire Verge", "Blackcleave Cliffs", "Stomping Ground", "Commercial District",
            "Thornspire Verge", "Copperline Gorge", "Temple Garden", "Lush Portico",
            "Hushwood Verge", "Razorverge Thicket", "Breeding Pool", "Hedge Maze",
            "Willowrush Verge", "Botanical Sanctum", "Overgrown Tomb", "Underground Mortuary",
            "Wastewood Verge", "Blooming Marsh", "Boseiju, Who Endures",
        ),
    },
    "jeskai": {
        # Consult the Star Charts, Teferi and Wrath of the Skies are the control
        # shell, and Galvanic Discharge is what makes it Jeskai. A colour rule
        # on sources fails here: the Azorius control lists run Steam Vents,
        # Watery Grave and Breeding Pool as extra colours for Prismatic
        # Ending and cast no red spell off them, 120 of the 123 lists on a
        # black source holding none. Read on the spell, the deck is 155 lists
        # since the bans, and a Breeding Pool beside the Discharge is a splash
        # inside it.
        "signature": ("Consult the Star Charts", "Teferi, Time Raveler", "Wrath of the Skies",
                      "Galvanic Discharge"),
        "off_colour": (),
        # Decks built on the shell that are not this one (Alejandro,
        # 2026-09-13): four-colour Omnath control on Wrenn and Six, the
        # Indomitable Creativity combo, and the Saheeli combo inside the
        # control shell, a hybrid brew.
        "excluded": ("Wrenn and Six", "Indomitable Creativity", "Saheeli Rai"),
    },
    "storm": {
        # Ral, Ruby Medallion and Past in Flames together. Ruby alone admits
        # the Belcher lists on Pinnacle Monk, which never run Ral or Past in
        # Flames; Ral alone admits an Izzet storm on Stormcatch Mentor with no
        # Medallion. No colour rule: the sideboard colours are the Wish
        # targets, and every list is the same red deck under them.
        "signature": ("Ral, Monsoon Mage", "Ruby Medallion", "Past in Flames"),
        "off_colour": (),
    },
    "livingend": {
        # Living End with the two cascade spells. The Sultai build on
        # Formidable Speaker and Overlord of the Balemurk shares Living End
        # and Shardless Agent and never runs Violent Outburst, and it is a
        # different deck. No colour rule: Temple Garden sits in 187 of the 326
        # lists beside no white spell, a fetchable land of the Temur shell.
        "signature": ("Living End", "Shardless Agent", "Violent Outburst"),
        "off_colour": (),
    },
}


def versions(archetype: str) -> tuple[str, ...]:
    """Every camp of an archetype in rule order, or nothing for one population."""
    if archetype == ARCHETYPE:
        return (*CAMPS, HYBRID_CAMP)
    rule = TRACKED_DECKS[archetype]
    if "variants" not in rule:
        return ()
    return (*(name for name, _ in rule["variants"]), rule["variant_default"])

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
            "mainboard holds Phelia, Exuberant Shepherd, Flickerwisp, Overlord of the "
            "Balemurk and Witch Enchanter, no red or green source, and none of Guide of "
            "Souls, Ocelot Pride, Estrid's Invocation, Stoneforge Mystic or Tidehollow "
            "Sculler. The esper version mainboards Watery Grave; the orzhov version does not."
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
            "mainboard holds all four of Goryo's Vengeance, Atraxa, Grand Unifier, "
            "Psychic Frog and Ephemerate, and none of Persist, Omniscience or Shifting "
            "Woodland. Green sources for casting Atraxa do not change membership, and there "
            "is no colour rule. The non-fallaji version is the one read."
        ),
    },
    "neoform": {
        "name": "Simic Neoform",
        "archetype": "neoform",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds all four of Neoform, Allosaurus Rider, Eldritch Evolution "
            "and Planar Genesis. No colour rule and no versions: every reading is the "
            "whole archetype's."
        ),
    },
    "oswald": {
        "name": "UW Oswald",
        "archetype": "oswald",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Oswald Fiddlebender and Grinding Station and no Kappa "
            "Cannoneer. No colour rule: a green splash is the same deck. No versions."
        ),
    },
    "zoo": {
        "name": "Domain Zoo",
        "archetype": "zoo",
        "camp": "traditional",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Territorial Kavu and Scion of Draco and none of Persist, Living "
            "End, Guide of Souls or Ocelot Pride. No colour rule. The frog version mainboards "
            "Psychic Frog and is the one read; the traditional version does not."
        ),
    },
    "broodscale": {
        "name": "Broodscale",
        "archetype": "broodscale",
        "camp": "lab",
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Basking Broodscale, Blade of the Bloodchief and Eldrazi Temple, "
            "and neither Dredger's Insight nor Mystic Forge. No colour rule. The gruul version mainboards Unholy Heat or Writhing Chrysalis, the lab version "
            "mainboards Ugin's Labyrinth and is the one read, and the mono-green version "
            "holds neither."
        ),
    },
    "devoted": {
        "name": "Devoted Combo",
        "archetype": "devoted",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Devoted Druid and Tyvar, Jubilant Brawler. No colour rule and "
            "no versions."
        ),
    },
    "affinity": {
        "name": "Affinity",
        "archetype": "affinity",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Kappa Cannoneer, Pinnacle Emissary, Weapons Manufacturing and "
            "Engineered Explosives and no Song of Creation. No colour rule and no versions."
        ),
    },
    "prowess": {
        "name": "Izzet Prowess",
        "archetype": "prowess",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Cori-Steel Cutter, Monastery Swiftspear, Dragon's Rage "
            "Channeler and at least two Steam Vents, and no Arclight Phoenix. No colour rule "
            "and no versions."
        ),
    },
    "trudge": {
        "name": "Trudge",
        "archetype": "trudge",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Slumbering Trudge, Fanatic of Rhonas and Ugin's Labyrinth. No "
            "colour rule and no versions."
        ),
    },
    "tron": {
        "name": "Tron",
        "archetype": "tron",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Urza's Tower, Urza's Mine, Urza's Power Plant and Karn, the "
            "Great Creator, and none of Chromatic Sphere, Chromatic Star, Stock Up, "
            "Malevolent Rumble or Devoted Druid. No colour rule and no versions."
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
            "Bombardment, no blue, black or green source, and none of Eldrazi Temple, "
            "Cori-Steel Cutter or Agatha's Soul Cauldron. No versions."
        ),
    },
    "ponza": {
        "name": "Boros Ponza",
        "archetype": "ponza",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Erode and Cleansing Wildfire and no Boom/Bust, and no blue, "
            "black or green source. No versions."
        ),
    },
    "dimir": {
        "name": "Dimir Midrange",
        "archetype": "dimir",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Psychic Frog and Quantum Riddler, no white, red or green "
            "source, and none of Necrodominance, Persist, Abhorrent Oculus, Goryo's Vengeance "
            "or Death's Shadow. No versions."
        ),
    },
    "jeskai": {
        "name": "Jeskai Control",
        "archetype": "jeskai",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Consult the Star Charts, Teferi, Time Raveler, Wrath of the "
            "Skies and Galvanic Discharge, and none of Wrenn and Six, Indomitable Creativity "
            "or Saheeli Rai. No colour rule and no versions."
        ),
    },
    "storm": {
        "name": "Storm",
        "archetype": "storm",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Ral, Monsoon Mage, Ruby Medallion and Past in Flames. No colour "
            "rule and no versions."
        ),
    },
    "livingend": {
        "name": "Temur Living End",
        "archetype": "livingend",
        "camp": None,
        "watch": (),
        "manabase": False,
        "membership": (
            "mainboard holds Living End, Shardless Agent and Violent Outburst. No colour rule "
            "and no versions."
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
MAJOR_EVENTS = (
    {"id": 434455, "label": "Pro Tour Amsterdam", "date": "2026-07-17", "format": "Modern"},
    {"id": 441441, "label": "Spotlight Brisbane", "date": "2026-08-29"},
    {"id": 405590, "label": "Spotlight Dallas", "date": "2026-09-05"},
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
