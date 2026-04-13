import requests

LAT = 39.7684   # Indianapolis
LON = -86.1581


def get_weather_data():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current_weather=true"
        "&daily=temperature_2m_max,temperature_2m_min,weathercode"
        "&timezone=auto"
    )

    res = requests.get(url, timeout=5)
    data = res.json()

    current = data["current_weather"]
    daily = data["daily"]

    return {
        "current_temp": round(current["temperature"]),
        "condition": map_weather_code(current["weathercode"]),
        "high": round(daily["temperature_2m_max"][0]),
        "low": round(daily["temperature_2m_min"][0]),

        "today_phases": [
            {"label": "AM", "temp": round(daily["temperature_2m_min"][0])},
            {"label": "PM", "temp": round(daily["temperature_2m_max"][0])},
            {"label": "EVE", "temp": round(daily["temperature_2m_min"][0] + 2)},
        ],

        "forecast": [
            {"day": "MON", "temp": round(daily["temperature_2m_max"][1])},
            {"day": "TUE", "temp": round(daily["temperature_2m_max"][2])},
            {"day": "WED", "temp": round(daily["temperature_2m_max"][3])},
        ],
    }


def map_weather_code(code: int) -> str:
    # very basic mapping for now
    if code == 0:
        return "CLEAR"
    elif code in [1, 2]:
        return "PARTLY CLOUDY"
    elif code == 3:
        return "CLOUDY"
    elif code in [51, 53, 55, 61, 63, 65]:
        return "RAIN"
    elif code in [95, 96, 99]:
        return "STORM"
    else:
        return "UNKNOWN"

