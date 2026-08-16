#!/usr/bin/env bash
# validate-toon.sh — strict-decode + TOON mistake heuristics
# Usage: validate-toon.sh <file.toon>
# Exit 0 = pass; 1 = fail

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "usage: validate-toon.sh <file.toon>" >&2
  exit 1
fi

fail=0

say() { printf '%s\n' "$*"; }
err() { printf 'FAIL: %s\n' "$*" >&2; fail=1; }

# --- Gate 1: comments ---
line_no=0
while IFS= read -r line || [[ -n "$line" ]]; do
  line_no=$((line_no + 1))
  [[ -z "${line// /}" ]] && continue
  if [[ "$line" =~ ^[[:space:]]*# ]]; then
    err "line $line_no: # comment not allowed in .toon files (CLI rejects)"
  fi
done < "$FILE"

first="$(grep -v '^[[:space:]]*$' "$FILE" | head -1 || true)"
if [[ -z "$first" ]]; then
  err "file is empty"
elif [[ ! "$first" =~ ^[A-Za-z0-9_\"\[] ]]; then
  err "first content line does not look like TOON (got: ${first:0:60})"
fi

if grep -q $'\xe2\x80\x94' "$FILE" || grep -q '—' "$FILE"; then
  err "contains em dash placeholder — use null for missing values"
fi

# Multiline primitive array: header key[N]: with nothing after colon, next line indented
prev=""
line_no=0
while IFS= read -r line || [[ -n "$line" ]]; do
  line_no=$((line_no + 1))
  if [[ "$prev" =~ ^([A-Za-z0-9_]+)\[([0-9]+)\]:[[:space:]]*$ ]]; then
    key="${BASH_REMATCH[1]}"
    if [[ "$line" =~ ^[[:space:]]{2,}[^[:space:]-] ]]; then
      err "line $line_no: primitive array '${key}' looks multiline — use inline key[N]: a,b,c"
    fi
  fi
  prev="$line"
done < "$FILE"

# Tabular [N] vs row count
line_no=0
expect_rows=0
rows_seen=0
in_table=0
header_key=""
flush_table() {
  if [[ $in_table -eq 1 && $rows_seen -ne $expect_rows ]]; then
    err "tabular '${header_key}': declared ${expect_rows} rows but saw ${rows_seen}"
  fi
  in_table=0
}
while IFS= read -r line || [[ -n "$line" ]]; do
  line_no=$((line_no + 1))
  if [[ "$line" =~ ^([A-Za-z0-9_]+)\[([0-9]+)\]\{[^}]+\}:[[:space:]]*$ ]]; then
    flush_table
    header_key="${BASH_REMATCH[1]}"
    expect_rows="${BASH_REMATCH[2]}"
    rows_seen=0
    in_table=1
    continue
  fi
  if [[ $in_table -eq 1 ]]; then
    if [[ "$line" =~ ^[[:space:]]{2,}[^[:space:]] ]]; then
      rows_seen=$((rows_seen + 1))
    else
      flush_table
    fi
  fi
done < "$FILE"
flush_table

# --- Strict decode (authoritative) ---
say "strict-decode: $FILE"
set +e
pnpm dlx @toon-format/cli -d --strict "$FILE" >/dev/null
decode_ec=$?
set -e
if [[ $decode_ec -ne 0 ]]; then
  err "pnpm dlx @toon-format/cli -d --strict failed (exit $decode_ec)"
fi

if [[ $fail -ne 0 ]]; then
  say "validate-toon: FAILED ($FILE)"
  exit 1
fi
say "validate-toon: OK ($FILE)"
exit 0
