"""Archetype membership: the mainboard rules, then the camp within one."""

from pathlib import Path

from . import config
from .parse import Decklist, parse_cache


def _rules() -> dict[str, dict]:
    """Every membership rule in the order it is tested: Goryo's, then the tracked decks."""
    goryos = {"signature": config.SIGNATURE_CARDS, "excluded_engines": config.EXCLUDED_ENGINES}
    return {config.ARCHETYPE: goryos, **config.TRACKED_DECKS}


def _holds_core(rule: dict, mainboard: dict[str, int]) -> bool:
    """Whether the mainboard holds the rule's signature, which is what the fall-out is read over."""
    return all(card in mainboard for card in rule["signature"])


def _reason(rule: dict, decklist: Decklist) -> str | None:
    """Why a mainboard holding the rule's core still does not answer to it, or none.

    The engine names are the registry's, so the fall-out can say which deck a
    list turned out to be. A source outside the deck's colours and a floor a
    signature card falls under are the other two reasons.
    """
    main = decklist.mainboard
    for engine in rule.get("excluded_engines", ()):
        if any(card in main for card in config.ENGINES[engine]):
            return engine
    if any(card in main for card in rule.get("off_colour", ())):
        return "off-colour"
    if any(main.get(card, 0) < copies for card, copies in rule.get("floor", {}).items()):
        return "floor"
    return None


def archetype(decklist: Decklist) -> str | None:
    """The first archetype whose rule the mainboard answers to, or none.

    Goryo's is tested before the tracked decks, so a list takes one name and
    never two. A rule is its signature cards, all in the mainboard, less any
    engine of another deck: a list carrying more than one engine belongs to
    nothing, which is what `config.ENGINES` and each rule's `excluded_engines`
    say. A tracked rule may also name the colours the deck comes in, and set a
    floor on a signature card's copies. A mainboard over `config.MAINBOARD_MAX`
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


def camp(mainboard: dict[str, int]) -> str:
    """The variant camp a mainboard's divergence-card count commits it to.

    Takes the mainboard rather than a list, the rule reading nothing else of one.
    """
    copies = mainboard.get(config.DIVERGENCE_CARD, 0)
    for name, counts in config.CAMPS.items():
        if copies in counts:
            return name
    return config.HYBRID_CAMP


def variant(name: str, mainboard: dict[str, int]) -> str | None:
    """The camp a member of `name` belongs to, by that archetype's own rule.

    Goryo's forks on how many copies of one card a list runs;
    a tracked deck forks on whether it runs a card at all, which is what a
    colour split is. Its rule is ordered: the first version whose cards the
    mainboard holds any of names the camp, and a list holding none takes the
    default. Both read the mainboard alone. A tracked deck with no variant rule
    is one population, and its members carry no camp.
    """
    if name == config.ARCHETYPE:
        return camp(mainboard)
    rule = config.TRACKED_DECKS[name]
    if "variants" not in rule:
        return None
    for camp_name, cards in rule["variants"]:
        if any(mainboard.get(card, 0) for card in cards):
            return camp_name
    return rule["variant_default"]


def classify_cache(raw_dir: Path) -> list[Decklist]:
    """The seam harness: cached payloads through parse and classify."""
    lists = parse_cache(raw_dir)
    for decklist in lists:
        decklist.archetype = archetype(decklist)
        if decklist.archetype:
            decklist.camp = variant(decklist.archetype, decklist.mainboard)
    return lists
