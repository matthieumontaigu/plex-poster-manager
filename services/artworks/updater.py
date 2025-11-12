from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.artworks import Artworks
    from models.movie import Movie
    from services.artworks.retriever import ArtworksRetriever
    from services.artworks.selector import ArtworksSelector
    from services.artworks.uploader import ArtworksUploader

logger = logging.getLogger(__name__)


class ArtworksUpdater:
    """Coordinates the process of retrieving, matching, and uploading artworks."""

    def __init__(
        self,
        artworks_retriever: ArtworksRetriever,
        artworks_selector: ArtworksSelector,
        artworks_uploader: ArtworksUploader,
    ) -> None:
        self.retriever = artworks_retriever
        self.selector = artworks_selector
        self.uploader = artworks_uploader

    def process(self, movie: Movie) -> tuple[Artworks, bool]:
        """
        Fetch and upload artworks for a given movie.

        Returns:
            tuple[Artworks, bool]: The fetched artworks and whether the upload was successful.
        """
        artworks = self.retriever.retrieve(movie)
        selected_artworks = self.selector.select(artworks, movie)
        uploaded = self.uploader.upload(movie, selected_artworks)
        return artworks, uploaded

    def fetch(self, movie: Movie) -> Artworks:
        artworks = self.retriever.retrieve(movie)
        selected_artworks = self.selector.select(artworks, movie)
        return selected_artworks

    def update(
        self, movie: Movie, current_artworks: Artworks | None
    ) -> tuple[str, Artworks]:
        """
        Update a single movie's artworks.

        Returns:
            str: status among ["success", "imperfect_artworks", "identical_artworks", "upload_failed"]
        """
        new_artworks = self.fetch(movie)

        if new_artworks == current_artworks:
            return "unchanged_artworks", new_artworks

        uploaded = self.uploader.upload(movie, new_artworks)
        if not uploaded:
            return "upload_failed", new_artworks

        if self.selector.are_empty(new_artworks):
            return "empty_artworks", new_artworks

        if not self.selector.are_perfect(new_artworks, movie):
            return "imperfect_artworks", new_artworks

        return "success", new_artworks
