"""The Space: a menu over the current week's reports, staged as static files.

The Space holds one report per tracked deck under a stable name and an index
that lists them. Nothing else goes up: no data, no code, because the reports
are self-contained HTML and the Space's whole job is to hand them out.
"""

import shutil
from pathlib import Path

from . import config
from .weekly import _STYLE, week_label

CONTACT_NAME = "Alejandro de la Fuente"
CONTACT_EMAIL = "alejandrofuentepinero@gmail.com"
CONTACT_DISCORD = "alejandrofp92"

DEK = "Weekly reports on Modern archetypes: MTGO presence, conversion and build, with paper events in the storyline."

# The line the renderer writes where no summary exists. A report on it is a
# report with its headline missing, and the deploy refuses it rather than
# publishing a page that says so at the top.
PENDING = 'class="pending"'

_INDEX_STYLE = """
.page { max-width: 940px; }
header { border: 0; padding: 0; margin: 0 0 32px; }
h1 { font-size: 30px; color: var(--ink); }
.dek { font-size: 14px; max-width: 560px; margin-top: 8px; line-height: 1.5; }
.week { color: var(--ink-2); font-size: 13px; margin: 14px 0 0; }
.decks { list-style: none; margin: 0; padding: 0; display: grid; gap: 18px;
         grid-template-columns: repeat(2, 1fr); }
.decks a { display: flex; align-items: center; justify-content: center; min-height: 140px;
           background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
           padding: 24px; color: var(--ink); text-decoration: none; text-align: center;
           font-size: 21px; font-weight: 600; letter-spacing: -0.01em;
           transition: transform 120ms ease, border-color 120ms ease, color 120ms ease; }
.decks a:hover { transform: translateY(-2px); border-color: var(--accent);
                 color: color-mix(in srgb, var(--accent) 80%, var(--ink)); }
@media (max-width: 520px) { .decks { grid-template-columns: 1fr; } }
footer { color: var(--ink-3); font-size: 13px; margin-top: 56px; padding-top: 18px;
         border-top: 1px solid var(--line); }
footer a { color: inherit; }
"""


def latest_reports(reports: Path = config.REPORT_DIR) -> dict[str, Path]:
    """The newest rendered report per tracked deck, keyed by deck."""
    found = {}
    for deck in config.REPORTS:
        rendered = sorted(reports.glob(f"{deck}-????-??-??.html"))
        if not rendered:
            raise SystemExit(f"no rendered report for {deck} under {reports}")
        found[deck] = rendered[-1]
    return found


def build(out: Path = config.SITE_DIR, reports: Path = config.REPORT_DIR) -> str:
    """Stage the index and one report per deck under `out`; returns the week.

    Refuses a report still on the pending line and refuses reports that
    disagree on the week, because the index promises one week for all of them.
    """
    latest = latest_reports(reports)
    weeks = {path.stem.removeprefix(f"{deck}-") for deck, path in latest.items()}
    if len(weeks) != 1:
        raise SystemExit(f"reports disagree on the week: {', '.join(sorted(weeks))}")
    week = weeks.pop()
    for deck, path in latest.items():
        if PENDING in path.read_text(encoding="utf-8"):
            raise SystemExit(f"{deck} has no summary for {week}: write it and re-render")

    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    for deck, path in latest.items():
        shutil.copyfile(path, out / f"{deck}.html")
    (out / "index.html").write_text(index(week), encoding="utf-8")
    shutil.copyfile(config.REPO_ROOT / "deploy" / "README.md", out / "README.md")
    return week


def index(week: str) -> str:
    decks = sorted(config.REPORTS.items(), key=lambda item: item[1]["name"])
    cards = "\n".join(
        f'  <li><a href="{deck}.html">{report["name"]}</a></li>' for deck, report in decks
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{config.SITE_TITLE}</title><style>{_STYLE}{_INDEX_STYLE}</style></head>"
        f"""<body><div class="page">
<header>
  <h1>{config.SITE_TITLE}</h1>
  <p class="dek">{DEK}</p>
  <p class="week">Reports for the week ending {week_label(week)}</p>
</header>
<ul class="decks">
{cards}
</ul>
<footer>{CONTACT_NAME} &middot; <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> &middot; Discord {CONTACT_DISCORD}</footer>
</div></body></html>"""
    )
