#!/usr/bin/env bash
# Refresh the bundled skills from the platform repo's MCP skill sources.
#   scripts/sync-skills.sh /path/to/kinetic
# Only skills that work over the HOSTED endpoint (OAuth, no token) belong here.
# PAT/SDK skills (forge-build-from-zero, forge-realtime-apps) are deliberately
# left out: their setup is `pip install` + mint a token, which is the opposite
# of what this plugin promises.
set -euo pipefail
KINETIC="${1:?usage: sync-skills.sh /path/to/kinetic}"
SRC="$KINETIC/scripts/skills/desktop"
DST="$(cd "$(dirname "$0")/.." && pwd)/plugins/esoul/skills"
HOSTED=(browser-use cloud-browser forge-app-builder math-explainer-video openai-invoices porkbun)
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
echo "ok"
