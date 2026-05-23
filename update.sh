#!/usr/bin/env bash
# update.sh — regenerate this academic homepage from ARIS-in-AI-Offer sources
#             and deploy to 63986182.xyz via GitHub Pages.
#
# Sources of truth (edit these, then run this script):
#   $ARIS_DIR/site/profile.yml
#   $ARIS_DIR/site/bio.md
#   $ARIS_DIR/site/news.md
#   $ARIS_DIR/site/publications.bib
#
# Usage:
#   ./update.sh                      # default commit message: "update homepage (YYYY-MM-DD)"
#   ./update.sh "add NeurIPS paper"  # custom commit message
#
# Env overrides:
#   ARIS_DIR=/path/to/ARIS-in-AI-Offer  (default: ~/projects/ARIS-in-AI-Offer)

set -euo pipefail

ARIS_DIR="${ARIS_DIR:-$HOME/projects/ARIS-in-AI-Offer}"
SITE_DIR="$ARIS_DIR/site"
HOMEPAGE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Pre-flight
[[ -d "$SITE_DIR" ]]             || { echo "FATAL: $SITE_DIR missing (set ARIS_DIR=...)" >&2; exit 1; }
[[ -f "$SITE_DIR/profile.yml" ]] || { echo "FATAL: $SITE_DIR/profile.yml missing — run 'aris-homepage init' first" >&2; exit 1; }
command -v gh >/dev/null         || { echo "FATAL: gh CLI not on PATH" >&2; exit 1; }

# Render (runs DBLP fact-check)
echo "→ rendering from $SITE_DIR ..."
( cd "$SITE_DIR" && python3 "$ARIS_DIR/tools/aris_homepage.py" render --persona theory-minimal )

# Sync into deploy repo
cp "$SITE_DIR/index.html" "$HOMEPAGE_DIR/index.html"

cd "$HOMEPAGE_DIR"

# Early-exit if unchanged
if git diff --quiet index.html; then
  echo "✓ index.html unchanged — nothing to deploy"
  exit 0
fi

# Commit + push
MSG="${1:-update homepage ($(date +%Y-%m-%d))}"
git add index.html
git commit -m "$MSG"
git push

# Wait for Pages build
echo "→ waiting for GitHub Pages build ..."
until [[ "$(gh api repos/Yafei-Liu99/Yafei-Liu99.github.io/pages --jq '.status' 2>/dev/null)" == "built" ]]; do
  sleep 4
done

echo "✓ live: https://63986182.xyz/"
