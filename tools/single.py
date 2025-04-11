import re

from client.apple_tv.extract import get_apple_tv_artworks
from client.plex.manager import PlexManager


class PlexUploader:
    def __init__(self, plex_manager: PlexManager) -> None:
        self.plex_manager = plex_manager

    def upload_logo_from_url(self, plex_url: str, logo_url: str) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        self.plex_manager.upload_logo(plex_movie_id, logo_url)

    def upload_apple_tv_from_url(self, plex_url: str, apple_tv_url: str) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        self.upload_apple_tv(plex_movie_id, apple_tv_url)

    def upload_apple_tv(self, plex_movie_id: int, apple_tv_url: str) -> None:
        background_url, logo_url = get_apple_tv_artworks(apple_tv_url)
        self.plex_manager.upload_background(plex_movie_id, background_url)
        self.plex_manager.upload_logo(plex_movie_id, logo_url)

    def upload_apple_tv_background_from_url(
        self, plex_url: str, apple_tv_url: str
    ) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        self.upload_apple_tv_background(plex_movie_id, apple_tv_url)

    def upload_apple_tv_background(self, plex_movie_id: int, apple_tv_url: str) -> None:
        background_url, _ = get_apple_tv_artworks(apple_tv_url)
        self.plex_manager.upload_background(plex_movie_id, background_url)

    def upload_apple_tv_logo_from_url(self, plex_url: str, apple_tv_url: str) -> None:
        plex_movie_id = self.get_plex_movie_id(plex_url)
        self.upload_apple_tv_logo(plex_movie_id, apple_tv_url)

    def upload_apple_tv_logo(self, plex_movie_id: int, apple_tv_url: str) -> None:
        _, logo_url = get_apple_tv_artworks(apple_tv_url)
        self.plex_manager.upload_logo(plex_movie_id, logo_url)

    @staticmethod
    def get_plex_movie_id(url):
        match = re.search(r"metadata%2F(\d+)&", url)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("No integer found in the URL")
