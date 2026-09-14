"""Network layer: fetch a major paper event's standings and lists into the raw cache.

Melee is the second source of decklist-level data and the only one that is not
MTGO. It is here for one reason: a Spotlight publishes every finisher, where a
challenge publishes its top 32. That difference is the whole value of the source
and also the whole hazard, so the two never share a table (see `spotlight.py`).

Three endpoints do the work. The standings of a round carry the ranking of the
entire field as it stood, with each player's match record and the id of the list
they registered; the pairings of a round carry its matches and who won them; the
decklist page carries the cards. None is a documented API, the first two being
the site's own DataTables plumbing, so all three are pinned here and nowhere
else.

The site names modal double-faced cards `Front // Back` where MTGO names them by
the front face alone. Left alone that is not a missing card, it is a missing
archetype: every Blink list fails membership on Witch Enchanter and the deck
reads as absent from paper entirely. Folding to the front face is therefore part
of fetching, not part of reading.
"""

import html
import re
import time

import requests

from . import config

BASE = "https://melee.gg"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

# The round buttons the tournament page carries, in the order it lists them, and
# the two halves of a decklist page. Scraped rather than requested as JSON
# because the site publishes no endpoint for either.
ROUND_RE = re.compile(r'class="btn btn-gray round-selector" data-id="(\d+)" data-name="([^"]*)"')
CATEGORY_RE = re.compile(
    r'<div class="decklist-category-title">([^<]*)</div>(.*?)'
    r'(?=<div class="decklist-category">|\Z)',
    re.S,
)
RECORD_RE = re.compile(
    r'<span class="decklist-record-quantity">(\d+)</span>\s*'
    r'<a class="decklist-record-name"[^>]*>([^<]*)</a>',
    re.S,
)

# The columns the standings grid asks for. The endpoint is a DataTables source
# and answers an incomplete column spec with a 500, so the list is exact.
COLUMNS = (
    "Rank",
    "Player",
    "Decklists",
    "MatchRecord",
    "GameRecord",
    "Points",
    "OpponentMatchWinPercentage",
    "TeamGameWinPercentage",
    "OpponentGameWinPercentage",
)

# The same, for the pairings grid. A second DataTables source and so a second
# exact spec, and its round id rides in the path where the standings endpoint
# takes it in the body.
MATCH_COLUMNS = ("TableNumber", "PodNumber", "Teams", "Decklists", "ResultString")

PAGE = 500  # standings rows per request
TIMEOUT = 90
ATTEMPTS = 5
BACKOFF = 10  # seconds, lengthening with each attempt
PAUSE = 0.45  # between decklist fetches, this being someone else's server

# One connection across the run rather than one per request. A field is one page
# per registered list, and opened afresh each time each page pays a TCP handshake
# and a TLS handshake before it is even asked for: 0.45s of a measured 2.05s
# page, eleven minutes of RC Baltimore's 1494. Held open they are paid once, and
# a single connection is the gentler thing to hold against someone else's server
# than fifteen hundred handshakes. The User-Agent rides here because it is the
# same on every request; what varies stays at the call.
SESSION = requests.Session()
SESSION.headers["User-Agent"] = UA


class Unavailable(RuntimeError):
    """The site never served a page carrying what was asked for."""


def _request(method: str, path: str, usable, **kwargs) -> requests.Response:
    """The response, retried until `usable` says it carries what was asked for."""
    url = f"{BASE}{path}"
    # Read once and not per attempt. Popped inside the loop it was gone by the
    # second one, so a retried standings request went up without the
    # `X-Requested-With` and `Referer` the endpoint answers on, and the retry
    # that was meant to rescue the call was a differently shaped call.
    headers = kwargs.pop("headers", {})
    for attempt in range(1, ATTEMPTS + 1):
        try:
            response = SESSION.request(method, url, timeout=TIMEOUT, headers=headers, **kwargs)
            response.raise_for_status()
            if usable(response):
                return response
        except (requests.RequestException, ValueError) as dropped:
            if attempt == ATTEMPTS:
                raise Unavailable(f"{url}: {dropped}") from dropped
        if attempt < ATTEMPTS:
            time.sleep(BACKOFF * attempt)
    raise Unavailable(f"{url} served no usable response in {ATTEMPTS} attempts")


def details(tournament: int) -> dict:
    """The event's own metadata: its published name, organiser and start."""
    response = _request(
        "GET",
        f"/Tournament/GetTournamentDetails/{tournament}",
        lambda r: "Name" in r.json(),
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    return response.json()


def _listed(tournament: int) -> list[tuple[str, str]]:
    """The id and name of each round the page lists, in the order it lists them.

    The page carries the round selector twice, once over the standings and once
    over the pairings, so the buttons are deduplicated rather than counted.
    """
    response = _request("GET", f"/Tournament/View/{tournament}", lambda r: ROUND_RE.search(r.text))
    found = list(dict.fromkeys(ROUND_RE.findall(response.text)))
    if not found:
        raise Unavailable(f"tournament {tournament} published no rounds")
    return found


def final_round(tournament: int) -> tuple[str, str, list[tuple[str, str]]]:
    """The last round whose standings the event published, and what it played after.

    The last round and not the last Swiss one: its standings are the final
    ranking of the whole field, the top cut in playoff order and everyone else
    on Swiss tiebreakers. Taken as the page lists them rather than by name,
    since an event that ran no playoff ends on a numbered round.

    Standings and matches are published separately, and an organiser can post
    one without the other. RC Baltimore bulk-published every round through the
    Semifinals in a single second and left the Finals, a round the page marks
    completed and whose match it did serve, with no standings at all. Read at
    the last round listed the fetch is blocked on an empty field; read one round
    back it is the whole event bar the two players still playing. So the walk
    stops at the last round that published a field and hands back what was
    played after it, for `results` to read and `_advance` to fold in.
    """
    played = _listed(tournament)
    for position in range(len(played) - 1, -1, -1):
        round_id, name = played[position]
        if _standings_page(tournament, round_id, 0, length=1)["recordsTotal"]:
            return round_id, name, played[position + 1 :]
        time.sleep(PAUSE)
    raise Unavailable(f"tournament {tournament} has published no standings for any round")


def results(tournament: int, round_id: str) -> list[dict]:
    """Each decided match of one round, as the pairings grid published it.

    The winner is the competitor holding the games, read off the grid rather
    than off the result line, which is prose the site assembles for a reader. A
    match with no result, without two sides, or with the games level is not a
    before and an after, and is left out.
    """
    first = _matches_page(tournament, round_id, 0)
    total, rows = first["recordsTotal"], list(first["data"])
    while len(rows) < total:
        time.sleep(PAUSE)
        rows += _matches_page(tournament, round_id, len(rows))["data"]
    decided = []
    for row in rows:
        sides = row.get("Competitors") or []
        if not row.get("HasResult") or len(sides) != 2:
            continue
        won, lost = sorted(sides, key=lambda side: side["GameWinsAndGameByes"], reverse=True)
        if won["GameWinsAndGameByes"] == lost["GameWinsAndGameByes"]:
            continue
        decided.append({"winner": won["TeamId"], "loser": lost["TeamId"]})
    return decided


def _advance(rows: list[dict], decided: list[dict]) -> None:
    """Fold a played round's results into the standings taken before it.

    A playoff match is two players holding two adjacent ranks, so the round
    moves two things and no more: the winner takes the win and the better of the
    two ranks, the loser takes the loss and the worse. Points are left alone,
    stopping at the end of the Swiss as they do, and so are the tiebreakers and
    the game record, none of which this module keeps.
    """
    by_team = {row["TeamId"]: row for row in rows}
    for match in decided:
        winner, loser = by_team.get(match["winner"]), by_team.get(match["loser"])
        if not winner or not loser:
            continue
        winner["MatchWins"] += 1
        loser["MatchLosses"] += 1
        winner["Rank"], loser["Rank"] = sorted((winner["Rank"], loser["Rank"]))


def _grid(columns: tuple[str, ...], start: int, length: int, **extra: str) -> dict:
    """The form a DataTables source wants, over the columns it is asked for."""
    form = {
        "draw": "1",
        "start": str(start),
        "length": str(length),
        "search[value]": "",
        "search[regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
        **extra,
    }
    for index, column in enumerate(columns):
        form |= {
            f"columns[{index}][data]": column,
            f"columns[{index}][name]": column,
            f"columns[{index}][searchable]": "true",
            f"columns[{index}][orderable]": "true",
            f"columns[{index}][search][value]": "",
            f"columns[{index}][search][regex]": "false",
        }
    return form


def _standings_page(tournament: int, round_id: str, start: int, length: int = PAGE) -> dict:
    response = _request(
        "POST",
        "/Standing/GetRoundStandings",
        lambda r: not r.json().get("Error") and "recordsTotal" in r.json(),
        data=_grid(COLUMNS, start, length, roundId=str(round_id)),
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE}/Tournament/View/{tournament}",
        },
    )
    return response.json()


def _matches_page(tournament: int, round_id: str, start: int, length: int = PAGE) -> dict:
    response = _request(
        "POST",
        f"/Match/GetRoundMatches/{round_id}",
        lambda r: "recordsTotal" in r.json(),
        data=_grid(MATCH_COLUMNS, start, length),
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE}/Tournament/View/{tournament}",
        },
    )
    return response.json()


def rounds(tournament: int) -> list[dict]:
    """Every round the event played, in order, with the format it was played in.

    The round buttons carry no format, so it comes off a single standings row
    per round. One small request each, which is nothing beside a field's worth
    of decklists, and it is the only way to tell a Pro Tour's draft rounds from
    its constructed ones.
    """
    response = _request("GET", f"/Tournament/View/{tournament}", lambda r: ROUND_RE.search(r.text))
    played = []
    for round_id, name in dict.fromkeys(ROUND_RE.findall(response.text)):
        rows = _standings_page(tournament, round_id, 0, length=1)["data"]
        played.append(
            {"id": round_id, "name": name, "format": rows[0]["FormatName"] if rows else None}
        )
        time.sleep(PAUSE)
    if not played:
        raise Unavailable(f"tournament {tournament} published no rounds")
    return played


def _blocks(played: list[dict], fmt: str) -> list[tuple[str | None, str]]:
    """Each unbroken run of rounds in one format, as the round before it and its last.

    A record is published as a running total over the whole event, so a format's
    own record is the difference across the run: the standings at the end of the
    block, less the standings at the round before it started.
    """
    blocks: list[tuple[str | None, str]] = []
    for index, entry in enumerate(played):
        if entry["format"] != fmt:
            continue
        if blocks and index and blocks[-1][1] == played[index - 1]["id"]:
            blocks[-1] = (blocks[-1][0], entry["id"])
        else:
            blocks.append((played[index - 1]["id"] if index else None, entry["id"]))
    return blocks


def _totals(tournament: int, round_id: str) -> dict[int, tuple[int, int, int]]:
    """Each team's running match record as it stood after a round."""
    return {
        row["TeamId"]: (row["MatchWins"], row["MatchLosses"], row["MatchDraws"])
        for row in standings(tournament, round_id)
    }


def format_record(tournament: int, blocks: list[tuple[str | None, str]]) -> dict[int, tuple]:
    """Each team's record over one format's rounds alone, by difference.

    A Pro Tour ranks sixteen rounds of two formats under one record, six of them
    draft. Reported whole, a Modern deck's win rate is most of a limited win rate
    and the column means nothing, so the draft rounds are subtracted off rather
    than dressed up.
    """
    record: dict[int, list[int]] = {}
    for before, last in blocks:
        opening = _totals(tournament, before) if before else {}
        for team, closing in _totals(tournament, last).items():
            was = opening.get(team, (0, 0, 0))
            running = record.setdefault(team, [0, 0, 0])
            for slot in range(3):
                running[slot] += closing[slot] - was[slot]
    return {team: tuple(values) for team, values in record.items()}


def standings(tournament: int, round_id: str) -> list[dict]:
    """Every row of that round's standings, paged until the field is complete.

    A round the site lists but has published no standings for answers with an
    empty set rather than an error, and an empty set pages to completion on the
    first request: nought of nought rows is a complete field by the arithmetic
    below. Left to it the fetch caches an event of no lists and says so in one
    line, which reads as a deck nobody took rather than as data that has not
    arrived, and the cache it overwrites was the good copy. The organiser posts
    the last round's standings some time after the last match is reported, so
    this is a wait and not a failure, and the message says which.
    """
    first = _standings_page(tournament, round_id, 0)
    total, rows = first["recordsTotal"], list(first["data"])
    if not total:
        raise Unavailable(
            f"tournament {tournament} has published no standings for round {round_id} yet"
        )
    while len(rows) < total:
        time.sleep(PAUSE)
        rows += _standings_page(tournament, round_id, len(rows))["data"]
    if len(rows) != total:
        raise Unavailable(f"tournament {tournament}: {len(rows)} of {total} standings rows")
    return rows


def front_face(name: str) -> str:
    """The name MTGO publishes a card under, given the name melee publishes.

    Melee writes a modal double-faced card as `Front // Back`; MTGO writes the
    front face alone. Every reading downstream matches card names literally
    against MTGO's history, so the fold happens here or every comparison across
    the two sources quietly misses.

    A split card is written the same way by melee and is not the same case: MTGO
    publishes both halves under one name, `Wear/Tear`, so folded to its front
    face it becomes `Wear`, a card no MTGO list has ever registered. Every paper
    row for it then reads as the event adopting a card the deck has never
    played, and the fortnight after reads as the deck dropping it again.
    `config.SPLIT_COLOURS` is the history's split cards, so a melee name landing
    on one of its keys keeps both halves and everything else folds.

    The printing aliases apply after it, the same ones and for the same reason
    the MTGO parse applies them: two names for one card split its history down
    the middle wherever they are not merged at the point names become counts.
    """
    full = html.unescape(name).strip()
    joined = full.replace(" // ", "/")
    if joined in config.SPLIT_COLOURS:
        return joined
    face = full.split(" // ")[0].strip()
    return config.CARD_ALIASES.get(face, face)


def boards(markup: str) -> tuple[dict[str, int], dict[str, int]]:
    """A decklist page's mainboard and sideboard, by card name and count.

    The page groups cards under type headings and the sideboard under its own,
    so the split is the heading rather than a count: a list with a companion
    heading would otherwise put it in the mainboard.
    """
    main: dict[str, int] = {}
    side: dict[str, int] = {}
    for title, body in CATEGORY_RE.findall(markup):
        board = side if title.strip().lower().startswith(("sideboard", "companion")) else main
        for quantity, name in RECORD_RE.findall(body):
            card = front_face(name)
            board[card] = board.get(card, 0) + int(quantity)
    return main, side


def decklist(decklist_id: str) -> tuple[dict[str, int], dict[str, int]]:
    """One registered list, as its page publishes it."""
    response = _request(
        "GET", f"/Decklist/View/{decklist_id}", lambda r: "decklist-record-name" in r.text
    )
    return boards(response.text)


def tournament(tournament_id: int, known: dict | None = None, played_in: str | None = None) -> dict:
    """A whole major event: its metadata, its final standings, and every list.

    `known` is a cache of lists already fetched, keyed by decklist id. A field
    of nine hundred is nine hundred requests to someone else's server, so a
    refetch costs nothing it does not have to.

    `played_in` names the constructed format, at an event that played more than
    one. A Pro Tour is three draft pods and ten rounds of Modern under a single
    ranking, and its top 8 is a draft pod too, so the event is read at the end of
    its last Modern round: that is the last standing the Modern deck earned, and
    the playoff reorders the top 8 on limited results alone. The record kept is
    the Modern rounds by themselves, for the reason `format_record` gives.
    """
    known = known or {}
    meta = details(tournament_id)
    record: dict[int, tuple] = {}
    later: list[tuple[str, str]] = []
    if played_in:
        played = rounds(tournament_id)
        constructed = [entry for entry in played if entry["format"] == played_in]
        if not constructed:
            raise Unavailable(f"tournament {tournament_id} published no {played_in} round")
        round_id, round_name = constructed[-1]["id"], constructed[-1]["name"]
        record = format_record(tournament_id, _blocks(played, played_in))
    else:
        round_id, round_name, later = final_round(tournament_id)
    rows = standings(tournament_id, round_id)
    # A round whose standings never arrived but whose matches did. The pairings
    # grid carries the result, so the ranking is advanced by the match rather
    # than left a round short or filled in by hand. Stops at the first round
    # that published nothing, an event being read forward and not in pieces.
    advanced = []
    for later_id, later_name in later:
        decided = results(tournament_id, later_id)
        if not decided:
            break
        _advance(rows, decided)
        advanced.append(later_name)
        time.sleep(PAUSE)
    rows.sort(key=lambda row: row["Rank"])
    lists = []
    for row in rows:
        players = row["Team"]["Players"]
        for entry in row["Decklists"]:
            cached = known.get(entry["DecklistId"])
            if cached:
                main, side = cached["main"], cached["side"]
            else:
                main, side = decklist(entry["DecklistId"])
                time.sleep(PAUSE)
            wins, losses, draws = record.get(
                row["TeamId"], (row["MatchWins"], row["MatchLosses"], row["MatchDraws"])
            )
            lists.append(
                {
                    "decklist_id": entry["DecklistId"],
                    "rank": row["Rank"],
                    "pilot": players[0]["Username"] if players else None,
                    "name": entry["DecklistName"].strip(),
                    "record": f"{wins}-{losses}-{draws}",
                    "wins": wins,
                    "losses": losses,
                    "draws": draws,
                    "points": row["Points"],
                    "main": main,
                    "side": side,
                }
            )
    return {
        "tournament": {
            "id": tournament_id,
            "name": meta.get("Name"),
            "organiser": meta.get("OrganizationName"),
            "start": meta.get("StartDate"),
            "round": round_name,
            # Empty at an event whose last round published its standings, which
            # is every event but the one that did not. Named so the file says
            # what it is: a ranking read at one round and carried forward by the
            # matches of the rounds after it.
            "advanced": advanced,
            "format": played_in,
            "players": len(rows),
        },
        "lists": lists,
    }
