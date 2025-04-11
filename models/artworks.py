class Artworks:
    def __init__(self) -> None:
        self.data: dict[str, dict[str, str]] = {
            "poster": {},
            "background": {},
            "logo": {},
        }
        self._texted_artworks = ["poster", "logo"]
        self._textless_artworks = ["background"]
        self.can_update_texted = True

    def get(self) -> dict[str, dict[str, str]]:
        return self.data

    def allow_texted_update(self) -> None:
        self.can_update_texted = True

    def disallow_texted_update(self) -> None:
        self.can_update_texted = False

    def is_complete(self) -> bool:
        return all(self.data[key] for key in ["poster", "background", "logo"])

    def is_missing(self, key: str) -> bool:
        return not self.data[key]

    def is_any_missing(self) -> bool:
        if any(self.is_missing(key) for key in self._textless_artworks):
            return True

        if self.can_update_texted:
            return any(self.is_missing(key) for key in self._texted_artworks)

        return False

    def update(self, key: str, url: str, country: str) -> bool:
        if not url or self.data[key]:
            return False

        if key in self._texted_artworks and not self.can_update_texted:
            return False

        self.data[key] = {"url": url, "country": country}
        return True
