from __future__ import annotations

from typing import TYPE_CHECKING

from client.apple_tv.extract import get_apple_tv_artworks
from services.provider.base import Provider

if TYPE_CHECKING:
    from client.google.search_engine import SearchEngine


class AppleProvider(Provider):
    """Metadata source that combines iTunes and Apple TV data."""

    @property
    def name(self) -> str:
        return "apple"

    def __init__(self, search_engine: SearchEngine) -> None:
        self.search_engine = search_engine

    def get_artworks(
        self,
        title: str,
        directors: list[str],
        year: int,
        country: str,
        entity: str = "movie",
    ) -> tuple[str | None, str | None, str | None]:

        apple_tv_url = self.search_engine.query(title, directors, year, country, entity)
        if not apple_tv_url:
            return None, None, None

        _, poster_url, background_url, logo_url = get_apple_tv_artworks(apple_tv_url)
        return poster_url, background_url, logo_url
