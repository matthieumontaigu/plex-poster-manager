# plex-poster-manager

`plex-poster-manager` is a tool for managing and updating movie artworks (posters, backgrounds, logos) on a Plex server. It integrates with external APIs like TMDB and Apple TV to fetch and upload artworks.

## Features
- Fetch and upload posters, backgrounds, and logos for movies.
- Update release dates for movies.
- Handle missing artworks and recently added movies.
- Batch and single movie artwork updates.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/plex-poster-manager.git
   cd plex-poster-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Launch the Service

To start the service and continuously update artworks:
```bash
python main.py --config-path /path/to/config.json
```

**Example Config File (`config.json`):**
```json
{
  "credentials": {
    "plex_url": "http://your-plex-server:32400",
    "plex_token": "your-plex-token",
    "tmdb_api_key": "your-tmdb-api-key"
  },
  "artworks": {
    "match_title": true,
    "update_release_date": true,
    "recent_update_interval": 3600,
    "missing_artwork_interval": 86400
  },
  "storage": {
    "cache_path": "./cache",
    "log_path": "./logs"
  }
}
```

---

### Using `ArtworksUpdater`

`ArtworksUpdater` is responsible for fetching and updating artworks for a specific movie.

**Example:**
```python
from client.plex.manager import PlexManager
from services.artworks_updater import ArtworksUpdater
from services.metadata_manager import MetadataManager

plex_manager = PlexManager("http://your-plex-server:32400", "your-plex-token")
metadata_manager = MetadataManager(tmdb_api_requester)

artworks_updater = ArtworksUpdater(
    plex_manager,
    metadata_manager,
    plex_country="us",
    countries=["us", "fr"],
    match_title=True,
    update_release_date=True,
    api_call_interval=1.0
)

movie = {
    "plex_movie_id": 12345,
    "title": "Inception",
    "release_date": "2010-07-16"
}

is_missing, artworks = artworks_updater.update_artworks(movie)
if is_missing:
    print(f"Missing artworks for {movie['title']}")
else:
    print(f"Artworks updated for {movie['title']}")
```

---

### Using `PlexManager`

`PlexManager` provides methods to interact with the Plex server, such as fetching movies and uploading artworks.

**Example:**
```python
from client.plex.manager import PlexManager

plex_manager = PlexManager("http://your-plex-server:32400", "your-plex-token")

# Fetch all movies
all_movies = plex_manager.get_all_movies()
print(f"Found {len(all_movies)} movies on Plex.")

# Upload a poster
plex_movie_id = 12345
poster_url = "https://example.com/poster.jpg"
success = plex_manager.upload_poster(plex_movie_id, poster_url)
if success:
    print("Poster uploaded successfully!")
else:
    print("Failed to upload poster.")
```

---

## Batch Editing

To perform batch edits on movies:
```bash
python tools/batch.py --plex-url http://your-plex-server:32400 \
                      --plex-token your-plex-token \
                      --tmdb-api-key your-tmdb-api-key \
                      --date-from 1609459200 \
                      --number-of-edits 10
```

---

## Single Movie Updates

To update artworks for a single movie:
```python
from tools.single import PlexUploader
from client.plex.manager import PlexManager

plex_manager = PlexManager("http://your-plex-server:32400", "your-plex-token")
uploader = PlexUploader(plex_manager)

plex_url = "http://your-plex-server/web/index.html#!/server/12345/details?key=metadata%2F67890"
apple_tv_url = "https://tv.apple.com/movie/inception"

uploader.upload_apple_tv_from_url(plex_url, apple_tv_url)
```

---

## Logging

Logs are stored in the path specified in the `log_path` field of the config file. Use these logs to debug or monitor the service.

---

## Contributing

Feel free to submit issues or pull requests to improve the project.

---

## License

This project is licensed under the MIT License.