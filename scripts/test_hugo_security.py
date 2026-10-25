#!/usr/bin/env python3
"""Check that Hugo escapes heading IDs consistently in its generated ToC."""
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile


class LinksAndHeadings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.hrefs.append(attrs.get("href"))
        if tag == "h2":
            self.ids.append(attrs.get("id"))


def main():
    with tempfile.TemporaryDirectory(prefix="hugo-security-") as directory:
        root = Path(directory)
        (root / "layouts").mkdir()
        (root / "content").mkdir()
        (root / "hugo.toml").write_text(
            'baseURL = "https://example.invalid/"\n'
            'disableKinds = ["rss", "taxonomy", "term", "sitemap"]\n',
            encoding="utf-8",
        )
        (root / "layouts/all.html").write_text(
            "{{ .TableOfContents }}{{ .Content }}", encoding="utf-8"
        )
        # Benign entity text detects double interpretation without executable HTML.
        (root / "content/check.md").write_text(
            '---\ntitle: Regression\n---\n## Heading {id="anchor&amp;marker"}\n',
            encoding="utf-8",
        )
        subprocess.run(
            [os.environ.get("HUGO_BIN", "hugo"), "--source", str(root)],
            check=True, capture_output=True, text=True,
        )
        parsed = LinksAndHeadings()
        parsed.feed((root / "public/check/index.html").read_text(encoding="utf-8"))
        if parsed.ids != ["anchor&amp;marker"] or parsed.hrefs != ["#" + parsed.ids[0]]:
            raise SystemExit("FAIL: ToC heading IDs are not escaped consistently (GHSA-wcpj-vcvm-j4pg)")
        print("PASS: ToC heading ID escaping regression")


if __name__ == "__main__":
    main()
