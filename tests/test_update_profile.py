import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from unittest.mock import patch
from urllib.error import URLError

spec = importlib.util.spec_from_file_location("profile", Path(__file__).resolve().parents[1] / "scripts/update_profile.py")
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.text = "Intro\n<!-- metrics:start -->\n<!-- metrics:end -->\n<!-- release:start -->\nPrevious pick\n<!-- release:end -->\nFooter"
        self.payload = {"ok": True, "date": "2026-11-02", "release": {
            "artist": "Artist & friends", "title": "<Record>",
            "url": "https://www.discogs.com/release/123",
        }}

    def test_successful_updates_are_idempotent_and_escape_api_text(self):
        updated = profile.update_readme(self.text, self.payload, True)
        self.assertEqual(updated, profile.update_readme(updated, self.payload, True))
        self.assertTrue(updated.startswith("Intro\n"))
        self.assertTrue(updated.endswith("Footer"))
        self.assertIn("Artist &amp; friends — &lt;Record&gt;", updated)
        self.assertIn("2026-11-02", updated)

    def test_unavailable_services_preserve_previous_content(self):
        self.assertEqual(self.text, profile.update_readme(self.text))

    def test_metrics_link_requires_render(self):
        self.assertNotIn("github-metrics.svg", profile.update_readme(self.text, self.payload))
        self.assertIn("github-metrics.svg", profile.update_readme(self.text, self.payload, True))

    def test_untrusted_url_is_rejected(self):
        self.payload["release"]["url"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            profile.release_markup(self.payload)

    def test_missing_markers_are_rejected(self):
        with self.assertRaises(ValueError):
            profile.update_readme("No markers", self.payload)

    def test_network_and_api_failures_preserve_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text(self.text)
            with patch.object(profile, "ROOT", root):
                with patch.object(profile, "urlopen", side_effect=URLError("offline")):
                    profile.main()
                self.assertEqual(self.text, readme.read_text())
                response = io.BytesIO(json.dumps({"ok": False}).encode())
                with patch.object(profile, "urlopen", return_value=response):
                    profile.main()
                self.assertEqual(self.text, readme.read_text())


if __name__ == "__main__":
    unittest.main()
