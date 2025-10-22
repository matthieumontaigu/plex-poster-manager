from abc import ABC, abstractmethod


class Provider(ABC):
    """Metadata source that combines iTunes and Apple TV data."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def get_artworks(
        self, title: str, directors: list[str], year: int, country: str, entity: str
    ) -> tuple[str | None, str | None, str | None]: ...
