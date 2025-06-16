from utils.string_utils import are_match


class Artworks:
    def __init__(self, movie_title: str, should_match_title: bool) -> None:
        self.data: dict[str, dict[str, str]] = {
            "poster": {},
            "background": {},
            "logo": {},
        }
        self.movie_title = movie_title
        self.should_match_title = should_match_title

        self._texted_artworks = ["poster", "logo"]
        self._textless_artworks = ["background"]

    def get(self) -> dict[str, dict[str, str]]:
        return self.data

    def is_complete(self) -> bool:
        return all(self.data[key] for key in ["poster", "background", "logo"])

    def is_missing(self, key: str) -> bool:
        return not self.data[key]

    def update(
        self,
        key: str,
        url: str | None,
        country: str,
        title: str,
        source: str = "",
        override: bool = False,
    ) -> bool:
        if not url or (self.data[key] and not override):
            return False

        if key in self._texted_artworks and not self.can_update_texted(title):
            return False

        self.data[key] = {"url": url, "country": country, "title": title}
        if source:
            self.data[key]["source"] = source
        return True

    def should_handle(self, title: str) -> bool:
        if self._is_any_textless_artwork_missing():
            return True

        if not self._is_any_texted_artwork_missing():
            return False

        return self.can_update_texted(title)

    def can_update_texted(self, title: str) -> bool:
        if not self.should_match_title:
            return True

        return are_match(title, self.movie_title)

    def logo_matches_poster(self) -> bool:
        poster_title = self.data["poster"].get("title")
        logo_title = self.data["logo"].get("title")
        if not poster_title or not logo_title:
            return True

        return are_match(poster_title, logo_title)

    def get_poster_country(self) -> str | None:
        return self.data["poster"].get("country")

    def _is_any_textless_artwork_missing(self) -> bool:
        return any(self.is_missing(key) for key in self._textless_artworks)

    def _is_any_texted_artwork_missing(self) -> bool:
        return any(self.is_missing(key) for key in self._texted_artworks)
