import logging
import time

from client.plex.manager import PlexManager
from services.artworks_updater import ArtworksUpdater
from storage.movies_cache import MoviesCache

logger = logging.getLogger(__name__)


class ArtworksService:
    def __init__(
        self,
        artworks_updater: ArtworksUpdater,
        plex_manager: PlexManager,
        recent_update_interval: int,
        missing_artwork_interval: int,
        cache_path: str,
        api_call_interval: float = 1.0,
    ) -> None:
        self.artworks_updater = artworks_updater
        self.plex_manager = plex_manager

        self.recent_update_interval = recent_update_interval
        self.missing_artwork_interval = missing_artwork_interval
        self.last_recent_update = 0.0
        self.last_missing_artwork_update = 0.0
        self.api_call_interval = api_call_interval

        self.recently_added_cache = MoviesCache(
            cache_path, "recently_added", retention_seconds=3600 * 24 * 10
        )  # 10 days retention to avoid the case where a movie is removed causing older movies to be reprocessed
        self.missing_artworks_cache = MoviesCache(cache_path, "missing_artworks")

        self.running = False
        self.sleep_duration = min(recent_update_interval, missing_artwork_interval)

    def start(self) -> None:
        logger.info("Starting ArtworksService...")
        self.running = True
        while self.running:
            try:
                self.handle()
            except Exception:
                logger.exception("Error in handle loop")
            time.sleep(self.sleep_duration)

    def handle(self) -> None:
        now = time.time()
        self.missing_artworks_cache.load()

        if now - self.last_recent_update >= self.recent_update_interval:
            self.update_recently_added()
            self.last_recent_update = now

        if now - self.last_missing_artwork_update >= self.missing_artwork_interval:
            self.update_missing_artworks()
            self.last_missing_artwork_update = now

        self.recently_added_cache.save()
        # Only save if a movie has been added or removed, not if artworks have been updated
        self.missing_artworks_cache.save()

    def update_recently_added(self) -> None:

        recently_added_movies = self.plex_manager.get_recently_added_movies()
        for movie in recently_added_movies:

            if movie in self.recently_added_cache:
                continue

            tmdb_id = self.plex_manager.get_tmdb_id(movie["plex_movie_id"])
            if not tmdb_id:
                logger.warning(
                    f"\nMovie {movie['title']} is not matched, will be ignored.\n"
                )
                continue

            status = self.update_movie_artworks(movie)

            if status in ("success", "incomplete_artworks"):
                self.recently_added_cache.add(movie)

            if status == "incomplete_artworks":
                self.missing_artworks_cache.add(movie)

            time.sleep(self.api_call_interval)

        if recently_added_movies:
            last_movie = recently_added_movies[-1]
            self.recently_added_cache.clear(last_movie)

        logger.info("\nFinished updating latest movies from Plex\n\n")

    def update_missing_artworks(self) -> None:

        to_remove = []
        for plex_movie_id, movie in self.missing_artworks_cache.items():
            if not self.plex_manager.exists(plex_movie_id):
                to_remove.append(movie)
                continue

            status = self.update_movie_artworks(movie)
            if status == "success":
                to_remove.append(movie)

            time.sleep(self.api_call_interval)

        self.missing_artworks_cache.remove_all(to_remove)

        logger.info("\nFinished updating missing artworks from Plex\n\n")

    def update_movie_artworks(self, movie: dict) -> str:
        title = movie["title"]

        current_artworks = movie.get("artworks")
        artworks, release_date = self.artworks_updater.get_artworks(movie)

        if artworks == current_artworks:
            logger.warning(f"\n⚠️ No new artworks for {title}\n")
            return "no_new_artworks"

        uploaded = self.artworks_updater.upload_artworks(movie, artworks, release_date)
        if not uploaded:
            logger.warning(f"\n⚠️ Failed to upload artworks for {title}\n")
            return "upload_failed"

        is_complete = self.artworks_updater.is_complete(artworks)
        if not is_complete:
            movie["artworks"] = artworks
            logger.warning(f"\n⚠️ New artworks but not complete for {title}\n")
            return "incomplete_artworks"

        logger.info(f"\n✅ All artworks found for {title}\n")
        return "success"
