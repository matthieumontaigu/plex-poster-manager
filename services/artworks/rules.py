from __future__ import annotations

from typing import TYPE_CHECKING

from utils.string_utils import are_match

if TYPE_CHECKING:
    from models.artworks import Artworks, Image
    from models.movie import Movie


class ArtworkRuleset:
    """
    Defines the logic for deciding whether a new artwork should replace an existing one.
    """

    def __init__(self, match_target_title: bool) -> None:
        self.match_target_title = match_target_title
        self.perfect_source = "apple"

    def can_accept_localized_title(
        self, localized_title: str, movie_title: str
    ) -> bool:
        if not self.match_target_title:
            return True
        return are_match(localized_title, movie_title)

    def can_replace(
        self,
        artwork_name: str,
        new: Image | None,
        current: Image | None,
        movie_title: str,
    ) -> bool:
        """
        Return True if the new image should replace the current one.
        Assuming current images are always higher priority.
        """
        if new is None:
            return False

        if current is not None:
            return self.can_override_current(current, new)

        if artwork_name == "poster":
            return self.can_replace_poster(new, movie_title)

        if artwork_name == "background":
            return self.can_replace_background()

        if artwork_name == "logo":
            return self.can_replace_logo(new, movie_title)

        raise ValueError(f"Unknown artwork type: {artwork_name}")

    def can_override_current(self, current: Image, new: Image) -> bool:
        return current["source"] != new["source"]

    def can_replace_poster(self, poster: Image, movie_title: str) -> bool:
        return not self.match_target_title or are_match(poster["title"], movie_title)

    def can_replace_background(self) -> bool:
        return True

    def can_replace_logo(self, logo: Image, movie_title: str) -> bool:
        return not self.match_target_title or are_match(logo["title"], movie_title)

    def is_complete(self, artworks: Artworks) -> bool:
        return all(artworks[key] for key in ["poster", "background", "logo"])

    def is_perfect(self, artworks: Artworks, movie: Movie) -> bool:
        """
        Check if all artworks are from the perfect source or match the movie's metadata country.

        Returns True if all required artworks (poster, background, logo) exist and each one
        is either from the perfect source or from the movie's metadata country.
        """
        required_artwork_types = ["poster", "background", "logo"]

        for artwork_type in required_artwork_types:
            image = artworks[artwork_type]
            if not image:
                return False

            is_perfect_source = image["source"] == self.perfect_source
            is_matching_country = image["country"] == movie["metadata_country"]

            if not (is_perfect_source or is_matching_country):
                return False

        return True

    def is_logo_matching_poster(self, artworks: Artworks, movie: Movie) -> bool:
        logo, poster = artworks["logo"], artworks["poster"]
        if not logo or not poster:
            return True

        if poster["country"] != movie["metadata_country"]:
            return True

        return are_match(logo["title"], poster["title"])
