from __future__ import annotations

from typing import TYPE_CHECKING

from client.apple_tv.attributes import Attributes, item_from_attributes
from client.apple_tv.extract import get_apple_tv_artworks
from client.google.scoring import REQUIRED_SCORE, TargetSpec
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

        attributes, poster_url, background_url, logo_url = get_apple_tv_artworks(
            apple_tv_url
        )
        target = TargetSpec(
            title=title,
            directors=directors,
            year=year,
            country=country,
            entity=entity,
        )
        if not self.validate_attributes(attributes, apple_tv_url, target):
            return None, None, None

        return poster_url, background_url, logo_url

    def validate_attributes(
        self, attributes: Attributes | None, apple_tv_url: str, target: TargetSpec
    ) -> bool:
        if not attributes:
            return False

        item = item_from_attributes(apple_tv_url, attributes)
        score = self.search_engine.scorer.compute(item, target)
        return score is not None and score >= REQUIRED_SCORE
