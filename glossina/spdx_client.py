"""Download and normalize SPDX license/exception texts."""

from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import urljoin
from urllib.request import urlopen

BASE_LICENSE_URL = "https://spdx.org/licenses/"
LIST_URLS = {
    "licenses": f"{BASE_LICENSE_URL}licenses.json",
    "exceptions": f"{BASE_LICENSE_URL}exceptions.json",
}


def fetch_json(url: str, timeout: int = 30) -> dict:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def normalize_details_url(details_url: str) -> str:
    if details_url.startswith(("http://", "https://")):
        return details_url.replace("http://", "https://").removesuffix(".html") + ".json"

    joined = urljoin(BASE_LICENSE_URL, details_url)
    return joined.removesuffix(".html") + ".json"


def _build_entry(category: str, item: dict) -> dict:
    details = fetch_json(normalize_details_url(item["detailsUrl"]))

    id_key = "licenseId" if category == "licenses" else "licenseExceptionId"
    text_key = "licenseText" if category == "licenses" else "licenseExceptionText"

    return {
        "id": details.get(id_key) or item.get(id_key),
        "name": details.get("name") or item.get("name"),
        "text": details.get(text_key, ""),
        "category": category,
        "reference": (details.get("seeAlso") or [f"{BASE_LICENSE_URL}{item.get('reference', '')}"])[0],
    }


def download_spdx_corpus(include_exceptions: bool = True, concurrency: int = 10) -> list[dict]:
    categories = ["licenses", "exceptions"] if include_exceptions else ["licenses"]
    corpus: list[dict] = []

    for category in categories:
        listing = fetch_json(LIST_URLS[category])
        items = listing.get(category, [])

        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
            loaded = list(pool.map(lambda item: _build_entry(category, item), items))

        corpus.extend(entry for entry in loaded if entry.get("text"))

    return corpus
