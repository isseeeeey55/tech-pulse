---
title: "【Claude Code】v2.1.91・v2.1.92 リリースノートまとめ"
date: 2026-04-04T08:01:11+09:00
draft: false
tags: ["claude-code", "mcp", "bedrock", "skills", "plugins", "cost", "performance", "security"]
categories: ["Claude Code Updates"]
summary: "v2.1.91・v2.1.92 のClaude Codeリリースノートまとめ。Bedrock対話型セットアップウィザード、MCPツール結果500K対応、/costのモデル別内訳、forceRemoteSettingsRefreshなど計32件"
---

![](/images/claude-code-updates-20260404/header.png)

## はじめに

Claude Code v2.1.91 と v2.1.92 がリリースされました。v2.1.92 では Bedrock の対話型セットアップウィザード、`/cost` のモデル別内訳表示、起動時にリモート設定の取得を強制する `forceRemoteSettingsRefresh` ポリシーが追加されています。v2.1.91 では MCP ツール結果の最大500K対応と `disableSkillShellExecution` 設定が入りました。合計32件の変更です。

## 注目アップデート深掘り

### Bedrock 対話型セットアップウィザード（v2.1.92）

![Bedrock セットアップウィザードのフロー](/images/claude-code-updates-20260404/bedrock-wizard.png)

ログイン画面で「3rd-party platform」を選択した際に、Bedrock 向けの対話型セットアップウィザードが起動するようになりました。AWS 認証、リージョン設定、クレデンシャル検証、モデルピニングまでガイド付きで進められます。

これまで Bedrock で Claude Code を使うには、環境変数を手動で設定する必要がありました。`AWS_PROFILE`、`AWS_REGION`、`ANTHROPIC_MODEL` などを正しく設定する手順はドキュメントを読まないと分からず、チームへの展開時にハマりがちだったポイントです。ウィザードがこれを一画面で解決してくれます。

### MCP ツール結果の大容量対応 — 最大500K（v2.1.91）

> **MCP ツール結果のサイズ制限とは？**
> Claude Code は MCP サーバーからのツール結果が一定サイズを超えると自動的に切り詰めます。DB スキーマのダンプや大きな API レスポンスが途中で切れる原因になっていました。

MCP ツール結果に `_meta["anthropic/maxResultSizeChars"]` アノテーションを付与することで、最大500K文字まで切り詰めずに受け取れるようになりました。

```json
{
  "content": [{ "type": "text", "text": "... 大きなDBスキーマやクエリ結果 ..." }],
  "_meta": { "anthropic/maxResultSizeChars": 500000 }
}
```

MCP サーバー開発者向けの機能です。DB スキーマの全量取得や大きな検索結果の返却で切り詰めが発生していた場合、サーバー側でこのアノテーションを付けるだけで解消できます。

### forceRemoteSettingsRefresh ポリシー（v2.1.92）

> **リモート管理設定（managed settings）とは？**
> 組織の管理者が Claude Code の設定を一元配信する仕組みです。モデル制限やツール権限などを `managed-settings.d/` 経由でチーム全体に適用できます。

`forceRemoteSettingsRefresh` ポリシーを設定すると、CLI 起動時にリモート管理設定を必ず最新取得し、取得に失敗した場合は起動しません（fail-closed）。

オフライン時にキャッシュ済みの古い設定で動いてしまうリスクを排除できます。セキュリティポリシーが厳しい環境（金融、医療など）で、設定の鮮度を保証したい場合に有用です。

## 実用的な活用ポイント

**`/cost` のモデル別・キャッシュヒット内訳（v2.1.92）**: サブスクリプションユーザー向けに、`/cost` でモデルごとの使用量とキャッシュヒット率が確認できるようになりました。どのモデルがトークンを消費しているか把握できます。

**disableSkillShellExecution（v2.1.91）**: スキル・プラグイン内でのインラインシェル実行を無効化する設定です。信頼できないスキルやマーケットプレイスから取得したプラグインに対して、シェル実行を制限できます。Bash ツール自体には影響しません。

```json
{ "disableSkillShellExecution": true }
```

**Write ツールのdiff計算高速化（v2.1.92）**: タブ・`&`・`$` を含むファイルで60%高速化されました。大きなファイルの書き込みが速くなります。

**プロンプトキャッシュ失効ヒント（v2.1.92）**: Pro ユーザーがセッションに戻った際、プロンプトキャッシュが失効していると次のターンで送信されるアンキャッシュトークン数が表示されます。コスト感覚を掴みやすくなりました。

**`--resume` のトランスクリプト断裂修正（v2.1.91）**: 非同期書き込みが失敗した場合に会話履歴が途切れる問題が修正されています。長時間セッションの継続が安定しました。

## 全変更点一覧

### v2.1.92（19件）

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | Bedrock 対話型セットアップウィザード | ログイン画面から認証・リージョン・モデル設定をガイド付きで実行 |
| Feature | `forceRemoteSettingsRefresh` ポリシー | 起動時にリモート設定を強制取得、失敗時は起動拒否（fail-closed） |
| Feature | `/cost` モデル別・キャッシュヒット内訳 | サブスクリプションユーザー向けに使用量の詳細表示 |
| Feature | `/release-notes` 対話型バージョン選択 | バージョンピッカーでリリースノートを参照 |
| Feature | Remote Control セッション名のホスト名プレフィックス | デフォルトで `hostname-graceful-unicorn` 形式に |
| Feature | プロンプトキャッシュ失効ヒント | Pro ユーザー向けにアンキャッシュトークン数を表示 |
| Fix | サブエージェントの tmux ペインカウント失敗 | tmux ウィンドウの削除・リナンバー後にスポーン不可になる問題を修正 |
| Fix | Stop フックの誤動作 | 小型モデルの `ok:false` で Stop フックが失敗する問題を修正 |
| Fix | ストリーミングの配列/オブジェクトバリデーション | JSON エンコード文字列として送出されるフィールドの検証を修正 |
| Fix | 拡張思考の空白テキストブロック | 空白のみのテキストブロックで API 400 エラーになる問題を修正 |
| Fix | フィードバックサーベイの誤送信 | auto-pilot のキー入力や連続プロンプトの数字衝突を修正 |
| Fix | フルスクリーンの「esc to interrupt」ヒント | テキスト選択時に「esc to clear」と重複表示される問題を修正 |
| Fix | Homebrew 更新プロンプトのチャンネル修正 | `claude-code` → stable、`claude-code@latest` → latest に修正 |
| Fix | `ctrl+e` のカーソル移動 | 行末で次の行末にジャンプする問題を修正 |
| Fix | フルスクリーンのスクロール重複表示 | iTerm2・Ghostty 等で同一メッセージが2箇所に表示される問題を修正 |
| Fix | idle-return のトークンヒント | セッション累計ではなく現在のコンテキストサイズを表示するよう修正 |
| Fix | プラグイン MCP サーバーの接続停滞 | 未認証の claude.ai コネクタと重複する場合にスタックする問題を修正 |
| Performance | Write ツールの diff 計算高速化 | タブ・`&`・`$` を含むファイルで60%高速化 |
| Change | `/tag`・`/vim` コマンド削除 | vim モードは `/config` → Editor mode から切替 |

### v2.1.91（13件）

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | MCP ツール結果 `_meta` アノテーション | `maxResultSizeChars` で最大500Kまで切り詰め回避 |
| Feature | `disableSkillShellExecution` 設定 | スキル/プラグインのインラインシェル実行を無効化 |
| Feature | ディープリンクの複数行プロンプト | `claude-cli://open?q=` で `%0A` エンコード改行に対応 |
| Feature | プラグイン `bin/` 実行ファイル対応 | 同梱した実行ファイルを Bash ツールから直接実行可能に |
| Fix | `--resume` トランスクリプト断裂 | 非同期書き込み失敗時に会話履歴が途切れる問題を修正 |
| Fix | `cmd+delete` の行頭削除 | iTerm2、kitty、WezTerm、Ghostty、Windows Terminal で修正 |
| Fix | リモートセッションのプランモード | コンテナ再起動後にプランファイルを見失う問題を修正 |
| Fix | `permissions.defaultMode: "auto"` の JSON スキーマ検証 | settings.json での設定が正しく検証されるよう修正 |
| Fix | Windows バージョンクリーンアップ | アクティブバージョンのロールバックコピーを保護するよう修正 |
| Improvement | `/feedback` の利用不可時メッセージ | 使えない理由を表示（以前は無言で非表示） |
| Improvement | `/claude-api` スキルのガイダンス強化 | エージェント設計パターン、ツール設計、キャッシュ戦略のガイドを改善 |
| Performance | Bun での `stripAnsi` 高速化 | `Bun.stripANSI` へのルーティングでパフォーマンス向上 |
| Performance | Edit ツールの `old_string` 短縮 | 短いアンカーで出力トークンを削減 |

## まとめ

2バージョン合計32件。v2.1.92 の Bedrock セットアップウィザードは、AWS 環境で Claude Code を展開する際の初期設定の手間を一掃してくれます。`forceRemoteSettingsRefresh` もエンタープライズ向けには刺さるポリシー設定。v2.1.91 の MCP 500K 対応は、大きなデータを扱う MCP サーバーの実用性を上げています。バグ修正も20件近く、特に tmux 連携やフルスクリーンモードのスクロール問題など、日常的に遭遇しやすいものが潰されています。
