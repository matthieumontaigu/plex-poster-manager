import logging
import time

from client.apple_tv.extract import get_apple_tv_artworks
from client.itunes.extract import get_itunes_artworks
from client.plex.manager import PlexManager
from services.metadata_manager import MetadataManager
from utils.string_utils import are_match

logger = logging.getLogger(__name__)


class ArtworksUpdater:
    def __init__(
        self,
        plex_manager: PlexManager,
        metadata_manager: MetadataManager,
        countries: list[str] = ["fr", "us", "gb", "be", "ch", "lu"],
        match_title: bool = True,
        update_release_date: bool = False,
    ) -> None:
        self.plex_manager = plex_manager
        self.metadata_manager = metadata_manager

        self.countries = countries
        self.match_title = match_title
        self.update_release_date = update_release_date
        self._api_call_interval = 1.0

    def update_artworks(self, movie: dict) -> None:
        logger.info(f"Processing artworks for {movie['title']}")

        plex_movie_id = movie["plex_movie_id"]
        title = movie["title"]
        artworks = self.get_artworks(movie)
        for artwork_type, artwork in artworks.items():
            success = self.update_artwork(artwork_type, artwork, plex_movie_id)
            self._log_upload_result(success, artwork_type, title, plex_movie_id)
            time.sleep(self._api_call_interval)

    def update_artwork(
        self, artwork_type: str, artwork: dict[str, str], plex_movie_id: int
    ) -> bool | None:
        if not artwork:
            return None

        elif artwork_type == "poster":
            poster_url = artwork["url"]
            return self.plex_manager.upload_poster(plex_movie_id, poster_url)

        elif artwork_type == "background":
            background_url = artwork["url"]
            return self.plex_manager.upload_background(plex_movie_id, background_url)

        elif artwork_type == "logo":
            logo_url = artwork["url"]
            return self.plex_manager.upload_logo(plex_movie_id, logo_url)

        elif self.update_release_date and artwork_type == "release_date":
            release_date = artwork["date"]
            return self.plex_manager.update_release_date(plex_movie_id, release_date)

        else:
            return None

    def get_artworks(self, movie: dict) -> dict[str, dict[str, str]]:
        year = self.get_year(movie)

        artworks: dict[str, dict[str, str]] = {
            "poster": {},
            "background": {},
            "logo": {},
            "release_date": {},
        }
        for country in self.countries:
            if artworks["poster"] and artworks["background"] and artworks["logo"]:
                break

            localized_title = self.get_localized_title(movie, country)
            if not localized_title:
                continue

            should_update = self.should_update(movie["title"], localized_title)
            should_extract_artworks = self.should_extract(should_update, artworks)
            if not should_extract_artworks:
                continue

            logger.info(f"Fetching {country.upper()} artworks for {movie['title']}")

            country_artworks = self.extract_artworks(
                localized_title, movie["director"], year, country
            )
            if country_artworks is None:
                if country == "fr":
                    logger.error(
                        f"No FR artworks found for {localized_title}: {movie['plex_movie_id']}"
                    )
                continue

            poster_url, background_url, logo_url, release_date = country_artworks

            if poster_url and not artworks["poster"] and should_update:
                logger.info(f"Found {country.upper()} poster for {localized_title}")
                artworks["poster"] = {
                    "url": poster_url,
                    "country": country,
                }
            if background_url and not artworks["background"]:
                logger.info(f"Found {country.upper()} background for {localized_title}")
                artworks["background"] = {
                    "url": background_url,
                    "country": country,
                }
            if logo_url and not artworks["logo"] and should_update:
                logger.info(f"Found {country.upper()} logo for {localized_title}")
                artworks["logo"] = {
                    "url": logo_url,
                    "country": country,
                }
            if release_date and country == "fr" and self.update_release_date:
                logger.info(f"Found release date for {localized_title}: {release_date}")
                artworks["release_date"] = {
                    "date": release_date,
                    "country": country,
                }
            time.sleep(self._api_call_interval)

        return artworks

    def get_localized_title(self, movie: dict, country: str) -> str | None:
        if country == "fr":
            return movie["title"]

        tmdb_id = movie.get("tmdb_id") or self.plex_manager.get_tmdb_id(
            movie["plex_movie_id"]
        )
        if not tmdb_id:
            return None
        return self.metadata_manager.get_localized_title(tmdb_id, country)

    def get_year(self, movie: dict) -> int:
        year = int(movie["release_date"][:4])
        return year

    def should_extract(
        self, should_update: bool, artworks: dict[str, dict[str, str]]
    ) -> bool:
        if not artworks["background"]:
            return True

        if not artworks["poster"] or not artworks["logo"]:
            return should_update

        return False

    def should_update(self, plex_title, localized_title) -> bool:
        is_title_match = are_match(plex_title, localized_title)
        return not self.match_title or is_title_match

    def extract_artworks(
        self, title: str, directors: list[str], year: int, country: str
    ) -> tuple[str, str, str, str] | None:
        artworks = get_itunes_artworks(title, directors, year, country)
        if artworks is None:
            return None

        itunes_url, poster_url, release_date = artworks

        time.sleep(self._api_call_interval)

        background_url, logo_url = get_apple_tv_artworks(itunes_url)
        return poster_url, background_url, logo_url, release_date

    def _log_upload_result(
        self, success: bool | None, artwork_type: str, title: str, plex_movie_id: int
    ) -> None:
        if success is None:
            if artwork_type != "release_date":
                logger.warning(f"No {artwork_type} found for {title}: {plex_movie_id}")
            return

        if success:
            logger.info(f"Uploaded {artwork_type} for {title}")
        else:
            logger.error(f"Failed to upload {artwork_type} for {title}")
