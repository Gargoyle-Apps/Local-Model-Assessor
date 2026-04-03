#!/usr/bin/env bash
set -euo pipefail

# Validates skills-harness consistency:
#   1. Every directory under _skills/ has a matching row in _index.md
#   2. Every row in _index.md has a matching directory under _skills/
#   3. Each SKILL.md has required frontmatter fields
#   4. Each SKILL.md name field matches its directory name
#   5. Rules blocks in all templates match the canonical _rules.md

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(dirname "$HARNESS_DIR")/_skills"
INDEX_FILE="$(dirname "$HARNESS_DIR")/_index.md"
RULES_FILE="$HARNESS_DIR/_rules.md"

errors=0

# Use ((++errors)) not ((errors++)) — with set -e, post-increment returns status 1 when the
# value was 0 and aborts the script. Pre-increment is always non-zero. Requires bash 3+.
err() { echo "ERROR: $1" >&2; ((++errors)) || true; }
warn() { echo "WARN:  $1" >&2; }

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

# --- 1 & 2: Index ↔ directory consistency ---

if [[ ! -f "$INDEX_FILE" ]]; then
  err "_index.md not found at $INDEX_FILE"
else
  index_names=()
  while IFS='|' read -r _ name _rest; do
    name="$(trim "$name")"
    [[ -z "$name" || "$name" == "name" || "$name" == "---"* ]] && continue
    index_names+=("$name")
  done < "$INDEX_FILE"

  for name in "${index_names[@]}"; do
    if [[ ! -d "$SKILLS_DIR/$name" ]]; then
      err "Index lists '$name' but no directory at _skills/$name/"
    fi
    if [[ ! -f "$SKILLS_DIR/$name/SKILL.md" ]]; then
      err "Index lists '$name' but no SKILL.md at _skills/$name/SKILL.md"
    fi
  done

  if [[ -d "$SKILLS_DIR" ]]; then
    for dir in "$SKILLS_DIR"/*/; do
      dir_name="$(basename "$dir")"
      found=false
      for name in "${index_names[@]}"; do
        [[ "$name" == "$dir_name" ]] && found=true && break
      done
      if ! $found; then
        err "Directory _skills/$dir_name/ exists but has no row in _index.md"
      fi
    done
  fi
fi

# --- 3 & 4: Frontmatter validation ---

required_fields=("name" "description" "triggers" "dependencies" "version")

if [[ -d "$SKILLS_DIR" ]]; then
  for skill_file in "$SKILLS_DIR"/*/SKILL.md; do
    [[ ! -f "$skill_file" ]] && continue
    dir_name="$(basename "$(dirname "$skill_file")")"

    in_frontmatter=false
    frontmatter_closed=false
    # Pipe-delimited list of seen keys (bash 3.2–compatible; no associative arrays)
    found_keys="|"
    fm_name=""

    while IFS= read -r line; do
      if [[ "$line" == "---" ]]; then
        if $in_frontmatter; then
          frontmatter_closed=true
          break
        else
          in_frontmatter=true
          continue
        fi
      fi
      if $in_frontmatter; then
        key="$(trim "$(echo "$line" | cut -d: -f1)")"
        for f in "${required_fields[@]}"; do
          if [[ "$key" == "$f" ]]; then
            found_keys="${found_keys}${f}|"
            if [[ "$f" == "name" ]]; then
              fm_name="$(trim "$(echo "$line" | cut -d: -f2-)")"
            fi
          fi
        done
      fi
    done < "$skill_file"

    if ! $frontmatter_closed; then
      err "$dir_name/SKILL.md: no valid YAML frontmatter (missing closing ---)"
      continue
    fi

    for f in "${required_fields[@]}"; do
      if [[ "$found_keys" != *"|${f}|"* ]]; then
        err "$dir_name/SKILL.md: missing required frontmatter field '$f'"
      fi
    done

    if [[ -n "$fm_name" && "$fm_name" != "$dir_name" ]]; then
      err "$dir_name/SKILL.md: frontmatter name '$fm_name' does not match directory name '$dir_name'"
    fi
  done
fi

# --- 5: Rules block sync ---

if [[ -f "$RULES_FILE" ]]; then
  canonical="$(sed -n '/^# Rules$/,$ p' "$RULES_FILE" | tail -n +2)"

  for tmpl in "$HARNESS_DIR"/*_template.md; do
    [[ ! -f "$tmpl" ]] && continue
    tmpl_name="$(basename "$tmpl")"

    tmpl_rules="$(sed -n '/^## Rules$/,/^<!-- END/ { /^<!-- END/d; p; }' "$tmpl" | tail -n +2)"
    if [[ -z "$tmpl_rules" ]]; then
      tmpl_rules="$(sed -n '/^## Rules$/,$ p' "$tmpl" | tail -n +2)"
    fi

    tmpl_rules="$(echo "$tmpl_rules" | sed '/^$/d')"
    canonical_clean="$(echo "$canonical" | sed '/^$/d')"

    if [[ "$tmpl_rules" != "$canonical_clean" ]]; then
      err "$tmpl_name: Rules block differs from _rules.md"
    fi
  done
else
  warn "_rules.md not found; skipping Rules sync check"
fi

# --- Summary ---

echo ""
if (( errors == 0 )); then
  echo "All checks passed."
else
  echo "$errors error(s) found."
  exit 1
fi
