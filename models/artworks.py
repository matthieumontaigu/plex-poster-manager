from typing import TypedDict


class Image(TypedDict):
    url: str
    country: str
    language: str
    title: str
    source: str


class Metadata(TypedDict):
    value: str
    country: str


class Artworks(TypedDict):
    poster: Image | None
    background: Image | None
    logo: Image | None
    release_date: Metadata | None


def build_image(
    url: str | None, country: str, language: str, title: str, source: str
) -> Image | None:
    if url is None:
        return None

    return {
        "url": url,
        "country": country,
        "language": language,
        "title": title,
        "source": source,
    }


def build_metadata(value: str | None, country: str) -> Metadata | None:
    if value is None:
        return None

    return {
        "value": value,
        "country": country,
    }
