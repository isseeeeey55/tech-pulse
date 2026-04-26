# Tech Pulse

AWS・Claude Code・New Relic・OpenAI Codex CLI の最新アップデートを、SRE視点でわかりやすく解説する技術ブログです。

**https://tech-pulse.dev/**

## 記事カテゴリ

| カテゴリ | 内容 | 更新頻度 |
|---------|------|---------|
| AWS Updates | AWS What's New のアップデートまとめ | 毎日 |
| Claude Code Updates | Claude Code リリースノートまとめ | リリース時 |
| New Relic Updates | New Relic プラットフォーム・Agent アップデートまとめ | 月次 |
| Codex CLI Updates | OpenAI Codex CLI リリースノートまとめ（安定版のみ） | リリース時 |

## 記事生成パイプライン

```
RSS / Release Feed
    ↓ 毎時取得（EventBridge + Lambda）
Slack 通知チャンネル
    ↓ 毎朝 8:00 JST（EventBridge + Lambda）
Tech Pulse リポジトリに draft: true で push
    ↓ Claude Code でレビュー・精査・公開
GitHub Pages にデプロイ
```

- **RSS-Notifier**: RSS フィードを毎時チェックし、新着を Slack に通知
- **Article-Publisher (x4)**: Slack の通知を集約し、Bedrock (Claude) で記事を生成して `draft: true` で push
- **レビュー・公開**: Claude Code のブログ公開スキルで精査・画像生成・公開

## Tech Stack

| 項目 | 技術 |
|------|------|
| Static Site Generator | [Hugo](https://gohugo.io/) |
| Theme | [PaperMod](https://github.com/adityatelange/hugo-PaperMod) |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions |
| 記事自動生成 | AWS Lambda + EventBridge + Bedrock |
| ヘッダー画像 | Playwright (HTML → PNG) |

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
