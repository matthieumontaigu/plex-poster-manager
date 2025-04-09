from datetime import datetime

from client.itunes.search import search_movies
from utils.string_utils import normalize


def get_itunes_artworks(
    title: str, directors: list[str], country: str
) -> tuple[str, str, str]:
    candidates = search_movies(country, title.lower())
    match = get_matching_movie(candidates, title, directors)
    if not match:
        return "", "", ""

    itunes_url, poster_url, release_date = get_artworks(match)
    return itunes_url, poster_url, release_date


def get_matching_movie(
    candidates: list[dict], title: str, directors: list[str]
) -> dict:
    if len(candidates) == 1:
        return candidates[0]

    for candidate in candidates:
        if is_matching(candidate, title, directors):
            return candidate
    return {}


def is_matching(candidate: dict, title: str, directors: list[str]) -> bool:
    same_title = is_title_match(title, candidate["trackName"])
    same_director = is_director_match(directors, candidate["artistName"])
    return same_title and same_director


def is_title_match(
    title: str,
    candidate_title: str,
) -> bool:
    return normalize(title) in normalize(candidate_title)


def is_director_match(directors: list[str], candidate_director: str) -> bool:
    """
    directors = ["Jason Hand", " Dana Ledoux Miller", "David G. Derrick, Jr."]
    candidate_director = "Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr."
    """
    candidate_director = normalize(candidate_director)
    if not directors:
        return True
    for director in directors:
        director = normalize(director)
        if director in candidate_director:
            return True
    return False


def get_artworks(movie: dict) -> tuple[str, str, str]:
    """
    {
        "wrapperType": "track",
        "kind": "feature-movie",
        "collectionId": 1417412575,
        "trackId": 1370224078,
        "artistName": "Anthony Russo & Joe Russo",
        "collectionName": "Avengers 3-Movie Collection",
        "trackName": "Avengers: Infinity War",
        "collectionCensoredName": "Avengers 3-Movie Collection",
        "trackCensoredName": "Avengers: Infinity War",
        "collectionArtistId": 410641764,
        "collectionArtistViewUrl": "https://itunes.apple.com/us/artist/buena-vista-home-entertainment-inc/410641764?uo=4",
        "collectionViewUrl": "https://itunes.apple.com/us/movie/avengers-infinity-war/id1370224078?uo=4",
        "trackViewUrl": "https://itunes.apple.com/us/movie/avengers-infinity-war/id1370224078?uo=4",
        "previewUrl": "https://video-ssl.itunes.apple.com/itunes-assets/Video115/v4/ab/3b/9a/ab3b9ac8-e641-50f0-d0c5-70ac3f90ea4f/mzvf_5172850007233101562.640x354.h264lc.U.p.m4v",
        "artworkUrl30": "https://is1-ssl.mzstatic.com/image/thumb/Video114/v4/4c/7c/ad/4c7cad06-3c2f-ba1f-cf66-fd41f69d9557/pr_source.lsr/30x30bb.jpg",
        "artworkUrl60": "https://is1-ssl.mzstatic.com/image/thumb/Video114/v4/4c/7c/ad/4c7cad06-3c2f-ba1f-cf66-fd41f69d9557/pr_source.lsr/60x60bb.jpg",
        "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/Video114/v4/4c/7c/ad/4c7cad06-3c2f-ba1f-cf66-fd41f69d9557/pr_source.lsr/100x100bb.jpg",
        "collectionPrice": 19.99,
        "trackPrice": 19.99,
        "trackRentalPrice": 3.99,
        "collectionHdPrice": 19.99,
        "trackHdPrice": 19.99,
        "trackHdRentalPrice": 3.99,
        "releaseDate": "2018-04-27T07:00:00Z",
        "collectionExplicitness": "notExplicit",
        "trackExplicitness": "notExplicit",
        "discCount": 1,
        "discNumber": 1,
        "trackCount": 3,
        "trackNumber": 1,
        "trackTimeMillis": 9003660,
        "country": "USA",
        "currency": "USD",
        "primaryGenreName": "Action & Adventure",
        "contentAdvisoryRating": "PG-13",
        "shortDescription": "An unprecedented cinematic journey ten years in the making and spanning the entire Marvel Cinematic",
        "longDescription": "An unprecedented cinematic journey ten years in the making and spanning the entire Marvel Cinematic Universe, Marvel Studios’ Avengers: Infinity War brings to the screen the ultimate, deadliest showdown of all time. The Avengers and their Super Hero allies must be willing to sacrifice all in an attempt to defeat the powerful Thanos before his blitz of devastation and ruin puts an end to the universe.",
        "hasITunesExtras": True,
    }
    """
    itunes_url = movie["trackViewUrl"]
    poster_url = movie["artworkUrl100"].replace("100x100bb", "2000x0w")
    release_date = datetime.strptime(
        movie["releaseDate"], "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%Y-%m-%d")

    return itunes_url, poster_url, release_date
