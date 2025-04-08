import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from requests import Response


def get_movies(api_response: Response) -> list[dict[str, str | list[str] | None]]:
    root = ET.fromstring(api_response.content)

    movies = []
    for movie in root.findall("Video"):
        movie_attributes = {
            "plex_movie_id": movie.attrib.get("ratingKey"),
            "title": movie.attrib.get("title"),
            "year": movie.attrib.get("year"),
            "added_date": movie.attrib.get("addedAt"),
            "release_date": movie.attrib.get("originallyAvailableAt"),
            "director": get_directors(movie),
            "tmdb_id": get_tmdb_id(movie),
        }
        movies.append(movie_attributes)
    return movies


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
