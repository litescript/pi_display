#!/usr/bin/env bash
set -euo pipefail

SHOW_HELP=0
DISPLAY_EPAPER=0
FORCE_DISPLAY=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Pi-only default; harmless on PC unless --epaper is used
WAVESHARE_LIB="${WAVESHARE_LIB:-/home/litescript/e-Paper/RaspberryPi_JetsonNano/python/lib}"

for arg in "$@"; do
  case "$arg" in
    --epaper) DISPLAY_EPAPER=1 ;;
    --force) FORCE_DISPLAY=1 ;;
    --pc) PROJECT_DIR="/home/peter/code/pi_display/eink_dev" ;;
    -h|--help) SHOW_HELP=1 ;;
    *)
      echo "Unknown argument: $arg"
      SHOW_HELP=1
      ;;
  esac
done

VENV_PY="$PROJECT_DIR/.venv/bin/python"
PREVIEW_PATH="$PROJECT_DIR/output/preview.png"
STATE_DIR="$PROJECT_DIR/.state"
HASH_FILE="$STATE_DIR/preview.sha256"

cd "$PROJECT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting run (epaper=$DISPLAY_EPAPER force=$FORCE_DISPLAY)"

if [[ "$SHOW_HELP" -eq 1 ]]; then
  cat <<EOF
Usage:
  ./run.sh
  ./run.sh --epaper
  ./run.sh --epaper --force
  ./run.sh --pc
EOF
  exit 0
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: virtualenv python not found at $VENV_PY"
  exit 1
fi

mkdir -p "$STATE_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rendering preview..."
"$VENV_PY" -m src.renderers.render_preview

if [[ ! -f "$PREVIEW_PATH" ]]; then
  echo "Error: preview image not found at $PREVIEW_PATH"
  exit 1
fi

if [[ "$DISPLAY_EPAPER" -eq 1 ]]; then
  NEW_HASH="$(sha256sum "$PREVIEW_PATH" | awk '{print $1}')"
  OLD_HASH=""

  if [[ -f "$HASH_FILE" ]]; then
    OLD_HASH="$(cat "$HASH_FILE")"
  fi

  if [[ "$FORCE_DISPLAY" -eq 0 && "$NEW_HASH" == "$OLD_HASH" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Preview unchanged; skipping e-paper refresh."
    exit 0
  fi

  sudo -E env \
    PYTHONPATH=".:$WAVESHARE_LIB" \
    GPIOZERO_PIN_FACTORY=lgpio \
    "$VENV_PY" display_preview.py

  echo "$NEW_HASH" > "$HASH_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Display updated."
else
  xdg-open "$PREVIEW_PATH"
fi
