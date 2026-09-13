"""Archetype membership: the mainboard rules, then the camp within one."""

from collections import Counter
from pathlib import Path

from . import config
from .parse import Decklist, parse_cache

# The two reasons the splash line turns a list away with, which the weekly
# report counts together as the colour rule's exclusions.
COLOUR_REASONS = ("playset", "splash")


def _rules() -> dict[str, dict]:
    """Every membership rule in the order it is tested: Goryo's, then the tracked decks."""
    goryos = {"signature": config.SIGNATURE_CARDS, "excluded_engines": config.EXCLUDED_ENGINES}
    return {config.ARCHETYPE: goryos, **config.TRACKED_DECKS}


def _holds_core(rule: dict, mainboard: dict[str, int]) -> bool:
    """Whether the mainboard holds the rule's core, which is what the fall-out is read over.

    The core is every signature card, and where the rule names `either`, all
    the cards of any one of its groups as well: a deck with a second entry path.
    """
    return all(card in mainboard for card in rule["signature"]) and any(
        all(card in mainboard for card in group) for group in rule.get("either", ((),))
    )


def _beyond_splash(copies: dict[str, int], exempt: tuple[str, ...] = ()) -> str | None:
    """Whether a set of spells is more than a splash: a playset of one, or five in all.

    A light splash does not move a list out of its deck (Alejandro, 2026-09-13):
    four or fewer cards is a splash, five or more is a deck that goes deeper
    into the colour, and a full playset of one card is the other deck's card
    whatever the total.

    A rule may exempt a card from the playset clause and nothing else, which is
    how a deck that fills a slot to the meta keeps its own lists (Alejandro,
    2026-09-13): four off-colour removal spells under the five-card line are
    still the deck, where a playset of an engine or a threat is another deck's.
    """
    if any(count >= 4 for card, count in copies.items() if card not in exempt):
        return "playset"
    if sum(copies.values()) >= 5:
        return "splash"
    return None


def _spells_outside(decklist: Decklist, colours: frozenset[str]) -> dict[str, int]:
    """The mainboard's nonland cards outside the colours, with their copies.

    Lands are excluded, saying nothing on their own; a card with no colour on
    record is colourless.
    """
    return {
        card: copies
        for card, copies in decklist.mainboard.items()
        if card not in decklist.land_names and decklist.colours.get(card, frozenset()) - colours
    }


def _reason(rule: dict, decklist: Decklist) -> str | None:
    """Why a mainboard holding the rule's core still does not answer to it, or none.

    The engine names are the registry's, so the fall-out can say which deck a
    list turned out to be; a pair the rule weighs is named the same way. The
    splash line on the deck's colours, a floor a signature card falls under and
    a supporting tier the list holds too few of are the other reasons.
    """
    main = decklist.mainboard
    for engine in rule.get("excluded_engines", ()):
        if any(card in main for card in config.ENGINES[engine]):
            return engine
    if "outweighed" in rule:
        name, pair, anchor = rule["outweighed"]
        if all(card in main for card in pair) and anchor not in main:
            return name
    if "colours" in rule and (
        beyond := _beyond_splash(
            _spells_outside(decklist, rule["colours"]), rule.get("playset_exempt", ())
        )
    ):
        return beyond
    if any(main.get(card, 0) < copies for card, copies in rule.get("floor", {}).items()):
        return "floor"
    count, cards = rule.get("supporting", (0, ()))
    if sum(card in main for card in cards) < count:
        return "supporting"
    return None


def archetype(decklist: Decklist) -> str | None:
    """The first archetype whose rule the mainboard answers to, or none.

    Goryo's is tested before the tracked decks, so a list takes one name and
    never two. A rule is its signature cards, all in the mainboard, less any
    engine of another deck: a list carrying more than one engine belongs to
    nothing, which is what `config.ENGINES` and each rule's `excluded_engines`
    say. A tracked rule may also name the colours the deck comes in, read on the
    splash line over the spells the mainboard casts, and set a floor on a
    signature card's copies. A mainboard over `config.MAINBOARD_MAX`
    is a list published with its sideboard in the main and answers to no rule.
    """
    if sum(decklist.mainboard.values()) > config.MAINBOARD_MAX:
        return None
    for name, rule in _rules().items():
        if _holds_core(rule, decklist.mainboard) and _reason(rule, decklist) is None:
            return name
    return None


def fallout(decklist: Decklist) -> list[tuple[str, str]]:
    """The decks whose core an unclassified list holds, each with why it turned the list away.

    Empty for a member: a list another rule claimed is that deck's, not fall-out
    from the ones it also resembles. Every exclusion is therefore visible, so a
    deck adopting another deck's engine card shows up as a growing count rather
    than as a silent decline.
    """
    if decklist.archetype or sum(decklist.mainboard.values()) > config.MAINBOARD_MAX:
        return []
    return [
        (name, reason)
        for name, rule in _rules().items()
        if _holds_core(rule, decklist.mainboard) and (reason := _reason(rule, decklist))
    ]


def _cast(decklist: Decklist) -> frozenset[str]:
    """The colours the mainboard casts, read on its spells and never on its sources."""
    return frozenset().union(
        *(
            decklist.colours.get(card, frozenset())
            for card in decklist.mainboard
            if card not in decklist.land_names
        ),
        frozenset(),
    )


def _spells(decklist: Decklist) -> frozenset[str]:
    """The mainboard's spells, its sources saying nothing about which version it is."""
    return frozenset(decklist.mainboard) - decklist.land_names


def _rule_colours(rule: dict, version: str, published: dict[str, frozenset[str]]) -> set[str]:
    """The colours a version's rule is drawn on: its markers' own, and any it names.

    Read off the rule and not off the population, which is the one place the two
    readings part. Broodscale's Gruul half casts red in 339 of its 387 lists and
    colourless Writhing Chrysalis holds the other 48, so a population bar set at
    `config.VERSION_MARKER_SHARE` throws red away by two points and the version
    drawn on red has no colour at all. The rule says red, and red is what no
    other version of that deck casts.
    """
    cards = next((cards for name, cards in rule.get("variants", ()) if name == version), ())
    return {colour for name, colour in rule.get("colour_variants", ()) if name == version}.union(
        *(published.get(card, frozenset()) for card in cards), frozenset()
    )


def _carrying(population: list[Decklist], feature) -> Counter:
    """How many lists of a population carry each feature any of them has."""
    return Counter(f for decklist in population for f in feature(decklist))


def _carried(population: list[Decklist], feature) -> set[str]:
    """What `config.VERSION_MARKER_SHARE` of a population carries."""
    counted = _carrying(population, feature)
    return {
        f for f, count in counted.items() if count >= config.VERSION_MARKER_SHARE * len(population)
    }


def _absent(candidates: set[str], default: list[Decklist], feature) -> list[str]:
    """Those candidates the default version's population does without.

    The half that does the work. Black is in three quarters of mono-green
    Broodscale off Dismember, which Phyrexian mana casts, and blue and black are
    in every traditional Zoo list because the deck is five colours: read without
    this, a version's own colours would be read as its neighbour's and the table
    would name whole populations.
    """
    counted = _carrying(default, feature)
    return sorted(
        f for f in candidates if counted[f] < (1 - config.VERSION_MARKER_SHARE) * len(default)
    )


# The two shapes a marker is read in, each over what it is read off: the
# colours a mainboard casts, and the spells it holds.
FEATURES = {"colour": _cast, "card": _spells}


def version_markers(lists: list[tuple[str, Decklist]]) -> list[tuple[str, str, str, str]]:
    """What says a mainboard is a named version's and not its deck's default: deck, version, kind, marker.

    What the pass-three sweep read is read here: the colours a named version is
    drawn on, and the cards nine tenths of its population holds. The two are
    read differently on purpose. A colour comes off the rule, which names the
    cards a version is drawn on and sometimes the colour itself, because a
    version can be drawn on a colour without its whole population casting it:
    48 of the 387 Gruul Broodscale lists are on colourless Writhing Chrysalis
    alone. A card has no such rule to come off, so it comes off the population,
    and a version thinner than `config.TRACK_MIN_LISTS` has no population to
    read: nine tenths of a one-list version is every card in one decklist,
    which is how green Tron alone raised 27 colourless lists on a card the rule
    calls a build.

    Read over the population given and never over the lists a marker is later
    put to, which is what lets a paper event be read at all: one event's field
    is nine lists where the bar wants a population, and MTGO is the population
    that has one.
    """
    published: dict[str, frozenset[str]] = {}
    for _, decklist in lists:
        published.update(decklist.colours)
    markers = []
    for deck, rule in config.TRACKED_DECKS.items():
        if not (default := rule.get("variant_default")) or not rule.get("version_boundary", True):
            continue
        members: dict[str, list[Decklist]] = {}
        for _, decklist in lists:
            if decklist.archetype == deck:
                members.setdefault(decklist.camp, []).append(decklist)
        if not (fallen := members.get(default, [])):
            continue
        for version in config.versions(deck):
            if version == default:
                continue
            named = members.get(version, [])
            markers += [
                (deck, version, "colour", marker)
                for marker in _absent(_rule_colours(rule, version, published), fallen, _cast)
            ]
            # The cards are a population reading where the colours are a rule
            # reading, so they alone need a population to read.
            if len(named) >= config.TRACK_MIN_LISTS:
                markers += [
                    (deck, version, "card", marker)
                    for marker in _absent(_carried(named, _spells), fallen, _spells)
                ]
    return markers


def markers_held(
    markers: list[tuple[str, str, str]], decklist: Decklist
) -> list[tuple[str, str, str]]:
    """Those of a deck's markers a mainboard holds, each read in its own shape.

    Takes the markers rather than reading them, so the population that says
    what a marker is and the lists it is put to can be two rooms: MTGO is the
    only field large enough to carry the bar, and a paper event is the only
    place some of the lists are.
    """
    read = {kind: feature(decklist) for kind, feature in FEATURES.items()}
    return [
        (version, kind, marker)
        for version, kind, marker in markers
        if marker in read[kind]
    ]


def version_boundary(lists: list[tuple[str, Decklist]]) -> list[tuple[str, str, str, str, str]]:
    """Every default-version member whose mainboard is a named version's, and what says so.

    A version rule reads its markers in order and drops everything else into the
    default, so the default is the one version no list is ever read into: a list
    that is a named version on every other reading but happens to hold no marker
    takes it silently and its storyline is read as the default's. Pass three
    found five such lists by hand, two Pro Tour Broodscale lists casting
    Lightning Bolt and SuperCow12653's two Blink lists casting Teferi, and
    nothing in the build would have found either.

    Sources say nothing either way, the way they say nothing to the splash line,
    or Blink's fetching Orzhov lists and Broodscale's Stomping Ground come back
    as boundary cases that `CONTEXT.md` already rules out. A deck whose rule
    says `version_boundary` is false is left out whole, every signal the check
    could raise there having been ruled a build already.
    """
    marked: dict[str, list[tuple[str, str, str]]] = {}
    for deck, version, kind, marker in version_markers(lists):
        marked.setdefault(deck, []).append((version, kind, marker))
    rows = []
    for list_id, decklist in lists:
        markers = marked.get(decklist.archetype)
        if not markers or decklist.camp != config.TRACKED_DECKS[decklist.archetype]["variant_default"]:
            continue
        rows += [
            (list_id, decklist.archetype, version, kind, marker)
            for version, kind, marker in markers_held(markers, decklist)
        ]
    return rows


def camp(mainboard: dict[str, int]) -> str:
    """The variant camp a mainboard's divergence-card count commits it to.

    Takes the mainboard rather than a list, the rule reading nothing else of one.
    """
    copies = mainboard.get(config.DIVERGENCE_CARD, 0)
    for name, counts in config.CAMPS.items():
        if copies in counts:
            return name
    return config.HYBRID_CAMP


def variant(name: str, decklist: Decklist) -> str | None:
    """The camp a member of `name` belongs to, by that archetype's own rule.

    Goryo's forks on how many copies of one card a list runs;
    a tracked deck forks on whether it runs a card at all, which is what a
    colour split is. Its rule is ordered: the first version whose cards the
    mainboard holds any of names the camp, then the first colour the mainboard
    casts a spell of, and a list holding none takes the default. A tracked deck
    with no variant rule is one population, and its members carry no camp.
    """
    mainboard = decklist.mainboard
    if name == config.ARCHETYPE:
        return camp(mainboard)
    rule = config.TRACKED_DECKS[name]
    if "variants" not in rule and "colour_variants" not in rule:
        return None
    for camp_name, cards in rule.get("variants", ()):
        if any(mainboard.get(card, 0) for card in cards):
            return camp_name
    # A version read by colour is read on the colour itself and never on the
    # splash line (Alejandro, 2026-09-13): a list that casts any spell of the
    # colour is that colour's version, a playset naming a build and not a
    # version. Blink's Esper half is the one such version, its marker being a
    # land the card rules above cannot see off a fetch.
    for camp_name, colour in rule.get("colour_variants", ()):
        if any(
            colour in decklist.colours.get(card, frozenset())
            for card in mainboard
            if card not in decklist.land_names
        ):
            return camp_name
    return rule["variant_default"]


def classify_cache(raw_dir: Path) -> list[Decklist]:
    """The seam harness: cached payloads through parse and classify."""
    lists = parse_cache(raw_dir)
    for decklist in lists:
        decklist.archetype = archetype(decklist)
        if decklist.archetype:
            decklist.camp = variant(decklist.archetype, decklist)
    return lists
