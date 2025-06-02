import unittest

from storage.movies_cache import MoviesCache


class TestMoviesCacheNoPatch(unittest.TestCase):
    def setUp(self):
        self.cache = MoviesCache("dummy_path", "dummy_file")

    def test_add_and_contains(self):
        movie = {"plex_movie_id": 1, "added_date": 100}
        # Ensure the movie is not in the cache initially
        self.assertNotIn(movie, self.cache)
        self.cache.add(movie)
        # Check if the movie is now in the cache
        self.assertIn(movie, self.cache)
        self.assertTrue(self.cache.updated)

    def test_add_duplicate(self):
        movie = {"plex_movie_id": 2, "added_date": 200}
        self.cache.add(movie)
        self.cache.updated = False
        # Adding the same movie again should not update the cache
        self.cache.add(movie)
        self.assertIn(movie, self.cache)
        self.assertFalse(self.cache.updated)

    def test_remove(self):
        movie = {"plex_movie_id": 3, "added_date": 300}
        self.cache.add(movie)
        self.cache.updated = False
        # Ensure the movie is in the cache before removing
        self.cache.remove(movie)
        self.assertNotIn(movie, self.cache)
        self.assertTrue(self.cache.updated)

    def test_remove_nonexistent(self):
        movie = {"plex_movie_id": 4, "added_date": 400}
        self.cache.remove(movie)
        self.assertFalse(self.cache.updated)

    def test_remove_all(self):
        movies = [
            {"plex_movie_id": 5, "added_date": 500},
            {"plex_movie_id": 6, "added_date": 600},
        ]
        for m in movies:
            self.cache.add(m)
        self.cache.updated = False
        self.cache.remove_all(movies)
        for m in movies:
            self.assertNotIn(m, self.cache)
        self.assertTrue(self.cache.updated)

    def test_clear(self):
        movies = [
            {"plex_movie_id": 7, "added_date": 100},
            {"plex_movie_id": 8, "added_date": 200},
            {"plex_movie_id": 9, "added_date": 300},
        ]
        for m in movies:
            self.cache.add(m)
        self.cache.updated = False
        # Clear movies added before 200
        self.cache.clear({"plex_movie_id": 8, "added_date": 200})
        self.assertNotIn({"plex_movie_id": 7, "added_date": 100}, self.cache)
        self.assertIn({"plex_movie_id": 8, "added_date": 200}, self.cache)
        self.assertIn({"plex_movie_id": 9, "added_date": 300}, self.cache)
        self.assertTrue(self.cache.updated)

    def test_clear_with_retention(self):
        self.cache = MoviesCache("dummy_path", "dummy_file", 100)
        movies = [
            {"plex_movie_id": 7, "added_date": 100},
            {"plex_movie_id": 8, "added_date": 200},
            {"plex_movie_id": 9, "added_date": 300},
        ]
        for m in movies:
            self.cache.add(m)
        self.cache.updated = False
        # Clear movies added before 200
        self.cache.clear({"plex_movie_id": 8, "added_date": 200})
        self.assertIn({"plex_movie_id": 7, "added_date": 100}, self.cache)
        self.assertIn({"plex_movie_id": 8, "added_date": 200}, self.cache)
        self.assertIn({"plex_movie_id": 9, "added_date": 300}, self.cache)
        self.assertFalse(self.cache.updated)

    def test_items(self):
        movie = {"plex_movie_id": 10, "added_date": 1000}
        self.cache.add(movie)
        items = list(self.cache.items())
        self.assertEqual(len(items), 1)
        key, value = items[0]
        self.assertEqual(key, 10)
        self.assertEqual(value, movie)

    def test_get_key(self):
        movie = {"plex_movie_id": 11, "added_date": 1100}
        self.assertEqual(self.cache.get_key(movie), 11)


if __name__ == "__main__":
    unittest.main()
