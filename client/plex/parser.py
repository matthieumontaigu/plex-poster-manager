import xml.etree.ElementTree as ET

from requests import Response


def get_movies(api_response: Response) -> list[dict[str, str | None]]:
    root = ET.fromstring(api_response.content)

    movies = []
    for movie in root.findall("Video"):
        movies.append(
            {
                "plex_movie_id": movie.attrib.get("ratingKey"),
                "title": movie.attrib.get("title"),
                "release_date": movie.attrib.get("originallyAvailableAt"),
            }
        )
    return movies
