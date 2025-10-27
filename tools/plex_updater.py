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
        id = self.get_plex_id(plex_url)
        _, poster_url, background_url, logo_url = get_apple_tv_artworks(apple_tv_url)
        if poster:
            self.upload_image(id, "poster", poster_url)
        if background:
            self.upload_image(id, "background", background_url)
        if logo:
            self.upload_image(id, "logo", logo_url)

    def upload_image(self, id: int, image_type: str, image_url: str | None) -> None:
        if image_url is None:
            logger.warning(f"No {image_type} found in Apple TV.")
            return None
        self.plex_manager.upload_image(id, image_type, image_url)
        logger.info(f"Uploaded {image_type} from Apple TV for ID {id}.")

    def upload_logo_from_url(self, plex_url: str, logo_url: str) -> None:
        id = self.get_plex_id(plex_url)
        self.plex_manager.upload_logo(id, logo_url)

    @staticmethod
    def get_plex_id(url):
        match = re.search(r"metadata%2F(\d+)&", url)
        if match:
            return int(match.group(1))
        else:
            raise ValueError("No integer found in the URL")


if __name__ == "__main__":
    import argparse

    from utils.file_utils import load_json_file
    from utils.logger import setup_logging

    setup_logging()

    parser = argparse.ArgumentParser(description="Update Plex item images.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Commands")

    # Apple subparser
    apple_parser = subparsers.add_parser(
        "apple", help="Update Plex item images from Apple TV"
    )
    apple_parser.add_argument(
        "--config-path", type=str, required=True, help="Path to config file"
    )
    apple_parser.add_argument(
        "--plex-url", type=str, required=True, help="Plex item URL"
    )
    apple_parser.add_argument(
        "--apple-url", type=str, required=True, help="Apple TV item URL"
    )

    # Logo subparser
    logo_parser = subparsers.add_parser(
        "logo", help="Upload logo from URL to Plex item"
    )
    logo_parser.add_argument(
        "--config-path", type=str, required=True, help="Path to config file"
    )
    logo_parser.add_argument(
        "--plex-url", type=str, required=True, help="Plex item URL"
    )
    logo_parser.add_argument(
        "--logo-url", type=str, required=True, help="Logo image URL"
    )

    args = parser.parse_args()
    config = load_json_file(args.config_path)
    plex_manager = PlexManager(**config["plex"])
    plex_updater = PlexUpdater(plex_manager)

    if args.command == "apple":
        plex_updater.update(args.plex_url, args.apple_url)
    elif args.command == "logo":
        plex_updater.upload_logo_from_url(args.plex_url, args.logo_url)
