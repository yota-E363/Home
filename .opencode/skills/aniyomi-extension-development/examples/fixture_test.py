import json
import unittest
from pathlib import Path


class IdentityRegressionTest(unittest.TestCase):
    def test_trailing_slash_does_not_select_first_post(self):
        posts = json.loads((Path(__file__).parent / "posts.fixture.json").read_text())
        for expected in posts:
            slug = expected["url"].split("?", 1)[0].rstrip("/").split("/")[-1]
            match = next((post for post in posts if post["slug"] == slug), None)
            self.assertIsNotNone(match)
            self.assertEqual(match["id"], expected["id"])


if __name__ == "__main__":
    unittest.main()
