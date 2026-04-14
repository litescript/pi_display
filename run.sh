#!/usr/bin/env bash
set -euo pipefail

SHOW_HELP=0
DISPLAY_EPAPER=0

for arg in "$@"; do
  case "$arg" in
    --epaper)
      DISPLAY_EPAPER=1
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
  cat <<'EOF'
Usage:
  ./run.sh            Render preview and open it locally
  ./run.sh --epaper   Render preview and push it to the Waveshare display
EOF
  exit 0
fi

source .venv/bin/activate

python -m src.renderers.render_preview

if [[ "$DISPLAY_EPAPER" -eq 1 ]]; then
  sudo -E env PYTHONPATH=. GPIOZERO_PIN_FACTORY=lgpio .venv/bin/python display_preview.py
else
  xdg-open output/preview.png
fi
