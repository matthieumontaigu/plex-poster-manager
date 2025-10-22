from __future__ import annotations

import re
from dataclasses import dataclass

from client.google.utils import (
    clean_title,
    extract_path,
    norm_text,
    parse_release_year,
    similarity,
)

DISALLOWED_RE = re.compile(
    "|".join(
        [
            r"/search\?",
            r"^/api\b",
            r"^/uts/",
            r"ctx_shelf=edt\.shelf\.PersonShelf1",
            r"^/includes/commerce/",
            r"/sporting-event/",
            r"/collection/(trailers|related|bonus-content|clubs|spotlight|other-games)/",
        ]
    )
)

CANONICAL_RE = re.compile(r"^/([a-z]{2,3})/(show|movie)/.+/umc\.cm[cp]\.[\w.]+/?$")


@dataclass(slots=True)
class ItemView:
    url: str
    title: str | None
    director: str | None
    release_year: int | None


@dataclass(slots=True)
class TargetSpec:
    title: str
    directors: list[str]
    year: int
    country: str
    entity: str  # "movie" | "show"


STRONG_SCORE = 4.0  # 2.0 for title match, 1.0 for director, 1.0 for year
REQUIRED_SCORE = 1.9  # at least a title match at 95% or matching director and year


class Scorer:
    """
    Computes a score for a Google CSE item projected to ItemView against a TargetSpec.
    """

    def __init__(
        self,
        *,
        title_threshold: float = 0.75,
    ) -> None:
        self.title_threshold = title_threshold

    def is_candidate_url(self, url: str) -> bool:
        if not (url and url.startswith("https://tv.apple.com/")):
            return False
        return not DISALLOWED_RE.search(extract_path(url))

    def compute(self, item: ItemView, target: TargetSpec) -> float | None:
        path = extract_path(item.url)
        if not CANONICAL_RE.match(path):
            return None

        if not f"/{target.entity}/" in path:
            return None

        if not f"/{target.country}/" in path:
            return None

        title_score = 0.0
        if item.title:
            title_score = get_title_score(
                target.title, item.title, self.title_threshold
            )
            if title_score < 0:
                return None

        year_score = 0.0
        if item.release_year:
            year_score = get_year_score(target.year, item.release_year)
            if year_score < 0:
                return None

        director_score = 0.0
        if item.director:
            director_score = get_director_score(target.directors, item.director)
            if director_score < 0:
                return None

        return title_score + director_score + year_score


def get_title_score(target_title: str, title: str, threshold: float) -> float:
    similarity_score = similarity(target_title, title)
    if similarity_score < 0.5:
        return -1.0
    if similarity_score < threshold:
        return 0.0
    return similarity_score * 2.0


def get_year_score(target_year: int, year: int) -> float:
    if target_year <= year <= target_year + 1:
        return 1.0
    if year < target_year - 2 or year > target_year + 2:
        return -1.0
    return 0.0


def get_director_score(target_directors: list[str], director: str | None) -> float:
    """
    Compute a signed score for director similarity.

    Returns:
        1.0  → strong match (director clearly matches one of the targets)
        0.0  → uncertain or no information
       -1.0  → strong mismatch (different people, avoid false positives)
    """
    if not target_directors or not director or director == "Unknown":
        return 0.0

    # Normalize and flatten
    director_norm = norm_text(director)
    if not director_norm:
        return 0.0

    # Strong match if any target is included in candidate string
    for target_director in target_directors:
        target_norm = norm_text(target_director)
        if not target_norm:
            continue
        if similarity(target_norm, director_norm) >= 0.9:
            return 1.0

    # Otherwise aggregate all targets into one string
    target_combined = "".join(norm_text(d) for d in target_directors)
    sim = similarity(target_combined, director_norm)

    return -1.0 if sim < 0.5 else 0.0


# ---------------- helper to build ItemView from CSE raw ----------------


def item_from_cse(raw: dict) -> ItemView:
    url = (raw.get("link") or "").split("#", 1)[0].split("?", 1)[0]

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

    return ItemView(
        url=url,
        title=title,
        director=director,
        release_year=release_year,
    )
