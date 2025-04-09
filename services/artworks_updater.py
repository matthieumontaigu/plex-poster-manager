import logging
import time

from client.apple_tv.extract import get_apple_tv_artworks
from client.itunes.extract import get_itunes_artworks
from client.plex.manager import PlexManager
from services.metadata_manager import MetadataManager


class ArtworksUpdater:
    def __init__(
        self, plex_manager: PlexManager, metadata_manager: MetadataManager
    ) -> None:
        self.plex_manager = plex_manager
        self.metadata_manager = metadata_manager
        self.countries = ["fr", "us", "gb"]
        self.logger = logging.getLogger(__name__)

    def update_artworks(self, movie: dict) -> None:
        self.logger.info(f"Processing artworks for {movie['title']}")

        plex_movie_id = movie["plex_movie_id"]
        title = movie["title"]
        artworks = self.get_artworks(movie)
        for artwork_type, artwork in artworks.items():
            if not artwork:
                if artwork_type == "release_date":
                    continue
                self.logger.warning(f"No {artwork_type} found for movie {title}")
                continue

            elif artwork_type == "poster":
                poster_url = artwork["url"]
                success = self.plex_manager.upload_poster(plex_movie_id, poster_url)
                if success:
                    self.logger.info(f"Uploaded poster for movie {title}")
                else:
                    self.logger.error(f"Failed to upload poster for movie {title}")
                time.sleep(0.5)

            elif artwork_type == "background":
                background_url = artwork["url"]
                success = self.plex_manager.upload_background(
                    plex_movie_id, background_url
                )
                if success:
                    self.logger.info(f"Uploaded background for movie {title}")
                else:
                    self.logger.error(f"Failed to upload background for movie {title}")
                time.sleep(0.5)

            elif artwork_type == "logo":
                logo_url = artwork["url"]
                success = self.plex_manager.upload_logo(plex_movie_id, logo_url)
                if success:
                    self.logger.info(f"Uploaded logo for movie {title}")
                else:
                    self.logger.error(f"Failed to upload logo for movie {title}")
                time.sleep(0.5)

            elif artwork_type == "release_date":
                release_date = artwork["date"]
                self.plex_manager.update_release_date(plex_movie_id, release_date)
                time.sleep(0.5)

            else:
                self.logger.error(
                    f"Unknown artwork type: {artwork_type} for movie {title}"
                )
                continue

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

            self.logger.info(f"Fetching artworks for {movie['title']} in {country}")

            title = self.get_movie_title(movie, country)
            if not title:
                continue

            country_artworks = self.extract_artworks(
                title, movie["director"], year, country
            )
            if country_artworks is None:
                if country == "fr":
                    self.logger.warning(f"No FR artworks found for {title}")
                continue

            poster_url, background_url, logo_url, release_date = country_artworks

            if poster_url and not artworks["poster"]:
                self.logger.info(
                    f"Found {country.upper()} poster for {title}: {poster_url}"
                )
                artworks["poster"] = {
                    "url": poster_url,
                    "country": country,
                }
            if background_url and not artworks["background"]:
                self.logger.info(
                    f"Found {country.upper()} background for {title}: {background_url}"
                )
                artworks["background"] = {
                    "url": background_url,
                    "country": country,
                }
            if logo_url and not artworks["logo"]:
                self.logger.info(
                    f"Found {country.upper()} logo for {title}: {logo_url}"
                )
                artworks["logo"] = {
                    "url": logo_url,
                    "country": country,
                }
            if release_date and country == "fr":
                self.logger.info(f"Found release date for {title}: {release_date}")
                artworks["release_date"] = {
                    "date": release_date,
                    "country": country,
                }
            time.sleep(1.0)

        return artworks

    def get_movie_title(self, movie: dict, country: str) -> str | None:
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

    @staticmethod
    def extract_artworks(
        title: str, directors: list[str], year: int, country: str
    ) -> tuple[str, str, str, str] | None:
        artworks = get_itunes_artworks(title, directors, year, country)
        if artworks is None:
            return None

        itunes_url, poster_url, release_date = artworks
        time.sleep(1.0)
        background_url, logo_url = get_apple_tv_artworks(itunes_url)
        return poster_url, background_url, logo_url, release_date
