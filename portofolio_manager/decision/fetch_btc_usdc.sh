#!/usr/bin/env bash
set -euo pipefail

# Config via env vars (override as needed)
# SYMBOL: Binance symbol, e.g., BTCUSDC or BTCUSDT
# INTERVAL: Binance interval (e.g., 1m, 5m, 15m, 1h, 4h, 1d)
# START: ISO datetime (UTC) "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
# END: ISO datetime (UTC) "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD" (default now)
# OUTPUT_FILE: CSV output path

SYMBOL=${SYMBOL:-BTCUSDC}
INTERVAL=${INTERVAL:-1h}
START=${START:-2019-01-01 00:00:00}
END=${END:-}
OUTPUT_FILE=${OUTPUT_FILE:-data/btc_usdc.csv}

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Dependencies
command -v jq >/dev/null 2>&1 || { echo "Error: jq is required. Install with 'brew install jq' or your package manager." >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "Error: curl is required." >&2; exit 1; }

# macOS `date` supports -j -f for parsing
parse_epoch_ms() {
  local ds="$1"
  # Try full datetime then date-only
  if epoch=$(date -u -j -f "%Y-%m-%d %H:%M:%S" "$ds" +%s 2>/dev/null); then
    :
  elif epoch=$(date -u -j -f "%Y-%m-%d" "$ds" +%s 2>/dev/null); then
    :
  else
    echo "Failed to parse date: $ds" >&2
    exit 1
  fi
  echo $((epoch * 1000))
}

# Map interval → milliseconds
interval_ms_for() {
  case "$1" in
    1m) echo 60000 ;;
    3m) echo 180000 ;;
    5m) echo 300000 ;;
    15m) echo 900000 ;;
    30m) echo 1800000 ;;
    1h) echo 3600000 ;;
    2h) echo 7200000 ;;
    4h) echo 14400000 ;;
    6h) echo 21600000 ;;
    8h) echo 28800000 ;;
    12h) echo 43200000 ;;
    1d) echo 86400000 ;;
    3d) echo 259200000 ;;
    1w) echo 604800000 ;;
    1M) echo 2592000000 ;; # approx 30d
    *) echo "Unsupported INTERVAL: $1" >&2; exit 1 ;;
  esac
}

START_MS=$(parse_epoch_ms "$START")
if [[ -n "$END" ]]; then
  END_MS=$(parse_epoch_ms "$END")
else
  END_MS=$(( $(date -u +%s) * 1000 ))
fi
if (( END_MS <= START_MS )); then
  echo "END must be after START" >&2; exit 1
fi

INTERVAL_MS=$(interval_ms_for "$INTERVAL")

echo "Fetching $SYMBOL $INTERVAL from $START (ms=$START_MS) to ${END:-now} (ms=$END_MS)"

# Header
echo "time,open,high,low,close,volume" > "$OUTPUT_FILE"

BASE_URL="https://api.binance.com/api/v3/klines"
cursor=$START_MS
total=0
req=0

while (( cursor < END_MS )); do
  url="$BASE_URL?symbol=$SYMBOL&interval=$INTERVAL&limit=1000&startTime=$cursor"
  json=$(curl -fsS "$url")
  count=$(echo "$json" | jq 'length')
  if (( count == 0 )); then
    break
  fi

  echo "$json" | jq -r '
    .[] | [
      ((.[0] / 1000) | floor | strftime("%Y-%m-%d %H:%M:%S")),
      .[1], .[2], .[3], .[4], .[5]
    ] | @csv
  ' >> "$OUTPUT_FILE"

  last_open=$(echo "$json" | jq '.[-1][0]')
  cursor=$(( last_open + INTERVAL_MS ))
  total=$(( total + count ))
  req=$(( req + 1 ))
  # Progress line
  echo ".. fetched batch #$req (+$count rows, total=$total), cursor=$(date -u -r $((cursor/1000)) "+%Y-%m-%d %H:%M:%S")" >&2
  # Gentle rate limiting
  sleep 0.25
done

echo "✅ Saved $total rows to $OUTPUT_FILE"