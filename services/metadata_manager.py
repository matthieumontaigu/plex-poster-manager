from client.tmdb.api import TMDBAPIRequester


class MetadataManager:
    def __init__(self, api_requester: TMDBAPIRequester) -> None:
        self.api_requester = api_requester
        self.country_languages = {"fr": "fr", "us": "en", "gb": "en", "ca": "fr"}

    def get_localized_title(self, movie_id: int, country: str) -> str:
        """Fetch the localized title for a movie based on the country."""
        if country not in self.country_languages:
            raise ValueError(f"Unsupported country code: {country}")
        return self.get_movie_title(movie_id, self.country_languages[country])

    def get_movie_title(self, movie_id: int, language: str) -> str:
        """Fetch the movie title by its ID."""
        title = self.api_requester.get_movie_title(movie_id, language)
        return title
