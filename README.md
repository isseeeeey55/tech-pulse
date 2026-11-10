# Tech Pulse

AWS・Claude Code・New Relic・OpenAI Codex CLI の最新アップデートを、SRE視点でわかりやすく解説する技術ブログです。

**https://tech-pulse.dev/**

## 運用状態: 記事の定期生成停止中

RSS の定期収集・Slack 通知・記事ドラフトの定期生成は停止中です。以下のパイプラインは、定期実行を有効にした場合の構成を示しています。
既存の記事・画像と GitHub Pages のデプロイ設定は残しています。記事の定期生成と、サイトのビルド・デプロイは別の処理です。

## 記事カテゴリ

| カテゴリ | 内容 | 定期生成の状態 |
|---------|------|---------|
| AWS Updates | AWS What's New のアップデートまとめ | 停止中 |
| Claude Code Updates | Claude Code リリースノートまとめ | 停止中 |
| New Relic Updates | New Relic プラットフォーム・Agent アップデートまとめ | 停止中 |
| Codex CLI Updates | OpenAI Codex CLI リリースノートまとめ（安定版のみ） | 停止中 |

## 記事生成パイプライン（定期実行停止中）

```
RSS / Release Feed
    ↓ 毎時取得（EventBridge + Lambda）
Slack 通知チャンネル
    ↓ 毎朝 8:00 JST（EventBridge + Lambda）
Tech Pulse リポジトリに draft: true で push
    ↓ Claude Code でレビュー・精査・公開
GitHub Pages にデプロイ
```

- **RSS-Notifier**: 有効時は RSS フィードを毎時チェックし、新着を Slack に通知
- **Article-Publisher (x4)**: 有効時は毎朝 8:00 JST に Slack の通知を集約し、Bedrock (Claude) で記事を生成して `draft: true` で push
- **レビュー・公開**: Claude Code のブログ公開スキルで精査・画像生成・公開

## Tech Stack

| 項目 | 技術 |
|------|------|
| Static Site Generator | [Hugo](https://gohugo.io/) Extended（CI: 0.168.0） |
| Theme | [PaperMod](https://github.com/adityatelange/hugo-PaperMod) |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions |
| 記事自動生成 | AWS Lambda + EventBridge + Bedrock（定期実行停止中） |
| ヘッダー画像 | Playwright (HTML → PNG) |

## Local Development

CI と同じ Hugo Extended 0.168.0 と Python 3 を使用します。以下のローカル確認では、記事生成 Lambda の起動やサイトのデプロイは行いません。

```bash
# Clone
$ git clone --recursive https://github.com/isseeeeey55/tech-pulse.git
$ cd tech-pulse

# Start dev server
$ hugo server --buildDrafts

# Security regression test
$ python3 scripts/test_hugo_security.py

# Build
$ hugo --minify --baseURL "https://tech-pulse.dev/"
```

## CI / Deployment

[`deploy.yml`](.github/workflows/deploy.yml) は `main` への push または手動実行で、Hugo のセキュリティ回帰テスト・ビルド・GitHub Pages へのデプロイを行います。
現在は PR 用の検証トリガーがないため、PR 作成だけではこのワークフローは実行されません。確認目的で手動実行するとデプロイまで進むので、PR の検証には上記のローカルテストとビルドを使います。

## Directory Structure

```
tech-pulse/
├── .github/workflows/   # GitHub Actions deploy workflow
├── content/posts/       # Blog articles (Markdown)
├── scripts/             # Hugo security regression test
├── static/images/       # Header images, diagrams
├── themes/PaperMod/     # Theme (git submodule)
└── hugo.toml            # Site configuration
```

## License

Blog content is &copy; 2026 Tech Pulse. All rights reserved.

Hugo and PaperMod are used under their respective licenses.
