#!/usr/bin/env python3
import importlib.util
import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from pathlib import Path

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("v4", ROOT / "saradahentai_catalogue_v4.py")
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)


class FixtureTests(unittest.TestCase):
    def test_wordpress_and_classification_fixture(self):
        post = json.loads((ROOT / "fixtures/post.json").read_text())
        embedded = post["_embedded"]["wp:term"]
        terms = [term for group in embedded for term in group]
        tags = [term["name"] for term in terms if term["taxonomy"] == "post_tag"]
        categories = [term["name"] for term in terms if term["taxonomy"] == "category"]
        result = v4.classify(tags, categories, json.loads((ROOT / "saradahentai_v4_classification_rules.example.json").read_text()))
        self.assertEqual(result["artists"], ["Ada"])
        self.assertEqual(result["characters"], ["Character X"])
        self.assertEqual(result["categories"], ["Illustration"])
        self.assertEqual(result["unclassified_tags"], ["uncertain tag"])

    def test_html_video_metadata_and_duration(self):
        html = (ROOT / "fixtures/page.html").read_text()
        parser = v4.Parser()
        parser.feed(html)
        self.assertEqual(parser.videos[0][0], "/wp-content/uploads/fixture.mp4")
        self.assertEqual(v4.duration_seconds("PT2M3.2S"), 123.2)
        self.assertIn("og:video", parser.meta)

    def test_media_oembed_and_post_detail_fixture(self):
        post = json.loads((ROOT / "fixtures/post.json").read_text())
        media = json.loads((ROOT / "fixtures/media.json").read_text())
        oembed = json.loads((ROOT / "fixtures/oembed.json").read_text())
        self.assertEqual(post["title"]["rendered"], "Fixture &amp; Publication")
        self.assertEqual([item["id"] for item in media], [8100, 8101, 8102])
        self.assertEqual(oembed["author_name"], "Public Author")
        self.assertEqual([item["source_url"] for item in media[1:]], [
            "https://saradahentai.com/wp-content/uploads/gallery-1.jpg",
            "https://saradahentai.com/wp-content/uploads/gallery-2.jpg",
        ])

    def test_trailing_slash_keeps_catalogue_detail_identity(self):
        posts = json.loads((ROOT / "fixtures/posts.json").read_text())
        for post in posts:
            catalogue_url = post["link"].replace("https://saradahentai.com", "")
            slug = catalogue_url.split("?", 1)[0].rstrip("/").split("/")[-1]
            matches = [candidate for candidate in posts if candidate["slug"] == slug]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["id"], post["id"])
            self.assertEqual(matches[0]["title"], post["title"])

    def test_http_403_is_recorded_without_retry_or_bypass(self):
        class ForbiddenHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(403)
                self.end_headers()

            def log_message(self, *_args):
                pass

        server = HTTPServer(("127.0.0.1", 0), ForbiddenHandler)
        Thread(target=server.handle_request, daemon=True).start()
        client = v4.Client(f"http://127.0.0.1:{server.server_port}/", 0, 2)
        self.assertIsNone(client.get(client.base + "blocked"))
        self.assertEqual(client.errors[0]["status"], 403)
        server.server_close()

    def test_mp4_header_is_bounded_parser_input(self):
        data = bytearray(b"x" * 64)
        data[20:24] = b"mvhd"
        data[24] = 0
        data[36:40] = (1000).to_bytes(4, "big")
        data[40:44] = (123200).to_bytes(4, "big")
        self.assertEqual(v4.mp4_duration(bytes(data)), 123.2)


if __name__ == "__main__":
    unittest.main()
