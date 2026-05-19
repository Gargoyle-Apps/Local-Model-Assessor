#!/usr/bin/env bash
set -euo pipefail

# Validates skills-harness consistency:
#   1. Every directory under _skills/ has a matching row in _index.md
#   2. Every row in _index.md has a matching directory under _skills/
#   3. Each SKILL.md has required frontmatter fields
#   4. Each SKILL.md name field matches its directory name
#   5. Rules blocks in all templates match the canonical _rules.md
#   6. Symlinks in .agents/skills/ and .claude/skills/ are valid (if present)
#   7. kit_version in _meta.yml matches newest CHANGELOG release, README, and AGENTS_skills.md

QUIET=false
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=true ;;
  esac
done

# Resolve the script's own location WITHOUT following symlinks, so subtree-vendored
# installs (where .skills/_harness/ is a symlink into .skills-harness/.skills/_harness/)
# still derive the consumer's _skills/_index.md/repo root rather than the subtree's.
# See gh issue #3, friction point 5.
script_src="${BASH_SOURCE[0]:-$0}"
script_dir="$(dirname "$script_src")"
HARNESS_DIR="${SKILLS_HARNESS_DIR:-$(cd "$script_dir" && pwd -L)}"
SKILLS_DIR="${SKILLS_DIR:-$(dirname "$HARNESS_DIR")/_skills}"
INDEX_FILE="${SKILLS_INDEX:-$(dirname "$HARNESS_DIR")/_index.md}"
RULES_FILE="${SKILLS_RULES:-$HARNESS_DIR/_rules.md}"
REPO_ROOT="${SKILLS_REPO_ROOT:-$(dirname "$(dirname "$HARNESS_DIR")")}"

# Auto-detect consumer-vs-kit role for the kit-surface checks (CHANGELOG/README/AGENTS_skills.md
# version assertions). These only make sense in the upstream kit repo; consumers shouldn't
# need to mirror them. Detection signals:
#   - .skills-harness/ subtree directory at REPO_ROOT (subtree-vendored install), OR
#   - role: consumer in .skills/_meta.yml
# The SKILLS_CHECK_KIT_SURFACES env var still wins if set explicitly (0/1).
if [[ -z "${SKILLS_CHECK_KIT_SURFACES:-}" ]]; then
  SKILLS_CHECK_KIT_SURFACES=1
  if [[ -d "$REPO_ROOT/.skills-harness" ]]; then
    SKILLS_CHECK_KIT_SURFACES=0
  else
    META_FILE_AUTO="$(dirname "$HARNESS_DIR")/_meta.yml"
    if [[ -f "$META_FILE_AUTO" ]] && grep -qE '^role:[[:space:]]*consumer[[:space:]]*$' "$META_FILE_AUTO"; then
      SKILLS_CHECK_KIT_SURFACES=0
    fi
  fi
fi

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
      # Guard: bash has no nullglob by default, so an empty dir leaves '*/' literal.
      [[ -d "$dir" ]] || continue
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

# --- 6: Symlink validation (optional) ---

for symdir in ".agents/skills" ".claude/skills"; do
  symdir_abs="$REPO_ROOT/$symdir"
  [[ ! -d "$symdir_abs" ]] && continue

  for link in "$symdir_abs"/*/; do
    # Guard: skip unexpanded glob when directory is empty (bash has no nullglob by default)
    [[ ! -e "${link%/}" && ! -L "${link%/}" ]] && continue
    name="$(basename "${link%/}")"

    if [[ ! -L "${link%/}" ]]; then
      warn "$symdir/$name is not a symlink"
      continue
    fi

    if [[ ! -d "${link%/}" ]]; then
      err "$symdir/$name is a broken symlink (target: $(readlink "${link%/}"))"
      continue
    fi

    if [[ ! -f "${link%/}/SKILL.md" ]]; then
      warn "$symdir/$name symlink target has no SKILL.md"
    fi
  done
done

# --- 7: Kit version surfaces (_meta.yml, CHANGELOG, README, AGENTS_skills.md) ---

META_FILE="$(dirname "$HARNESS_DIR")/_meta.yml"
CHANGELOG_FILE="$REPO_ROOT/CHANGELOG.md"
README_FILE="$REPO_ROOT/README.md"
BOOTSTRAP_FILE="$REPO_ROOT/AGENTS_skills.md"

if [[ -f "$META_FILE" ]]; then
  meta_line="$(grep -E '^kit_version:' "$META_FILE" | head -1 || true)"
  meta_ver="${meta_line#kit_version:}"
  meta_ver="$(trim "$meta_ver")"
  meta_ver="${meta_ver#\"}"
  meta_ver="${meta_ver%\"}"

  if [[ -z "$meta_ver" ]]; then
    err "_meta.yml: could not parse kit_version"
  else
    # All three kit-version surface checks (CHANGELOG, README, AGENTS_skills.md)
    # only make sense in the upstream kit repo. Consumers auto-skip via the
    # SKILLS_CHECK_KIT_SURFACES detection at the top of this script. See gh
    # issue #3, friction point 6.
    if [[ "${SKILLS_CHECK_KIT_SURFACES:-1}" == "1" ]]; then
      if [[ -f "$CHANGELOG_FILE" ]]; then
        cl_line="$(grep -E '^## \[[0-9]' "$CHANGELOG_FILE" | head -1 || true)"
        if [[ -z "$cl_line" ]]; then
          err "CHANGELOG.md: no release heading like ## [x.y.z] found after intro"
        else
          cl_ver="$(echo "$cl_line" | sed -E 's/^## \[([^]]+)\].*/\1/')"
          if [[ "$cl_ver" != "$meta_ver" ]]; then
            err "CHANGELOG first release [$cl_ver] does not match _meta.yml kit_version ($meta_ver)"
          fi
        fi
      else
        err "CHANGELOG.md not found at $CHANGELOG_FILE (required for kit version check)"
      fi

      if [[ -f "$README_FILE" ]]; then
        if ! grep -Fq "**Current release:** \`${meta_ver}\`" "$README_FILE"; then
          err "README.md: expected **Current release:** \`${meta_ver}\` to match .skills/_meta.yml"
        fi
      else
        err "README.md not found at $README_FILE (required for kit version check)"
      fi

      if [[ -f "$BOOTSTRAP_FILE" ]]; then
        if ! grep -Fq "**Kit version:** \`${meta_ver}\`" "$BOOTSTRAP_FILE"; then
          err "AGENTS_skills.md: expected **Kit version:** \`${meta_ver}\` to match .skills/_meta.yml"
        fi
      else
        err "AGENTS_skills.md not found at $BOOTSTRAP_FILE (required for kit version check)"
      fi
    fi
  fi
else
  warn ".skills/_meta.yml not found; skipping kit version surface check"
fi

# --- Summary ---

echo ""
if (( errors == 0 )); then
  $QUIET || echo "All checks passed."
else
  echo "$errors error(s) found."
  exit 1
fi
