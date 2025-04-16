import unittest
from unittest.mock import MagicMock, patch

from services.artworks_updater import ArtworksUpdater


class TestArtworksUpdater(unittest.TestCase):
    def setUp(self):
        self.plex_manager = MagicMock()
        self.metadata_retriever = MagicMock()

        self.time_patcher = patch("time.sleep", return_value=None)
        self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)

    def test_get_artworks_no_artworks(self):
        """Movie not found in iTunes, no artworks"""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [None]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {"poster": {}, "background": {}, "logo": {}}
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_no_artworks_multiple_countries(self):
        """Movie not found in iTunes, no artworks"""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us", "gb", "de", "lu"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            None,
            None,
            None,
            None,
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {"poster": {}, "background": {}, "logo": {}}
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_simple_case(self):
        """Movie found in iTunes, artworks available"""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", "logo_url_fr", "2025-02-12"),
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries(self):
        """Movie found in FR and US, artworks available in both countries, FR used."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", "logo_url_fr", "2025-02-12"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-02-14"),
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_background_missing(self):
        """Movie poster and found in FR and US, background only in US."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", None, "logo_url_fr", "2025-02-12"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-02-14"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = [
            "Captain America : Brave New World"
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_plex_country_match_title_1(self):
        """Movie not found in FR, but found in US, FR title does match US title (with match_title on). So US poster and logo used."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-02-14"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = [
            "Captain America : Brave New World"
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_plex_country_match_title_2(
        self,
    ):
        """Movie not found in FR, but found in US, FR title does not match US title (with match_title on). So US poster and logo ignored."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {},
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Snow White",
            },
            "logo": {},
        }
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_plex_country_match_title_3(
        self,
    ):
        """Movie not found in FR, but found in US, FR title does not match US title but ignored (with match_title off). So US poster and logo used."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=False,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {"url": "poster_url_us", "country": "us", "title": "Snow White"},
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Snow White",
            },
            "logo": {"url": "logo_url_us", "country": "us", "title": "Snow White"},
        }
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_logo_match_title_1(self):
        """Movie found in FR without FR logo, and FR title does match US title (with match_title on). US logo is used."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-02-12"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-02-14"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = [
            "Captain America : Brave New World"
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_logo_match_title_2(
        self,
    ):
        """Movie found in FR without FR logo, and FR title does not match US title (with match_title on), US logo is ignored."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-03-19"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "logo": {},
        }
        expected_release_date = "2025-03-19"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_no_logo_match_title_3(
        self,
    ):
        """Movie found in FR without FR logo, and FR title does not match US title, but ignored (with match_title off). US logo is used."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=False,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-03-19"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "logo": {"url": "logo_url_us", "country": "us", "title": "Snow White"},
        }
        expected_release_date = "2025-03-19"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode(
        self,
    ):
        """Movie found in FR without FR logo, and FR title does not match US title, but ignored (with match_title off). US logo is not matching poster so replaced by a TMDB Logo."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=False,
            match_logo=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-03-19"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]
        self.metadata_retriever.get_tmdb_logo_url.side_effect = ["logo_url_fr"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "logo": {
                "url": "logo_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
                "source": "tmdb",
            },
        }
        expected_release_date = "2025-03-19"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode_no_tmdb_logo(
        self,
    ):
        """Movie found in FR without FR logo, and FR title does not match US title, but ignored (with match_title off). US logo is not matching poster but kept because no TMDB Logo found."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=False,
            match_logo=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-03-19"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]
        self.metadata_retriever.get_tmdb_logo_url.side_effect = [None]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Blanche Neige",
            },
            "logo": {"url": "logo_url_us", "country": "us", "title": "Snow White"},
        }
        expected_release_date = "2025-03-19"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode_no_need_to_match_1(self):
        """Movie found in FR without FR logo, and FR title does match US title, so US logo is used. Logo matching is skipped because already matching."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
            match_logo=True,
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-02-12"),
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-02-14"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = [
            "Captain America : Brave New World"
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Captain America : Brave New World",
            },
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode_no_need_to_match_2(self):
        """Movie found in FR without FR logo nor US logo. Logo matching is skipped."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
            match_logo=True,
        )

        movie = {
            "title": "Captain America : Brave New World",
            "year": "2025",
            "director": ["Julius Onah"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            ("poster_url_fr", "background_url_fr", None, "2025-02-12"),
            ("poster_url_us", "background_url_us", None, "2025-02-14"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = [
            "Captain America : Brave New World"
        ]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "background": {
                "url": "background_url_fr",
                "country": "fr",
                "title": "Captain America : Brave New World",
            },
            "logo": {},
        }
        expected_release_date = "2025-02-12"

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode_no_need_to_match_3(
        self,
    ):
        """Movie not found in FR and FR title does not match US title, but ignored (with match_title off), so US artworks used. Logo matching is skipped because poster is US."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=False,
            match_logo=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {
                "url": "poster_url_us",
                "country": "us",
                "title": "Snow White",
            },
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Snow White",
            },
            "logo": {
                "url": "logo_url_us",
                "country": "us",
                "title": "Snow White",
            },
        }
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_get_artworks_two_countries_match_logo_mode_no_need_to_match_4(
        self,
    ):
        """Movie not found in FR and FR title does not match US title (with match_title on), so US artworks are ignored. Logo matching is skipped because no artworks."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
            countries=["fr", "us"],
            match_title=True,
            match_logo=True,
        )

        movie = {
            "title": "Blanche Neige",
            "year": "2025",
            "director": ["Marc Webb"],
            "plex_movie_id": 1111,
        }

        self.metadata_retriever.get_apple_artworks.side_effect = [
            None,
            ("poster_url_us", "background_url_us", "logo_url_us", "2025-03-21"),
        ]
        self.metadata_retriever.get_localized_title.side_effect = ["Snow White"]

        artworks, release_date = self.artworks_updater.get_artworks(movie)

        expected_artworks = {
            "poster": {},
            "background": {
                "url": "background_url_us",
                "country": "us",
                "title": "Snow White",
            },
            "logo": {},
        }
        expected_release_date = None

        self.assertEqual(artworks, expected_artworks)
        self.assertEqual(release_date, expected_release_date)

    def test_is_complete_all_artworks_match_plex_country(self):
        """All artworks match the Plex country, should return True."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
        )

        artworks = {
            "poster": {"url": "poster_url", "country": "fr"},
            "background": {"url": "background_url", "country": "fr"},
            "logo": {"url": "logo_url", "country": "fr"},
        }

        result = self.artworks_updater.is_complete(artworks)
        self.assertTrue(result)

    def test_is_complete_artwork_with_different_country(self):
        """At least one artwork has a different country, should return False."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
        )

        artworks = {
            "poster": {"url": "poster_url", "country": "fr"},
            "background": {"url": "background_url", "country": "us"},
            "logo": {"url": "logo_url", "country": "fr"},
        }

        result = self.artworks_updater.is_complete(artworks)
        self.assertFalse(result)

    def test_is_complete_all_artworks_match_plex_country_with_source(self):
        """All artworks match the Plex country but one has source, should return False."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
        )

        artworks = {
            "poster": {"url": "poster_url", "country": "fr"},
            "background": {"url": "background_url", "country": "fr"},
            "logo": {"url": "logo_url", "country": "fr", "source": "tmdb"},
        }

        result = self.artworks_updater.is_complete(artworks)
        self.assertFalse(result)

    def test_is_complete_one_missing_artwork(self):
        """One missing artwork, should return False."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
        )

        artworks = {
            "poster": {"url": "poster_url", "country": "fr"},
            "background": {"url": "background_url", "country": "fr"},
            "logo": {},
        }

        result = self.artworks_updater.is_complete(artworks)
        self.assertFalse(result)

    def test_is_complete_empty_artworks(self):
        """Empty artworks dictionary, should return False."""
        self.artworks_updater = ArtworksUpdater(
            plex_manager=self.plex_manager,
            metadata_retriever=self.metadata_retriever,
            plex_country="fr",
        )

        artworks = {}

        result = self.artworks_updater.is_complete(artworks)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
