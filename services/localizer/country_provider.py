from __future__ import annotations

from typing import TYPE_CHECKING

from models.artworks import build_image, build_metadata

if TYPE_CHECKING:
    from models.artworks import Image, Metadata
    from models.movie import Movie
    from services.localizer.localizer import Localizer
    from services.provider.base import Provider


class CountryProvider:

    def __init__(self, provider: Provider, localizer: Localizer, country: str) -> None:
        self.provider = provider
        self.localizer = localizer
        self.country = country
        self.language = self.localizer.get_language(country)
        self.source = provider.name

        self.base_image = {
            "country": self.country,
            "language": self.language,
            "source": self.source,
        }

    def get_artworks(
        self, movie: Movie, localized_title: str
    ) -> tuple[Image | None, Image | None, Image | None, Metadata | None]:
        search_args = (localized_title, movie["director"], movie["year"], self.country)

        base_image = {"title": localized_title, **self.base_image}

        poster_url, background_url, logo_url = self.provider.get_artworks(*search_args)

        poster = build_image(poster_url, **base_image)
        background = build_image(background_url, **base_image)
        logo = build_image(logo_url, **base_image)

        release_date_str = self.provider.get_release_date(*search_args)
        release_date = build_metadata(release_date_str, self.country)

        return poster, background, logo, release_date

    def get_localized_title(self, movie: Movie) -> str | None:
        return self.localizer.get_localized_title(movie, self.language)
