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
    daily_payload = _get_forecast("daily")
    hourly_payload = _get_forecast("hourly")

    daily = _extract_forecast_list(daily_payload)
    hourly = _extract_forecast_list(hourly_payload)

    attrs = state.get("attributes", {})
    raw_condition = state.get("state")

    current_temp = _round_or_none(attrs.get("temperature"))
    current_condition = ha_condition_to_label(raw_condition)

    today = daily[0] if len(daily) > 0 else {}
    tomorrow = daily[1] if len(daily) > 1 else {}
    day_after = daily[2] if len(daily) > 2 else {}
    third_day = daily[3] if len(daily) > 3 else {}

    today_high = _round_or_none(today.get("temperature"))
    today_low = _round_or_none(today.get("templow"))

    am_temp = _pick_hourly_temp(hourly, target_hour=9)
    pm_temp = _pick_hourly_temp(hourly, target_hour=15)
    eve_temp = _pick_hourly_temp(hourly, target_hour=20)

    return {
        "node": "KITCHEN-BOX",
        "wifi": "OK",
        "ha": "OK",
        "updated": datetime.now().strftime("%H:%M"),
        "refresh_in": "30m",
        "current_temp": current_temp if current_temp is not None else (today_high or 0),
        "condition": current_condition,
        "condition_raw": raw_condition,
        "condition_icon": ha_condition_to_icon(raw_condition),
        "high": today_high if today_high is not None else 0,
        "low": today_low if today_low is not None else 0,
        "today": {
            "am": {
                "label": "AM",
                "temp": am_temp if am_temp is not None else (today_low if today_low is not None else 0),
            },
            "pm": {
                "label": "PM",
                "temp": pm_temp if pm_temp is not None else (today_high if today_high is not None else 0),
            },
            "eve": {
                "label": "EVE",
                "temp": eve_temp if eve_temp is not None else midpoint(today_high, today_low),
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


def _get_forecast(forecast_type: str) -> Any:
    response = requests.post(
        f"{HA_URL}/api/services/weather/get_forecasts?return_response",
        headers=HEADERS,
        json={
            "entity_id": HA_WEATHER_ENTITY,
            "type": forecast_type,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _extract_forecast_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and HA_WEATHER_ENTITY in payload:
        entity_block = payload[HA_WEATHER_ENTITY]
        forecast = entity_block.get("forecast", [])
        if isinstance(forecast, list):
            return forecast

    if isinstance(payload, dict) and "service_response" in payload:
        sr = payload["service_response"]
        if isinstance(sr, dict) and HA_WEATHER_ENTITY in sr:
            entity_block = sr[HA_WEATHER_ENTITY]
            forecast = entity_block.get("forecast", [])
            if isinstance(forecast, list):
                return forecast

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


def _pick_hourly_temp(hourly: list[dict[str, Any]], target_hour: int) -> int | None:
    if not hourly:
        return None

    best_item: dict[str, Any] | None = None
    best_distance: int | None = None

    for item in hourly:
        dt = item.get("datetime")
        temp = item.get("temperature")
        if dt is None or temp is None:
            continue

        try:
            hour = datetime.fromisoformat(dt).astimezone().hour
        except ValueError:
            continue

        distance = abs(hour - target_hour)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_item = item

    if best_item is None:
        return None

    return _round_or_none(best_item.get("temperature"))


def forecast_day_label(dt: str | None) -> str:
    if not dt:
        return "---"
    return datetime.fromisoformat(dt).astimezone().strftime("%a").upper()


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


def ha_condition_to_icon(condition: str | None) -> str:
    mapping = {
        "clear-night": "clear_moon",
        "cloudy": "cloudy",
        "fog": "cloudy",
        "hail": "storm",
        "lightning": "storm",
        "lightning-rainy": "storm",
        "partlycloudy": "partly_cloudy",
        "pouring": "rain",
        "rainy": "rain",
        "snowy": "cloudy",
        "snowy-rainy": "rain",
        "sunny": "sunny",
        "windy": "cloudy",
        "windy-variant": "cloud_moon",
        "exceptional": "storm",
    }
    return mapping.get(condition or "", "cloudy")


def get_mock_data() -> dict[str, Any]:
    now = datetime.now()
    return {
        "node": "KITCHEN-BOX",
        "wifi": "OK",
        "ha": "OK",
        "updated": now.strftime("%H:%M"),
        "refresh_in": "30m",
        "current_temp": 72,
        "condition": "PARTLY CLOUDY",
        "condition_raw": "partlycloudy",
        "condition_icon": "partly_cloudy",
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

