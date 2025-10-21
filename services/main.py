import argparse
from typing import NotRequired, TypedDict, cast

from client.plex.manager import PlexManager
from client.tmdb.api import TMDBAPIRequester
from services.artworks.retriever import ArtworksRetriever
from services.artworks.selector import ArtworksSelector
from services.artworks.updater import ArtworksUpdater
from services.artworks.uploader import ArtworksUploader
from services.localizer.localizer import Localizer
from services.provider.apple import AppleProvider
from services.provider.logo.tmdb import TMDBLogoProvider
from services.scheduler.schedules import get_schedule_from_config
from services.scheduler.task_scheduler import TaskSchedulerService
from services.tasks.artworks_reverter_task import ArtworksReverterTask
from services.tasks.missing_artworks_task import MissingArtworksTask
from services.tasks.recently_added_task import RecentlyAddedTask
from storage.movies_cache import MoviesCache
from utils.file_utils import load_json_file
from utils.logger import setup_logging


class PlexConfig(TypedDict):
    plex_url: str
    plex_token: str
    metadata_country: str
    metadata_path: str


class TMDBConfig(TypedDict):
    api_token: str


class RetrieverConfig(TypedDict):
    countries: list[str]


class SelectorConfig(TypedDict):
    match_movie_title: bool
    match_logo_poster: bool
    target_source: str


class ReverterConfig(TypedDict):
    artworks_types: list[str]


class ArtworksConfig(TypedDict):
    retriever: RetrieverConfig
    selector: SelectorConfig
    reverter: ReverterConfig


class ScheduleConfig(TypedDict):
    type: str
    params: tuple[int, ...]


class CacheConfig(TypedDict):
    cache_path: str
    retention_days: NotRequired[int]


class Config(TypedDict):
    plex: PlexConfig
    tmdb: TMDBConfig
    artworks: ArtworksConfig
    schedules: dict[str, ScheduleConfig]
    cache: CacheConfig
    log_path: str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduled tasks for movie artworks.")
    parser.add_argument(
        "--config-path",
        required=True,
        help="Path to the JSON config file",
    )
    args = parser.parse_args()

    config_path = args.config_path
    config = cast(Config, load_json_file(config_path))

    setup_logging(config["log_path"])

    plex_config = config["plex"]
    plex_manager = PlexManager(**plex_config)

    tmdb_config = config["tmdb"]
    tmdb_requester = TMDBAPIRequester(tmdb_config["api_token"])

    artworks_config = config["artworks"]

    selector_config = artworks_config["selector"]
    artworks_selector = ArtworksSelector(**selector_config)

    retriever_config = artworks_config["retriever"]
    apple_provider = AppleProvider()
    localizer = Localizer(tmdb_requester)
    countries_priority = retriever_config["countries"]
    logo_provider = TMDBLogoProvider(tmdb_requester)
    artworks_retriever = ArtworksRetriever(
        apple_provider,
        localizer,
        countries_priority,
        fallback_logo_provider=logo_provider,
    )

    artworks_uploader = ArtworksUploader(plex_manager, upload_interval=1.0)
    artworks_updater = ArtworksUpdater(
        artworks_retriever, artworks_selector, artworks_uploader
    )

    cache_config = config["cache"]
    cache_path = cache_config["cache_path"]
    retention_days = cache_config.get("retention_days", 0)
    retention_seconds = retention_days * 86400

    recently_added_cache = MoviesCache(cache_path, "recently_added", retention_seconds)
    missing_artworks_cache = MoviesCache(cache_path, "missing_artworks")

    recently_added_task = RecentlyAddedTask(
        plex_manager, artworks_updater, recently_added_cache, missing_artworks_cache
    )

    missing_artworks_task = MissingArtworksTask(
        plex_manager, artworks_updater, missing_artworks_cache
    )

    reverter_config = artworks_config["reverter"]
    artwork_reverter_task = ArtworksReverterTask(plex_manager, **reverter_config)

    schedules = config["schedules"]
    tasks = [
        (
            "recently_added",
            recently_added_task.run,
            get_schedule_from_config(**schedules["recently_added"]),
        ),
        (
            "missing_artworks",
            missing_artworks_task.run,
            get_schedule_from_config(**schedules["missing_artworks"]),
        ),
        (
            "artworks_reverter",
            artwork_reverter_task.run,
            get_schedule_from_config(**schedules["artworks_reverter"]),
        ),
    ]
    scheduler = TaskSchedulerService(tasks)
    scheduler.start()
