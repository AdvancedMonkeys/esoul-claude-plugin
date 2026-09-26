#!/usr/bin/env bash
# Refresh the bundled skills from the platform repo's MCP skill sources.
#   scripts/sync-skills.sh /path/to/kinetic
# Only skills that work over the HOSTED endpoint (OAuth, no token) belong here.
# PAT/SDK skills (forge-build-from-zero, forge-realtime-apps) are deliberately
# left out: their setup is `pip install` + mint a token, which is the opposite
# of what this plugin promises. So are skills that automate a named third
# party's site (openai-invoices, porkbun): browser-use teaches the general
# method, and a public plugin should not ship per-vendor account automation.
# cloud-browser is folded INTO browser-use — one skill, tools and discipline.
set -euo pipefail
KINETIC="${1:?usage: sync-skills.sh /path/to/kinetic}"
SRC="$KINETIC/scripts/skills/desktop"
DST="$(cd "$(dirname "$0")/.." && pwd)/plugins/esoul/skills"
HOSTED=(memory browser-use forge-app-builder math-explainer-video block-notes slideshow training-monitor research-study)
for s in "${HOSTED[@]}"; do
  [ -f "$SRC/$s/SKILL.md" ] || { echo "missing source: $s" >&2; exit 1; }
  rm -rf "${DST:?}/$s"; mkdir -p "$DST/$s"
  (cd "$SRC/$s" && find . -type f ! -name '*.zip' ! -path '*/__pycache__/*' ! -name '*.pyc' -print0 \
    | xargs -0 -I{} cp --parents {} "$DST/$s/")
  echo "synced $s"
done
cp "$KINETIC/.claude/skills/build-esoul-website/SKILL.md" "$DST/build-esoul-website/SKILL.md" && echo "synced build-esoul-website"
# The hosted endpoint has none of these; a skill naming one fails on first call.
if grep -rnE '`(find_tools|run_tool|tool_help|memory_[a-z]+|spreadsheet_(get|add)_rows)`' "$DST" ; then
  echo "^^ references tools the hosted endpoint does not have" >&2; exit 1
fi
# browser-use must name exactly the cloud browser's real tools — no phantoms,
# nothing undocumented. Read them from the toolkit source, not from memory.
APP="$KINETIC/src/application-interfaces/cloud-browser/app.tsx"
REAL=$(grep -oE '\[`browser_[a-z_]+_\$\{base\}`\]' "$APP" | grep -oE 'browser_[a-z_]+' | sed 's/_$//' | sort -u)
USED=$(cat "$DST"/browser-use/SKILL.md "$DST"/browser-use/reference/*.md | grep -oE '\bbrowser_[a-z_]+[a-z]' | grep -v '^browser_plan_limit$' | sort -u)
PHANTOM=$(comm -13 <(echo "$REAL") <(echo "$USED")); MISSING=$(comm -23 <(echo "$REAL") <(echo "$USED"))
if [ -n "$PHANTOM" ]; then echo "browser-use names tools that do not exist: $PHANTOM" >&2; exit 1; fi
if [ -n "$MISSING" ]; then echo "browser-use never mentions real tools: $MISSING" >&2; exit 1; fi
echo "browser-use: $(echo "$REAL" | wc -l) tools, all real, all documented"
echo "ok"
