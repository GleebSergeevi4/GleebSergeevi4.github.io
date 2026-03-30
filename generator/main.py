from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from fetch_matches import (
    get_today_matches,
    get_tomorrow_matches,
    get_yesterday_matches,
)
from render import render_matches_page, save_root_index, write_rendered_page


SITE_URL = os.getenv("SITE_URL", "https://gleebsergeevi4.github.io/")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _save_nojekyll(output_root: Path) -> Path:
    path = output_root / ".nojekyll"
    path.write_text("", encoding="utf-8")
    return path


def _save_json(output_root: Path, slug: str, matches: list[dict[str, Any]]) -> Path:
    api_dir = output_root / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    api_file = api_dir / f"{slug}.json"
    api_file.write_text(
        json.dumps(matches, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return api_file


def generate_site(save_api_json: bool = True) -> list[Path]:
    pages: list[tuple[str, str, str, str, list[dict[str, Any]]]] = [
        (
            "yesterday",
            "Киберспортивные матчи за вчера",
            "Матчи за вчерашний день",
            "Список завершённых киберспортивных матчей за вчерашний день.",
            get_yesterday_matches(),
        ),
        (
            "today",
            "Киберспортивные матчи на сегодня",
            "Матчи на сегодняшний день",
            "Актуальный список киберспортивных матчей на сегодня.",
            get_today_matches(),
        ),
        (
            "tomorrow",
            "Киберспортивные матчи на завтра",
            "Матчи на завтрашний день",
            "Расписание киберспортивных матчей на завтрашний день.",
            get_tomorrow_matches(),
        ),
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    created_files: list[Path] = [
        save_root_index(OUTPUT_DIR, SITE_URL),
        _save_nojekyll(OUTPUT_DIR),
    ]

    for slug, title, h1, description, matches in pages:
        page_url = f"{SITE_URL.rstrip('/')}/{slug}/"
        html = render_matches_page(
            page_title=title,
            h1_title=h1,
            page_description=description,
            canonical_url=page_url,
            site_url=SITE_URL,
            matches=matches,
        )
        created_files.append(write_rendered_page(OUTPUT_DIR, slug, html))

        if save_api_json:
            created_files.append(_save_json(OUTPUT_DIR, slug, matches))

    return created_files


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Генерация статического сайта матчей")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Непрерывно обновлять данные и пересобирать страницы",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Интервал обновления в секундах для режима --watch (по умолчанию: 60)",
    )
    return parser


def _run_once() -> None:
    files = generate_site()
    for file_path in files:
        print(f"Сгенерировано: {file_path}")


def _run_watch(interval: int) -> None:
    safe_interval = max(60, interval)
    print(f"Запущен watch-режим. Интервал обновления: {safe_interval} сек.")
    print("Остановка: Ctrl+C")

    try:
        while True:
            print("\n--- Новый цикл генерации ---")
            try:
                _run_once()
            except Exception as exc:
                print(f"Ошибка обновления: {exc}")
            print(f"Ожидание {safe_interval} сек. до следующего обновления...")
            time.sleep(safe_interval)
    except KeyboardInterrupt:
        print("\nWatch-режим остановлен.")


if __name__ == "__main__":
    args = _build_cli().parse_args()
    if args.watch:
        _run_watch(args.interval)
    else:
        _run_once()