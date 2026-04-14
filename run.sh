#!/usr/bin/env bash
set -euo pipefail

SHOW_HELP=0
DISPLAY_EPAPER=0
FORCE_DISPLAY=0

PROJECT_DIR="/home/litescript/code/pi_display"
VENV_PY="$PROJECT_DIR/.venv/bin/python"
WAVESHARE_LIB="${WAVESHARE_LIB:-/home/litescript/e-Paper/RaspberryPi_JetsonNano/python/lib}"
PREVIEW_PATH="$PROJECT_DIR/output/preview.png"
STATE_DIR="$PROJECT_DIR/.state"
HASH_FILE="$STATE_DIR/preview.sha256"

cd "$PROJECT_DIR"

for arg in "$@"; do
  case "$arg" in
    --epaper) DISPLAY_EPAPER=1 ;;
    --force) FORCE_DISPLAY=1 ;;
    -h|--help) SHOW_HELP=1 ;;
    *)
      echo "Unknown argument: $arg"
      SHOW_HELP=1
      ;;
  esac
done

if [[ "$SHOW_HELP" -eq 1 ]]; then
  cat <<EOF
Usage:
  ./run.sh
  ./run.sh --epaper
  ./run.sh --epaper --force
EOF
  exit 0
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "Error: virtualenv python not found at $VENV_PY"
  exit 1
fi

mkdir -p "$STATE_DIR"

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
    echo "Preview unchanged; skipping e-paper refresh."
    exit 0
  fi

  sudo -E env \
    PYTHONPATH=".:$WAVESHARE_LIB" \
    GPIOZERO_PIN_FACTORY=lgpio \
    "$VENV_PY" display_preview.py

  echo "$NEW_HASH" > "$HASH_FILE"
  echo "Display updated."
else
  xdg-open "$PREVIEW_PATH"
fi
