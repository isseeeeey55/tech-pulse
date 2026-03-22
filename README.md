# Tech Pulse

AWS と Claude Code の最新アップデートを、SRE視点でわかりやすく解説する技術ブログです。

**https://isseeeeey55.github.io/tech-pulse/**

## Tech Stack

| 項目 | 技術 |
|------|------|
| Static Site Generator | [Hugo](https://gohugo.io/) |
| Theme | [PaperMod](https://github.com/adityatelange/hugo-PaperMod) |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions |

## Local Development

```bash
# Clone
$ git clone --recursive https://github.com/isseeeeey55/tech-pulse.git
$ cd tech-pulse

# Start dev server
$ hugo server --buildDrafts

# Build
$ hugo --minify
```

## Directory Structure

```
tech-pulse/
├── .github/workflows/   # GitHub Actions deploy workflow
├── content/posts/       # Blog articles (Markdown)
├── static/images/       # Header images, diagrams
├── themes/PaperMod/     # Theme (git submodule)
└── hugo.toml            # Site configuration
```

## License

Blog content is &copy; 2026 Tech Pulse. All rights reserved.

Hugo and PaperMod are used under their respective licenses.
