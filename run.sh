#!/usr/bin/env bash
source .venv/bin/activate
python src/renderers/render_preview.py
xdg-open output/preview.png
