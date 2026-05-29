#!/usr/bin/env bash
# BRAINS Research Skill - bash installer (macOS / Linux / WSL)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
RESEARCH_ROOT="${RESEARCH_ROOT:-}"

echo "BRAINS Research Skill installer"
echo "Repo root:    $REPO_ROOT"
echo "Claude home:  $CLAUDE_HOME"
echo ""

# 1. config.json
if [ ! -f "$REPO_ROOT/config.json" ]; then
    cp "$REPO_ROOT/config.json.example" "$REPO_ROOT/config.json"
    echo "Created config.json from config.json.example."
    if [ -z "$RESEARCH_ROOT" ]; then
        read -r -p "Research root path (Enter to keep default): " RESEARCH_ROOT
    fi
    if [ -n "$RESEARCH_ROOT" ]; then
        python -c "
import json
p = '$REPO_ROOT/config.json'
d = json.load(open(p))
d['research_root'] = '$RESEARCH_ROOT'
json.dump(d, open(p, 'w'), indent=2)
print('research_root set to:', d['research_root'])
"
    fi
else
    echo "config.json already exists - keeping it."
fi

# 2. Validate
ROOT=$(python -c "import json; print(json.load(open('$REPO_ROOT/config.json'))['research_root'])")
if [ ! -d "$ROOT" ]; then
    echo "WARNING: research_root does not exist or is unreachable: $ROOT" >&2
fi

# 3. venv + install
if [ ! -d "$REPO_ROOT/.venv" ]; then
    python -m venv "$REPO_ROOT/.venv"
fi
"$REPO_ROOT/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$REPO_ROOT/.venv/bin/python" -m pip install -e "$REPO_ROOT[dev]"

# 4. Skill bundle
SKILL_DIR="$CLAUDE_HOME/skills/brains-research"
rm -rf "$SKILL_DIR"
mkdir -p "$SKILL_DIR"
rsync -a --exclude '.venv' --exclude '.git' --exclude 'research-data' --exclude 'tests' "$REPO_ROOT/" "$SKILL_DIR/"
echo "Skill installed at: $SKILL_DIR"

# 5. Slash commands (copy every brains-research-*.md from commands/)
mkdir -p "$CLAUDE_HOME/commands"
cp "$REPO_ROOT/commands/"brains-research-*.md "$CLAUDE_HOME/commands/"
echo "Slash commands installed at: $CLAUDE_HOME/commands"

echo ""
echo "Done."
echo "Try: /brains-research-status"
