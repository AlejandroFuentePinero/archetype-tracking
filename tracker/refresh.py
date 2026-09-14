"""The refresh entry point: cache a range of days' events, then rebuild the store."""

import json
from datetime import date, timedelta
from pathlib import Path

from . import config, index, mtgo, store


def refresh(
    since: str = config.HISTORY_START,
    until: str | None = None,
    raw_dir: Path = config.RAW_DIR,
    db_path: Path = config.DB_PATH,
    source=mtgo,
    today: str | None = None,
) -> index.Change:
    """Cache every published `config.FORMAT` event from `since` to `until`, then rebuild.

    A settled event on disk is never refetched, so the backfill runs once and
    every later refresh costs the month indexes plus what the site has published
    since. The last `config.UNSETTLED_DAYS` days are the exception: a league dump
    is still gaining 5-0s while its day runs, so those days are fetched again and
    overwritten until they settle. Which days those are is a fact about now, not
    about the range asked for, so a range running past today ends today.

    Settled is a fact about the capture as well as about the calendar, and used
    to be only about the calendar. A run on the day itself catches a league dump
    part filled, and the calendar then moves past it and freezes what it caught:
    2026-08-23 froze at 7 lists and 2026-08-28 at 25, against a median league
    day of 60. So a capture taken inside its own day's unsettled window is
    refetched whatever the calendar says, and a day is skipped only where both
    the day and the capture have settled.

    An event with nothing on disk is a gap, and so is a settled day the site
    will not serve: reaching the fetch at all means the capture on disk was
    taken inside its own window, so that fetch is a repair of a file already
    judged short, and passing over it in silence is how a run reports success
    while leaving 2026-08-28 at 25 lists. An unsettled day the site will not
    serve keeps the capture it already has without a word, because that refetch
    was for what the day may have gained, not because the capture was wrong.

    What the run brought in is read off the index either side of the rebuild,
    and is returned rather than printed: an ingest that cannot say what it
    ingested leaves the question to be answered by hand from a cache that is not
    committed, and the days it is hardest to answer for are exactly the
    overwritten ones. A run that ends on a gap raises instead, so the gap is the
    news; the index still stands and the next run reports across both.
    """
    today = today or date.today().isoformat()
    until = min(until or today, today)
    settled = date.fromisoformat(until) - timedelta(days=config.UNSETTLED_DAYS)
    raw_dir.mkdir(parents=True, exist_ok=True)
    before = index.read(db_path)
    gaps = []
    for slug in source.event_slugs(since, config.FORMAT, until, today):
        path = raw_dir / f"{slug}.json"
        cached = path.exists()
        day = mtgo.slug_day(slug)
        repair = cached and day < settled.isoformat()
        if repair and _captured_late(path, day):
            continue
        try:
            payload = source.fetch_payload(slug)
        except mtgo.Unavailable as gap:
            if not cached:
                gaps.append(str(gap))
            elif repair:
                gaps.append(f"{gap}: the capture on disk was taken inside its own day and is short")
            continue
        # MTGO publishes a challenge's decklists before its standings, so a run
        # inside that window catches the field with no finishes under it. Parsed
        # it reads as a league, there being no `standings` to tell the two
        # apart, and takes the whole build down on the `name` a league carries
        # and a challenge does not; cached and read, it would put a full bracket
        # of lists in the top-32 population with no placement between them. It
        # is data that has not arrived rather than an event nobody won, so it is
        # left uncached and reported like any other gap. Seen once in 628
        # captures, on 2026-09-13, and the same slug served its standings twenty
        # minutes later.
        if "brackets" in payload and "standings" not in payload:
            gaps.append(f"{slug}: published its decklists and not yet its standings")
            continue
        # Filed under the name the payload gives itself, not under the slug the
        # index asked for. The site lists an event under a wrongly dated slug
        # and then corrects the listing, serving the same payload under both, so
        # a cache filed by slug ends up holding one event under two names: 12 of
        # 628 captures, one of them the 2026-09-12 challenge listed as
        # 2026-09-10. `parse_cache` counts such an event once, but it keeps
        # whichever name sorts first, which is the misdated one as often as not
        # and is a fact about the alphabet rather than about the capture. Filed
        # by identity there is one file, and the corrected listing overwrites
        # the capture taken under the wrong date rather than sitting beside it.
        filed = raw_dir / f"{payload['site_name']}.json"
        # The settle gate at the top of the loop asks whether `slug`.json is on
        # disk, and for these 12 it never is, the capture being filed under the
        # corrected name: the gate cannot fire and a day that has finished
        # publishing would be overwritten from the wrong slug on every run. Read
        # a second time here under the day the payload gives itself, the
        # misdated slug carrying a day that is not the event's and would age the
        # capture by the size of the site's own error.
        if filed != path:
            filed_day = mtgo.slug_day(payload["site_name"])
            if (
                filed.exists()
                and filed_day < settled.isoformat()
                and _captured_late(filed, filed_day)
            ):
                continue
        # Landed whole or not at all: a capture half written by a run that died
        # would be a settled file the cache never refetches and never parses.
        partial = filed.with_suffix(".partial")
        partial.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        partial.replace(filed)

    store.build(raw_dir, db_path)
    if gaps:
        raise mtgo.Unavailable(
            f"{len(gaps)} published event(s) the site would not serve; "
            f"everything else is cached, so re-run to pick them up:\n  " + "\n  ".join(gaps)
        )
    # Read back rather than kept from the rebuild, so what the run reports is
    # what the committed file says and not what this process believed it wrote.
    after = index.read(db_path)
    return index.Change(index.difference(after, before), index.difference(before, after))


def _captured_late(path: Path, day: str) -> bool:
    """Whether a cached capture was taken after its day had finished publishing.

    The file's own timestamp, the cache being written by this program and by
    nothing else. A capture taken `config.UNSETTLED_DAYS` after the day it
    covers has seen whatever that day was going to gain; one taken on the day
    has not, and nothing in the calendar can tell the two apart later.
    """
    captured = date.fromtimestamp(path.stat().st_mtime)
    return (captured - date.fromisoformat(day)).days >= config.UNSETTLED_DAYS
