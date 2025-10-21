from __future__ import annotations

from collections.abc import ItemsView
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from models.movie import Movie

from storage.cache import Cache


class MoviesCache:
    def __init__(self, path: str, filename: str, retention_seconds: int = 0) -> None:
        self.cache = Cache(path, filename)
        self.retention_seconds = retention_seconds

    def add(self, movie: Movie) -> None:
        id = self.get_id(movie)
        if id not in self.cache:
            self.cache.add(id, movie)

    def remove(self, movie: Movie) -> None:
        id = self.get_id(movie)
        if id in self.cache:
            self.cache.remove(id)

    def remove_all(self, movies: list[Movie]) -> None:
        for movie in movies:
            self.remove(movie)

    def clear(self, movie: Movie) -> None:
        prune_before_ts = movie["added_date"] - self.retention_seconds

        movies_ids_before = [
            id
            for id, cached_movie in self.cache.items()
            if cached_movie["added_date"] < prune_before_ts
        ]
        for id in movies_ids_before:
            self.cache.remove(id)

    def load(self) -> None:
        self.cache.load()

    def save(self) -> None:
        self.cache.save()

    def get_id(self, movie: Movie) -> int:
        return movie["plex_movie_id"]

    def items(self) -> ItemsView[int, Movie]:
        return self.cache.items()

    def __contains__(self, movie: Movie) -> bool:
        id = self.get_id(movie)
        return id in self.cache

    def __iter__(self):
        return iter(self.cache)
