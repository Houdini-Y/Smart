import requests
import csv
import os
from typing import List, Dict

BASE_API = "https://www.noon.com/_svc/catalog/api/v3/search"
BASE_SITE = "https://www.noon.com/egypt-en"
IMAGE_CDN = "https://f.nooncdn.com/p/v1686225580/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": BASE_SITE,
}


def crawl_noon_to_csv(
    query: str,
    output_path: str = "noon_products.csv",
    page: int = 1,
    limit: int = 20,
    append: bool = False,
) -> int:
    """
    Fast & reliable Noon crawler using JSON API.
    Saves data in SAME structure as other platforms.
    """

    params = {
        "q": query,
        "country": "eg",
        "page": page,
        "limit": limit,
    }

    print(f"⚡ Noon API search: '{query}'")

    r = requests.get(
        BASE_API,
        headers=HEADERS,
        params=params,
        timeout=15,
    )
    r.raise_for_status()

    data = r.json()
    products = data.get("products", [])

    rows: List[Dict] = []

    for item in products:
        image_key = item.get("image_key", "")
        image_url = f"{IMAGE_CDN}{image_key}.jpg" if image_key else ""

        rows.append({
            "title": item.get("name", ""),
            "price": str(item.get("price", {}).get("value", "")),
            "rating": str(item.get("rating", "")),
            "image": image_url,
            "product_link": f"{BASE_SITE}/{item.get('url', '')}",
            "description": "",
            "search_query": query,
            "website": "Noon",
        })

    if not rows:
        print("⚠️ No products returned from Noon API")
        return 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fieldnames = [
        "title", "price", "rating",
        "image", "product_link",
        "description", "search_query", "website"
    ]

    mode = "a" if append else "w"
    file_exists = append and os.path.exists(output_path)

    with open(output_path, mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Saved {len(rows)} Noon products")
    return len(rows)
