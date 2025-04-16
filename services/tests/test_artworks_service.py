import copy
import unittest
from unittest.mock import ANY, MagicMock, patch

from client.plex.manager import PlexManager
from services.artworks_service import ArtworksService
from services.artworks_updater import ArtworksUpdater
from storage.movies_cache import MoviesCache


class TestArtworksService(unittest.TestCase):
    def setUp(self):
        self.artworks_updater = MagicMock(spec=ArtworksUpdater)
        self.plex_manager = MagicMock(spec=PlexManager)
        self.recent_update_interval = 60
        self.missing_artwork_interval = 120
        self.cache_path = "/tmp/cache"

        self.service = ArtworksService(
            self.artworks_updater,
            self.plex_manager,
            self.recent_update_interval,
            self.missing_artwork_interval,
            self.cache_path,
        )

        self.service.recently_added_cache = MagicMock(spec=MoviesCache)
        self.service.missing_artworks_cache = MagicMock(spec=MoviesCache)

    def test_update_recently_added(self):

        recently_added_movies = [
            {"title": "Movie 1", "id": 1},
            {"title": "Movie 2", "id": 2},
            {"title": "Movie 3", "id": 3},
        ]
        self.plex_manager.get_recently_added_movies.return_value = recently_added_movies

        self.artworks_updater.update_artworks.side_effect = [
            (["artwork1"], True, True),  # Movie 1: All artworks found
            (["artwork2"], True, False),  # Movie 2: Missing artworks
            (["artwork3"], False, True),  # Movie 3: Upload failed
        ]

        self.service.update_recently_added()

        # Get recently added movies
        self.plex_manager.get_recently_added_movies.assert_called_once()

        # Update artworks for each movie
        self.artworks_updater.update_artworks.assert_any_call(recently_added_movies[0])
        self.artworks_updater.update_artworks.assert_any_call(recently_added_movies[1])
        self.artworks_updater.update_artworks.assert_any_call(recently_added_movies[2])

        # Add successful movies to recently_added_cache
        self.service.recently_added_cache.add.assert_any_call(recently_added_movies[0])
        self.service.recently_added_cache.add.assert_any_call(recently_added_movies[1])

        # Add missing artworks to missing_artworks_cache
        self.service.missing_artworks_cache.add.assert_called_once_with(
            {"title": "Movie 2", "id": 2, "artworks": ["artwork2"]}
        )
        self.service.recently_added_cache.clear.assert_called_once_with(
            recently_added_movies[-1]
        )

    @patch("time.sleep", return_value=None)
    def test_update_missing_artworks(self, mock_time):
        cached_movies = {
            1: {"title": "Movie 1", "id": 1, "artworks": ["artwork1"]},
            2: {"title": "Movie 2", "id": 2, "artworks": ["artwork2"]},
            3: {"title": "Movie 3", "id": 3, "artworks": ["artwork3"]},
            4: {"title": "Movie 4", "id": 4, "artworks": ["artwork4"]},
            5: {"title": "Movie 5", "id": 5, "artworks": ["artwork5"]},
        }

        self.service.missing_artworks_cache.items.return_value = cached_movies.items()

        # Movie 2 does not exist
        self.plex_manager.exists.side_effect = [
            True,
            False,
            True,
            True,
            True,
        ]

        # Movie 3 has no new artworks
        self.artworks_updater.get_artworks.side_effect = [
            (["new_artwork1"], "2025-01-01"),
            (["artwork3"], "2025-01-03"),
            (["new_artwork4"], "2025-01-04"),
            (["new_artwork5"], "2025-01-05"),
        ]

        # Movie 4 artworks upload fails
        self.artworks_updater.upload_artworks.side_effect = [True, False, True]

        # Movie 5 has no complete artworks
        self.artworks_updater.is_complete.side_effect = [True, False]

        # Call the method under test
        self.service.update_missing_artworks()

        self.plex_manager.exists.assert_any_call(1)
        self.plex_manager.exists.assert_any_call(2)
        self.plex_manager.exists.assert_any_call(3)
        self.plex_manager.exists.assert_any_call(4)
        self.plex_manager.exists.assert_any_call(5)

        # Movie 2 ignored because it does not exist
        self.artworks_updater.get_artworks.assert_any_call(
            {"title": "Movie 1", "id": 1, "artworks": ANY}
        )
        self.artworks_updater.get_artworks.assert_any_call(
            {"title": "Movie 3", "id": 3, "artworks": ANY}
        )
        self.artworks_updater.get_artworks.assert_any_call(
            {"title": "Movie 4", "id": 4, "artworks": ANY}
        )
        self.artworks_updater.get_artworks.assert_any_call(
            {"title": "Movie 5", "id": 5, "artworks": ANY}
        )

        # Movie 3 ignored because no new artworks
        self.artworks_updater.upload_artworks.assert_any_call(
            {"title": "Movie 1", "id": 1, "artworks": ANY},
            ["new_artwork1"],
            "2025-01-01",
        )
        self.artworks_updater.upload_artworks.assert_any_call(
            {"title": "Movie 4", "id": 4, "artworks": ANY},
            ["new_artwork4"],
            "2025-01-04",
        )
        self.artworks_updater.upload_artworks.assert_any_call(
            {"title": "Movie 5", "id": 5, "artworks": ANY},
            ["new_artwork5"],
            "2025-01-05",
        )

        # Movie 4 ignored because upload failed
        self.artworks_updater.is_complete.assert_any_call(["new_artwork1"])
        self.artworks_updater.is_complete.assert_any_call(["new_artwork5"])

        # Movie 5 is not complete
        self.assertEqual(cached_movies[3]["artworks"], ["artwork3"])
        self.assertEqual(cached_movies[4]["artworks"], ["artwork4"])
        self.assertEqual(cached_movies[5]["artworks"], ["new_artwork5"])

        # Movie 1 is removed because artworks are complete
        # Movie 2 is removed because not existing
        self.service.missing_artworks_cache.remove_all.assert_called_once_with(
            [
                {"title": "Movie 1", "id": 1, "artworks": ["artwork1"]},
                {"title": "Movie 2", "id": 2, "artworks": ["artwork2"]},
            ]
        )


if __name__ == "__main__":
    unittest.main()
