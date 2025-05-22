import time

from client.apple_tv.extract import get_apple_tv_artworks
from client.itunes.extract import get_itunes_artworks
from client.tmdb.api import TMDBAPIRequester


class MetadataRetriever:
    def __init__(self, tmdb_api_requester: TMDBAPIRequester) -> None:
        self.tmdb_api_requester = tmdb_api_requester
        self.api_call_interval = 1.0
        self.country_languages = {
            "fr": "fr",
            "us": "en",
            "gb": "en",
            "au": "en",
            "nz": "en",
            "ca": "fr",
            "be": "fr",
            "lu": "fr",
            "ch": "fr",
            "de": "de",
            "it": "it",
            "es": "es",
        }

    def get_localized_title(self, movie_id: int | None, country: str) -> str | None:
        """Fetch the localized title for a movie based on the country."""
        if country not in self.country_languages:
            raise ValueError(f"Unsupported country code: {country}")
        if not movie_id:
            return None
        return self.get_movie_title(movie_id, self.country_languages[country])

    def get_movie_title(self, movie_id: int, language: str) -> str | None:
        """Fetch the movie title by its ID."""
        title = self.tmdb_api_requester.get_movie_title(movie_id, language)
        return title

    def get_tmdb_logo_url(self, movie_id: int | None, language: str) -> str | None:
        """Fetch the movie logo by its ID."""
        if not movie_id:
            return None
        return self.tmdb_api_requester.get_movie_logo_url(movie_id, language)

    def get_apple_artworks(
        self, title: str, directors: list[str], year: int, country: str
    ) -> tuple[str, str, str, str] | None:
        artworks = get_itunes_artworks(title, directors, year, country)
        if artworks is None:
            return None

        itunes_url, poster_url, release_date = artworks

        time.sleep(self.api_call_interval)

        background_url, logo_url = get_apple_tv_artworks(itunes_url)
        return poster_url, background_url, logo_url, release_date
