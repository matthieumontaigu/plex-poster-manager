import logging
import time

from client.plex.manager import PlexManager
from models.artworks import Artworks
from services.metadata_retriever import MetadataRetriever

logger = logging.getLogger(__name__)


class ArtworksUpdater:
    def __init__(
        self,
        plex_manager: PlexManager,
        metadata_retriever: MetadataRetriever,
        plex_country: str = "fr",
        countries: list[str] = ["fr", "us", "gb", "be", "ch", "lu"],
        match_title: bool = True,
        match_logo: bool = False,
        update_release_date: bool = False,
        api_call_interval: float = 1.0,
    ) -> None:
        self.plex_manager = plex_manager
        self.metadata_retriever = metadata_retriever

        self.plex_country = plex_country
        self.countries = countries
        self.match_title = match_title
        self.match_logo = match_logo
        self.update_release_date = update_release_date
        self.api_call_interval = api_call_interval

    def update_artworks(
        self, movie: dict
    ) -> tuple[dict[str, dict[str, str]], bool, bool]:
        artworks, release_date = self.get_artworks(movie)
        uploaded = self.upload_artworks(movie, artworks, release_date)
        is_complete = self.is_complete(artworks)

        return artworks, uploaded, is_complete

    def upload_artworks(
        self,
        movie: dict,
        artworks: dict[str, dict[str, str]],
        release_date: str | None = None,
    ) -> bool:
        logger.info(f"Uploading artworks for {movie['title']}")

        plex_movie_id = movie["plex_movie_id"]
        title = movie["title"]
        uploaded = True
        for artwork_type, artwork in artworks.items():
            success = self.upload_artwork(artwork_type, artwork, plex_movie_id, title)
            uploaded &= success
            time.sleep(self.api_call_interval)

        if self.update_release_date and release_date:
            success = self.plex_manager.update_release_date(plex_movie_id, release_date)
            movie["itunes_release_date"] = release_date
            self._log_upload_result(success, "release_date", title, plex_movie_id)

        return uploaded

    def upload_artwork(
        self, artwork_type: str, artwork: dict[str, str], plex_movie_id: int, title: str
    ) -> bool:
        if not artwork:
            logger.warning(f"No {artwork_type} found for {title}: {plex_movie_id}")
            return True

        elif artwork_type == "poster":
            poster_url = artwork["url"]
            success = self.plex_manager.upload_poster(plex_movie_id, poster_url)

        elif artwork_type == "background":
            background_url = artwork["url"]
            success = self.plex_manager.upload_background(plex_movie_id, background_url)

        elif artwork_type == "logo":
            logo_url = artwork["url"]
            success = self.plex_manager.upload_logo(plex_movie_id, logo_url)

        else:
            raise ValueError(
                f"Invalid artwork type: {artwork_type}. Expected one of: poster, background, logo."
            )

        self._log_upload_result(success, artwork_type, title, plex_movie_id)
        return success

    def is_complete(
        self,
        artworks: dict[str, dict[str, str]],
    ) -> bool:
        if not artworks:
            return False

        return all(
            artwork
            and artwork["country"] == self.plex_country
            and "source" not in artwork
            for artwork in artworks.values()
        )

    def get_artworks(self, movie: dict) -> tuple[dict[str, dict[str, str]], str | None]:
        logger.info(f"Retrieving artworks for {movie['title']}")

        title = movie["title"]
        year = movie["year"]

        artworks = Artworks(title, self.match_title)
        release_date = None
        for country in self.countries:

            country_release_date = self.get_country_artworks(
                artworks, movie, year, country
            )
            if country == self.plex_country:
                release_date = country_release_date

            if artworks.is_complete():
                break

            time.sleep(self.api_call_interval)

        self.match_logo_to_poster(movie, artworks)

        return artworks.get(), release_date

    def get_country_artworks(
        self, artworks: Artworks, movie: dict, year: int, country: str
    ) -> str | None:
        country_title = self.get_country_title(movie, country)
        if not country_title:
            return None

        if not artworks.should_handle(country_title):
            return None

        logger.info(f"Fetching {country.upper()} artworks for {movie['title']}")

        country_artworks = self.metadata_retriever.get_apple_artworks(
            country_title, movie["director"], year, country
        )
        if country_artworks is None:
            self._log_missing_artworks(movie, country)
            return None

        poster_url, background_url, logo_url, country_release_date = country_artworks

        updated = artworks.update("poster", poster_url, country, country_title)
        self._log_found_artwork(updated, "poster", country_title, country)

        updated = artworks.update("background", background_url, country, country_title)
        self._log_found_artwork(updated, "background", country_title, country)

        updated = artworks.update("logo", logo_url, country, country_title)
        self._log_found_artwork(updated, "logo", country_title, country)

        return country_release_date

    def get_country_title(self, movie: dict, country: str) -> str | None:
        if country == self.plex_country:
            return movie["title"]

        tmdb_id = self.get_tmdb_id(movie)
        return self.metadata_retriever.get_localized_title(tmdb_id, country)

    def match_logo_to_poster(self, movie: dict, artworks: Artworks) -> None:
        """
        Match logo to poster if poster is in the same country as the plex server.
        This is useful for countries where the logo is not available in the Apple API.
        Exceptions:
        - If the logo is already set and matches the poster, the logo will not be updated.
        - If the poster is not in the same country as the plex server, the logo will not be updated.
        - If the logo cannot be matched to the poster (e.g. not found in TMDB), the logo will not be updated.
        """
        if not self.match_logo:
            return

        if (
            artworks.logo_matches_poster()
            or artworks.get_poster_country() != self.plex_country
        ):
            return

        tmdb_id = self.get_tmdb_id(movie)
        tmdb_logo_url = self.metadata_retriever.get_tmdb_logo_url(
            tmdb_id, self.plex_country
        )
        updated = artworks.update(
            "logo",
            tmdb_logo_url,
            self.plex_country,
            movie["title"],
            "tmdb",
            override=True,
        )

        self._log_found_artwork(
            updated, "logo", movie["title"], self.plex_country, "tmdb"
        )

    def get_tmdb_id(self, movie: dict) -> int | None:
        tmdb_id = movie.get("tmdb_id") or self.plex_manager.get_tmdb_id(
            movie["plex_movie_id"]
        )
        if not tmdb_id:
            return None

        try:
            tmdb_id_int = int(tmdb_id)
        except (TypeError, ValueError):
            return None

        movie["tmdb_id"] = tmdb_id_int
        return tmdb_id_int

    def _log_missing_artworks(self, movie: dict, country: str) -> None:
        title = movie["title"]
        plex_movie_id = movie["plex_movie_id"]
        if country == self.plex_country:
            logger.error(
                f"No {country.upper()} artworks found for {title}: {plex_movie_id}"
            )

    def _log_found_artwork(
        self,
        found: bool,
        artwork_type: str,
        title: str,
        country: str,
        source: str = "",
    ) -> None:
        if found:
            source = f"{source} " if source else ""
            logger.info(f"Found {source}{country.upper()} {artwork_type} for {title}")

    def _log_upload_result(
        self, success: bool | None, artwork_type: str, title: str, plex_movie_id: int
    ) -> None:
        if success:
            logger.info(f"Uploaded {artwork_type} for {title}")
        else:
            logger.error(f"Failed to upload {artwork_type} for {title}")
