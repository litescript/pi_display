#!/usr/bin/env bash
source .venv/bin/activate
python -m src.renderers.render_preview
xdg-open output/preview.png
