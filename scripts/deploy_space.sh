#!/bin/sh
# Deploy the current week's reports to a protected Hugging Face Space.
#
# Usage: scripts/deploy_space.sh <user>/<space>
#
# `tracker site` stages the index and one report per deck, and refuses a report
# with no summary or reports that disagree on the week. The Space is created
# protected on first use and its visibility is checked before every upload,
# because `hf upload` would otherwise create a public one at the Hub's default.
# Protected hides the repository and leaves the running app open to anyone with
# the URL, which is the whole intent: readers get the pages, nobody gets the tree.
set -eu

SPACE="${1:?usage: scripts/deploy_space.sh <user>/<space>}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

uv run tracker site
WEEK=$(grep -o 'week ending [0-9-]*' site/index.html | head -1)

hf repos create "$SPACE" --type space --space-sdk static --protected --exist-ok >/dev/null

# Protected and private both answer `private: true`; anything else is public,
# and a public Space offers its files tab to the world.
if ! hf spaces info "$SPACE" --format json | grep -q '"private": *true'; then
    echo "Refusing to deploy: $SPACE is public. Set it to protected under Settings." >&2
    exit 1
fi

hf upload "$SPACE" site . --type space --delete "*" --commit-message "Deploy reports, $WEEK"
echo "Deployed $WEEK to https://huggingface.co/spaces/$SPACE"
