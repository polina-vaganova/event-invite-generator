"""
Парсер событий afisha.ru.

Достаёт данные из СТАБИЛЬНЫХ источников страницы, а не из случайной вёрстки:
  1. OpenGraph-теги (og:title, og:image, og:description);
  2. JSON-LD (schema.org) — жанр, дата, длительность, площадка, цена и т.д.

Это «костыль прототипа»: в реальном внедрении данные приходили бы из
внутреннего API Афиши. Здесь парсер играет роль наполнителя каталога.
"""
import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

MONTHS_RU = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]


def is_afisha_url(url: str) -> bool:
    """Проверяет, что ссылка ведёт на afisha.ru или её поддомен."""
    try:
        host = urlparse(url).hostname or ""
        host = host.removeprefix("www.")
        return host == "afisha.ru" or host.endswith(".afisha.ru")
    except ValueError:
        return False


def event_id_from_url(url: str) -> str:
    """Достаёт ID события из ссылки (без сетевого запроса)."""
    return _url_parts(url)[0]


def _url_parts(url: str) -> tuple[str, str, str]:
    """Возвращает (id, slug, category) из пути URL."""
    path = urlparse(url).path
    segments = [s for s in path.split("/") if s]
    category = segments[0] if segments else "event"
    last = segments[-1] if segments else ""
    m = re.search(r"(\d+)$", last)
    event_id = m.group(1) if m else last
    slug = re.sub(r"-?\d+$", "", last) or last
    return event_id, slug, category


def _looks_blocked(html: str) -> bool:
    """Распознаёт анти-бот заглушку Афиши («Один момент…»)."""
    if re.search(r"<title>\s*(Один момент|Just a moment|Подождите|Проверка|Доступ)", html, re.I):
        return True
    return len(html) < 5000 and not re.search(r"og:title|application/ld\+json", html, re.I)


def _fetch_html(url: str) -> tuple[str, str]:
    """Скачивает HTML с ретраями. Возвращает (html, final_url)."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    last_error = "неизвестно"
    for attempt in range(1, 5):
        try:
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code != 200:
                raise RuntimeError(f"Афиша вернула статус {resp.status_code}")
            html = resp.text
            if _looks_blocked(html):
                raise RuntimeError("Афиша показала проверку доступа")
            return html, str(resp.url)
        except Exception as err:  # noqa: BLE001 — намеренно ловим всё для ретрая
            last_error = str(err)
            if attempt < 4:
                time.sleep(0.5 * attempt)
    raise RuntimeError(
        f"Не удалось получить событие с Афиши ({last_error}). "
        "Попробуйте ещё раз или выберите событие из каталога."
    )


def _extract_jsonld(soup: BeautifulSoup) -> list[dict]:
    """Собирает все JSON-LD объекты со страницы в плоский список."""
    blocks: list[dict] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if isinstance(item, dict):
                graph = item.get("@graph")
                if isinstance(graph, list):
                    blocks.extend(b for b in graph if isinstance(b, dict))
                else:
                    blocks.append(item)
    return blocks


EVENT_TYPE_RE = re.compile(
    r"Movie|Event|Theater|Theatre|Music|Exhibition|Screening|Festival|Comedy|"
    r"Dance|Play|Visual|Sports|Restaurant|FoodEstablishment|Place|CreativeWork|Product",
    re.I,
)
SERVICE_TYPE_RE = re.compile(r"BreadcrumbList|WebSite|WebPage|Organization|SearchAction", re.I)


def _ld_types(block: dict) -> list[str]:
    t = block.get("@type")
    arr = t if isinstance(t, list) else [t]
    return [x for x in arr if isinstance(x, str)]


def _select_main_ld(blocks: list[dict]) -> dict:
    """Выбирает главный JSON-LD блок — описание самого события."""
    for b in blocks:
        types = _ld_types(b)
        if any(EVENT_TYPE_RE.search(t) and not SERVICE_TYPE_RE.search(t) for t in types):
            return b
    for b in blocks:
        if isinstance(b.get("name"), str) and not any(SERVICE_TYPE_RE.search(t) for t in _ld_types(b)):
            return b
    return {}


def _pick_name(value) -> str | None:
    """Нормализует поле: строка / {name} / список таких."""
    if not value:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list):
        names = [n for n in (_pick_name(v) for v in value) if n]
        return ", ".join(names) or None
    if isinstance(value, dict):
        name = value.get("name")
        return name.strip() if isinstance(name, str) and name.strip() else None
    return None


def _pick_names(value) -> list[str] | None:
    if not value:
        return None
    arr = value if isinstance(value, list) else [value]
    names = [n for n in (_pick_name(v) for v in arr) if n]
    return names or None


def _pick_image(value) -> str | None:
    if not value:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return _pick_image(value[0]) if value else None
    if isinstance(value, dict):
        url = value.get("url")
        return url if isinstance(url, str) else None
    return None


def _strip_html(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = (
        text.replace("&nbsp;", " ").replace("&amp;", "&")
        .replace("&quot;", '"').replace("&#39;", "'")
    )
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text).strip()
    return text or None


def _humanize_duration(value: str | None) -> str | None:
    if not value:
        return None
    m = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?$", value)
    if not m:
        return value
    parts = []
    if m.group(1):
        parts.append(f"{m.group(1)} ч")
    if m.group(2):
        parts.append(f"{m.group(2)} мин")
    return " ".join(parts) or None


def _format_date(value: str | None) -> str | None:
    """ISO-дату → «29 августа 2026, 19:00». Время 00:00 опускаем."""
    if not value:
        return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?", value)
    if not m:
        return value
    year, month, day, hh, mm = m.groups()
    month_name = MONTHS_RU[int(month) - 1] if 1 <= int(month) <= 12 else month
    date_part = f"{int(day)} {month_name} {year}"
    if hh and mm and not (hh == "00" and mm == "00"):
        return f"{date_part}, {hh}:{mm}"
    return date_part


def _split_genres(value: str | None) -> list[str] | None:
    if not value:
        return None
    parts = [p.strip() for p in re.split(r"[,;/]", value) if p.strip()]
    return parts or None


def _clean_rating(value) -> str | None:
    if value is None:
        return None
    try:
        return str(value) if float(value) > 0 else None
    except (TypeError, ValueError):
        return None


def _pick_price(ld: dict) -> str | None:
    """Цена из offers.price / lowPrice или priceRange → «от 850 ₽»."""
    price_range = ld.get("priceRange")
    if isinstance(price_range, str) and price_range.strip():
        return price_range.strip()
    offers_raw = ld.get("offers")
    offers = offers_raw if isinstance(offers_raw, list) else ([offers_raw] if offers_raw else [])
    prices = []
    for o in offers:
        if not isinstance(o, dict):
            continue
        p = o.get("lowPrice", o.get("price"))
        try:
            num = float(p)
            if num > 0:
                prices.append(num)
        except (TypeError, ValueError):
            continue
    if not prices:
        return None
    return f"от {int(min(prices))} ₽"


def parse_afisha_event(url: str) -> dict:
    """Скачивает и парсит страницу события afisha.ru → словарь события."""
    if not is_afisha_url(url):
        raise ValueError("Ссылка должна вести на afisha.ru")

    html, final_url = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    def og(prop: str) -> str | None:
        tag = soup.find("meta", attrs={"property": f"og:{prop}"})
        content = tag.get("content").strip() if tag and tag.get("content") else None
        return content or None

    ld = _select_main_ld(_extract_jsonld(soup))
    event_id, slug, category = _url_parts(final_url)

    h1 = soup.find("h1")
    title = _pick_name(ld.get("name")) or og("title") or (h1.get_text().strip() if h1 else slug)

    return {
        "id": event_id,
        "slug": slug,
        "sourceUrl": final_url,
        "category": category,
        "title": title,
        # alternateName у фильмов = оригинальное название, у событий = жанр
        "originalTitle": _pick_name(ld.get("alternateName")) if category == "movie" else None,
        "image": _pick_image(ld.get("image")) or og("image"),
        "description": _strip_html(_pick_name(ld.get("description")) or og("description")),
        "genres": _pick_names(ld.get("genre"))
        or (_split_genres(_pick_name(ld.get("alternateName"))) if category != "movie" else None),
        "date": _format_date(_pick_name(ld.get("startDate") or ld.get("datePublished"))),
        "country": _pick_name(ld.get("countryOfOrigin")),
        "duration": _humanize_duration(_pick_name(ld.get("duration"))),
        "ageRating": _pick_name(ld.get("contentRating") or ld.get("typicalAgeRange")),
        "director": _pick_name(ld.get("director") or ld.get("organizer") or ld.get("author")),
        "venue": _pick_name(ld.get("location")),
        "price": _pick_price(ld),
        "rating": _clean_rating((ld.get("aggregateRating") or {}).get("ratingValue")),
        "parsedAt": datetime.now(timezone.utc).isoformat(),
    }
