import argparse

from client.plex.manager import PlexManager
from client.tmdb.api import TMDBAPIRequester
from services.artworks_service import ArtworksService
from services.artworks_updater import ArtworksUpdater
from services.metadata_retriever import MetadataRetriever
from utils.file_utils import load_json_file
from utils.logger import setup_logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch edit movie artworks.")
    parser.add_argument(
        "--config-path",
        required=True,
        help="Path to the JSON file containing config",
    )
    args = parser.parse_args()
    config_path = args.config_path
    config = load_json_file(config_path)

    credentials = config["credentials"]
    plex_url = credentials["plex_url"]
    plex_token = credentials["plex_token"]
    tmdb_api_key = credentials["tmdb_api_key"]

    artworks_config = config["artworks"]
    match_title = artworks_config["match_title"]
    match_logo = artworks_config["match_logo"]
    update_release_date = artworks_config["update_release_date"]
    recent_update_interval = artworks_config["recent_update_interval"]
    missing_artwork_interval = artworks_config["missing_artwork_interval"]
    artworks_api_interval = artworks_config["artworks_api_interval"]

    storage_config = config["storage"]
    cache_path = storage_config["cache_path"]
    log_path = storage_config["log_path"]

    setup_logging(log_path)

    plex_manager = PlexManager(plex_url, plex_token)
    tmdb_api_requester = TMDBAPIRequester(tmdb_api_key)
    metadata_retriever = MetadataRetriever(tmdb_api_requester)
    artworks_updater = ArtworksUpdater(
        plex_manager,
        metadata_retriever,
        match_title=match_title,
        match_logo=match_logo,
        update_release_date=update_release_date,
        api_call_interval=artworks_api_interval / 6,
    )
    artworks_service = ArtworksService(
        artworks_updater,
        plex_manager,
        recent_update_interval,
        missing_artwork_interval,
        cache_path,
        api_call_interval=artworks_api_interval,
    )
    artworks_service.start()
