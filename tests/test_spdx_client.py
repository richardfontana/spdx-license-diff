import unittest
from unittest.mock import patch

from glossina.spdx_client import (
    BASE_LICENSE_URL,
    _build_entry,
    download_spdx_corpus,
    normalize_details_url,
)


class SpdxClientTests(unittest.TestCase):
    def test_normalize_details_url_for_absolute_and_relative(self) -> None:
        self.assertEqual(
            normalize_details_url("http://spdx.org/licenses/MIT.html"),
            "https://spdx.org/licenses/MIT.json",
        )
        self.assertEqual(
            normalize_details_url("MIT.html"),
            f"{BASE_LICENSE_URL}MIT.json",
        )

    @patch("glossina.spdx_client.fetch_json")
    def test_build_entry_prefers_details_values(self, mock_fetch_json) -> None:
        mock_fetch_json.return_value = {
            "licenseId": "MIT",
            "name": "MIT License",
            "licenseText": "Permission is hereby granted",
            "seeAlso": ["https://spdx.org/licenses/MIT.html"],
        }

        entry = _build_entry("licenses", {"detailsUrl": "MIT.html", "reference": "MIT.html"})

        self.assertEqual(entry["id"], "MIT")
        self.assertEqual(entry["name"], "MIT License")
        self.assertIn("Permission", entry["text"])
        self.assertEqual(entry["reference"], "https://spdx.org/licenses/MIT.html")

    @patch("glossina.spdx_client.fetch_json")
    def test_download_spdx_corpus_excludes_empty_text_entries(self, mock_fetch_json) -> None:
        def fake_fetch(url, timeout=30):  # noqa: ARG001
            if url.endswith("licenses.json"):
                return {"licenses": [{"detailsUrl": "MIT.html", "reference": "MIT.html", "licenseId": "MIT"}]}
            if url.endswith("exceptions.json"):
                return {
                    "exceptions": [
                        {
                            "detailsUrl": "Classpath-exception-2.0.html",
                            "reference": "Classpath-exception-2.0.html",
                            "licenseExceptionId": "Classpath-exception-2.0",
                        }
                    ]
                }
            if url.endswith("MIT.json"):
                return {"licenseId": "MIT", "name": "MIT", "licenseText": "MIT text", "seeAlso": ["https://example.test/mit"]}
            return {
                "licenseExceptionId": "Classpath-exception-2.0",
                "name": "Classpath",
                "licenseExceptionText": "",
            }

        mock_fetch_json.side_effect = fake_fetch

        corpus = download_spdx_corpus(include_exceptions=True, concurrency=1)

        self.assertEqual(len(corpus), 1)
        self.assertEqual(corpus[0]["id"], "MIT")


if __name__ == "__main__":
    unittest.main()
