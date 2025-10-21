# search/apple_tv_search_engine.py

from __future__ import annotations

import html
import logging
import os
import re
import time
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher

import requests

logger = logging.getLogger(__name__)

GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
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
STRONG_MATCH = 9.5  # a bit higher since we enforce metadata

# ---------------------- helper scoring you provided --------------------------


def get_year_score(target_year: int, year: int) -> float:
    if target_year <= year <= target_year + 1:
        return 1.0
    if year < target_year - 2 or year > target_year + 2:
        return -1.0
    return 0.0


# ---------------------- small utils -----------------------------------------


def _strip_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )


def _norm_text(s: str) -> str:
    s = html.unescape((s or "").strip().lower())
    s = _strip_accents(s)
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _similarity(a: str, b: str) -> float:
    """Return similarity in [0,1] using SequenceMatcher over normalized strings."""
    a_n = _norm_text(a)
    b_n = _norm_text(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def _first_int4(s: str) -> int | None:
    """Find a 4-digit year."""
    m = re.search(r"\b(19|20)\d{2}\b", s or "")
    return int(m.group(0)) if m else None


def _parse_release_year(iso_or_text: str) -> int | None:
    """
    Accepts full ISO ('2025-05-14T00:00:00Z') or anything containing a year
    and returns the year as int.
    """
    t = (iso_or_text or "").strip()
    # ISO-8601 quick path
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).year
    except Exception:
        pass
    return _first_int4(t)


# ---------------------- data model (optional future use) ---------------------


@dataclass(slots=True)
class ItemView:
    url: str
    page_title: str
    apple_title: str | None
    director: str | None
    release_year: int | None


# ---------------------- main class ------------------------------------------


class SearchEngine:
    """
    Google Programmable Search (Custom Search JSON API) helper for tv.apple.com.

    Enforced matching (robust mode):
      - apple:title ~ title  >= 0.90  (reject otherwise, if apple:title present)
      - og:video:director ~ any(directors) >= 0.90  (when directors provided and tag present)
      - og:video:release_date feeds year scoring (get_year_score)
    """

    def __init__(
        self,
        api_key: str | None = None,
        cse_id: str | None = None,
        *,
        session: requests.Session | None = None,
        min_interval_s: float = 1.0,
        timeout_s: float = 15.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")
        if not self.api_key or not self.cse_id:
            raise ValueError("Google API key and CSE ID are required (args or env).")

        self.session = session or requests.Session()
        self.min_interval_s = float(min_interval_s)
        self.timeout_s = float(timeout_s)
        self._last_call_ts = 0.0
        self.query_count = 0  # local accounting if you need it

    # -- main entry -----------------------------------------------------------

    def query(
        self,
        title: str,
        directors: Iterable[str] | None,
        year: int | None,
        country: str,
        entity: str,  # "movie" | "show"
    ) -> str | None:
        entity = self._normalize_entity(entity)
        country = self._normalize_country(country)
        directors_list = [d for d in (directors or []) if d]

        queries = self._build_queries(title, directors_list, year, country, entity)
        best_score, best_url = 0.0, None

        for q in queries:
            for raw in self._google_search(q):
                item = self._project_item(raw)
                if not self._is_candidate_url(item.url):
                    continue

                # --- metadata gates (strict) ---
                # apple:title gate (if present)
                if item.apple_title:
                    if _similarity(item.apple_title, title) < 0.90:
                        continue  # hard reject

                # director gate (if provided + present)
                if directors_list and item.director:
                    if not self._director_ok(directors_list, item.director):
                        continue  # hard reject

                score = self._base_score(item.url, item.page_title, title, country)
                # Add year score if both provided (else neutral)
                if year and item.release_year:
                    score += get_year_score(year, item.release_year)

                if score > best_score:
                    best_score, best_url = score, item.url
                    if best_score >= STRONG_MATCH:
                        return best_url

        return best_url

    # -- query construction ---------------------------------------------------

    def _build_queries(
        self,
        title: str,
        directors: list[str],
        year: int | None,
        country: str,
        entity: str,
    ) -> list[str]:
        t = self._quote(title)
        base = f"site:tv.apple.com/{country}/{entity} {t}"

        queries: list[str] = []
        if year:
            queries.append(f'{base} "{year}"')
        if directors:
            queries.append(f"{base} {self._quote(directors[0])}")
        queries.append(base)
        return queries

    # -- google api -----------------------------------------------------------

    def _google_search(self, query: str, num: int = 10) -> list[dict]:
        self._respect_min_interval()
        self.query_count += 1

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(max(num, 1), 10),
            "safe": "off",
        }

        backoff = 0.6
        for attempt in range(4):
            try:
                r = self.session.get(
                    GOOGLE_ENDPOINT, params=params, timeout=self.timeout_s
                )
                if r.status_code in (429, 500, 502, 503, 504):
                    raise _TransientHTTPError(r.status_code, r.text)
                r.raise_for_status()
                data = r.json()
                return data.get("items", []) or []
            except _TransientHTTPError as e:
                if attempt == 3:
                    logger.warning(
                        "Google CSE transient %s (final) for %r", e.status, query
                    )
                    return []
                time.sleep(backoff)
                backoff *= 1.6
            except requests.RequestException as e:
                logger.warning("Google CSE request failed: %s", e)
                return []
            finally:
                self._last_call_ts = time.monotonic()
        return []

    def _respect_min_interval(self) -> None:
        delta = time.monotonic() - self._last_call_ts
        if delta < self.min_interval_s:
            time.sleep(self.min_interval_s - delta)

    # -- projection & filters -------------------------------------------------

    def _project_item(self, raw: dict) -> ItemView:
        url = self._normalize_url(raw.get("link", ""))
        page_title = raw.get("title") or ""

        metatags = {}
        try:
            # Google CSE usually flattens to a single dict in list
            meta_list = raw.get("pagemap", {}).get("metatags", [])
            if meta_list:
                metatags = dict(meta_list[0])  # shallow copy
        except Exception:
            metatags = {}

        apple_title = metatags.get("apple:title") or None
        director = metatags.get("og:video:director") or None
        release_raw = metatags.get("og:video:release_date") or None
        release_year = _parse_release_year(release_raw) if release_raw else None

        return ItemView(
            url=url,
            page_title=page_title,
            apple_title=apple_title,
            director=director,
            release_year=release_year,
        )

    def _is_candidate_url(self, url: str) -> bool:
        if not (url and url.startswith("https://tv.apple.com/")):
            return False
        return not DISALLOWED_RE.search(self._extract_path(url))

    # -- scoring --------------------------------------------------------------

    def _base_score(
        self,
        url: str,
        page_title: str,
        requested_title: str,
        locale: str,
    ) -> float:
        score = 0.0
        path = self._extract_path(url)

        if CANONICAL_RE.match(path):
            score += 4.0
        elif f"/{locale}/" in path and ("/movie/" in path or "/show/" in path):
            score += 2.5

        if f"/{locale}/" in path:
            score += 1.2

        # Title token overlap (fallback signal; metadata already gated)
        req = self._tokens(requested_title)
        tit = self._tokens(page_title)
        if req and tit:
            score += min(3.0, 0.8 * len(req & tit))

        if "utm_" in url or "?" in url:
            score -= 0.2

        return score

    # -- director strict matching --------------------------------------------

    def _director_ok(self, targets: list[str], candidate: str) -> bool:
        """
        Accept if ANY target director is >= 0.90 similar to the candidate string.
        Candidate might contain multiple names (commas, ampersands).
        """
        cand = _norm_text(candidate)
        if not cand:
            return False

        # Fast path: explicit containment as normalized substring
        for t in targets:
            tn = _norm_text(t)
            if not tn:
                continue
            if tn in cand or cand in tn:
                return True
            if _similarity(tn, cand) >= 0.90:
                return True

        # Split candidate on common delimiters and compare parts
        parts = re.split(r"[,&/]| et | and ", cand)
        parts = [p.strip() for p in parts if p.strip()]
        for t in targets:
            tn = _norm_text(t)
            if not tn:
                continue
            if any(_similarity(tn, p) >= 0.90 for p in parts):
                return True

        return False

    # -- small utils ----------------------------------------------------------

    @staticmethod
    def _normalize_url(url: str) -> str:
        if not url:
            return url
        return url.split("#", 1)[0].split("?", 1)[0]

    @staticmethod
    def _extract_path(url: str) -> str:
        m = re.match(r"^https?://[^/]+(/.*)$", url)
        return m.group(1) if m else "/"

    @staticmethod
    def _quote(s: str) -> str:
        s = (s or "").strip()
        s = re.sub(r"\s+", " ", s)
        return f'"{s}"' if " " in s else s

    @staticmethod
    def _tokens(text: str) -> set[str]:
        t = _norm_text(text)
        return {w for w in t.split() if len(w) > 1}

    @staticmethod
    def _normalize_entity(entity: str) -> str:
        e = (entity or "").strip().lower()
        if e not in {"movie", "show"}:
            raise ValueError("entity must be 'movie' or 'show'")
        return e

    @staticmethod
    def _normalize_country(country: str) -> str:
        c = (country or "").strip().lower()
        if not c:
            raise ValueError("country (lowercase) is required")
        return c


# --- errors ------------------------------------------------------------------


class _TransientHTTPError(Exception):
    def __init__(self, status: int, msg: str = ""):
        super().__init__(f"Transient HTTP {status}: {msg}")
        self.status = status
