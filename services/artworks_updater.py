from client.apple_tv.extract import extract_artworks
from client.itunes.searcher import iTunesSearcher
from client.plex.manager import PlexManager

# filepath: /Users/matthieu/dev/plex-poster-manager/services/artworks_updater.py


class ArtworksUpdater:
    def __init__(self, plex_manager: PlexManager, itunes_searcher: iTunesSearcher):
        self.plex_manager = plex_manager
        self.itunes_searcher = itunes_searcher

    def update_artworks(self, movie: dict) -> None:
        movie = self.get_artworks(movie)
        self.plex_manager.update_artworks(
            movie["plex_movie_id"],
            movie.get("poster_url", ""),
            movie.get("background_url", ""),
            movie.get("logo_url", ""),
        )

    def get_artworks(self, movie: dict) -> dict[str, str]:
        """
        Fetches artworks for a given movie by searching on iTunes and extracting artworks.
        :param movie: A dictionary containing movie details.
        :return: A dictionary with artwork URLs (e.g., logo, background).
        """
        # Search for the movie on iTunes
        itunes_movie = self.itunes_searcher.search_movie(movie)
        if not itunes_movie:
            return movie
        else:
            movie.update(itunes_movie)
        # Extract artworks from the iTunes URL
        apple_tv_artworks = extract_artworks(itunes_movie["itunes_url"])
        if apple_tv_artworks:
            movie.update(apple_tv_artworks)
        return movie
