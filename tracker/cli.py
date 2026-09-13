"""Terminal entry points: refresh a day, then freeze and render a tracked deck's week."""

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from . import config, index, melee, site, spotlight, weekly
from .refresh import refresh
from .store import arrivals, fallout


# How many of the archetype's arrivals are named before the rest become a count.
# A run against a standing index brings in a day or two and never reaches this;
# the run that does is the first one, whose index was empty and whose arrivals
# are therefore the whole history. That is not news and must not be printed as
# though it were, but it is not nothing either, so what was dropped is counted
# rather than left silent.
NAMED_ARRIVALS = 20


def _ingest_lines(change: index.Change, ours: list[dict]) -> list[str]:
    """What the run brought in: the field as a count, the archetype by name.

    The count is of lists and not of events, because the days hardest to speak
    about are the ones already cached: an unsettled league dump gains 5-0s
    through its own day, so a run reporting events alone would say nothing
    arrived on exactly the day something did. The event count goes beside it
    rather than instead of it, a fresh day and a day that grew being different
    news.
    """
    if not change.added and not change.withdrawn:
        return ["  no list published since the last run"]
    events = {row.event_id for row in change.added}
    lines = [
        f"  {len(change.added)} new list(s) across {len(events)} event(s),"
        f" {len(ours)} of them Goryo's"
    ]
    for row in ours[:NAMED_ARRIVALS]:
        finish = f"#{row['placement']}" if row["placement"] else "5-0"
        lines.append(
            f"    {row['date']}  {row['event']:<26} {finish:<5}"
            f" {row['camp']:<12} {row['pilot']}"
        )
    if len(ours) > NAMED_ARRIVALS:
        lines.append(f"    and {len(ours) - NAMED_ARRIVALS} more, further back")
    if change.withdrawn:
        # Not a gap and not an error: the site republishes an event under a
        # wrongly dated slug and later takes one of them down. Said out loud
        # because lists leaving the history quietly is the same failure as
        # lists arriving quietly, which is what the index exists to stop.
        lines.append(f"  {len(change.withdrawn)} list(s) the site no longer publishes")
    return lines


def _fallout_lines(rows: list[dict], today: str | None = None) -> list[str]:
    """Every list a rule turned away though it holds the deck's core, as counts.

    Per deck and per reason, the reason being the engine's name or the colour
    or floor rule, with the last fortnight's share beside the total: a deck
    adopting another deck's engine card is a count growing here week on week,
    where its own report would only show a decline.
    """
    if not rows:
        return ["  no list holding a deck's core was turned away"]
    today = today or date.today().isoformat()
    since = (date.fromisoformat(today) - timedelta(days=config.TRACK_BIN_DAYS)).isoformat()
    recent = [row for row in rows if row["date"] >= since]
    lines = [
        f"  {len({row['list_id'] for row in rows})} list(s) holding a deck's core and turned away,"
        f" {len({row['list_id'] for row in recent})} in the last {config.TRACK_BIN_DAYS} days"
    ]
    total = Counter((row["archetype"], row["reason"]) for row in rows)
    fresh = Counter((row["archetype"], row["reason"]) for row in recent)
    for key, count in sorted(total.items()):
        lines.append(f"  {key[0]}: {key[1]} {count} ({fresh[key]} recent)")
    return lines


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="tracker", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("refresh", help="cache published events and rebuild the store")
    fetch.add_argument("--since", default=config.HISTORY_START, help="YYYY-MM-DD")
    fetch.add_argument("--until", help="YYYY-MM-DD, defaults to today")


    tracked = commands.add_parser("weekly", help="freeze and render a tracked deck's weekly report")
    tracked.add_argument("--deck", default="blink", choices=sorted(config.REPORTS))
    tracked.add_argument("--week", help="the Monday keying the week to report, defaults to the last full week")

    stage = commands.add_parser("site", help="stage the Space: an index over the latest report per deck")
    stage.add_argument("--out", type=Path, default=config.SITE_DIR)

    spot = commands.add_parser("event-fetch", help="cache a major paper event's standings and lists")
    spot.add_argument("--id", type=int, help="melee tournament id, defaults to every one configured")

    args = parser.parse_args(argv)
    if args.command == "event-fetch":
        wanted = [s for s in config.MAJOR_EVENTS if args.id in (None, s["id"])]
        if not wanted:
            print(f"{args.id} is not a configured event; add it to config.MAJOR_EVENTS")
            return
        config.MELEE_DIR.mkdir(parents=True, exist_ok=True)
        for entry in wanted:
            path = spotlight.cached(entry)
            # Kept once fetched. A field of nine hundred is nine hundred requests
            # to someone else's server, and a played-out event does not change.
            known = (
                {row["decklist_id"]: row for row in spotlight.load(entry)["lists"]}
                if path.exists()
                else {}
            )
            print(f"{entry['label']} ({entry['id']}): {len(known)} list(s) already cached")
            payload = melee.tournament(entry["id"], known, entry.get("format"))
            path.write_text(json.dumps(payload), encoding="utf-8")
            meta = payload["tournament"]
            print(f"  {meta['name']}")
            print(f"  {meta['players']} players, {len(payload['lists'])} lists, "
                  f"read at {meta['round']} -> {path}")
        return

    if args.command == "weekly":
        report = config.REPORTS[args.deck]
        week = args.week or weekly.last_complete_week()
        added = weekly.freeze(deck=args.deck, through=week)
        reading = weekly.facts(deck=args.deck, week=week)
        if "error" in reading:
            print(f"{week}: {reading['error']}")
            return
        print(f"{report['name']}, week ending {weekly.week_label(week)}")
        print(f"  froze {added['weeks_added']} week(s), {added['timeline_added']} timeline row(s)")
        challenge, conversion = reading["challenge"], reading["conversion"]
        print(f"  {challenge['lists']} finish(es) in swiss-like tournaments, "
              f"{challenge['share']:.1%} of top 32"
              f"{', VOLUME ELEVATED' if challenge['spiking'] else ''}")
        print(f"  {conversion['top8']} top 8 ({conversion['top8_share']:.1%} of the band), "
              f"{conversion['top16']} top 16")
        print(f"  {reading['leagues']['trophies']} trophy(ies)")
        observed = ", ".join(
            f"{name} {seen['lists']}" for name, seen in reading["versions"].items()
        )
        print(f"  versions observed: {observed}")
        print(f"  numbers at {weekly.write_facts(reading, args.deck)}")
        print(f"  report at {weekly.render(deck=args.deck, week=week)}")
        summary = weekly.deck_dir(args.deck) / "summary" / f"{week}.md"
        if not summary.exists():
            print(f"  NO SUMMARY: write {summary} and re-run to render it in")
        return

    if args.command == "site":
        week = site.build(args.out)
        print(f"week ending {weekly.week_label(week)}, staged at {args.out}")
        return

    if args.command == "refresh":
        change = refresh(args.since, args.until)
        print(f"since {args.since}: raw cache in {config.RAW_DIR}, store at {config.DB_PATH}")
        print(f"index at {index.path()}, commit it to keep the run comparable")
        print("\n".join(_ingest_lines(change, arrivals(change.added))))
        print("fall-out, every list holding a tracked deck's core that no rule claimed:")
        print("\n".join(_fallout_lines(fallout())))
        return
