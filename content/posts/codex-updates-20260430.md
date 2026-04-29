---
title: "【Codex CLI】rust-v0.126.0-alpha 系 リリースノートまとめ"
date: 2026-04-30T08:01:26+09:00
draft: false
tags: ["codex", "rust", "permission-profile", "sandbox", "bedrock", "gpt-5.4", "plugin", "mcp", "tool-suggest", "windows", "network-proxy", "tui"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.126.0 alpha 系（v0.125.0 以降の進行中変更）のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260430/header.png)

## はじめに

OpenAI Codex CLI は、2026年4月24日にリリースされた **rust-v0.125.0** 以降、**rust-v0.126.0-alpha** 系として継続的にアルファリリースが進んでいます。本記事執筆時点（2026年4月30日）の最新は **rust-v0.126.0-alpha.16**（公開: 2026-04-30 06:36 JST）であり、v0.126.0 GA はまだ公開されていません。

このスパンの主な変更は、**サンドボックス権限モデルの再設計（パーミッションプロファイル）**、**`--full-auto` の非推奨化**、**Bedrock Mantle エンドポイント / GPT-5.4 モデル対応**、**プラグインのリモートインストールキャッシュ**、**Tool suggest の発動条件改善**、**Windows / network-proxy 周りの安定化** です。alpha 段階の集約となるため、運用導入は GA を待つのが安全ですが、CI 検証や Bedrock 移行の準備としては早めに把握しておく価値のある内容です。

---

## 注目アップデート深掘り

### サンドボックス権限の「パーミッションプロファイル」体系への統一

最大の変更は、**明示的サンドボックスパーミッションプロファイル**（#20117）と**サンドボックスプロファイル設定コントロール**（#20118）の追加です。あわせて、内部実装側でも `linux-sandbox: switch helper plumbing to PermissionProfile`（#20106）など、ヘルパーの配線もプロファイルベースに切り替わりました。

従来は「approval mode」「`--full-auto`」「読み取り専用モード」など個別フラグでサンドボックス挙動を切り替える形でしたが、今回の変更で **CLI 側に名前付きの「パーミッションプロファイル」を定義し、実行時に切り替える** モデルへ統一されています。これに伴い、**`--full-auto` は非推奨**（#20133）となり、`permissions: remove legacy read-only access modes`（#19449）/ `remove cwd special path`（#19841）/ `remove core legacy policy round trips`（#19394）といった legacy 系コードも削除済みです。

権限プロファイルは、TUI / ユーザーターン / MCP サンドボックス状態 / シェルエスカレーション / app-server API といった各レイヤー間で同一プロファイルを参照する設計が v0.125.0 で完成しており、v0.126.0-alpha 系では **CLI 側からの明示指定インターフェースが整備された** 形になります。

> **Note:** alpha 段階では、`--full-auto` を使うスクリプトに非推奨警告が出始めます。GA 切り替え前に、CI / 自動化スクリプトの実行モード指定をパーミッションプロファイル名ベースに移行しておくと安全です。

### Bedrock Mantle エンドポイント更新と GPT-5.4 モデル ID 対応

AWS Bedrock 経由で Codex CLI を利用しているユーザー向けに、**Bedrock Mantle エンドポイントの更新** と **GPT-5.4 モデル ID** の対応が入りました（#20109）。あわせて、**モデルプロバイダー単位でのキャパビリティ無効化**（#19442、`feat: disable capabilities by model provider`）と **プロバイダー機能境界の app-server クライアントへの公開**（#20049、`feat: expose provider capability bounds to app server clients`）も追加されています。

具体的なメリットは以下です。

- Bedrock 経由の最新モデル切り替えが、CLI を再ビルドせずに設定で完結
- プロバイダーごとに使えない機能（例：構造化出力非対応モデル）を CLI が事前に把握し、無効化することで失敗呼び出しを抑制
- app-server を組み込む側は、利用可能なキャパビリティ境界をクライアント側で取得できるため、フォールバック実装がシンプル化

Bedrock 経由運用では、エンドポイントとモデル ID の整合が崩れると面倒なエラーになりやすいため、alpha 段階で挙動を確認しておくと GA 後の切り替えが滑らかになります。

### プラグインとツール周りの体験向上

プラグインまわりでは、**リモートインストール済みプラグインキャッシュ（skills / MCP 用）**（#20096）と、**`/plugins` のマーケットプレイスインストールフロー**（#18704）が追加されています。さらに、**外部ソースから MCP / Subagents / hooks / commands を検出してインポート**（#19949）するサポートも入り、既存ワークフローからの移行コストが下がっています。

Tool suggest（コンテキストに応じて使うべきツールを推奨する仕組み）も、**発動条件の改善**（#20091）と、**特定ツールでの無効化サポート**（#20072）が入りました。「常に提案されると邪魔なツール」だけ提案対象から外す運用が可能になります。

---

## 実用的な活用ポイント

### CI / 本番自動化での `--full-auto` 移行

`--full-auto` は v0.126.0-alpha 系で非推奨警告が出始めます。GA で削除されると CI が突然壊れるため、いまのうちに**パーミッションプロファイル名ベースの起動コマンドへ書き換え**ておくと安心です。`feat(cli): add sandbox profile config controls`（#20118）により、設定ファイル側でプロファイル切替が完結できるため、CI 環境変数で profile 名を渡すパターンがシンプルです。

### Bedrock 経由運用の準備

Bedrock Mantle エンドポイント更新と GPT-5.4 対応は、本番投入前に **dev / staging で alpha を動かして接続性を検証**しておくのが安全です。プロバイダー単位のキャパビリティ無効化が入ったため、`output_config: Extra inputs are not permitted` のような構造化出力エラーは、対応していないモデルに対して自動的に抑制される動きになります。

### Windows / プロキシ環境での安定化

Windows での運用は、**core shell env vars の拡充**（#20089）と **pseudoconsole 属性ハンドリング**（#20042）、**process management エッジケース修正**（#19211）など、地味だが効くフィックスが多数入っています。社内プロキシ越しに Codex CLI を動かしているチームには、**network-proxy 系の連続修正**（#19184, #19995, #19999, #20001, #20002）も歓迎すべき変更です。

---

## 主な変更点一覧（v0.125.0 → rust-v0.126.0-alpha.16）

| カテゴリ | PR | 概要 |
|---|---|---|
| Feature | #20117 | CLI に明示的サンドボックスパーミッションプロファイル追加 |
| Feature | #20118 | CLI からのサンドボックスプロファイル設定コントロール |
| Deprecation | #20133 | `--full-auto` を非推奨化 |
| Feature | #20109 | Bedrock Mantle エンドポイント更新 / GPT-5.4 モデル ID 対応 |
| Feature | #19442 | モデルプロバイダー単位でキャパビリティを無効化 |
| Feature | #20049 | プロバイダー機能境界を app-server クライアントに公開 |
| Feature | #20096 | skills / MCP 用のリモートインストール済みプラグインキャッシュ |
| Feature | #18704 | `/plugins` マーケットプレイスインストールフロー |
| Feature | #19949 | 外部ソースから MCP / Subagents / hooks / commands を検出してインポート |
| Improvement | #20091 | Tool suggest の発動条件改善 |
| Improvement | #20072 | 特定ツールで Tool suggest を無効化可能に |
| Internal | #20106 | linux-sandbox ヘルパー配線を PermissionProfile に切替 |
| Internal | #20172-20174 | TUI から core protocol 依存を段階的に除去（[1/7]〜[3/7]） |
| Improvement | #20089 | Windows: core shell env vars セットを拡充 |
| Fix | #20042 | Windows: pseudoconsole 属性ハンドリングをサンドボックス PTY 向けに修正 |
| Fix | #19211 | Windows: プロセス管理のエッジケース改善 |
| Fix | #19184 | network-proxy: deferred な拒否を正しく処理 |
| Fix | #19995 | network-proxy: ホストマッチングを正規化 |
| Fix | #19999 | network-proxy: connect ターゲットを再チェック |
| Fix | #20001 | network-proxy: linux ブリッジヘルパーを堅牢化 |
| Fix | #20002 | network-proxy: バイパスデフォルトを厳格化 |
| Feature | #17088 | codex-analytics: サーバーリクエスト / レスポンスの取り込み |
| Feature | #19895 | External agent session サポート |
| Feature | #19708 | エージェントアイデンティティ向け cloud requirements ロード |

---

## まとめ

rust-v0.126.0-alpha 系は、**サンドボックス権限の「プロファイル」モデルへの集約** を中心に、Bedrock / モデルプロバイダー回り、プラグイン体験、Windows / プロキシ運用の地盤強化が並行して進んだ期間でした。`--full-auto` の非推奨化は、CI / 自動化スクリプトを抱えるチームにとって GA 前の事前対応が必要なポイントです。

GA 公開はまだですが、alpha 段階の挙動を dev / staging で動かしておくと、Bedrock 経由運用や CI のサンドボックス指定の見直しがスムーズになります。GA リリース時には、本記事の変更点一覧を読み直すと差分のキャッチアップが早いはずです。

---

## 📚 Codex CLI をもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [openai/codex リリース一覧（GitHub Releases）](https://github.com/openai/codex/releases)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)
