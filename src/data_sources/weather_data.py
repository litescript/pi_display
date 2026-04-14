from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

HA_URL = os.environ["HA_URL"].rstrip("/")
HA_TOKEN = os.environ["HA_TOKEN"].strip()
HA_WEATHER_ENTITY = os.environ.get("HA_WEATHER_ENTITY", "weather.forecast_home").strip()

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}


def get_live_data() -> dict[str, Any]:
    state = _get_current_state()
    forecast_payload = _get_daily_forecast()
    forecast_list = _extract_forecast_list(forecast_payload)

    attrs = state.get("attributes", {})

    current_temp = _round_or_none(attrs.get("temperature"))
    current_condition = ha_condition_to_label(state.get("state"))

    today = forecast_list[0] if len(forecast_list) > 0 else {}
    tomorrow = forecast_list[1] if len(forecast_list) > 1 else {}
    day_after = forecast_list[2] if len(forecast_list) > 2 else {}
    third_day = forecast_list[3] if len(forecast_list) > 3 else {}

    today_high = _round_or_none(today.get("temperature"))
    today_low = _round_or_none(today.get("templow"))

    return {
        "node": "KITCHEN-BOX",
        "wifi": "OK",
        "ha": "OK",
        "updated": datetime.now().strftime("%H:%M"),
        "refresh_in": "30m",
        "current_temp": current_temp if current_temp is not None else today_high or 0,
        "condition": current_condition,
        "high": today_high if today_high is not None else 0,
        "low": today_low if today_low is not None else 0,
        "today": {
            "am": {
                "label": "AM",
                "temp": today_low if today_low is not None else 0,
            },
            "pm": {
                "label": "PM",
                "temp": today_high if today_high is not None else 0,
            },
            "eve": {
                "label": "EVE",
                "temp": midpoint(today_high, today_low),
            },
        },
        "forecast": [
            {
                "day": forecast_day_label(tomorrow.get("datetime")),
                "temp": _round_or_zero(tomorrow.get("temperature")),
            },
            {
                "day": forecast_day_label(day_after.get("datetime")),
                "temp": _round_or_zero(day_after.get("temperature")),
            },
            {
                "day": forecast_day_label(third_day.get("datetime")),
                "temp": _round_or_zero(third_day.get("temperature")),
            },
        ],
        "uptime": "02:14",
        "ip": "192.168.1.56",
    }


def _get_current_state() -> dict[str, Any]:
    response = requests.get(
        f"{HA_URL}/api/states/{HA_WEATHER_ENTITY}",
        headers=HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _get_daily_forecast() -> dict[str, Any]:
    response = requests.post(
        f"{HA_URL}/api/services/weather/get_forecasts?return_response",
        headers=HEADERS,
        json={
            "entity_id": HA_WEATHER_ENTITY,
            "type": "daily",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _extract_forecast_list(payload: Any) -> list[dict[str, Any]]:
    # Expected shape:
    # {"weather.forecast_home": {"forecast": [...]}}
    if isinstance(payload, dict) and HA_WEATHER_ENTITY in payload:
        entity_block = payload[HA_WEATHER_ENTITY]
        forecast = entity_block.get("forecast", [])
        if isinstance(forecast, list):
            return forecast

    # Some HA/API paths may wrap the response data
    if isinstance(payload, dict) and "service_response" in payload:
        sr = payload["service_response"]
        if isinstance(sr, dict) and HA_WEATHER_ENTITY in sr:
            entity_block = sr[HA_WEATHER_ENTITY]
            forecast = entity_block.get("forecast", [])
            if isinstance(forecast, list):
                return forecast

    # Some callers may return a one-item list containing the mapping
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, dict) and HA_WEATHER_ENTITY in first:
            entity_block = first[HA_WEATHER_ENTITY]
            forecast = entity_block.get("forecast", [])
            if isinstance(forecast, list):
                return forecast

    raise KeyError(
        f"Could not find forecast data for {HA_WEATHER_ENTITY!r}. "
        f"Top-level payload type={type(payload).__name__}, "
        f"keys={list(payload.keys()) if isinstance(payload, dict) else 'n/a'}"
    )


def forecast_day_label(dt: str | None) -> str:
    if not dt:
        return "---"
    return datetime.fromisoformat(dt).strftime("%a").upper()


def midpoint(high: int | None, low: int | None) -> int:
    if high is None and low is None:
        return 0
    if high is None:
        return low or 0
    if low is None:
        return high
    return round((high + low) / 2)


def _round_or_none(value: Any) -> int | None:
    if value is None:
        return None
    return round(float(value))


def _round_or_zero(value: Any) -> int:
    rounded = _round_or_none(value)
    return rounded if rounded is not None else 0


def ha_condition_to_label(condition: str | None) -> str:
    mapping = {
        "clear-night": "CLEAR",
        "cloudy": "CLOUDY",
        "fog": "FOG",
        "hail": "HAIL",
        "lightning": "STORM",
        "lightning-rainy": "STORM",
        "partlycloudy": "PARTLY CLOUDY",
        "pouring": "RAIN",
        "rainy": "RAIN",
        "snowy": "SNOW",
        "snowy-rainy": "WINTRY MIX",
        "sunny": "CLEAR",
        "windy": "WINDY",
        "windy-variant": "WINDY",
        "exceptional": "ALERT",
    }
    if not condition:
        return "UNKNOWN"
    return mapping.get(condition, condition.replace("-", " ").upper())

