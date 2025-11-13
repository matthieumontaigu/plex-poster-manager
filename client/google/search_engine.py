from __future__ import annotations

import logging
import os
import time

import requests

from client.google.scoring import (
    REQUIRED_SCORE,
    STRONG_SCORE,
    Scorer,
    TargetSpec,
    item_from_cse,
)
from client.google.utils import quote

logger = logging.getLogger(__name__)

GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


class SearchEngine:
    """
    Thin Google Programmable Search client for tv.apple.com.
    - country/entity-scoped queries only: site:tv.apple.com/{country}/{entity}
    - scoring/gating delegated to Scorer (easy to unit-test)
    """

    def __init__(
        self,
        api_key: str,
        cse_id: str,
        *,
        session: requests.Session | None = None,
        min_interval_s: float = 0.5,
        timeout_s: float = 20.0,
        scorer: Scorer | None = None,
    ) -> None:
        self.api_key = api_key
        self.cse_id = cse_id
        if not self.api_key or not self.cse_id:
            raise ValueError("Google API key and CSE ID are required (args or env).")

        self.session = session or requests.Session()
        self.min_interval_s = float(min_interval_s)
        self.timeout_s = float(timeout_s)
        self._last_call_ts = 0.0
        self.query_count = 0

        self.scorer = scorer or Scorer()

    # --- public API ---

    def query(
        self,
        title: str,
        directors: list[str],
        year: int,
        country: str,
        entity: str,  # "movie" | "show"
    ) -> str | None:
        entity = self._normalize_entity(entity)
        country = self._normalize_country(country)

        target = TargetSpec(
            title=title, directors=directors, year=year, country=country, entity=entity
        )
        queries = self._build_queries(title, directors, country, entity)

        best_score, best_url = 0.0, None
        seen: set[str] = set()

        for q in queries:
            for raw in self._google_search(q):
                item = item_from_cse(raw)
                if item.url in seen:
                    continue
                seen.add(item.url)

                if not self.scorer.is_candidate_url(item.url):
                    continue

                score = self.scorer.compute(item, target)
                logger.debug("Score: %s, Item: %s", score, item)
                if score is None:
                    continue

                if score > best_score:
                    best_score, best_url = score, item.url
                    if best_score >= STRONG_SCORE:
                        return best_url

        return best_url if best_score >= REQUIRED_SCORE else None

    # --- internals ---

    def _build_queries(
        self,
        title: str,
        directors: list[str],
        country: str,
        entity: str,
    ) -> list[str]:
        base = f"site:tv.apple.com/{country}/{entity} {title}"
        queries: list[str] = []
        if directors:
            queries.append(f"{base} {quote(directors[0])}")
        queries.append(base)
        return queries

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
                return r.json().get("items") or []
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


class _TransientHTTPError(Exception):
    def __init__(self, status: int, msg: str = ""):
        super().__init__(f"Transient HTTP {status}: {msg}")
        self.status = status
