from __future__ import annotations

from typing import TYPE_CHECKING

from models.artworks import build_image
from utils.string_utils import are_match

if TYPE_CHECKING:
    from models.artworks import Artworks, Image
    from models.movie import Movie
    from services.provider.logo.base import LogoProvider


class FallbackLogoProvider:

    def __init__(self, logo_provider: LogoProvider) -> None:
        self.logo_provider = logo_provider

    def get_logo(self, movie: Movie, artworks: Artworks) -> Image | None:
        poster = artworks["poster"]
        if not poster:
            return None

        return self.fetch_logo(movie, poster["country"], poster["title"])

    def fetch_logo(self, movie: Movie, country: str, title: str) -> Image | None:
        tmdb_id = movie["tmdb_id"]
        if not tmdb_id:
            return None

        logo_url = self.logo_provider.get_logo(tmdb_id, country)

        base_logo = {
            "title": title,
            "country": country,
            "source": self.logo_provider.name,
        }
        logo = build_image(logo_url, **base_logo)
        return logo
