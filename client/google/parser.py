from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from client.google.utils import first_int4, normalize_url

if TYPE_CHECKING:
    from client.apple_tv.attributes import Attributes


@dataclass(slots=True)
class ItemView:
    url: str
    title: str | None
    director: str | None
    release_year: int | None
    lang: str | None = None


def parse_item_from_cse(raw: dict) -> ItemView:
    raw_url = raw.get("link") or ""
    url = normalize_url(raw_url)

    metatags = {}
    try:
        meta_list = raw.get("pagemap", {}).get("metatags", [])
        if meta_list:
            metatags = dict(meta_list[0])
    except Exception:
        pass

    apple_title = metatags.get("apple:title")
    page_title = raw.get("title")
    if apple_title:
        title = apple_title
    elif page_title:
        title = clean_title(page_title)
    else:
        title = None

    director = metatags.get("og:video:director") or None

    release_year = None
    if raw_year := metatags.get("og:video:release_date"):
        release_year = parse_release_year(raw_year)

    lang = parse_lang(raw_url)

    return ItemView(
        url=url,
        title=title,
        director=director,
        release_year=release_year,
        lang=lang,
    )


def parse_item_from_apple_tv_attributes(url: str, attributes: Attributes) -> ItemView:
    title = attributes["name"]
    directors = attributes.get("director")
    director = directors[0]["name"] if directors else None
    date = attributes["datePublished"]
    release_year = parse_release_year(date)

    return ItemView(
        url=url,
        title=title,
        director=director,
        release_year=release_year,
    )


def clean_title(s: str) -> str:
    s = re.sub(r"\s*-\s*Apple\s*TV\s*$", "", s)
    s = html.unescape((s or "").strip())
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_release_year(iso_or_text: str) -> int | None:
    t = (iso_or_text or "").strip()
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).year
    except Exception:
        pass
    return first_int4(t)


def parse_lang(url: str) -> str | None:
    m = re.search(r"[?&]l=([a-z]{2})(?:&|$)", url or "")
    return m.group(1) if m else None
