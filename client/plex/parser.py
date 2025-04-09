import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from requests import Response


def get_movies(
    api_response: Response,
) -> list[dict[str, str | int | list[str] | None]]:
    root = parse_xml(api_response)
    return _get_movies(root)


def get_movie_attributes(
    api_response: Response,
) -> dict[str, str | int | list[str] | None]:
    root = parse_xml(api_response)
    movie = root.find("Video")
    if movie is None:
        return {}
    return _get_movie_attributes(movie)


def parse_xml(api_response: Response) -> Element:
    return ET.fromstring(api_response.content)


def _get_movies(root: Element) -> list[dict[str, str | int | list[str] | None]]:
    movies = []
    for movie in root.findall("Video"):
        movie_attributes = _get_movie_attributes(movie)
        movies.append(movie_attributes)
    return movies


def _get_movie_attributes(movie: Element) -> dict[str, str | int | list[str] | None]:
    """Extract movie attributes from the XML element."""
    addedAt = movie.attrib.get("addedAt")
    added_date = int(addedAt) if addedAt else 0
    attributes = {
        "plex_movie_id": movie.attrib.get("ratingKey"),
        "title": movie.attrib.get("title"),
        "year": movie.attrib.get("year"),
        "added_date": added_date,
        "release_date": movie.attrib.get("originallyAvailableAt"),
        "director": get_directors(movie),
    }
    tmdb_id = get_tmdb_id(movie)
    if tmdb_id:
        attributes["tmdb_id"] = tmdb_id
    return attributes


def get_directors(movie: Element) -> list[str]:
    directors = movie.findall(".//Director")
    directors_names: list[str] = []
    if not directors:
        return directors_names

    for director in directors:
        name = director.attrib.get("tag")
        if name:
            directors_names.append(name)
    return directors_names


def get_tmdb_id(movie: Element) -> str | None:
    guid = movie.findall(".//Guid")
    if not guid:
        return None

    for g in guid:
        id = g.attrib.get("id")
        if id and id.startswith("tmdb://"):
            # Return the TMDB ID by stripping the prefix
            return id.split("://")[-1]

    return None
