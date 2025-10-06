from abc import ABC, abstractmethod


class LogoProvider(ABC):
    """Abstracts a secondary source for logos, separate from main provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the logo provider."""
        ...

    @abstractmethod
    def get_logo(self, movie_id: int, language: str) -> str | None:
        """Return logo image or None if not available."""
        ...
