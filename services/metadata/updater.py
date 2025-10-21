from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.plex.manager import PlexManager
    from models.movie import Movie
    from services.localizer.localizer import Localizer

logger = logging.getLogger(__name__)


class MetadataUpdater:
    """Coordinates the process of retrieving, matching, and uploading artworks."""

    def __init__(
        self,
        plex_manager: PlexManager,
        localizer: Localizer,
    ) -> None:
        self.plex_manager = plex_manager
        self.localizer = localizer

    def update_release_date(self, movie: Movie) -> bool:
        if movie["tmdb_id"] is None:
            logger.warning(
                f"Movie '{movie['title']}' does not have a TMDB ID. Cannot update release date."
            )
            return False

        release_date = self.localizer.get_country_release_date(
            movie["tmdb_id"], movie["metadata_country"]
        )
        if release_date is None:
            logger.warning(
                f"Could not find release date for movie '{movie['title']}' "
                f"in country '{movie['metadata_country']}'"
            )
            return False

        release_date = datetime.fromisoformat(release_date).strftime("%Y-%m-%d")
        self.plex_manager.update_release_date(movie["plex_movie_id"], release_date)
        logger.info(
            f"Updated release date for movie '{movie['title']}' " f"to '{release_date}'"
        )
        return True
