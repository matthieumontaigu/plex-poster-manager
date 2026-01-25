from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from client.plex.manager import PlexManager

logger = logging.getLogger(__name__)


def delete_last_uploaded_image(
    plex_manager: PlexManager,
    movie_id: int,
    image_type: Literal["posters", "art", "clearLogos"],
) -> None:
    """
    Deletes the last uploaded image of a given type for a specific movie.

    :param plex_manager: An instance of the PlexManager.
    :param movie_id: The ID of the movie.
    :param image_type: The type of image to delete ('posters', 'art', or 'clearLogos').
    """
    bundle_path = plex_manager.get_movie_bundle_path(movie_id)
    if not bundle_path:
        logger.error(f"Could not find bundle path for movie {movie_id}.")
        return

    uploads_folder = Path(bundle_path) / "Uploads" / image_type
    if not uploads_folder.is_dir():
        logger.info(f"No uploads folder found for {image_type} for movie {movie_id}.")
        return

    files = [
        (p, datetime.fromtimestamp(p.stat().st_mtime))
        for p in uploads_folder.iterdir()
        if p.is_file()
    ]

    if not files:
        logger.info(f"No uploaded {image_type} found for movie {movie_id}.")
        return

    latest_file, _ = max(files, key=lambda item: item[1])

    try:
        os.remove(latest_file)
        logger.info(f"Deleted {latest_file}")
    except OSError as e:
        logger.error(f"Error deleting file {latest_file}: {e}")
