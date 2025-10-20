from __future__ import annotations

from typing import TYPE_CHECKING

from utils.string_utils import are_match

if TYPE_CHECKING:
    from models.artworks import Artworks, Image
    from models.movie import Movie


class ArtworksSelector:
    def __init__(
        self,
        match_movie_title: bool = False,
        match_logo_poster: bool = False,
        target_source: str = "apple",
    ) -> None:
        """
        Initialize the ArtworksSelector.

        Args:
            match_movie_title (bool): Whether to match movie title when selecting artworks
            match_logo_poster (bool): Whether to match logos to posters
        """
        self.match_movie_title = match_movie_title
        self.match_logo_poster = match_logo_poster
        self.target_source = target_source

    def select(self, artworks: Artworks, movie: Movie) -> Artworks:
        selected_artworks: Artworks = {
            "poster": self.select_poster(artworks["poster"], movie),
            "background": self.select_background(artworks["background"]),
            "logo": self.select_logo(
                artworks["logo"],
                artworks.get("fallback_logo"),
                artworks["poster"],
                movie,
            ),
        }
        return selected_artworks

    def select_poster(self, poster: Image | None, movie: Movie) -> Image | None:
        if poster is None or not self.is_matching_movie_title(poster, movie):
            return None

        return poster

    def select_background(self, background: Image | None) -> Image | None:
        return background

    def is_matching_movie_title(self, image: Image, movie: Movie) -> bool:
        return not self.match_movie_title or are_match(image["title"], movie["title"])

    def is_logo_matching_poster_title(self, logo: Image, poster: Image | None) -> bool:
        return (
            poster is None
            or not self.match_logo_poster
            or are_match(logo["title"], poster["title"])
        )

    def passes_title_checks(
        self, logo: Image | None, movie: Movie, poster: Image | None
    ) -> bool:
        return (
            logo is not None
            and self.is_matching_movie_title(logo, movie)
            and self.is_logo_matching_poster_title(logo, poster)
        )

    def select_logo(
        self,
        logo: Image | None,
        fallback_logo: Image | None,
        poster: Image | None,
        movie: Movie,
    ) -> Image | None:
        """
        Select which logo to return between `logo` and `fallback_logo` based on:
        - Whether the item exists
        - Optional title matching with movie title (match_movie_title)
        - Optional title matching with poster title (match_logo_poster)
        - Poster country preference when both exist (prefer item matching poster's country; if both match, prefer `logo`).
        """
        if logo is None and fallback_logo is None:
            return None

        if (logo is None) ^ (fallback_logo is None):
            logo = logo or fallback_logo
            return logo if self.passes_title_checks(logo, movie, poster) else None

        assert logo is not None and fallback_logo is not None
        preferred_order = [logo, fallback_logo]
        if poster is not None:
            logo_matches_country = logo["country"] == poster["country"]
            fallback_matches_country = fallback_logo["country"] == poster["country"]
            if fallback_matches_country and not logo_matches_country:
                preferred_order = [fallback_logo, logo]

        for candidate in preferred_order:
            if self.passes_title_checks(candidate, movie, poster):
                return candidate

        return None

    def select_fallback_or_not(self, logo: Image, fallback_logo: Image) -> Image:
        if fallback_logo is None:
            return logo

        if logo["country"] == fallback_logo["country"]:
            return logo

        return fallback_logo

    def are_perfect(self, artworks: Artworks, movie: Movie) -> bool:
        """
        Check if all artworks are from the perfect source and match the movie's metadata country.
        """
        required_artwork_types = ["poster", "background", "logo"]

        for artwork_type in required_artwork_types:
            image = artworks[artwork_type]
            if not image:
                return False

            is_perfect_source = image["source"] == self.target_source
            is_matching_country = image["country"] == movie["metadata_country"]

            if not is_perfect_source or not is_matching_country:
                return False

        return True
