from __future__ import annotations

import requests

from datetime import datetime
from typing import Any

# Lat/Lon for Home
LAT = 39.86679
LON = -85.98334


def get_live_data() -> dict[str, Any]:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,weather_code"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min"
        "&temperature_unit=fahrenheit"
        "&wind_speed_unit=mph"
        "&precipitation_unit=inch"
        "&timezone=auto"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    payload = r.json()

    current = payload["current"]
    daily = payload["daily"]

    days = daily["time"]
    highs = daily["temperature_2m_max"]
    lows = daily["temperature_2m_min"]
    codes = daily["weather_code"]

    return {
        "node": "KITCHEN-BOX",
        "wifi": "OK",
        "ha": "OK",
        "updated": datetime.now().strftime("%H:%M"),
        "refresh_in": "18m",
        "current_temp": round(current["temperature_2m"]),
        "condition": weather_code_to_label(current["weather_code"]),
        "high": round(highs[0]),
        "low": round(lows[0]),
        "today": {
            "am": {"label": "AM", "temp": round(lows[0])},
            "pm": {"label": "PM", "temp": round(highs[0])},
            "eve": {"label": "EVE", "temp": round((highs[0] + lows[0]) / 2)},
        },
        "forecast": [
            {"day": day_label(days[1]), "temp": round(highs[1])},
            {"day": day_label(days[2]), "temp": round(highs[2])},
            {"day": day_label(days[3]), "temp": round(highs[3])},
        ],
        "uptime": "02:14",
        "ip": "192.168.1.56",
    }


def day_label(iso_date: str) -> str:
    from datetime import datetime
    return datetime.fromisoformat(iso_date).strftime("%a").upper()


def weather_code_to_label(code: int) -> str:
    if code == 0:
        return "CLEAR"
    if code in (1, 2):
        return "PARTLY CLOUDY"
    if code == 3:
        return "CLOUDY"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "RAIN"
    if code in (95, 96, 99):
        return "STORM"
    return "UNKNOWN"

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

