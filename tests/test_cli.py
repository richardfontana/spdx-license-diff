import io
import json
import tempfile
import unittest
from argparse import Namespace
from unittest.mock import patch

from glossina import cli


class CliTests(unittest.TestCase):
    @patch("sys.argv", ["glossina", "--text", "hello", "--top", "5", "--min-score", "33"])
    def test_parse_args_accepts_valid_values(self) -> None:
        args = cli.parse_args()
        self.assertEqual(args.text, "hello")
        self.assertEqual(args.top, 5)
        self.assertEqual(args.min_score, 33)

    @patch("sys.argv", ["glossina", "--top", "0"])
    def test_parse_args_rejects_invalid_top(self) -> None:
        with self.assertRaises(SystemExit):
            cli.parse_args()

    def test_resolve_input_prefers_text_then_file_then_stdin(self) -> None:
        args = Namespace(text="direct", file=None)
        self.assertEqual(cli.resolve_input(args), "direct")

        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=True) as tmp:
            tmp.write("from file")
            tmp.flush()
            args = Namespace(text=None, file=tmp.name)
            self.assertEqual(cli.resolve_input(args), "from file")

        args = Namespace(text=None, file=None)
        with patch("sys.stdin.isatty", return_value=False), patch("sys.stdin.read", return_value="from stdin"):
            self.assertEqual(cli.resolve_input(args), "from stdin")

    def test_main_outputs_json_when_requested(self) -> None:
        fake_args = Namespace(text="sample", file=None, top=1, min_score=0.0, no_exceptions=True, json=True)
        fake_matches = [{"id": "MIT", "name": "MIT", "score": 99.0, "dice": 99.0, "lev_percent": 99.0}]

        with patch("glossina.cli.parse_args", return_value=fake_args), patch(
            "glossina.cli.download_spdx_corpus", return_value=[{"id": "MIT", "text": "sample"}]
        ), patch("glossina.cli.rank_matches", return_value=fake_matches), patch("sys.stdout", new_callable=io.StringIO) as stdout:
            rc = cli.main()

        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(stdout.getvalue()), fake_matches)


if __name__ == "__main__":
    unittest.main()
