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
    ) -> None:
        self.artworks_updater = artworks_updater
        self.plex_manager = plex_manager

        self.recent_update_interval = recent_update_interval
        self.missing_artwork_interval = missing_artwork_interval
        self.last_recent_update = 0.0
        self.last_missing_artwork_update = 0.0

        self.recently_added_cache = MoviesCache(cache_path, "recently_added")
        self.missing_artworks_cache = MoviesCache(cache_path, "missing_artworks")

        self.running = False
        self.sleep_duration = min(recent_update_interval, missing_artwork_interval)

    def start(self) -> None:
        self.running = True
        while self.running:
            try:
                self.handle()
            except Exception:
                logger.exception("Error in handle loop")
            time.sleep(self.sleep_duration)

    def handle(self) -> None:
        now = time.time()

        if now - self.last_recent_update >= self.recent_update_interval:
            self.update_recently_added()
            self.last_recent_update = now

        if now - self.last_missing_artwork_update >= self.missing_artwork_interval:
            self.update_missing_artworks()
            self.last_missing_artwork_update = now

        self.recently_added_cache.save()
        self.missing_artworks_cache.save()

    def update_recently_added(self) -> None:

        recently_added_movies = self.plex_manager.get_recently_added_movies()
        for movie in recently_added_movies:
            title = movie["title"]

            if movie in self.recently_added_cache:
                continue

            artworks, uploaded, is_complete = self.artworks_updater.update_artworks(
                movie
            )
            if not uploaded:
                logger.warning(f"\n⚠️ Failed to upload artworks for {title}\n")
                continue

            self.recently_added_cache.add(movie)

            if not is_complete:
                movie["artworks"] = artworks
                self.missing_artworks_cache.add(movie)
                logger.warning(f"\n⚠️ Missing artworks for {title}\n")
                continue

            logger.info(f"\n✅ All artworks found and updated for movie {title}\n")

        last_movie = recently_added_movies[-1]
        self.recently_added_cache.clear(last_movie)

        logger.info("\nFinished updating latest movies from Plex\n\n")

    def update_missing_artworks(self) -> None:

        to_remove = []
        for plex_movie_id, movie in self.missing_artworks_cache.items():
            title = movie["title"]

            if not self.plex_manager.exists(plex_movie_id):
                to_remove.append(movie)
                continue

            current_artworks = movie.get("artworks")
            artworks, release_date = self.artworks_updater.get_artworks(movie)

            if artworks == current_artworks:
                logger.warning(f"\n⚠️ No new artworks for {title}\n")
                continue

            uploaded = self.artworks_updater.upload_artworks(
                movie, artworks, release_date
            )
            if not uploaded:
                logger.warning(f"\n⚠️ Failed to upload artworks for {title}\n")
                continue

            is_complete = self.artworks_updater.is_complete(artworks)
            if not is_complete:
                movie["artworks"] = artworks
                logger.warning(f"\n⚠️ New artworks but not complete for {title}\n")
                continue

            to_remove.append(movie)
            logger.info(f"\n✅ All artworks found for {title}\n")

            time.sleep(15.0)

        self.missing_artworks_cache.remove_all(to_remove)

        logger.info("\nFinished updating missing artworks from Plex\n\n")
