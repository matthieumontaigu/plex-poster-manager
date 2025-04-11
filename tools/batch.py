import argparse

from client.plex.manager import PlexManager
from client.tmdb.api import TMDBAPIRequester
from services.artworks_updater import ArtworksUpdater
from services.metadata_manager import MetadataManager
from utils.logger import setup_logging


def batch_edit(
    artworks_updater: ArtworksUpdater,
    all_movies: list[dict],
    date_from: int,
    number_of_edits: int,
) -> None:
    all_movies_sorted = sorted(
        all_movies, key=lambda movie: movie["added_date"], reverse=True
    )
    edits = 0
    for movie in all_movies_sorted:
        if edits >= number_of_edits:
            break
        if movie["added_date"] > date_from:
            continue
        artworks_updater.update_artworks(movie)
        edits += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch edit movie artworks.")
    parser.add_argument("--plex-url", required=True, help="Plex server URL")
    parser.add_argument("--plex-token", required=True, help="Plex server token")
    parser.add_argument("--tmdb-api-key", required=True, help="TMDB API key")
    parser.add_argument(
        "--date-from", type=int, required=True, help="Date from (timestamp)"
    )
    parser.add_argument(
        "--number-of-edits", type=int, required=True, help="Number of edits to perform"
    )

    args = parser.parse_args()

    setup_logging()

    plex_manager = PlexManager(args.plex_url, args.plex_token)
    tmdb_api_requester = TMDBAPIRequester(args.tmdb_api_key)
    metadata_manager = MetadataManager(tmdb_api_requester)
    artworks_updater = ArtworksUpdater(plex_manager, metadata_manager, match_title=True)

    all_movies = plex_manager.get_all_movies()

    batch_edit(artworks_updater, all_movies, args.date_from, args.number_of_edits)
