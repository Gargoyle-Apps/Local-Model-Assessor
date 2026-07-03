#!/usr/bin/env bash
set -euo pipefail

# Regenerates the table rows in _index.md from SKILL.md frontmatter.
# Dry-run by default (prints drift, exits non-zero); --write performs edits.
#
# Usage: .skills/_harness/build-index.sh [--write]

HARNESS_DIR="${SKILLS_HARNESS_DIR:-$(cd "$(dirname "$0")" && pwd)}"
SKILLS_DIR="${SKILLS_DIR:-$(dirname "$HARNESS_DIR")/_skills}"
INDEX_FILE="${SKILLS_INDEX:-$(dirname "$HARNESS_DIR")/_index.md}"

WRITE=false
for arg in "$@"; do
  case "$arg" in
    --write) WRITE=true ;;
  esac
done

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

strip_quotes() {
  local v="$1"
  v="${v#\"}"
  v="${v%\"}"
  printf '%s' "$v"
}

strip_trailing_newlines() {
  local s="$1"
  while [[ "$s" == *$'\n' ]]; do
    s="${s%$'\n'}"
  done
  printf '%s' "$s"
}

escape_table_cell() {
  local v="$1"
  v="${v//$'\n'/ }"
  v="${v//|/\\|}"
  printf '%s' "$v"
}

parse_triggers_inline() {
  local val="$1"
  local inner item result="" rest
  inner="${val#\[}"
  inner="${inner%\]}"
  rest="$inner"
  while [[ -n "$rest" ]]; do
    if [[ "$rest" == *,* ]]; then
      item="${rest%%,*}"
      rest="${rest#*,}"
    else
      item="$rest"
      rest=""
    fi
    item="$(strip_quotes "$(trim "$item")")"
    [[ -z "$item" ]] && continue
    if [[ -n "$result" ]]; then
      result="$result, $item"
    else
      result="$item"
    fi
  done
  printf '%s' "$result"
}

parse_triggers_block_lines() {
  local result="" line tline item
  while [[ $# -gt 0 ]]; do
    line="$1"
    shift
    tline="$(trim "$line")"
    [[ "$tline" != -* ]] && break
    item="${tline#- }"
    item="$(strip_quotes "$(trim "$item")")"
    if [[ -n "$result" ]]; then
      result="$result, $item"
    else
      result="$item"
    fi
  done
  printf '%s' "$result"
}

parse_skill_frontmatter() {
  local skill_file="$1"
  fm_name="" fm_desc="" fm_triggers=""
  local in_fm=false
  local -a fm_lines=()

  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "---" ]]; then
      if $in_fm; then break
      else in_fm=true; continue
      fi
    fi
    if $in_fm; then
      fm_lines+=("$line")
    fi
  done < "$skill_file"

  local idx=0 line key val tline item
  while (( idx < ${#fm_lines[@]} )); do
    line="${fm_lines[idx]}"
    key="${line%%:*}"
    key="$(trim "$key")"
    val="${line#*:}"
    val="$(strip_quotes "$(trim "$val")")"

    case "$key" in
      name) fm_name="$val" ;;
      description) fm_desc="$val" ;;
      triggers)
        if [[ "$val" =~ ^\[.*\]$ ]]; then
          fm_triggers="$(parse_triggers_inline "$val")"
        elif [[ -z "$val" ]]; then
          local -a trigger_lines=()
          ((idx++)) || true
          while (( idx < ${#fm_lines[@]} )); do
            tline="$(trim "${fm_lines[idx]}")"
            [[ "$tline" != -* ]] && { idx=$((idx - 1)); break; }
            trigger_lines+=("${fm_lines[idx]}")
            ((idx++)) || true
          done
          if ((${#trigger_lines[@]} > 0)); then
            fm_triggers="$(parse_triggers_block_lines "${trigger_lines[@]}")"
          fi
        fi
        ;;
    esac
    idx=$((idx + 1))
  done
}

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "ERROR: _skills directory not found at $SKILLS_DIR" >&2
  exit 1
fi

if [[ ! -f "$INDEX_FILE" ]]; then
  echo "ERROR: _index.md not found at $INDEX_FILE" >&2
  exit 1
fi

# --- Read frontmatter from every SKILL.md ---

rows=""
for skill_dir in "$SKILLS_DIR"/*/; do
  [[ ! -d "$skill_dir" ]] && continue
  skill_file="$skill_dir/SKILL.md"
  [[ ! -f "$skill_file" ]] && continue

  parse_skill_frontmatter "$skill_file"

  if [[ -n "$fm_name" ]]; then
    rows="${rows}| $(escape_table_cell "$fm_name") | $(escape_table_cell "$fm_desc") | $(escape_table_cell "$fm_triggers") |
"
  fi
done

# --- Reconstruct the index preserving intro and trailing prose ---

table_header_line="$(grep -n '^| name ' "$INDEX_FILE" 2>/dev/null | head -1 | cut -d: -f1 || true)"
if [[ -z "$table_header_line" ]]; then
  echo "ERROR: no table header (| name ...) found in $INDEX_FILE" >&2
  exit 1
fi

intro="$(head -n $((table_header_line - 1)) "$INDEX_FILE" && printf x)"
intro="${intro%x}"

after_table_start="$(awk -v hdr="$table_header_line" 'NR>hdr && $0 !~ /^\|/ {print NR; exit}' "$INDEX_FILE")"

trailing=""
if [[ -n "$after_table_start" ]]; then
  trailing="$(tail -n +$after_table_start "$INDEX_FILE")"
fi

new_index="${intro}| name | description | triggers |
|------|-------------|----------|
${rows}${trailing}"

current="$(cat "$INDEX_FILE")"

if [[ "$(strip_trailing_newlines "$new_index")" == "$(strip_trailing_newlines "$current")" ]]; then
  echo "Index is in sync with skill frontmatter."
  exit 0
fi

if $WRITE; then
  printf '%s\n' "$(strip_trailing_newlines "$new_index")" > "$INDEX_FILE"
  echo "Updated _index.md."
else
  echo "Index drifted from skill frontmatter. Run with --write to fix."
  exit 1
fi
