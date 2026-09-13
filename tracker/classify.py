"""Archetype membership: the mainboard signature rules, then the camp within one."""

from pathlib import Path

from . import config
from .parse import Decklist, parse_cache


def archetype(decklist: Decklist) -> str | None:
    """The first archetype whose rule the mainboard answers to, or none.

    Goryo's is tested before the tracked decks, so a list takes one name and
    never two. Its rule is the signature cards, less a mainboard card that names
    another deck built on them. A tracked rule is its signature cards plus the
    colours the deck comes in, less any card that names another deck built on
    the signature: a build sharing the signature and splashing outside them, or
    carrying that card, is a different deck, not a variant of this one. A rule
    may also set a floor on a signature card's copies. A mainboard over
    `config.MAINBOARD_MAX` is a list published with its sideboard in the main
    and answers to no rule.
    """
    if sum(decklist.mainboard.values()) > config.MAINBOARD_MAX:
        return None
    if all(card in decklist.mainboard for card in config.SIGNATURE_CARDS) and not any(
        card in decklist.mainboard for card in config.EXCLUDED_CARDS
    ):
        return config.ARCHETYPE
    for name, rule in config.TRACKED_DECKS.items():
        if all(card in decklist.mainboard for card in rule["signature"]) and not any(
            card in decklist.mainboard for card in rule["off_colour"] + rule.get("excluded", ())
        ) and all(
            decklist.mainboard.get(card, 0) >= copies for card, copies in rule.get("floor", {}).items()
        ):
            return name
    return None


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
