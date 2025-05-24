import urllib.parse
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
    title = movie.attrib.get("title")
    cleaned_title = title.replace("\xa0", " ") if title else ""

    addedAt = movie.attrib.get("addedAt")
    added_date = int(addedAt) if addedAt else 0

    movie_year = movie.attrib.get("year")
    year = int(movie_year) if movie_year else 0

    attributes = {
        "plex_movie_id": movie.attrib.get("ratingKey"),
        "title": cleaned_title,
        "year": year,
        "added_date": added_date,
        "release_date": movie.attrib.get("originallyAvailableAt"),
        "director": get_directors(movie),
        "guid": movie.get("guid"),
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


def get_photos(api_response: Response) -> list[dict[str, str]]:
    """
    Extract photo URLs from the XML element.
    :param photos: The XML element containing photo information.
    :return: A list of photo URLs.
    """
    root = parse_xml(api_response)
    photos = []

    for photo in root.findall("Photo"):
        entry = {}
        for attr, value in photo.attrib.items():
            # Decode URL-encoded values
            entry[attr] = urllib.parse.unquote(value)
        photos.append(entry)

    return photos
