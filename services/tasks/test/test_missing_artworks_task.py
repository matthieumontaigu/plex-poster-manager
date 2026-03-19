from __future__ import annotations

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from services.tasks.missing_artworks_task import MissingArtworksTask

# Fixed timestamps used across all tests
_NOW = 1_000_000_000
_RECENT_THRESHOLD_DAYS = 7
_RECENT_DATE = _NOW - 1 * 86400  # 1 day ago  → within recent window
_OLD_DATE = _NOW - 30 * 86400  # 30 days ago → backlog


def _make_task(
    plex_manager,
    artworks_updater,
    cache,
    *,
    search_quota: int = 100,
    recent_threshold_days: int = _RECENT_THRESHOLD_DAYS,
) -> MissingArtworksTask:
    return MissingArtworksTask(
        plex_manager=plex_manager,
        artworks_updater=artworks_updater,
        missing_artworks_cache=cache,
        sleep_interval=0.0,
        search_quota=search_quota,
        recent_threshold_days=recent_threshold_days,
    )


def _make_cache(movies: dict) -> MagicMock:
    cache = MagicMock(spec_set=["load", "save", "items", "remove_all"])
    cache.items.return_value = movies.items()
    return cache


class TestMissingArtworksTaskStatusHandling(unittest.TestCase):
    """Status handling and cache mutations (all movies in backlog, ample quota)."""

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_update_missing_artworks(self, _mock_time, _mock_sleep):
        # --- arrange ---------------------------------------------------------
        plex_manager = Mock()
        artworks_updater = Mock()

        cached_movies = {
            1: {
                "title": "Movie 1",
                "id": 1,
                "added_date": _OLD_DATE,
                "artworks": ["artwork1"],
            },
            2: {
                "title": "Movie 2",
                "id": 2,
                "added_date": _OLD_DATE,
                "artworks": ["artwork2"],
            },
            3: {
                "title": "Movie 3",
                "id": 3,
                "added_date": _OLD_DATE,
                "artworks": ["artwork3"],
            },
            4: {
                "title": "Movie 4",
                "id": 4,
                "added_date": _OLD_DATE,
                "artworks": ["artwork4"],
            },
            5: {
                "title": "Movie 5",
                "id": 5,
                "added_date": _OLD_DATE,
                "artworks": ["artwork5"],
            },
            6: {"title": "Movie 6", "id": 6, "added_date": _OLD_DATE},
        }
        cache = _make_cache(cached_movies)

        # Movie 2 does not exist in Plex
        plex_manager.exists.side_effect = [True, False, True, True, True, True]

        # ArtworksUpdater.update returns (status, new_artworks, search_count)
        artworks_updater.update.side_effect = [
            ("success", ["new_artwork1"], 2),  # Movie 1 → removed
            ("unchanged_artworks", ["artwork3"], 2),  # Movie 3 → keep original
            ("upload_failed", ["new_artwork4"], 1),  # Movie 4 → keep original
            ("imperfect_artworks", ["new_artwork5"], 2),  # Movie 5 → update artworks
            ("empty_artworks", None, 2),  # Movie 6 → keep, no artworks
        ]

        task = _make_task(plex_manager, artworks_updater, cache)

        # --- act -------------------------------------------------------------
        task.run()

        # --- assert ----------------------------------------------------------
        plex_manager.exists.assert_has_calls(
            [call(1), call(2), call(3), call(4), call(5), call(6)],
            any_order=False,
        )

        # update called for all movies except the nonexistent one (Movie 2)
        self.assertEqual(artworks_updater.update.call_count, 5)
        update_call_ids = [
            c.args[0]["id"] for c in artworks_updater.update.call_args_list
        ]
        self.assertEqual(update_call_ids, [1, 3, 4, 5, 6])

        # Artworks mutations
        self.assertEqual(cached_movies[3]["artworks"], ["artwork3"])  # unchanged
        self.assertEqual(
            cached_movies[4]["artworks"], ["artwork4"]
        )  # upload_failed → untouched
        self.assertEqual(
            cached_movies[5]["artworks"], ["new_artwork5"]
        )  # imperfect → updated
        self.assertNotIn("artworks", cached_movies[6])  # empty → no artworks added

        # last_checked_date stamped on all processed movies
        for movie_id in [1, 3, 4, 5, 6]:
            self.assertEqual(cached_movies[movie_id]["last_checked_date"], _NOW)
        # nonexistent movie is not processed → no last_checked_date
        self.assertNotIn("last_checked_date", cached_movies[2])

        # Removed: Movie 1 (success) and Movie 2 (nonexistent)
        removed_ids = [m["id"] for m in cache.remove_all.call_args[0][0]]
        self.assertEqual(removed_ids, [1, 2])

        cache.load.assert_called_once()
        cache.save.assert_called_once()


class TestMissingArtworksTaskQuota(unittest.TestCase):
    """Quota-based prioritisation logic."""

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_recent_movies_processed_regardless_of_quota(self, _mock_time, _mock_sleep):
        """Recent movies are always processed even when quota is 0."""
        plex_manager = Mock()
        artworks_updater = Mock()

        cache = _make_cache(
            {1: {"title": "Recent", "id": 1, "added_date": _RECENT_DATE}}
        )
        plex_manager.exists.return_value = True
        artworks_updater.update.return_value = ("success", None, 5)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=0)
        task.run()

        artworks_updater.update.assert_called_once()

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_backlog_movies_processed_within_quota(self, _mock_time, _mock_sleep):
        """Backlog movies are all processed when the quota is sufficient."""
        plex_manager = Mock()
        artworks_updater = Mock()

        cache = _make_cache(
            {
                1: {"title": "Backlog 1", "id": 1, "added_date": _OLD_DATE},
                2: {"title": "Backlog 2", "id": 2, "added_date": _OLD_DATE},
            }
        )
        plex_manager.exists.return_value = True
        artworks_updater.update.return_value = ("success", None, 3)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=10)
        task.run()

        self.assertEqual(artworks_updater.update.call_count, 2)

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_backlog_deferred_when_quota_exhausted(self, _mock_time, _mock_sleep):
        """Backlog movies beyond the quota are not processed."""
        plex_manager = Mock()
        artworks_updater = Mock()

        cache = _make_cache(
            {
                1: {"title": "Backlog 1", "id": 1, "added_date": _OLD_DATE},
                2: {"title": "Backlog 2", "id": 2, "added_date": _OLD_DATE},
                3: {"title": "Backlog 3", "id": 3, "added_date": _OLD_DATE},
            }
        )
        plex_manager.exists.return_value = True
        # Each movie costs 4 searches; quota=5 → movies start while quota_remaining > 0
        # Movie 1: remaining=5 → process, cost 4 → remaining=1
        # Movie 2: remaining=1 → process, cost 4 → remaining=-3
        # Movie 3: remaining=-3 → deferred
        artworks_updater.update.return_value = ("success", None, 4)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=5)
        task.run()

        self.assertEqual(artworks_updater.update.call_count, 2)

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_backlog_sorted_by_last_checked_date(self, _mock_time, _mock_sleep):
        """
        Backlog movies are processed in ascending order of last_checked_date:
        never-checked (no field) first, then oldest-checked, then most-recently-checked.
        """
        plex_manager = Mock()
        artworks_updater = Mock()

        # A: checked recently, B: never checked, C: checked earlier
        cache = _make_cache(
            {
                10: {
                    "title": "A",
                    "id": 10,
                    "added_date": _OLD_DATE,
                    "last_checked_date": _NOW - 100,
                },
                20: {"title": "B", "id": 20, "added_date": _OLD_DATE},
                30: {
                    "title": "C",
                    "id": 30,
                    "added_date": _OLD_DATE,
                    "last_checked_date": _NOW - 200,
                },
            }
        )
        plex_manager.exists.return_value = True
        # quota=4, each call costs 2 → only 2 movies processed
        artworks_updater.update.return_value = ("empty_artworks", None, 2)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=4)
        task.run()

        # Expected order: B (key=0), C (key=_NOW-200), A (key=_NOW-100)
        # With quota=4 and cost=2: B and C are processed; A is deferred
        processed_ids = [
            c.args[0]["id"] for c in artworks_updater.update.call_args_list
        ]
        self.assertEqual(processed_ids, [20, 30])

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_last_checked_date_set_on_processed_movie(self, _mock_time, _mock_sleep):
        """last_checked_date is stamped on every movie that is actually processed."""
        plex_manager = Mock()
        artworks_updater = Mock()

        movie = {"title": "Movie", "id": 1, "added_date": _OLD_DATE}
        cache = _make_cache({1: movie})
        plex_manager.exists.return_value = True
        artworks_updater.update.return_value = ("unchanged_artworks", None, 1)

        task = _make_task(plex_manager, artworks_updater, cache)
        task.run()

        self.assertEqual(movie["last_checked_date"], _NOW)

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_skipped_backlog_movie_last_checked_date_not_updated(
        self, _mock_time, _mock_sleep
    ):
        """Backlog movies skipped due to quota exhaustion keep their old last_checked_date."""
        plex_manager = Mock()
        artworks_updater = Mock()

        old_checked = _NOW - 500
        # Movie 1 has no last_checked_date → sorts first; Movie 2 has one → sorts second
        cache = _make_cache(
            {
                1: {"title": "First", "id": 1, "added_date": _OLD_DATE},
                2: {
                    "title": "Skipped",
                    "id": 2,
                    "added_date": _OLD_DATE,
                    "last_checked_date": old_checked,
                },
            }
        )
        plex_manager.exists.return_value = True
        # quota=3, first movie costs 5 → exhausts quota; second is skipped
        artworks_updater.update.return_value = ("empty_artworks", None, 5)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=3)
        task.run()

        movies = dict(cache.items.return_value)
        self.assertEqual(movies[1]["last_checked_date"], _NOW)
        self.assertEqual(movies[2]["last_checked_date"], old_checked)

    @patch("services.tasks.missing_artworks_task.time.sleep", return_value=None)
    @patch("services.tasks.missing_artworks_task.time.time", return_value=float(_NOW))
    def test_nonexistent_movies_removed_regardless_of_quota(
        self, _mock_time, _mock_sleep
    ):
        """Movies absent from Plex are cleaned up from the cache even when quota is 0."""
        plex_manager = Mock()
        artworks_updater = Mock()

        movies = {
            1: {"title": "Gone", "id": 1, "added_date": _OLD_DATE},
            2: {"title": "Backlog", "id": 2, "added_date": _OLD_DATE},
        }
        cache = _make_cache(movies)
        plex_manager.exists.side_effect = [False, True]
        artworks_updater.update.return_value = ("empty_artworks", None, 1)

        task = _make_task(plex_manager, artworks_updater, cache, search_quota=0)
        task.run()

        removed_ids = [m["id"] for m in cache.remove_all.call_args[0][0]]
        self.assertIn(1, removed_ids)  # nonexistent → removed
        self.assertNotIn(2, removed_ids)  # quota=0, not processed, not removed


if __name__ == "__main__":
    unittest.main()
