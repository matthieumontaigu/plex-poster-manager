import unittest

from models.artworks import Artworks
from models.movie import Movie
from services.artworks.selector import ArtworksSelector


class TestArtworksSelector(unittest.TestCase):

    MOVIE: Movie = {
        "plex_movie_id": 1111,
        "title": "Pris au piège - Caught Stealing",
        "year": 2025,
        "added_date": 1700000000,
        "release_date": "2025-08-27",
        "director": ["Darren Aronofsky"],
        "metadata_country": "fr",
        "guid": None,
        "tmdb_id": None,
    }

    def test_all_match(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=True, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertEqual(selected["logo"], artworks["logo"])
        self.assertTrue(selector.are_perfect(selected, self.MOVIE))

    def test_no_FR_background(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=True, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertEqual(selected["logo"], artworks["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_title_without_option(self):
        selector = ArtworksSelector(
            match_movie_title=False, match_logo_poster=True, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertEqual(selected["logo"], artworks["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_title_with_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=True, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertIsNone(selected["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_logo_poster_with_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=True, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_logo_poster_without_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_logo_poster_without_both_options(self):
        selector = ArtworksSelector(
            match_movie_title=False, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertEqual(selected["logo"], artworks["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_poster_no_match_logo_poster_without_option_with_fallback(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "fr",
                "title": "Pris au piège - Caught Stealing",
                "source": "tmdb",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertEqual(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertEqual(selected["logo"], artworks["fallback_logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_logo_and_fallback_no_match_title_with_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "tmdb",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertIsNone(selected["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_logo_and_fallback_no_match_title_without_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": {
                "url": "logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "tmdb",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertIsNone(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"], artworks["logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))

    def test_fallback_only_no_match_title_without_option(self):
        selector = ArtworksSelector(
            match_movie_title=True, match_logo_poster=False, target_source="apple"
        )

        artworks: Artworks = {
            "poster": {
                "url": "poster_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "background": {
                "url": "background_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "apple",
            },
            "logo": None,
            "fallback_logo": {
                "url": "fallback_logo_url",
                "country": "us",
                "title": "Caught Stealing",
                "source": "tmdb",
            },
        }

        selected = selector.select(artworks, self.MOVIE)

        self.assertIsNone(selected["poster"], artworks["poster"])
        self.assertEqual(selected["background"], artworks["background"])
        self.assertIsNone(selected["logo"], artworks["fallback_logo"])
        self.assertFalse(selector.are_perfect(selected, self.MOVIE))


if __name__ == "__main__":
    unittest.main()
