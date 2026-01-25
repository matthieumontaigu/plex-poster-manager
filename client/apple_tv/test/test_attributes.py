import unittest

from client.apple_tv.attributes import get_umc_id


class TestAttributes(unittest.TestCase):
    def test_get_umc_id(self):
        # Test case from docstring
        self.assertEqual(
            get_umc_id("https://tv.apple.com/us/movie/the-matrix/umc.cmc.4xyz12345"),
            "umc.cmc.4xyz12345",
        )

        # Test with different valid URLs
        self.assertEqual(
            get_umc_id(
                "https://tv.apple.com/fr/movie/napoleon/umc.cmc.1234567890abcdef"
            ),
            "umc.cmc.1234567890abcdef",
        )
        self.assertEqual(
            get_umc_id("https://tv.apple.com/us/show/severance/umc.cmc.123"),
            "umc.cmc.123",
        )
        self.assertEqual(
            get_umc_id(
                "https://tv.apple.com/us/episode/good-news-about-hell/umc.cmc.abc-def_ghi.jkl"
            ),
            "umc.cmc.abc-def_ghi.jkl",
        )

        # Test with no UMC ID
        self.assertIsNone(get_umc_id("https://tv.apple.com/us/movie/the-matrix/"))
        self.assertIsNone(get_umc_id("https://www.apple.com"))

        # Test with malformed or empty URLs
        self.assertIsNone(get_umc_id(""))
        self.assertIsNone(get_umc_id("not a url"))
        self.assertIsNone(get_umc_id("https://tv.apple.com/us/movie/the-matrix/umc."))


if __name__ == "__main__":
    unittest.main()
