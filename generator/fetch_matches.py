import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from requests import HTTPError, RequestException


BASE_URL = "https://api.pandascore.co"
TOKEN = os.getenv("PANDASCORE_TOKEN", "SuwjiD5LI9MVkni7WtFmFHJ_hGjyQnl9Z35gmbpGqqjP-9gIghI")
TZ_NAME = "Europe/Moscow"
TIMEOUT = 30
MAX_RETRIES = 3
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


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
	last_error: Exception | None = None

	for attempt in range(1, MAX_RETRIES + 1):
		try:
			response = requests.get(
				f"{BASE_URL}{endpoint}",
				params=params,
				timeout=TIMEOUT,
			)
			response.raise_for_status()

			data = response.json()
			return data if isinstance(data, list) else []
		except HTTPError as exc:
			status_code = exc.response.status_code if exc.response is not None else None
			if status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
				time.sleep(2 * attempt)
				last_error = exc
				continue

			message = exc.response.text[:300] if exc.response is not None else str(exc)
			raise RuntimeError(f"Ошибка PandaScore {status_code}: {message}") from exc
		except RequestException as exc:
			if attempt < MAX_RETRIES:
				time.sleep(2 * attempt)
				last_error = exc
				continue
			raise RuntimeError(f"Сетевая ошибка PandaScore: {exc}") from exc

	raise RuntimeError(f"Не удалось получить данные после {MAX_RETRIES} попыток: {last_error}")


def get_yesterday_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=-1, range_field="end_at", sort="-end_at")
	return fetch_matches("/matches/past", params)


def get_today_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=0, range_field="begin_at", sort="begin_at")
	return fetch_matches("/matches/upcoming", params)


def get_tomorrow_matches() -> list[dict[str, Any]]:
	params = build_date_params(day_offset=1, range_field="begin_at", sort="begin_at")
	return fetch_matches("/matches/upcoming", params)
