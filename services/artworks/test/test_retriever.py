import unittest
from unittest.mock import MagicMock, patch

from models.movie import Movie
from services.artworks.retriever import ArtworksRetriever
from services.artworks.rules import ArtworkRuleset


class TestArtworksUpdater(unittest.TestCase):
    def setUp(self):
        self.provider = MagicMock()
        self.provider.name = "apple"
        self.localizer = MagicMock()
        self.logo_provider = MagicMock()
        self.logo_provider.name = "tmdb"

        self.time_patcher = patch("time.sleep", return_value=None)
        self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)

    def test_get_artworks_no_artworks(self):
        """Movie not found, no artworks"""

        countries = ["fr"]
        self.provider.get_artworks.return_value = (None, None, None)

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_no_artworks_multiple_countries(self):
        """Movie not found, no artworks"""

        countries = ["fr", "us", "gb", "de", "lu"]
        self.provider.get_artworks.return_value = (None, None, None)

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_simple_case(self):
        """Movie found in FR"""
        countries = ["fr"]
        self.provider.get_artworks.return_value = (
            "poster_url_fr",
            "background_url_fr",
            "logo_url_fr",
        )
        self.localizer.get_localized_title.return_value = (
            "Captain America : Brave New World"
        )

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries(self):
        """Movie found in FR and US"""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", "logo_url_fr"),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_background_missing(self):
        """Movie found in FR and US, background only in US."""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            ("poster_url_fr", None, "logo_url_fr"),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_logo_missing(self):
        """Movie found in FR and US, logo only in US."""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_background_and_logo_missing(self):
        """Movie found in FR and US, background and logo only in US."""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            ("poster_url_fr", None, None),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_FR_missing(self):
        """Movie not found in FR, but found in US, so US poster and logo used."""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            (None, None, None),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]

        self.artworks_retriever = ArtworksRetriever(
            self.provider, self.localizer, countries
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_logo_missing_fallback_FR(self):
        """Movie found in FR and US, logo only in US, fallback logo found in TMDB"""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None),
            ("poster_url_us", "background_url_us", "logo_url_us"),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]
        self.logo_provider.get_logo.return_value = "fallback_logo_url"

        self.artworks_retriever = ArtworksRetriever(
            self.provider,
            self.localizer,
            countries,
            fallback_logo_provider=self.logo_provider,
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": 1111,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "fr",
                "title": "Captain America : Brave New World",
                "source": "tmdb",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_logo_missing_fallback_US(self):
        """Movie only found in US without logo, fallback logo found in TMDB"""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            (None, None, None),
            ("poster_url_us", "background_url_us", None),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]
        self.logo_provider.get_logo.return_value = "fallback_logo_url"

        self.artworks_retriever = ArtworksRetriever(
            self.provider,
            self.localizer,
            countries,
            fallback_logo_provider=self.logo_provider,
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": 1111,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": None,
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "tmdb",
            },
        }
        self.assertEqual(artworks, expected_artworks)

    def test_get_artworks_two_countries_logo_missing_fallback_US_not_found(self):
        """Movie only found in US without logo, fallback logo not found in TMDB"""

        countries = ["fr", "us"]
        self.provider.get_artworks.side_effect = [
            (None, None, None),
            ("poster_url_us", "background_url_us", None),
        ]
        self.localizer.get_localized_title.side_effect = [
            "Captain America : Brave New World",
            "Captain America : Brave New World",
        ]
        self.logo_provider.get_logo.return_value = None

        self.artworks_retriever = ArtworksRetriever(
            self.provider,
            self.localizer,
            countries,
            fallback_logo_provider=self.logo_provider,
        )

        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Captain America : Brave New World",
            "year": 2025,
            "added_date": 1700000000,
            "release_date": "2025-02-12",
            "director": ["Julius Onah"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": 1111,
        }

        artworks = self.artworks_retriever.retrieve(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
                "source": "apple",
            },
            "logo": None,
        }
        self.assertEqual(artworks, expected_artworks)


if __name__ == "__main__":
    unittest.main()
