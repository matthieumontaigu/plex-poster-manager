from datetime import datetime

from client.itunes.api import iTunesAPIRequester
from utils.string_utils import normalize


class iTunesSearcher:
    def __init__(self):
        self.api_requester = iTunesAPIRequester()

    def search_movie(self, movie: dict) -> dict[str, str]:
        """
        {
            "plex_movie_id": "55720",
            "title": "Mickey 17",
            "year": "2025",
            "added_date": "1743864942",
            "release_date": "2025-03-05",
            "director": ["Bong Joon Ho"],
        }
        """
        country = self.get_country(movie)
        term = self.get_term(movie)
        candidates = self.api_requester.get_movies(country, term)
        matching_candidate = self.get_matching_movie(candidates, movie)
        if not matching_candidate:
            return {}
        formatted_movie = self.format_movie(matching_candidate)
        return formatted_movie

    def get_country(self, movie: dict) -> str:
        return "fr"

    def get_term(self, movie: dict) -> str:
        return movie["title"].lower()

    def get_matching_movie(self, candidates: list[dict], movie: dict) -> dict:
        for candidate in candidates:
            if self.is_matching(candidate, movie):
                return candidate
        return {}

    def format_movie(self, candidate: dict) -> dict:
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
        release_date = datetime.strptime(
            candidate["releaseDate"], "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%Y-%m-%d")

        return {
            "title": candidate["trackName"],
            "release_date": release_date,
            "poster_url": candidate["artworkUrl100"].replace("100x100bb", "2000x0w"),
            "itunes_url": candidate["trackViewUrl"],
        }

    def is_matching(self, candidate: dict, movie: dict) -> bool:
        is_title_match = self._is_match(movie["title"], candidate["trackName"])
        is_director_match = self.is_match_director(
            movie["director"], candidate["artistName"]
        )
        return is_title_match and is_director_match

    def _is_match(
        self,
        movie_title: str,
        candidate_title: str,
    ) -> bool:
        return normalize(movie_title) in normalize(candidate_title)

    def is_match_director(
        self, movie_directors: list[str], candidate_director: str
    ) -> bool:
        """Jason Hand, Dana Ledoux Miller & David G. Derrick, Jr."""
        candidate_director = normalize(candidate_director)
        if not movie_directors:
            return True
        for movie_director in movie_directors:
            movie_director = normalize(movie_director)
            if movie_director in candidate_director:
                return True
        return False
