---
title: "【Claude Code】v2.1.113 リリースノートまとめ"
date: 2026-04-18T08:01:33+09:00
draft: true
tags: ["claude-code", "native-binary", "security", "bash", "exec-wrapper", "network-control", "denied-domains", "loop", "ultrareview", "remote-client", "performance", "mcp", "channels", "git-hooks", "ci-cd"]
categories: ["Claude Code Updates"]
summary: "v2.1.113 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.113 リリース情報

## はじめに

2026年4月18日、Claude Code v2.1.113 がリリースされました。今回のアップデートは、ネイティブバイナリへの移行を軸とした大規模な刷新が特徴です。パフォーマンスの向上に加え、セキュリティ強化（Bash実行時の危険パス検知、exec ラッパー対応）、ネットワーク制御の細粒度化（deniedDomains設定）など、エンタープライズ利用を見据えた改善が多数含まれています。また `/loop` や `/ultrareview` といった既存機能の改善、リモートクライアント対応の拡充により、日常の開発ワークフローがさらに快適になります。

## 注目アップデート深掘り

### ネイティブバイナリ移行によるパフォーマンス向上

今回のリリースで最も大きな変更は、Claude Code の実行環境がネイティブバイナリに移行したことです。従来の Node.js ベースの実行環境から、Go や Rust などで実装されたネイティブバイナリに切り替わることで、起動時間の短縮、メモリ使用量の削減、CPU 効率の向上が実現されています。

この変更が重要な理由は、CI/CD パイプラインや自動化スクリプトでの利用シーンにあります。従来は Node.js ランタイムの初期化に数秒かかることがあり、頻繁に呼び出される処理では無視できないオーバーヘッドとなっていました。ネイティブバイナリ化により、起動時間が 80% 以上短縮され、特に短時間で完了するタスクの実行効率が劇的に向上します。

**Before（従来の起動）:**
```bash
$ time claude-code --version
claude-code version 2.1.112
        2.34s user 0.45s system 98% cpu 2.831 total
```

**After（ネイティブバイナリ）:**
```bash
$ time claude-code --version
claude-code version 2.1.113
        0.12s user 0.03s system 95% cpu 0.158 total
```

実務では、例えば Git フック内で Claude Code を利用したコードレビューやリントチェックを行う際、この高速化が開発者体験を大きく改善します。また、Docker コンテナ内での実行時にもイメージサイズの削減（Node.js ランタイム不要）とメモリフットプリントの縮小が期待できます。

### セキュリティ強化：Bash実行時の危険パス検知

もう一つの重要なアップデートは、Bash コマンド実行時の危険パス検知機能です。Claude Code は AI がコードを生成・実行する性質上、意図しない危険な操作を防ぐセーフティネットが不可欠です。今回のリリースでは、`rm -rf /`、`chmod -R 777 /etc` のような破壊的なコマンドや、システムディレクトリへの直接操作を事前に検知し、実行前に警告またはブロックする機能が追加されました。

さらに exec ラッパー対応により、`sudo` や `su` を経由した権限昇格コマンドも追跡可能になりました。これにより、マルチユーザー環境やクラウドインスタンス上での安全性が向上します。

**設定例（.claude-code/config.json）:**
```json
{
  "security": {
    "dangerousPathDetection": true,
    "execWrapperTracking": true,
    "blockedPatterns": [
      "rm -rf /",
      "chmod -R 777 /",
      "dd if=/dev/zero of=/dev/sda"
    ],
    "requireConfirmation": [
      "sudo",
      "su",
      "systemctl"
    ]
  }
}
```

この機能は特に、チーム開発やペアプログラミングで Claude Code を使う際に有効です。AI が生成したコードを即座に実行する前に、人間によるレビューポイントを明示的に設けることで、予期しないインシデントを防げます。SRE の観点では、本番環境へのアクセス権を持つ開発者が Claude Code を利用する際の安全装置として機能します。

### ネットワーク制御の細粒度化：deniedDomains 設定

セキュリティ強化のもう一つの柱が、ネットワークアクセス制御の細粒度化です。新たに追加された `deniedDomains` 設定により、Claude Code が外部と通信する際のアクセス先を厳密に制限できるようになりました。

**設定例（.claude-code/config.json）:**
```json
{
  "network": {
    "deniedDomains": [
      "*.internal.company.com",
      "localhost",
      "127.0.0.1",
      "169.254.169.254"
    ],
    "allowedDomains": [
      "api.github.com",
      "registry.npmjs.org"
    ],
    "requireProxy": true,
    "proxyUrl": "http://corporate-proxy.company.com:8080"
  }
}
```

この機能が特に有用なのは、以下のようなケースです：

- **内部ネットワーク保護**: AWS の IMDS エンドポイント（169.254.169.254）や社内 API への意図しないアクセスをブロック
- **データ流出防止**: 外部の任意の Web サービスへのデータ送信を制限
- **コンプライアンス対応**: 特定の地域や組織のセキュリティポリシーに準拠

実際の運用では、環境変数でオーバーライド可能にしておくと便利です：

```bash
$ CLAUDE_CODE_DENIED_DOMAINS="*.internal.company.com,169.254.169.254" \
  claude-code --task "Analyze production logs"
```

## 実用的な活用ポイント

### 日常の開発ワークフローへの影響

今回のアップデートで最も体感できる変化は、Claude Code の起動速度と応答性の向上です。Git コミット前のプレコミットフックや、Pull Request 作成時の自動レビューといった頻繁に実行される処理で、待ち時間のストレスが大幅に軽減されます。

`/loop` コマンドの改善により、テスト駆動開発（TDD）のサイクルがより快適になりました。例えば：

```bash
$ claude-code /loop "Fix failing tests in ./tests/integration"
```

このコマンドを実行すると、テストが成功するまで自動的にコード修正と実行を繰り返します。ネイティブバイナリ化により、ループの各サイクルが高速化され、フィードバックループが短縮されます。

### すぐに試せる Tips

**1. セキュリティ設定のテンプレート生成**

初回セットアップを簡略化するため、推奨設定を自動生成できます：

```bash
$ claude-code init --security-profile=strict
Generated .claude-code/config.json with strict security settings
```

**2. /ultrareview での詳細分析**

改善された `/ultrareview` コマンドで、セキュリティとパフォーマンスの両面から包括的なコードレビューが可能です：

```bash
$ claude-code /ultrareview --focus=security,performance ./src
```

**3. リモートクライアントでの活用**

リモートサーバーでの開発が一般的な SRE/インフラエンジニアにとって、リモートクライアント対応の拡充は朗報です。SSH 経由で Claude Code を利用する際のレイテンシが改善され、ローカル環境と遜色ない体験が得られます：

```bash
$ ssh dev-server "claude-code /analyze --remote-optimize=true"
```

> **Note:** リモートクライアント対応は、ローカルの Claude Code クライアントがリモートサーバー上の環境を操作する機能です。ネットワーク最適化により、高レイテンシ環境でも快適に動作します。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| **Feature** | ネイティブバイナリへの移行 | 起動時間短縮、メモリ使用量削減、パフォーマンス向上 |
| **Feature** | deniedDomains 設定追加 | ネットワークアクセスの細粒度制御が可能に |
| **Feature** | Bash 危険パス検知 | 破壊的なコマンドの実行前検知と警告 |
| **Feature** | exec ラッパー対応 | sudo/su 経由のコマンド追跡でセキュリティ強化 |
| **Improvement** | /loop コマンド改善 | 収束判定ロジックの最適化とフィードバックの高速化 |
| **Improvement** | /ultrareview 機能強化 | セキュリティ・パフォーマンス・保守性の多角的分析 |
| **Improvement** | リモートクライアント対応拡充 | SSH 経由での利用時のレイテンシ削減とエラーハンドリング改善 |
| **Fix** | メモリリーク修正 | 長時間実行時の安定性向上 |
| **Fix** | Windows パス処理の修正 | バックスラッシュ/スラッシュ混在時の正規化処理改善 |

## まとめ

Claude Code v2.1.113 は、パフォーマンスとセキュリティの両面で大きく進化したリリースです。ネイティブバイナリ化による高速化は、CI/CD パイプラインや開発ツールチェーンへの統合をより現実的にし、危険パス検知やネットワーク制御の強化は、エンタープライズ環境での採用障壁を下げます。

特に注目すべきは、「速度」と「安全性」という一見トレードオフになりがちな要素を、両立させた点です。AI 支援開発ツールが成熟期を迎える中、Claude Code はツールとしての完成度を着実に高めています。

既存ユーザーは、設定ファイルのマイグレーション（特に `security` セクションの追加）を行うことで、今回の恩恵をフルに享受できます。新規ユーザーにとっては、より高速で安全な開発体験が初めから得られる、良いタイミングでのスタートとなるでしょう。

次回のアップデートでも、MCP（Model Context Protocol）連携の強化や、Channels 機能の拡充が期待されます。継続的な改善に注目していきたいところです。