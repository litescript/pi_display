from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


WIDTH = 800
HEIGHT = 480

BG = "white"
FG = "black"
GRID = (185, 185, 185)

MARGIN = 24
CONTENT_LEFT = MARGIN
CONTENT_RIGHT = WIDTH - MARGIN

TOP_RAIL_H = 40

HERO_TOP = 72
HERO_HEIGHT = 142

TODAY_TOP = 272
TODAY_HEIGHT = 62

FORECAST_TOP = 356
FORECAST_HEIGHT = 62

SYSTEM_TOP = 438
SYSTEM_HEIGHT = 24

SAIRA = "assets/fonts/Saira-VariableFont_wdth,wght.ttf"
SHARETECH = "assets/fonts/ShareTech-Regular.ttf"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    except OSError:
        pass
    return ImageFont.load_default()

def get_mock_data() -> dict[str, Any]:
    now = datetime.now()
    return {
        "node": "KITCHEN-BOX",
        "wifi": "OK",
        "ha": "OK",
        "updated": now.strftime("%H:%M"),
        "refresh_in": "18m",
        "current_temp": 72,
        "condition": "PARTLY CLOUDY",
        "high": 78,
        "low": 61,
        "today": {
            "am": {"label": "AM", "temp": 65},
            "pm": {"label": "PM", "temp": 75},
            "eve": {"label": "EVE", "temp": 68},
        },
        "forecast": [
            {"day": "MON", "temp": 74},
            {"day": "TUE", "temp": 70},
            {"day": "WED", "temp": 77},
        ],
        "uptime": "02:14",
        "ip": "192.168.1.56",
    }


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def center_text_x(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    left: int,
    right: int,
) -> int:
    w, _ = text_size(draw, text, font)
    return left + ((right - left - w) // 2)


def draw_corner_brackets(
    draw: ImageDraw.ImageDraw,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: Any = FG,
    length: int = 18,
    width: int = 2,
) -> None:
    draw.line((x1, y1, x1 + length, y1), fill=color, width=width)
    draw.line((x1, y1, x1, y1 + length), fill=color, width=width)

    draw.line((x2 - length, y1, x2, y1), fill=color, width=width)
    draw.line((x2, y1, x2, y1 + length), fill=color, width=width)

    draw.line((x1, y2, x1 + length, y2), fill=color, width=width)
    draw.line((x1, y2 - length, x1, y2), fill=color, width=width)

    draw.line((x2 - length, y2, x2, y2), fill=color, width=width)
    draw.line((x2, y2 - length, x2, y2), fill=color, width=width)


def draw_top_rail(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.ImageFont], data: dict[str, Any]) -> None:
    y1 = MARGIN
    y2 = y1 + TOP_RAIL_H

    draw.line((CONTENT_LEFT, y2, CONTENT_RIGHT, y2), fill=FG, width=2)
    draw.line((CONTENT_LEFT, y1 + 8, CONTENT_RIGHT, y1 + 8), fill=GRID, width=1)

    left_text = data["node"]
    right_text = (
        f"WIFI {data['wifi']}  //  "
        f"HA {data['ha']}  //  "
        f"UPDATED {data['updated']}  //  "
        f"REFRESH IN {data['refresh_in']}"
    )

    draw.text((CONTENT_LEFT, y1 + 12), left_text, font=fonts["small_bold"], fill=FG)

    right_w, _ = text_size(draw, right_text, fonts["small"])
    draw.text((CONTENT_RIGHT - right_w, y1 + 12), right_text, font=fonts["small"], fill=FG)


def draw_hero(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.ImageFont], data: dict[str, Any]) -> None:
    x1 = CONTENT_LEFT + 36
    x2 = CONTENT_RIGHT - 36
    y1 = HERO_TOP
    y2 = HERO_TOP + HERO_HEIGHT

    draw_corner_brackets(draw, x1, y1, x2, y2, color=FG, length=18, width=2)

    draw.line((x1 + 18, y1 + 18, x2 - 18, y1 + 18), fill=GRID, width=1)
    draw.line((x1 + 18, y2 - 18, x2 - 18, y2 - 18), fill=GRID, width=1)

    draw.text((x1 + 10, y1 - 18), "PRIMARY WX PANEL", font=fonts["micro"], fill=FG)
    env_text = "ENV-01"
    env_w, _ = text_size(draw, env_text, fonts["micro"])
    draw.text((x2 - env_w, y1 - 18), env_text, font=fonts["micro"], fill=FG)
    draw.text((x1 + 12, y2 - 14), "LOCAL FORECAST MODEL", font=fonts["micro"], fill=FG)

    temp_text = f"{data['current_temp']}°"
    condition_text = data["condition"]
    hilo_text = f"H {data['high']}   L {data['low']}"

    hero_w = x2 - x1

    left_x1 = x1 + 28
    left_x2 = x1 + int(hero_w * 0.42)
    right_x = x1 + int(hero_w * 0.52)

# Left: big temp
    temp_x = left_x1 + 18
    temp_y = y1 - 32
    draw.text((temp_x, temp_y), temp_text, font=fonts["hero"], fill=FG)

# Right: treat condition + hi/lo as one grouped block
    cond_w, cond_h = text_size(draw, condition_text, fonts["cond"])
    hilo_w, hilo_h = text_size(draw, hilo_text, fonts["med"])

    group_h = cond_h + 8 + hilo_h
    group_y = y1 + (HERO_HEIGHT - group_h) // 2 - 18

    draw.text((right_x, group_y), condition_text, font=fonts["cond"], fill=FG)
    draw.text((right_x, group_y + cond_h + 8), hilo_text, font=fonts["med"], fill=FG)


def draw_three_column_band(
    draw: ImageDraw.ImageDraw,
    fonts: dict[str, ImageFont.ImageFont],
    title: str,
    y_top: int,
    height: int,
    items: list[dict[str, Any]],
    label_key: str,
    value_key: str,
) -> None:
    x1 = CONTENT_LEFT + 2
    x2 = CONTENT_RIGHT - 2
    y_rule = y_top
    y_bottom = y_top + height

    draw.line((x1, y_rule, x2, y_rule), fill=FG, width=2)
    draw.text((x1, y_rule - 16), title, font=fonts["micro"], fill=FG)

    total_w = x2 - x1
    col_w = total_w // 3

    for i, item in enumerate(items):
        cx1 = x1 + i * col_w
        cx2 = x1 + (i + 1) * col_w

        if i > 0:
            draw.line((cx1, y_rule + 8, cx1, y_bottom - 6), fill=GRID, width=1)

        label = str(item[label_key])
        value = f"{item[value_key]}°"

        label_x = center_text_x(draw, label, fonts["small_bold"], cx1, cx2)
        value_x = center_text_x(draw, value, fonts["med"], cx1, cx2)

        draw.text((label_x, y_rule + 10), label, font=fonts["small_bold"], fill=FG)
        draw.text((value_x, y_rule + 30), value, font=fonts["med"], fill=FG)


def draw_today_band(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.ImageFont], data: dict[str, Any]) -> None:
    items = [
        data["today"]["am"],
        data["today"]["pm"],
        data["today"]["eve"],
    ]
    draw_three_column_band(
        draw=draw,
        fonts=fonts,
        title="TODAY PHASES",
        y_top=TODAY_TOP,
        height=TODAY_HEIGHT,
        items=items,
        label_key="label",
        value_key="temp",
    )


def draw_forecast(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.ImageFont], data: dict[str, Any]) -> None:
    draw_three_column_band(
        draw=draw,
        fonts=fonts,
        title="3-DAY OUTLOOK",
        y_top=FORECAST_TOP,
        height=FORECAST_HEIGHT,
        items=data["forecast"],
        label_key="day",
        value_key="temp",
    )


def draw_system(draw: ImageDraw.ImageDraw, fonts: dict[str, ImageFont.ImageFont], data: dict[str, Any]) -> None:
    y = SYSTEM_TOP
    draw.line((CONTENT_LEFT, y, CONTENT_RIGHT, y), fill=FG, width=2)

    left = f"UPTIME {data['uptime']}"
    center = "NODE-01"
    right = data["ip"]

    draw.text((CONTENT_LEFT, y + 8), left, font=fonts["small"], fill=FG)

    center_x = center_text_x(draw, center, fonts["small"], CONTENT_LEFT, CONTENT_RIGHT)
    draw.text((center_x, y + 8), center, font=fonts["small"], fill=FG)

    right_w, _ = text_size(draw, right, fonts["small"])
    draw.text((CONTENT_RIGHT - right_w, y + 8), right, font=fonts["small"], fill=FG)


def main() -> None:
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    fonts = {
        "hero": load_font(SAIRA, 130),
        "cond": load_font(SAIRA, 28),
        "med": load_font(SAIRA, 24),
        "small_bold": load_font(SHARETECH, 18),
        "small": load_font(SAIRA, 16),
        "micro": load_font(SHARETECH, 12),
    }

    data = get_mock_data()

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    draw_top_rail(draw, fonts, data)
    draw_hero(draw, fonts, data)
    draw_today_band(draw, fonts, data)
    draw_forecast(draw, fonts, data)
    draw_system(draw, fonts, data)

    output_path = output_dir / "preview.png"
    img.save(output_path)
    print(f"Saved preview to {output_path.resolve()}")


if __name__ == "__main__":
    main()

