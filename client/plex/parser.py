from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING
from xml.etree.ElementTree import Element

if TYPE_CHECKING:
    from requests import Response

    from models.movie import Movie


def parse_movies(api_response: Response, country: str) -> list[Movie]:
    root = parse_xml(api_response)
    return _get_movies(root, country)


def parse_movie(api_response: Response, country: str) -> Movie | None:
    root = parse_xml(api_response)
    movie = root.find("Video")
    if movie is None:
        return None
    return _get_movie(movie, country)


def parse_xml(api_response: Response) -> Element:
    return ET.fromstring(api_response.content)


def _get_movies(root: Element, country: str) -> list[Movie]:
    movies = []
    for movie_element in root.findall("Video"):
        movie = _get_movie(movie_element, country)
        movies.append(movie)
    return movies


def _get_movie(movie: Element, country: str) -> Movie:
    """Extract movie attributes from the XML element."""
    plex_movie_id = movie.attrib.get("ratingKey")
    if plex_movie_id is None:
        raise ValueError("Movie element is missing 'ratingKey' attribute.")

    title = movie.attrib.get("title")
    cleaned_title = title.replace("\xa0", " ") if title else ""

    addedAt = movie.attrib.get("addedAt")
    added_date = int(addedAt) if addedAt else 0

    movie_year = movie.attrib.get("year")
    year = int(movie_year) if movie_year else 0

    attributes: Movie = {
        "plex_movie_id": int(plex_movie_id),
        "title": cleaned_title,
        "year": year,
        "added_date": added_date,
        "release_date": movie.attrib.get("originallyAvailableAt"),
        "director": get_directors(movie),
        "metadata_country": country,
        "guid": movie.get("guid"),
        "tmdb_id": get_tmdb_id(movie),
    }
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


def get_tmdb_id(movie: Element) -> int | None:
    guid = movie.findall(".//Guid")
    if not guid:
        return None

    for g in guid:
        id = g.attrib.get("id")
        if id and id.startswith("tmdb://"):
            # Return the TMDB ID by stripping the prefix
            return int(id.split("://")[-1])

    return None


def parse_photos(api_response: Response) -> list[dict[str, str]]:
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
