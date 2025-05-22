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

    @patch("time.sleep", return_value=None)
    def test_update_recently_added(self, mock_time):
        recently_added_movies = [
            {"title": "Movie 1", "plex_movie_id": 1},
            {"title": "Movie 2", "plex_movie_id": 2},
            {"title": "Movie 3", "plex_movie_id": 3},
            {"title": "Movie 3", "plex_movie_id": 4},
        ]
        self.plex_manager.get_recently_added_movies.return_value = recently_added_movies

        self.plex_manager.get_tmdb_id.side_effect = [
            "1111",
            "2222",
            "3333",
            None,  # Movie 4 will be ignored because not matched
        ]

        # Mock artworks_updater methods
        self.artworks_updater.get_artworks.side_effect = [
            (["artwork1"], "2025-01-01"),  # Movie 1: All artworks found
            (["artwork2"], "2025-01-02"),  # Movie 2: Missing artworks
            (["artwork3"], "2025-01-03"),  # Movie 3: Upload failed
        ]
        self.artworks_updater.upload_artworks.side_effect = [True, True, False]
        self.artworks_updater.is_complete.side_effect = [True, False, False]

        self.service.update_recently_added()

        # Ensure recently added movies are fetched
        self.plex_manager.get_recently_added_movies.assert_called_once()

        # Ensure get_tmdb_id is called for each movie
        self.plex_manager.get_tmdb_id.assert_any_call(
            recently_added_movies[0]["plex_movie_id"]
        )
        self.plex_manager.get_tmdb_id.assert_any_call(
            recently_added_movies[1]["plex_movie_id"]
        )
        self.plex_manager.get_tmdb_id.assert_any_call(
            recently_added_movies[2]["plex_movie_id"]
        )
        self.plex_manager.get_tmdb_id.assert_any_call(
            recently_added_movies[3]["plex_movie_id"]
        )

        # Ensure get_artworks is called for each movie
        self.artworks_updater.get_artworks.assert_any_call(recently_added_movies[0])
        self.artworks_updater.get_artworks.assert_any_call(recently_added_movies[1])
        self.artworks_updater.get_artworks.assert_any_call(recently_added_movies[2])

        # Ensure upload_artworks is called for each movie
        self.artworks_updater.upload_artworks.assert_any_call(
            recently_added_movies[0], ["artwork1"], "2025-01-01"
        )
        self.artworks_updater.upload_artworks.assert_any_call(
            recently_added_movies[1], ["artwork2"], "2025-01-02"
        )
        self.artworks_updater.upload_artworks.assert_any_call(
            recently_added_movies[2], ["artwork3"], "2025-01-03"
        )

        # Ensure is_complete is called for each movie
        self.artworks_updater.is_complete.assert_any_call(["artwork1"])
        self.artworks_updater.is_complete.assert_any_call(["artwork2"])

        # Ensure successful movies are added to recently_added_cache
        calls = [
            call[0][0] for call in self.service.recently_added_cache.add.call_args_list
        ]
        self.assertIn(recently_added_movies[0], calls)
        self.assertIn(recently_added_movies[1], calls)
        self.assertNotIn(recently_added_movies[2], calls)
        self.assertNotIn(recently_added_movies[3], calls)

        # Ensure movies with incomplete artworks are added to missing_artworks_cache
        self.service.missing_artworks_cache.add.assert_called_once_with(
            recently_added_movies[1]
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
