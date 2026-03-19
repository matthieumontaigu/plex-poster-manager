from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from models.movie import Movie
    from services.artworks.updater import ArtworksUpdater
    from storage.movies_cache import MoviesCache

logger = logging.getLogger(__name__)


class MissingArtworksTask:
    """
    Task that retries updating artworks for movies with missing or incomplete artworks.

    Responsibilities:
    - Iterate over cached "missing artworks" movies
    - Retry artwork update using ArtworksUpdater
    - Remove from cache once complete
    """

    def __init__(
        self,
        plex_manager: PlexManager,
        artworks_updater: ArtworksUpdater,
        missing_artworks_cache: MoviesCache,
        sleep_interval: float = 1.0,
        search_quota: int = 100,
        recent_threshold_days: int = 7,
    ) -> None:
        self.plex_manager = plex_manager
        self.artworks_updater = artworks_updater
        self.sleep_interval = sleep_interval
        self.search_quota = search_quota
        self.recent_threshold_days = recent_threshold_days

        self.cache = missing_artworks_cache

    def _process_movie(self, movie: Movie, now: float, to_remove: list[Movie]) -> int:
        current_artworks = movie.get("artworks")
        status, new_artworks, search_count = self.artworks_updater.update(
            movie, current_artworks
        )
        movie["last_checked_date"] = int(now)
        logger.debug(f"Search queries used for '{movie['title']}': {search_count}")

        if status == "success":
            logger.info(f"\u2713 Complete artworks found for {movie['title']}")
            to_remove.append(movie)
        elif status == "upload_failed":
            logger.warning(f"\u2717 Upload failed for {movie['title']}")
        elif status == "unchanged_artworks":
            logger.info(f"\u26a0 No changes for {movie['title']}")
        elif status == "empty_artworks":
            logger.info(f"\u26a0 No artworks found for {movie['title']}")
        elif status == "imperfect_artworks":
            movie["artworks"] = new_artworks
            logger.info(f"\u26a0 Incomplete artworks remain for {movie['title']}")

        time.sleep(self.sleep_interval)
        return search_count

    def run(self) -> None:
        self.cache.load()

        now = time.time()
        recent_cutoff = now - self.recent_threshold_days * 86400

        all_items = list(self.cache.items())
        recent = sorted(
            [(pid, m) for pid, m in all_items if m["added_date"] >= recent_cutoff],
            key=lambda x: x[1]["added_date"],
        )
        backlog = sorted(
            [(pid, m) for pid, m in all_items if m["added_date"] < recent_cutoff],
            key=lambda x: x[1].get("last_checked_date", 0),
        )

        to_remove = []
        quota_used = 0

        logger.info(
            f"Missing artworks: {len(recent)} recent, {len(backlog)} backlog "
            f"(quota: {self.search_quota})"
        )

        for plex_movie_id, movie in recent:
            if not self.plex_manager.exists(plex_movie_id):
                to_remove.append(movie)
                continue

            quota_used += self._process_movie(movie, now, to_remove)

        if quota_used > self.search_quota:
            logger.warning(
                f"Recent movies exceeded search quota "
                f"({quota_used}/{self.search_quota} CSE calls used)"
            )

        quota_remaining = self.search_quota - quota_used
        deferred = 0

        for plex_movie_id, movie in backlog:
            if not self.plex_manager.exists(plex_movie_id):
                to_remove.append(movie)
                continue

            if quota_remaining <= 0:
                deferred += 1
                continue

            search_count = self._process_movie(movie, now, to_remove)
            quota_used += search_count
            quota_remaining -= search_count

        if deferred:
            logger.info(
                f"⏭ {deferred} backlog movie(s) deferred to next run "
                f"(quota exhausted: {quota_used}/{self.search_quota} CSE calls)"
            )

        self.cache.remove_all(to_remove)
        self.cache.save()
