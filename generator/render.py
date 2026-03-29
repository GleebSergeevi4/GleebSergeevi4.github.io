from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from string import Template
from typing import Any


TEMPLATE_FILE = Path(__file__).resolve().parent / "template" / "matches.html"


def _format_time(value: str | None) -> str:
	if not value:
		return "Время уточняется"

	try:
		dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
		return dt.strftime("%d.%m.%Y %H:%M UTC")
	except ValueError:
		return escape(value)


def _team_name(match: dict[str, Any], index: int) -> str:
	opponents = match.get("opponents") or []
	if index >= len(opponents):
		return "TBD"

	team = opponents[index].get("opponent") or {}
	return str(team.get("name") or "TBD")


def _match_cards(matches: list[dict[str, Any]]) -> str:
	if not matches:
		return '<p class="empty">На выбранную дату матчи не найдены.</p>'

	cards: list[str] = []
	for match in matches:
		team_a = escape(_team_name(match, 0))
		team_b = escape(_team_name(match, 1))

		league = escape(str((match.get("league") or {}).get("name") or "Без лиги"))
		serie = escape(str((match.get("serie") or {}).get("name") or ""))
		status = escape(str(match.get("status") or "unknown"))
		start_at = _format_time(match.get("begin_at"))

		cards.append(
			"\n".join(
				[
					'<article class="match-card">',
					f'  <div class="teams">{team_a} <span>vs</span> {team_b}</div>',
					f'  <div class="meta">{league}{(" • " + serie) if serie else ""}</div>',
					f'  <div class="meta">Старт: {start_at}</div>',
					f'  <div class="status">Статус: {status}</div>',
					"</article>",
				]
			)
		)

	return "\n".join(cards)


def _schema(site_url: str) -> list[dict[str, Any]]:
	return [
		{
			"@context": "https://schema.org",
			"@type": "Organization",
			"name": "Esports Match Hub",
			"url": site_url,
			"logo": f"{site_url.rstrip('/')}/logo.png",
		},
		{
			"@context": "https://schema.org",
			"@type": "WebSite",
			"name": "Esports Match Hub",
			"url": site_url,
			"inLanguage": "ru",
		},
	]


def render_matches_page(
	*,
	page_title: str,
	h1_title: str,
	page_description: str,
	canonical_url: str,
	site_url: str,
	matches: list[dict[str, Any]],
	schema_org_jsonld: list[dict[str, Any]] | None = None,
) -> str:
	template = Template(TEMPLATE_FILE.read_text(encoding="utf-8"))

	cards_html = _match_cards(matches)
	schema_data = schema_org_jsonld if schema_org_jsonld is not None else _schema(site_url)
	schema_json = json.dumps(schema_data, ensure_ascii=False, separators=(",", ":"))

	return template.safe_substitute(
		title=escape(page_title),
		description=escape(page_description),
		canonical_url=escape(canonical_url),
		og_title=escape(page_title),
		og_description=escape(page_description),
		og_url=escape(canonical_url),
		h1_title=escape(h1_title),
		update_time=escape(datetime.utcnow().strftime("%d.%m.%Y %H:%M UTC")),
		matches_count=str(len(matches)),
		matches_cards=cards_html,
		schema_org_jsonld=schema_json,
	)


def write_rendered_page(output_root: Path, slug: str, html: str) -> Path:
	page_dir = output_root / slug
	page_dir.mkdir(parents=True, exist_ok=True)

	page_path = page_dir / "index.html"
	page_path.write_text(html, encoding="utf-8")
	return page_path

