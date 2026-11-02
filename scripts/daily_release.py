"""Choose from the current public Discogs collection once per Santiago date."""
from urllib.parse import urlencode, quote

COLLECTION = "https://api.discogs.com/users/mmmariam/collection/folders/0/releases"


def daily_release(existing, today, fetch_json):
    # Keep the first successful pick even if the collection changes later today.
    if existing and existing.get("ok") is True and existing.get("date") == today:
        return existing

    def page(number, size):
        query = urlencode({"page": number, "per_page": size, "sort": "added", "sort_order": "asc"})
        return fetch_json(f"{COLLECTION}?{query}")

    total = page(1, 1)["pagination"]["items"]
    if not isinstance(total, int) or total <= 0:
        raise ValueError("Discogs collection is empty")
    seed = 0
    for character in today:
        seed = (seed * 31 + ord(character)) & 0xFFFFFFFF
    index = seed % total
    item = page(index // 100 + 1, 100)["releases"][index % 100]
    info = item["basic_information"]
    image = info.get("cover_image") or info.get("thumb")
    return {
        "ok": True,
        "date": today,
        "collection_size": total,
        "release": {
            "title": info["title"],
            "artist": ", ".join(artist["name"] for artist in info["artists"]),
            "year": info.get("year"),
            "image": image,
            "cover": f"/api/discogs/cover?url={quote(image, safe='')}" if image else None,
            "url": f"https://www.discogs.com/release/{info['id']}",
        },
    }
