from __future__ import annotations

from typing import TYPE_CHECKING

from models.countries import LANGUAGE_CODES

if TYPE_CHECKING:
    from client.tmdb.api import TMDBAPIRequester
    from models.movie import Movie


class Localizer:
    """
    Handles localization and translation of movie titles across countries.

    This class resolves a movie title into its localized version for a specific country
    using TMDB as the primary source of translation data.
    """

    locales = {
        "fr": "fr-FR",
        "us": "en-US",
        "gb": "en-US",
        "ca": "fr-FR",
        "de": "de-DE",
        "it": "it-IT",
        "es": "es-ES",
    }

    def __init__(self, tmdb_api_requester: TMDBAPIRequester) -> None:
        """
        Args:
            tmdb_api_requester:
                Instance of TMDBAPIRequester used to query movie information from TMDB.
        """
        self.tmdb_api_requester = tmdb_api_requester
        self.country_languages = LANGUAGE_CODES

    def get_localized_title(self, movie: Movie, country: str) -> str | None:
        if country == movie["metadata_country"]:
            return movie["title"]

        tmdb_id = movie["tmdb_id"]
        if not tmdb_id:
            return None

        localized_title = self.get_country_title(tmdb_id, country)
        return localized_title

    def get_country_title(self, movie_id: int, country: str) -> str | None:
        """
        Retrieve the localized movie title for a given country.

        Args:
            movie_id: TMDB movie ID.
            country: Target country code (e.g. 'fr', 'us', 'de').

        Returns:
            The localized title string, or None if not found.
        """
        language = self.get_language(country)
        return self.get_language_title(movie_id, language)

    def get_language_title(self, movie_id: int, language: str) -> str | None:
        """Fetch the localized movie title from TMDB for a given language."""
        return self.tmdb_api_requester.get_movie_title(movie_id, language)

    def get_language(self, country: str) -> str:
        """Resolve a TMDB language code for a given country code."""
        if country not in self.country_languages:
            raise ValueError(f"Unsupported country code: {country}")

        return self.country_languages[country]

    def get_locale_code(self, country: str) -> str:
        """Resolve a TMDB logo language code for a given country code."""
        language = self.get_language(country)
        return self.locales.get(language, language)
