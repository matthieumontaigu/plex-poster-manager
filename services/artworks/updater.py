from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.artworks import Artworks
    from models.movie import Movie
    from services.artworks.retriever import ArtworksRetriever
    from services.artworks.uploader import ArtworksUploader

logger = logging.getLogger(__name__)


class ArtworksUpdater:
    """Coordinates the process of retrieving, matching, and uploading artworks."""

    def __init__(
        self, artworks_retriever: ArtworksRetriever, artworks_uploader: ArtworksUploader
    ) -> None:
        self.retriever = artworks_retriever
        self.uploader = artworks_uploader

    def update(self, movie: Movie) -> tuple[Artworks, bool]:
        artworks = self.retriever.retrieve(movie)

        uploaded = self.uploader.upload(movie, artworks)

        return artworks, uploaded
