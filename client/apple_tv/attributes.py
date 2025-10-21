import json
from typing import TypedDict, cast

from bs4 import BeautifulSoup


class Person(TypedDict):
    type: str
    name: str


class Attributes(TypedDict):
    context: str
    type: str  # "Movie" or "TVSeries"
    name: str
    description: str
    actor: list[Person]
    director: list[Person]
    datePublished: str
    image: str


def get_attributes(
    page: BeautifulSoup, strip_at_keys: bool = True
) -> Attributes | None:
    """
    Return the single Movie/TVSeries JSON-LD dict (with '@' stripped if requested),
    or None if not found.
    """
    # 1) Try known Apple-specific script IDs first (fast path)
    for known_id in ("schema:movie", "schema:tv-series"):
        tag = _select_jsonld_by_id(page, known_id)
        if not tag:
            continue
        data = _parse_jsonld(tag)
        result = _first_title_from_data(data)
        if result:
            return cast(Attributes, _finalize(result, strip_at_keys))

    # 2) Fallback: scan all JSON-LD blocks
    for tag in _iter_all_jsonld(page):
        data = _parse_jsonld(tag)
        result = _first_title_from_data(data)
        if result:
            return cast(Attributes, _finalize(result, strip_at_keys))

    return None


def _select_jsonld_by_id(page: BeautifulSoup, id_value: str):
    # Escape the colon in CSS selector
    return page.select_one(
        f'script#{id_value.replace(":", "\\:")}[type="application/ld+json"]'
    )


def _iter_all_jsonld(page: BeautifulSoup):
    return page.select('script[type="application/ld+json"]')


def _parse_jsonld(tag) -> dict | list | None:
    try:
        return json.loads(tag.get_text(strip=True))
    except Exception:
        return None


def _first_title_from_data(data: dict | list | None) -> dict | None:
    """Return the first dict with @type in ('Movie', 'TVSeries'), else None."""
    if data is None:
        return None
    if isinstance(data, dict):
        return data if data.get("@type") in ("Movie", "TVSeries") else None
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("@type") in ("Movie", "TVSeries"):
                return item
    return None


def _finalize(d: dict, strip_at_keys: bool) -> dict:
    d = _fix_text_fields(d)
    if strip_at_keys:
        d = _strip_at_prefix(d)
    return d


def _demojibake(s: str) -> str:
    """Fix common UTF-8 mojibake (e.g., â → ’) with a safe best-effort pass."""
    try:
        return s.encode("latin1", "ignore").decode("utf-8", "ignore")
    except Exception:
        return s


def _fix_text_fields(obj: dict) -> dict:
    for k in ("name", "description"):
        v = obj.get(k)
        if isinstance(v, str):
            obj[k] = _demojibake(v)
    return obj


def _strip_at_prefix(obj):
    # Recursively remove '@' prefix from all keys in dicts
    if isinstance(obj, dict):
        return {k.lstrip("@"): _strip_at_prefix(v) for k, v in obj.items()}
    # Recursively remove '@' prefix from all keys in dicts in lists
    if isinstance(obj, list):
        return [_strip_at_prefix(v) for v in obj]
    return obj
