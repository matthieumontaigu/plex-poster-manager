from client.plex.manager import PlexManager
from utils.file_utils import load_json_file

config_path = "config.json"
config = load_json_file(config_path)

credentials = config["credentials"]
plex_url = credentials["plex_url"]
plex_token = credentials["plex_token"]
plex_country = config["plex_metadata_country"]

plex_manager = PlexManager(plex_url, plex_token, plex_country)

recently_added_movies = plex_manager.get_recently_added_movies()
for movie in recently_added_movies:
    print(movie)
