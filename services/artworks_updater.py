import logging
import time

from client.apple_tv.extract import get_apple_tv_artworks
from client.itunes.extract import get_itunes_artworks
from client.plex.manager import PlexManager
from models.artworks import Artworks
from services.metadata_manager import MetadataManager
from utils.string_utils import are_match

logger = logging.getLogger(__name__)


class ArtworksUpdater:
    def __init__(
        self,
        plex_manager: PlexManager,
        metadata_manager: MetadataManager,
        plex_country: str = "fr",
        countries: list[str] = ["fr", "us", "gb", "be", "ch", "lu"],
        match_title: bool = True,
        update_release_date: bool = False,
        api_call_interval: float = 1.0,
    ) -> None:
        self.plex_manager = plex_manager
        self.metadata_manager = metadata_manager

        self.plex_country = plex_country
        self.countries = countries
        self.match_title = match_title
        self.update_release_date = update_release_date
        self.api_call_interval = api_call_interval

    def update_artworks(self, movie: dict) -> tuple[bool, dict[str, dict[str, str]]]:
        logger.info(f"Processing artworks for {movie['title']}")

        plex_movie_id = movie["plex_movie_id"]
        title = movie["title"]
        artworks, release_date = self.get_artworks(movie)

        is_missing = False
        for artwork_type, artwork in artworks.items():
            success = self.update_artwork(artwork_type, artwork, plex_movie_id)
            self._log_upload_result(success, artwork_type, title, plex_movie_id)
            is_missing |= self.is_missing_artwork(artwork, success)
            time.sleep(self.api_call_interval)

        if self.update_release_date and release_date:
            success = self.plex_manager.update_release_date(plex_movie_id, release_date)
            movie["itunes_release_date"] = release_date
            self._log_upload_result(success, "release_date", title, plex_movie_id)

        return is_missing, artworks

    def is_missing_artwork(
        self,
        artwork: dict[str, str],
        upload_success: bool | None,
    ) -> bool:
        if not upload_success:
            return True

        return artwork["country"] != self.plex_country

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

        else:
            return None

    def get_artworks(self, movie: dict) -> tuple[dict[str, dict[str, str]], str | None]:
        year = self.get_year(movie)

        artworks = Artworks()
        release_date = None
        for country in self.countries:
            if artworks.is_complete():
                break

            country_title = self.get_country_title(movie, country)
            if not country_title:
                continue

            if self.can_update_texted_artworks(movie["title"], country_title):
                artworks.allow_texted_update()
            else:
                artworks.disallow_texted_update()

            if not artworks.is_any_missing():
                continue

            logger.info(f"Fetching {country.upper()} artworks for {movie['title']}")

            country_artworks = self.extract_artworks(
                country_title, movie["director"], year, country
            )
            if country_artworks is None:
                self._log_missing_artworks(movie, country)
                continue

            poster_url, background_url, logo_url, country_release_date = (
                country_artworks
            )
            updated = artworks.update("poster", poster_url, country)
            self._log_found_artwork(updated, "poster", country_title, country)

            updated = artworks.update("background", background_url, country)
            self._log_found_artwork(updated, "background", country_title, country)

            updated = artworks.update("logo", logo_url, country)
            self._log_found_artwork(updated, "logo", country_title, country)

            if country == self.plex_country:
                release_date = country_release_date

            time.sleep(self.api_call_interval)

        return artworks.get(), release_date

    def get_year(self, movie: dict) -> int:
        year = int(movie["release_date"][:4])
        return year

    def get_country_title(self, movie: dict, country: str) -> str | None:
        if country == self.plex_country:
            return movie["title"]

        tmdb_id = movie.get("tmdb_id") or self.plex_manager.get_tmdb_id(
            movie["plex_movie_id"]
        )
        if not tmdb_id:
            return None

        return self.metadata_manager.get_localized_title(tmdb_id, country)

    def can_update_texted_artworks(self, plex_title: str, country_title: str) -> bool:
        is_title_match = are_match(plex_title, country_title)
        return not self.match_title or is_title_match

    def extract_artworks(
        self, title: str, directors: list[str], year: int, country: str
    ) -> tuple[str, str, str, str] | None:
        artworks = get_itunes_artworks(title, directors, year, country)
        if artworks is None:
            return None

        itunes_url, poster_url, release_date = artworks

        time.sleep(self.api_call_interval)

        background_url, logo_url = get_apple_tv_artworks(itunes_url)
        return poster_url, background_url, logo_url, release_date

    def _log_missing_artworks(self, movie: dict, country: str) -> None:
        title = movie["title"]
        plex_movie_id = movie["plex_movie_id"]
        if country == self.plex_country:
            logger.error(
                f"No {country.upper()} artworks found for {title}: {plex_movie_id}"
            )

    def _log_found_artwork(
        self, found: bool, artwork_type: str, title: str, country: str
    ) -> None:
        if found:
            logger.info(f"Found {country.upper()} {artwork_type} for {title}")

    def _log_upload_result(
        self, success: bool | None, artwork_type: str, title: str, plex_movie_id: int
    ) -> None:
        if success is None:
            logger.warning(f"No {artwork_type} found for {title}: {plex_movie_id}")
            return

        if success:
            logger.info(f"Uploaded {artwork_type} for {title}")
        else:
            logger.error(f"Failed to upload {artwork_type} for {title}")
