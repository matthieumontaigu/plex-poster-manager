import logging
import re

from client.apple_tv.extract import get_apple_tv_artworks
from client.plex.manager import PlexManager

logger = logging.getLogger(__name__)


class PlexUpdater:
    def __init__(self, plex_manager: PlexManager) -> None:
        self.plex_manager = plex_manager

    def update(
        self,
        plex_url: str,
        apple_tv_url: str,
        *,
        poster: bool = True,
        background: bool = True,
        logo: bool = True,
    ) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        _, poster_url, background_url, logo_url = get_apple_tv_artworks(apple_tv_url)
        if poster:
            self.upload_image(plex_movie_id, "poster", poster_url)
        if background:
            self.upload_image(plex_movie_id, "background", background_url)
        if logo:
            self.upload_image(plex_movie_id, "logo", logo_url)

    def upload_image(
        self, movie_id: int, image_type: str, image_url: str | None
    ) -> None:
        if image_url is None:
            logger.warning(f"No {image_type} found in Apple TV.")
            return None
        self.plex_manager.upload_image(movie_id, image_type, image_url)
        logger.info(f"Uploaded {image_type} from Apple TV for movie ID {movie_id}.")

    def upload_logo_from_url(self, plex_url: str, logo_url: str) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        self.plex_manager.upload_logo(plex_movie_id, logo_url)

    @staticmethod
    def get_plex_movie_id(url):
        match = re.search(r"metadata%2F(\d+)&", url)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("No integer found in the URL")
