from client.tmdb.api import TMDBAPIRequester


class MetadataManager:
    def __init__(self, api_requester: TMDBAPIRequester) -> None:
        self.api_requester = api_requester
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

    def get_localized_title(self, movie_id: int, country: str) -> str | None:
        """Fetch the localized title for a movie based on the country."""
        if country not in self.country_languages:
            raise ValueError(f"Unsupported country code: {country}")
        return self.get_movie_title(movie_id, self.country_languages[country])

    def get_movie_title(self, movie_id: int, language: str) -> str | None:
        """Fetch the movie title by its ID."""
        title = self.api_requester.get_movie_title(movie_id, language)
        return title

    def get_movie_logo_url(self, movie_id: int, language: str) -> str | None:
        """Fetch the movie logo by its ID."""
        logo = self.api_requester.get_movie_logo_url(movie_id, language)
        return logo
