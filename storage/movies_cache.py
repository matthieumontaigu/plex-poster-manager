from typing import Any, ItemsView

from storage.cache import Cache


class MoviesCache:
    def __init__(self, path: str, filename: str, retention_seconds: int = 0) -> None:
        self.cache = Cache(path, filename)
        self.updated = False
        self.retention_seconds = retention_seconds

    def add(self, movie: dict) -> None:
        key = self.get_key(movie)
        if key not in self.cache:
            self.cache.add(key, movie)
            self.updated = True

    def remove(self, movie: dict) -> None:
        key = self.get_key(movie)
        if key in self.cache:
            self.cache.remove(key)
            self.updated = True

    def remove_all(self, movies: list[dict]) -> None:
        for movie in movies:
            self.remove(movie)

    def clear(self, movie: dict) -> None:
        threshold = movie["added_date"]
        keys_before = [
            key
            for key in self.cache
            if self.cache.get(key)["added_date"] < threshold - self.retention_seconds
        ]
        for key in keys_before:
            self.cache.remove(key)
            self.updated = True

    def load(self) -> None:
        self.cache.load()

    def save(self) -> None:
        if self.updated:
            self.cache.save()
            self.updated = False

    def get_key(self, movie: dict) -> int:
        return movie["plex_movie_id"]

    def items(self) -> ItemsView[Any, Any]:
        return self.cache.items()

    def __contains__(self, movie: dict) -> bool:
        key = self.get_key(movie)
        return key in self.cache
