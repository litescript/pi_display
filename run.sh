#!/usr/bin/env bash
set -euo pipefail

SHOW_HELP=0
DISPLAY_EPAPER=0
FORCE_DISPLAY=0

WAVESHARE_LIB="${WAVESHARE_LIB:-/home/litescript/e-Paper/RaspberryPi_JetsonNano/python/lib}"
PREVIEW_PATH="output/preview.png"
STATE_DIR=".state"
HASH_FILE="$STATE_DIR/preview.sha256"

for arg in "$@"; do
  case "$arg" in
    --epaper)
      DISPLAY_EPAPER=1
      ;;
    --force)
      FORCE_DISPLAY=1
      ;;
    -h|--help)
      SHOW_HELP=1
      ;;
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
      Render preview and open it locally

  ./run.sh --epaper
      Render preview and push it to the Waveshare display only if the image changed

  ./run.sh --epaper --force
      Render preview and force a display refresh even if the image is unchanged

Environment:
  WAVESHARE_LIB
      Path to Waveshare python/lib directory
      Current: $WAVESHARE_LIB
EOF
  exit 0
fi

mkdir -p "$STATE_DIR"

source .venv/bin/activate

python -m src.renderers.render_preview

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
    .venv/bin/python display_preview.py

  echo "$NEW_HASH" > "$HASH_FILE"
  echo "Display updated."
else
  xdg-open "$PREVIEW_PATH"
fi
