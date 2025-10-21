# services/tests/test_recently_added_task.py
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from services.tasks.recently_added_task import RecentlyAddedTask


class TestRecentlyAddedTask(unittest.TestCase):
    @patch("services.tasks.recently_added_task.time.sleep", return_value=None)
    def test_run_recently_added(self, _mock_sleep):
        # --- arrange ---------------------------------------------------------
        plex_manager = Mock()
        artworks_updater = Mock()

        # Use MagicMock so magic method __contains__ is available
        recent_cache = MagicMock(
            spec_set=["load", "save", "add", "clear", "__contains__"]
        )
        missing_cache = MagicMock(spec_set=["load", "save", "add"])

        # Ensure we don't skip processing due to membership checks
        recent_cache.__contains__.return_value = False

        recently_added_movies = [
            {"title": "Movie 1", "plex_movie_id": 1},
            {"title": "Movie 2", "plex_movie_id": 2},
            {"title": "Movie 3", "plex_movie_id": 3},
            {"title": "Movie 4", "plex_movie_id": 4},  # unmatched → skipped
        ]
        plex_manager.get_recently_added_movies.return_value = recently_added_movies

        plex_manager.get_tmdb_id.side_effect = [
            "1111",  # Movie 1
            "2222",  # Movie 2
            "3333",  # Movie 3
            None,  # Movie 4 (unmatched)
        ]

        # ArtworksUpdater.update returns (status, artworks)
        artworks_updater.update.side_effect = [
            ("success", ["artwork1"]),  # Movie 1
            ("imperfect_artworks", ["artwork2"]),  # Movie 2
            ("upload_failed", ["artwork3"]),  # Movie 3
        ]

        task = RecentlyAddedTask(
            plex_manager=plex_manager,
            artworks_updater=artworks_updater,
            recently_added_cache=recent_cache,
            missing_artworks_cache=missing_cache,
            sleep_interval=0.0,
        )

        # --- act -------------------------------------------------------------
        task.run()

        # --- assert ----------------------------------------------------------
        plex_manager.get_recently_added_movies.assert_called_once()

        plex_manager.get_tmdb_id.assert_has_calls(
            [
                call(recently_added_movies[0]["plex_movie_id"]),
                call(recently_added_movies[1]["plex_movie_id"]),
                call(recently_added_movies[2]["plex_movie_id"]),
                call(recently_added_movies[3]["plex_movie_id"]),
            ],
            any_order=False,
        )

        # Artworks updater called for first three (matched)
        self.assertEqual(artworks_updater.update.call_count, 3)
        artworks_updater.update.assert_has_calls(
            [
                call(recently_added_movies[0], None),
                call(recently_added_movies[1], None),
                call(recently_added_movies[2], None),
            ],
            any_order=False,
        )

        # recently_added_cache.add called for success and imperfect only
        recent_added_calls = [c.args[0] for c in recent_cache.add.call_args_list]
        self.assertIn(recently_added_movies[0], recent_added_calls)  # success
        self.assertIn(recently_added_movies[1], recent_added_calls)  # imperfect
        self.assertNotIn(recently_added_movies[2], recent_added_calls)  # upload_failed
        self.assertNotIn(recently_added_movies[3], recent_added_calls)  # unmatched

        # missing_artworks_cache.add called exactly once for the imperfect case
        self.assertEqual(missing_cache.add.call_count, 1)
        added_to_missing = missing_cache.add.call_args.args[0]
        self.assertEqual(added_to_missing["title"], "Movie 2")
        self.assertEqual(added_to_missing["plex_movie_id"], 2)
        self.assertEqual(added_to_missing["artworks"], ["artwork2"])

        # recent cache clear called with last movie
        recent_cache.clear.assert_called_once_with(recently_added_movies[-1])

        # both caches were loaded and saved
        recent_cache.load.assert_called_once()
        missing_cache.load.assert_called_once()
        recent_cache.save.assert_called_once()
        missing_cache.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
