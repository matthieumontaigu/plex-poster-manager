import unittest

from models.movie import Movie
from storage.movies_cache import MoviesCache


class TestMoviesCacheNoPatch(unittest.TestCase):
    def setUp(self):
        self.cache = MoviesCache("dummy_path", "dummy_file")

    def test_add_and_contains(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        # Ensure the movie is not in the cache initially
        self.assertNotIn(movie, self.cache)
        self.cache.add(movie)
        # Check if the movie is now in the cache
        self.assertIn(movie, self.cache)

    def test_add_duplicate(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        self.cache.add(movie)
        # Adding the same movie again should not update the cache
        self.cache.add(movie)
        self.assertIn(movie, self.cache)

    def test_remove(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        self.cache.add(movie)
        self.assertIn(movie, self.cache)
        # Ensure the movie is in the cache before removing
        self.cache.remove(movie)
        self.assertNotIn(movie, self.cache)

    def test_remove_nonexistent(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        self.cache.remove(movie)
        self.assertNotIn(movie, self.cache)

    def test_remove_all(self):
        movies: list[Movie] = [
            {
                "plex_movie_id": 1111,
                "title": "Pris au piège - Caught Stealing",
                "year": 2025,
                "added_date": 100,
                "release_date": "2025-08-27",
                "director": ["Darren Aronofsky"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
            {
                "plex_movie_id": 2222,
                "title": "Eddington",
                "year": 2025,
                "added_date": 200,
                "release_date": "2025-07-16",
                "director": ["Ari Aster"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
        ]
        for m in movies:
            self.cache.add(m)
        self.cache.remove_all(movies)
        for m in movies:
            self.assertNotIn(m, self.cache)

    def test_clear(self):
        movies: list[Movie] = [
            {
                "plex_movie_id": 1111,
                "title": "Pris au piège - Caught Stealing",
                "year": 2025,
                "added_date": 100,
                "release_date": "2025-08-27",
                "director": ["Darren Aronofsky"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
            {
                "plex_movie_id": 2222,
                "title": "Eddington",
                "year": 2025,
                "added_date": 200,
                "release_date": "2025-07-16",
                "director": ["Ari Aster"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
            {
                "plex_movie_id": 3333,
                "title": "Marche ou crève",
                "year": 2025,
                "added_date": 300,
                "release_date": "2025-10-01",
                "director": ["Francis Lawrence"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
        ]
        for m in movies:
            self.cache.add(m)
        # Clear movies added before 200
        self.cache.clear(movies[1])
        self.assertNotIn(movies[0], self.cache)
        self.assertIn(movies[1], self.cache)
        self.assertIn(movies[2], self.cache)

    def test_clear_with_retention(self):
        self.cache = MoviesCache("dummy_path", "dummy_file", 100)
        movies: list[Movie] = [
            {
                "plex_movie_id": 1111,
                "title": "Pris au piège - Caught Stealing",
                "year": 2025,
                "added_date": 100,
                "release_date": "2025-08-27",
                "director": ["Darren Aronofsky"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
            {
                "plex_movie_id": 2222,
                "title": "Eddington",
                "year": 2025,
                "added_date": 200,
                "release_date": "2025-07-16",
                "director": ["Ari Aster"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
            {
                "plex_movie_id": 3333,
                "title": "Marche ou crève",
                "year": 2025,
                "added_date": 300,
                "release_date": "2025-10-01",
                "director": ["Francis Lawrence"],
                "metadata_country": "fr",
                "guid": None,
                "tmdb_id": None,
            },
        ]
        for m in movies:
            self.cache.add(m)
        # Clear movies added before 200
        self.cache.clear(movies[1])
        self.assertIn(movies[0], self.cache)
        self.assertIn(movies[1], self.cache)
        self.assertIn(movies[2], self.cache)

    def test_items(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        self.cache.add(movie)
        items = list(self.cache.items())
        self.assertEqual(len(items), 1)
        key, value = items[0]
        self.assertEqual(key, 1111)
        self.assertEqual(value, movie)

    def test_get_id(self):
        movie: Movie = {
            "plex_movie_id": 1111,
            "title": "Pris au piège - Caught Stealing",
            "year": 2025,
            "added_date": 100,
            "release_date": "2025-08-27",
            "director": ["Darren Aronofsky"],
            "metadata_country": "fr",
            "guid": None,
            "tmdb_id": None,
        }
        self.assertEqual(self.cache.get_id(movie), 1111)


if __name__ == "__main__":
    unittest.main()
