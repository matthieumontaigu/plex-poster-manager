from __future__ import annotations

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from services.tasks.missing_artworks_task import MissingArtworksTask


class TestMissingArtworksTask(unittest.TestCase):
    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    def test_update_missing_artworks(self, _mock_sleep):
        # --- arrange ---------------------------------------------------------
        plex_manager = Mock()
        artworks_updater = Mock()

        # Movies cache mock
        cache = MagicMock(spec_set=["load", "save", "items", "remove_all"])

        # Cached movies (keys are plex_movie_id)
        cached_movies = {
            1: {"title": "Movie 1", "id": 1, "artworks": ["artwork1"]},
            2: {"title": "Movie 2", "id": 2, "artworks": ["artwork2"]},
            3: {"title": "Movie 3", "id": 3, "artworks": ["artwork3"]},
            4: {"title": "Movie 4", "id": 4, "artworks": ["artwork4"]},
            5: {"title": "Movie 5", "id": 5, "artworks": ["artwork5"]},
        }
        cache.items.return_value = cached_movies.items()

        # Movie 2 does not exist
        plex_manager.exists.side_effect = [True, False, True, True, True]

        # ArtworksUpdater.update returns (status, new_artworks)
        # Movie 1: success → removed
        # Movie 3: unchanged_artworks → keep original
        # Movie 4: upload_failed → keep original
        # Movie 5: imperfect_artworks → update artworks, keep in cache
        artworks_updater.update.side_effect = [
            ("success", ["new_artwork1"]),  # for Movie 1
            ("unchanged_artworks", ["artwork3"]),  # for Movie 3
            ("upload_failed", ["new_artwork4"]),  # for Movie 4
            ("imperfect_artworks", ["new_artwork5"]),  # for Movie 5
        ]

        task = MissingArtworksTask(
            plex_manager=plex_manager,
            artworks_updater=artworks_updater,
            missing_artworks_cache=cache,
            sleep_interval=0.0,
        )

        # --- act -------------------------------------------------------------
        task.run()

        # --- assert ----------------------------------------------------------
        # Existence checks done for every cached key
        plex_manager.exists.assert_has_calls(
            [call(1), call(2), call(3), call(4), call(5)],
            any_order=False,
        )

        # ArtworksUpdater.update should be called for 1,3,4,5 (but not 2)
        self.assertEqual(artworks_updater.update.call_count, 4)
        # We can still sanity-check the first argument is the movie dict each time.
        update_calls_movies = [
            c.args[0]["id"] for c in artworks_updater.update.call_args_list
        ]
        self.assertEqual(update_calls_movies, [1, 3, 4, 5])

        # Side effects on cached movie dicts:
        # Movie 3 unchanged
        self.assertEqual(cached_movies[3]["artworks"], ["artwork3"])
        # Movie 4 unchanged (upload failed)
        self.assertEqual(cached_movies[4]["artworks"], ["artwork4"])
        # Movie 5 updated (imperfect_artworks branch)
        self.assertEqual(cached_movies[5]["artworks"], ["new_artwork5"])

        # Removed from cache:
        # - Movie 1 (success)
        # - Movie 2 (does not exist)
        cache.remove_all.assert_called_once_with(
            [
                {"title": "Movie 1", "id": 1, "artworks": ["artwork1"]},
                {"title": "Movie 2", "id": 2, "artworks": ["artwork2"]},
            ]
        )

        # Cache load/save called
        cache.load.assert_called_once()
        cache.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
