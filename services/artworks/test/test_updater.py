import unittest
from unittest.mock import MagicMock

from models.artworks import Artworks
from services.artworks.updater import ArtworksUpdater


class TestArtworksUpdaterAreBetter(unittest.TestCase):
    """Test cases for the are_better method of ArtworksUpdater."""

    def setUp(self):
        """Set up test fixtures."""
        self.retriever = MagicMock()
        self.selector = MagicMock()
        self.uploader = MagicMock()

        self.updater = ArtworksUpdater(
            artworks_retriever=self.retriever,
            artworks_selector=self.selector,
            artworks_uploader=self.uploader,
        )

    def test_are_better_with_identical_artworks(self):
        """Should return False when artworks are identical."""
        artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(artworks, artworks)

        self.assertFalse(result)

    def test_are_better_with_no_current_artworks(self):
        """Should return True when current_artworks is None."""
        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, None)

        self.assertTrue(result)

    def test_are_better_with_no_current_poster(self):
        """Should return True when current poster is None."""
        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertTrue(result)

    def test_are_better_with_no_new_poster(self):
        """Should return False when new poster is None but current poster exists."""
        new_artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertFalse(result)

    def test_are_better_with_higher_priority_country(self):
        """Should return True when new poster has higher priority country (lower rank)."""
        self.retriever.get_country_rank.side_effect = lambda country: {
            "fr": 0,  # Higher priority (lower rank)
            "us": 1,  # Lower priority (higher rank)
        }[country]

        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-fr.jpg",
                "country": "fr",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-us.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertTrue(result)
        self.retriever.get_country_rank.assert_any_call("us")
        self.retriever.get_country_rank.assert_any_call("fr")

    def test_are_better_with_lower_priority_country(self):
        """Should return False when new poster has lower priority country (higher rank)."""
        self.retriever.get_country_rank.side_effect = lambda country: {
            "fr": 0,  # Higher priority (lower rank)
            "us": 1,  # Lower priority (higher rank)
        }[country]

        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-us.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-fr.jpg",
                "country": "fr",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertFalse(result)
        self.retriever.get_country_rank.assert_any_call("fr")
        self.retriever.get_country_rank.assert_any_call("us")

    def test_are_better_with_equal_priority_country(self):
        """Should return True when new poster has equal priority country (same rank)."""
        self.retriever.get_country_rank.side_effect = lambda country: {
            "us": 1,
        }[country]

        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-new.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster-old.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertTrue(result)
        self.retriever.get_country_rank.assert_any_call("us")

    def test_are_better_with_different_backgrounds_same_poster(self):
        """Should return True when backgrounds differ and posters are identical."""
        self.retriever.get_country_rank.side_effect = lambda country: {
            "us": 1,
        }[country]

        artworks_with_background: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": {
                "url": "https://example.com/background.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "logo": None,
        }

        artworks_without_background: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "us",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(
            artworks_with_background, artworks_without_background
        )

        self.assertTrue(result)

    def test_are_better_both_posters_none(self):
        """Should return False when both new and current posters are None."""
        new_artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }

        current_artworks: Artworks = {
            "poster": None,
            "background": None,
            "logo": None,
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertFalse(result)

    def test_are_better_with_different_logo_sources_same_highest_priority_country(self):
        """Should return True when logos have different sources but same highest priority country."""
        self.retriever.get_country_rank.side_effect = lambda country: {
            "fr": 0,  # Highest priority
        }[country]

        new_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "fr",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": {
                "url": "https://example.com/logo-apple.png",
                "country": "fr",
                "title": "Test Movie",
                "source": "apple",
            },
        }

        current_artworks: Artworks = {
            "poster": {
                "url": "https://example.com/poster.jpg",
                "country": "fr",
                "title": "Test Movie",
                "source": "apple",
            },
            "background": None,
            "logo": {
                "url": "https://example.com/logo-tmdb.png",
                "country": "fr",
                "title": "Test Movie",
                "source": "tmdb",
            },
        }

        result = self.updater.are_better(new_artworks, current_artworks)

        self.assertTrue(result)
        self.retriever.get_country_rank.assert_any_call("fr")


if __name__ == "__main__":
    unittest.main()
