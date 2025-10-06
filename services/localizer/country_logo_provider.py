from __future__ import annotations

from typing import TYPE_CHECKING

from models.artworks import build_image

if TYPE_CHECKING:
    from models.artworks import Image
    from models.movie import Movie
    from services.localizer.localizer import Localizer
    from services.provider.logo.base import LogoProvider


class CountryLogoProvider:

    def __init__(
        self, logo_provider: LogoProvider, localizer: Localizer, country: str
    ) -> None:
        self.logo_provider = logo_provider
        self.localizer = localizer
        self.country = country
        self.language = self.localizer.get_language(country)
        self.locale_code = self.localizer.get_locale_code(country)
        self.source = logo_provider.name

        self.base_image = {
            "country": self.country,
            "language": self.language,
            "source": self.source,
        }

    def get_logo(self, movie: Movie) -> Image | None:
        tmdb_id = movie["tmdb_id"]
        if not tmdb_id:
            return None

        localized_title = self.localizer.get_localized_title(movie, self.language)
        if not localized_title:
            return None

        logo_url = self.logo_provider.get_logo(tmdb_id, self.locale_code)

        base_image = {"title": localized_title, **self.base_image}
        logo = build_image(logo_url, **base_image)
        return logo
