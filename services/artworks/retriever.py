from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from services.artworks.fallback_logo import FallbackLogoProvider
from services.localizer.country_provider import CountryProvider

if TYPE_CHECKING:
    from models.artworks import Artworks, Image
    from models.movie import Movie
    from services.localizer.localizer import Localizer
    from services.provider.base import Provider
    from services.provider.logo.base import LogoProvider

logger = logging.getLogger(__name__)


class ArtworksRetriever:
    """Fetches and assembles artworks from external metadata sources (Apple, TMDB)."""

    def __init__(
        self,
        provider: Provider,
        localizer: Localizer,
        countries_priority: list[str],
        retrieve_interval: float = 1.0,
        fallback_logo_provider: LogoProvider | None = None,
    ):
        if len(countries_priority) == 0:
            raise ValueError("At least one country must be specified")

        self.provider = provider
        self.localizer = localizer
        self.retrieve_interval = retrieve_interval

        self.countries_providers = [
            CountryProvider(provider, localizer, country)
            for country in countries_priority
        ]
        self.fallback_logo_provider = (
            FallbackLogoProvider(fallback_logo_provider)
            if fallback_logo_provider
            else None
        )

    def retrieve(self, movie: Movie) -> Artworks:
        artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }

        for country_provider in self.countries_providers:
            logger.info(
                f"Fetching {country_provider.country.upper()} artworks for '{movie['title']}'"
            )
            poster, background, logo = country_provider.get_artworks(movie)

            self.update_image(artworks, "poster", poster)
            self.update_image(artworks, "background", background)
            self.update_image(artworks, "logo", logo)

            if self.is_complete(artworks):
                break

            time.sleep(self.retrieve_interval)

        if self.fallback_logo_provider:
            fallback_logo = self.fallback_logo_provider.get_logo(movie, artworks)
            self.update_image(artworks, "fallback_logo", fallback_logo)

        return artworks

    def update_image(
        self, artworks: Artworks, artwork_name: str, new_image: Image | None
    ) -> None:
        current_image: Image | None = artworks.get(artwork_name)
        if new_image is None or current_image is not None:
            return None

        artworks[artwork_name] = new_image
        logger.info(
            f"Found {new_image['source']} {new_image['country'].upper()} {artwork_name} from  for '{new_image['title']}'"
        )
        return None

    def is_complete(self, artworks: Artworks) -> bool:
        return all(artworks[key] for key in ["poster", "background", "logo"])
