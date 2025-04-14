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

    def update_recently_added(self) -> None:

        recently_added_movies = self.plex_manager.get_recently_added_movies()
        for movie in recently_added_movies:
            if movie in self.recently_added_cache:
                continue

            is_missing, artworks = self.artworks_updater.update_artworks(movie)

            if is_missing:
                movie["artworks"] = artworks
                self.missing_artworks_cache.add(movie)
                logger.warning(f"❌ Missing artworks detected for {movie['title']}")
            else:
                logger.info(f"✅ Updated artworks for movie {movie['title']}")

            self.recently_added_cache.add(movie)

        last_movie = recently_added_movies[-1]
        self.recently_added_cache.clear(last_movie)

        self.recently_added_cache.save()
        logger.info("Finished updating latest movies from Plex")

    def update_missing_artworks(self) -> None:
        self.missing_artworks_cache.load()

        for plex_movie_id, movie in self.missing_artworks_cache.items():

            if not self.plex_manager.exists(plex_movie_id):
                self.missing_artworks_cache.remove(movie)
                continue

            is_missing, artworks = self.artworks_updater.update_artworks(movie)
            if is_missing:
                movie["artworks"] = artworks
                logger.warning(f"⚠️ Artworks still not complete for {movie['title']}")
            else:
                self.missing_artworks_cache.remove(movie)
                logger.info(f"✅ All artworks found for {movie['title']}")

            time.sleep(10.0)

        self.missing_artworks_cache.save()
        logger.info("Finished updating missing artworks from Plex")
