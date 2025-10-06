from client.apple_tv.extract import get_apple_tv_artworks
from client.itunes.extract import get_itunes_artworks
from services.provider.base import Provider


class AppleProvider(Provider):
    """Metadata source that combines iTunes and Apple TV data."""

    @property
    def name(self) -> str:
        return "apple"

    def get_artworks(
        self, title: str, directors: list[str], year: int, country: str
    ) -> tuple[str | None, str | None, str | None]:
        itunes_url, poster_url, _ = get_itunes_artworks(title, directors, year, country)
        if not itunes_url:
            return None, None, None

        background_url, logo_url = get_apple_tv_artworks(itunes_url)
        return poster_url, background_url, logo_url

    def get_release_date(
        self, title: str, directors: list[str], year: int, country: str
    ) -> str | None:
        _, _, release_date = get_itunes_artworks(title, directors, year, country)
        return release_date
