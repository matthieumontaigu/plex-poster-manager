from __future__ import annotations

import html
import re
import unicodedata

# ---------- text normalization & similarity ----------


def strip_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )


def norm_text(s: str) -> str:
    s = html.unescape((s or "").strip().lower())
    s = strip_accents(s)
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def similarity(a: str, b: str) -> float:
    # Lightweight, deterministic similarity without external deps (SequenceMatcher).
    # You can swap for rapidfuzz if you prefer.
    from difflib import SequenceMatcher

    a_n, b_n = norm_text(a), norm_text(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()


def quote(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return f'"{s}"' if " " in s else s


# ---------- dates & URL helpers ----------


def first_int4(s: str) -> int | None:
    m = re.search(r"\b(19|20)\d{2}\b", s or "")
    return int(m.group(0)) if m else None


def normalize_url(url: str) -> str:
    if not url:
        return url
    return url.split("#", 1)[0].split("?", 1)[0]


def extract_path(url: str) -> str:
    m = re.match(r"^https?://[^/]+(/.*)$", url)
    return m.group(1) if m else "/"
