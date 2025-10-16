from __future__ import annotations

from typing import TYPE_CHECKING

from models.countries import get_locale_code
from services.provider.logo.base import LogoProvider

if TYPE_CHECKING:
    from client.tmdb.api import TMDBAPIRequester


class TMDBLogoProvider(LogoProvider):
    """Fetches a localized logo from TMDB if available."""

    def __init__(self, tmdb_api_requester: TMDBAPIRequester):
        self.tmdb_api_requester = tmdb_api_requester

    @property
    def name(self) -> str:
        return "tmdb"

    def get_logo(self, movie_id: int, country: str) -> str | None:
        locale = get_locale_code(country)
        return self.tmdb_api_requester.get_movie_logo_url(movie_id, locale)
