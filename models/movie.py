from typing import NotRequired, TypedDict

from models.artworks import Artworks


class Movie(TypedDict):
    plex_movie_id: int
    title: str
    year: int
    added_date: int
    release_date: str | None
    director: list[str]
    metadata_country: str
    guid: str | None
    tmdb_id: int | None
    artworks: NotRequired[Artworks]
