from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image
from waveshare_epd import epd7in3e


PREVIEW_PATH = Path("output/preview.png")


def prepare_image(path: Path, epd: epd7in3e.EPD) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"Preview image not found: {path}")

    image = Image.open(path).convert("RGB")

    if image.size != (epd.width, epd.height):
        image = image.resize((epd.width, epd.height))

    return image


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    epd = epd7in3e.EPD()

    try:
        logging.info("Initializing display")
        epd.init()

        logging.info("Loading preview image")
        image = prepare_image(PREVIEW_PATH, epd)

        logging.info("Sending image to panel")
        epd.display(epd.getbuffer(image))

        logging.info("Putting display to sleep")
        epd.sleep()

    except Exception:
        logging.exception("Display update failed")
        try:
            epd.sleep()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()

