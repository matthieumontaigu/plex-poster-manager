import argparse
import logging
import time

from client.plex.manager import PlexManager
from utils.file_utils import load_json_file

logger = logging.getLogger(__name__)


def batch_revert_logos(
    plex_manager: PlexManager, movies: list[dict[str, str | int]]
) -> None:
    """
    Revert logos for a batch of movies to the last uploaded logo if agent logo is selected and there are uploaded logos.

    :param movies: List of movies with their Plex IDs.
    :param logos: Dictionary of logos keyed by movie Plex ID.
    """
    for movie in movies:
        plex_movie_id = movie["plex_movie_id"]
        logos = plex_manager.get_logos(plex_movie_id)
        should_revert = should_revert_logo(logos)
        if should_revert:
            logger.info(
                f"Should revert logo for {movie['title']} ({movie['plex_movie_id']})"
            )
            revert_logo(plex_manager, movie, logos)
        time.sleep(0.1)


def revert_logo(
    plex_manager: PlexManager, movie: dict[str, str | int], logos: list[dict[str, str]]
) -> bool:
    """
    Revert logos to the last uploaded logo if agent logo is selected and there are uploaded logos.

    :param logos: List of logos from Plex.
    :return: List of logos with the agent logo selected.
    """

    uploaded_logos = [logo for logo in logos if "upload" in logo["key"]]

    if len(uploaded_logos) == 0:
        logger.warning(
            f"No uploaded logos found to revert for {movie['title']} ({movie['plex_movie_id']})."
        )
        return False

    if len(uploaded_logos) > 1:
        logger.warning(
            f"Multiple uploaded logos found for {movie['title']} ({movie['plex_movie_id']}), please revert manually to the desired logo."
        )

    selected_logo = uploaded_logos[-1]  # Get the last uploaded logo
    selected_logo_path = plex_manager.get_movie_image_path(selected_logo["key"])
    logger.info(f"Will upload {selected_logo_path}.")

    success = plex_manager.upload_logo_file(movie["plex_movie_id"], selected_logo_path)
    if not success:
        logger.error(
            f"Failed to revert logo for movie {movie['title']} ({movie['plex_movie_id']})."
        )
        return False

    logger.info(
        f"Reverted logo for movie {movie['title']} ({movie['plex_movie_id']}) to the uploaded logo."
    )
    return True


def should_revert_logo(logos: list[dict[str, str | None]]) -> bool:
    """
    Check if the logo should be reverted based on the selected logo and uploaded logos.
    """
    agent_logo_selected, nb_uploaded_logos = analyze_logos(logos)
    return agent_logo_selected and nb_uploaded_logos > 0


def analyze_logos(logos: list[dict[str, str | None]]) -> tuple[bool, int]:
    agent_logo_selected = False
    nb_uploaded_logos = 0
    for logo in logos:
        if logo["key"] is None:
            continue
        if "tv.plex.agents.movie" in logo["key"] and logo["selected"] == "1":
            agent_logo_selected = True
        elif "upload" in logo["key"]:
            nb_uploaded_logos += 1

    return agent_logo_selected, nb_uploaded_logos


def main():
    parser = argparse.ArgumentParser(description="Batch revert logos for Plex movies.")
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
    storage = config["storage"]
    metadata_path = storage["metadata_path"]

    plex_manager = PlexManager(plex_url, plex_token, metadata_path)

    all_movies = plex_manager.get_all_movies()
    all_movies_sorted = sorted(
        all_movies, key=lambda movie: movie["added_date"], reverse=True
    )

    all_movies_subset = all_movies_sorted[100:]

    batch_revert_logos(plex_manager, all_movies_subset)


if __name__ == "__main__":
    main()
