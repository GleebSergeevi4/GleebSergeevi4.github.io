import os
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from requests import HTTPError


BASE_URL = "https://api.pandascore.co"
TOKEN = os.getenv("PANDASCORE_TOKEN", "SuwjiD5LI9MVkni7WtFmFHJ_hGjyQnl9Z35gmbpGqqjP-9gIghI")
TZ_NAME = "Europe/Moscow"
TIMEOUT = 30


def _tz(name: str) -> timezone | ZoneInfo:
	try:
		return ZoneInfo(name)
	except ZoneInfoNotFoundError:
		if name == "Europe/Moscow":
			return timezone(timedelta(hours=3), name="MSK")
		return timezone.utc


def _to_utc_iso(dt: datetime) -> str:
	return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _day_range(day_offset: int, tz_name: str = TZ_NAME) -> tuple[str, str]:
	tz = _tz(tz_name)
	target_day = (datetime.now(tz) + timedelta(days=day_offset)).date()

	start_local = datetime.combine(target_day, datetime.min.time(), tzinfo=tz)
	end_local = start_local + timedelta(days=1) - timedelta(seconds=1)
	return _to_utc_iso(start_local), _to_utc_iso(end_local)


def build_date_params(
	day_offset: int,
	range_field: str,
	per_page: int = 100,
	page: int = 1,
	sort: str | None = None,
) -> dict[str, Any]:
	start_iso, end_iso = _day_range(day_offset)
	params: dict[str, Any] = {
		"token": TOKEN,
		f"range[{range_field}]": f"{start_iso},{end_iso}",
		"per_page": per_page,
		"page": page,
	}

	if sort:
		params["sort"] = sort

	return params


def fetch_matches(endpoint: str, params: dict[str, Any]) -> list[dict[str, Any]]:
	response = requests.get(
		f"{BASE_URL}{endpoint}",
		params=params,
		timeout=TIMEOUT,
	)

	try:
		response.raise_for_status()
	except HTTPError as exc:
		raise RuntimeError(
			f"Ошибка PandaScore {response.status_code}: {response.text[:300]}"
		) from exc

	data = response.json()
	return data if isinstance(data, list) else []


def get_yesterday_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=-1, range_field="end_at", sort="-end_at")
	return fetch_matches("/matches/past", params)


def get_today_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=0, range_field="begin_at", sort="begin_at")
	return fetch_matches("/matches/upcoming", params)


def get_tomorrow_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=1, range_field="begin_at", sort="begin_at")
	return fetch_matches("/matches/upcoming", params)
