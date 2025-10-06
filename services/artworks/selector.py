from __future__ import annotations

from typing import TYPE_CHECKING

from utils.string_utils import are_match

if TYPE_CHECKING:
    from models.artworks import Artworks, Image, Metadata
    from models.movie import Movie
    from services.artworks.rules import ArtworkRuleset


class ArtworkSelector:
    """Applies rules to manage updates on an Artworks instance."""

    def __init__(
        self, artworks: Artworks, ruleset: ArtworkRuleset, movie: Movie
    ) -> None:
        self.artworks = artworks
        self.ruleset = ruleset
        self.movie = movie

    def update_image(self, artwork_name: str, new_image: Image | None) -> bool:
        current_image: Image | None = self.artworks[artwork_name]
        if not self.ruleset.can_replace(
            artwork_name, new_image, current_image, self.movie["title"]
        ):
            return False

        self.artworks[artwork_name] = new_image
        return True

    def update_metadata(
        self, metadata_name: str, new_metadata: Metadata | None
    ) -> bool:
        current_metadata: Metadata | None = self.artworks[metadata_name]
        if new_metadata is None or current_metadata is not None:
            return False

        self.artworks[metadata_name] = new_metadata
        return True

    def can_accept(self, localized_title: str) -> bool:
        return self.ruleset.can_accept_localized_title(
            localized_title, self.movie["title"]
        )

    def is_complete(self) -> bool:
        return self.ruleset.is_complete(self.artworks)

    def is_perfect(self) -> bool:
        return self.ruleset.is_perfect(self.artworks, self.movie)

    def get_country_to_match_logo(self) -> str | None:
        logo, poster = self.artworks["logo"], self.artworks["poster"]
        if not logo or not poster:
            return None

        if logo["country"] == poster["country"]:
            return None

        if are_match(logo["title"], poster["title"]):
            return None

        return poster["country"]
