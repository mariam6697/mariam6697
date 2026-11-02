import sys
from pathlib import Path
import unittest
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from daily_release import daily_release


def collection_fetch(count):
    def fetch(url):
        query = parse_qs(urlsplit(url).query)
        if query["per_page"] == ["1"]:
            return {"pagination": {"items": count}}
        start = (int(query["page"][0]) - 1) * 100
        return {"releases": [{"basic_information": {
            "id": i + 1, "title": f"Record {i + 1}", "artists": [{"name": "Artist"}],
            "cover_image": "https://i.discogs.com/cover.jpg",
        }} for i in range(start, min(start + 100, count))]}
    return fetch


class DailyReleaseTests(unittest.TestCase):
    def test_same_day_pick_is_frozen_without_network(self):
        existing = daily_release(None, "2026-11-02", collection_fetch(76))
        network = Mock(side_effect=AssertionError("Must not refetch today"))
        self.assertEqual(existing, daily_release(existing, "2026-11-02", network))
        network.assert_not_called()

    def test_next_day_uses_updated_collection(self):
        old = daily_release(None, "2026-11-02", collection_fetch(76))
        fetch = Mock(side_effect=collection_fetch(120))
        new = daily_release(old, "2026-11-03", fetch)
        self.assertEqual(new["collection_size"], 120)
        self.assertEqual(new["date"], "2026-11-03")
        self.assertEqual(fetch.call_count, 2)
        self.assertNotEqual(old["date"], new["date"])

    def test_pagination_can_select_newly_added_records(self):
        for day in range(1, 29):
            pick = daily_release(None, f"2026-11-{day:02}", collection_fetch(120))
            if int(pick["release"]["url"].rsplit("/", 1)[1]) > 76:
                break
        else:
            self.fail("Updated records were never eligible")

    def test_selection_is_deterministic_for_same_date_and_collection(self):
        self.assertEqual(daily_release(None, "2026-11-02", collection_fetch(120)),
                         daily_release(None, "2026-11-02", collection_fetch(120)))

    def test_empty_collection_is_rejected_without_overwriting_old_pick(self):
        old = daily_release(None, "2026-11-02", collection_fetch(76))
        with self.assertRaises(ValueError):
            daily_release(old, "2026-11-03", collection_fetch(0))
        self.assertEqual(old["collection_size"], 76)
