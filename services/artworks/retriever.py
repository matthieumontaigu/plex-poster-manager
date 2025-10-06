from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from services.artworks.selector import ArtworkSelector
from services.localizer.country_logo_provider import CountryLogoProvider
from services.localizer.country_provider import CountryProvider

if TYPE_CHECKING:
    from models.artworks import Artworks, Image
    from models.movie import Movie
    from services.artworks.rules import ArtworkRuleset
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
        artworks_ruleset: ArtworkRuleset,
        countries_priority: list[str],
        retrieve_interval: float = 1.0,
        fallback_logo_provider: LogoProvider | None = None,
    ):
        if len(countries_priority) == 0:
            raise ValueError("At least one country must be specified")

        self.provider = provider
        self.localizer = localizer
        self.artworks_ruleset = artworks_ruleset
        self.retrieve_interval = retrieve_interval
        self.fallback_logo_provider = fallback_logo_provider

        self.countries_providers = [
            CountryProvider(provider, localizer, country)
            for country in countries_priority
        ]

    def retrieve(self, movie: Movie) -> Artworks:
        artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
            "release_date": None,
        }
        selector = ArtworkSelector(artworks, self.artworks_ruleset, movie)

        for country_provider in self.countries_providers:
            localized_title = country_provider.get_localized_title(movie)
            if not localized_title:
                continue

            if not selector.can_accept(localized_title):
                continue

            logger.info(
                f"Fetching {country_provider.country.upper()} artworks for '{movie['title']}'"
            )
            poster, background, logo, release_date = country_provider.get_artworks(
                movie, localized_title
            )
            if selector.update_image("poster", poster):
                self.log_found_image("poster", poster)

            if selector.update_image("background", background):
                self.log_found_image("background", background)

            if selector.update_image("logo", logo):
                self.log_found_image("logo", logo)

            selector.update_metadata("release_date", release_date)

            if selector.is_complete():
                break

            time.sleep(self.retrieve_interval)

        fallback_logo = self.fetch_fallback_logo(movie, selector)
        if selector.update_image("logo", fallback_logo):
            self.log_found_image("logo", fallback_logo)

        return artworks

    def fetch_fallback_logo(
        self, movie: Movie, selector: ArtworkSelector
    ) -> Image | None:
        if self.fallback_logo_provider is None:
            return None

        country_to_match = selector.get_country_to_match_logo()
        if not country_to_match:
            return None

        country_logo_provider = CountryLogoProvider(
            self.fallback_logo_provider, self.localizer, country_to_match
        )
        return country_logo_provider.get_logo(movie)

    def log_found_image(self, name: str, image: Image | None) -> None:
        if image is None:
            return
        logger.info(
            f"Found {image['source']} {image['country'].upper()} {name} from  for '{image['title']}'"
        )
