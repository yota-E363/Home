import unittest
from pathlib import Path


KOTLIN = (
    Path(__file__).parent.parent
    / "saradahentai-build/src/en/saradahentai/src/eu/kanade/tachiyomi/extension/en/saradahentai/Saradahentai.kt"
)


class KotlinContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = KOTLIN.read_text(encoding="utf-8")

    def test_detail_lookup_requires_slug_and_permalink(self):
        self.assertIn("it.slug == slug && postLinkMatchesSlug(it, slug)", self.source)

    def test_update_lookup_requires_slug_and_permalink(self):
        self.assertIn("it.slug == requestedSlug && postLinkMatchesSlug(it, requestedSlug)", self.source)

    def test_manga_url_comes_from_parsed_permalink(self):
        self.assertIn("link.toHttpUrl().encodedPath", self.source)
        self.assertNotIn("removePrefix(baseUrl)", self.source)

    def test_gallery_is_image_only_and_domain_limited(self):
        self.assertIn("isImageMedia(it) && isAllowedUrl(it.sourceUrl)", self.source)

    def test_credits_use_explicit_containers(self):
        self.assertIn(".artist-credit a[href]", self.source)
        self.assertNotIn("[class*=artist]", self.source)

    def test_metadata_fetch_is_conditional(self):
        self.assertIn("if (fetchDetails) fetchMetadata(post) else null", self.source)

    def test_braces_are_balanced(self):
        self.assertEqual(self.source.count("{"), self.source.count("}"))


if __name__ == "__main__":
    unittest.main()
