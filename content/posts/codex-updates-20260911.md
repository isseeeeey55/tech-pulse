---
title: "【Codex CLI】Python SDK 0.154.0 リリースノートまとめ"
date: 2026-09-11T08:01:40+09:00
draft: false
tags: ["codex", "python-sdk", "reasoning-effort", "external-message", "turn-management", "hook-metadata", "notification", "event-stream", "resume", "fork", "service-tier", "protocol-model", "migration"]
categories: ["Codex CLI Updates"]
summary: "Python SDK 0.154.0 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260911/header.png)

# Codex Python SDK 0.154.0 リリースノート

## はじめに

OpenAI Codex の Python SDK `openai-codex` 0.154.0 が 2026年9月11日（JST。GitHub リリース日は 9月10日 UTC）に公開されました。インストールは `pip install --upgrade openai-codex==0.154.0` で、Python 3.10 以降が必要です。対応するランタイム `openai-codex-cli-bin==0.154.0` が同梱されています。

変更点は、reasoning effort の値 `max` / `ultra` の追加、`ExternalMessage` の追加、resume/fork 時の `include_turns` などのオプション追加、生成プロトコルモデルと通知の更新の4項目です。リリースノートには、アップグレード時に確認すべき移行事項が3点挙げられています。

## 注目アップデート深掘り

### 1. reasoning effort に `max` と `ultra` を追加

reasoning effort の値として `max` と `ultra` が追加されました（[#39662](https://github.com/openai/codex/pull/39662)）。各値の挙動や使い分けはリリースノートには書かれていないため、公式ドキュメントで確認してください。

### 2. `ExternalMessage` の追加

同期・非同期の `run()` と `turn()` に `ExternalMessage` を渡せるようになりました（[#44086](https://github.com/openai/codex/pull/44086)）。

- 外部コンテンツが、ターンを開始したり、実行中の通常ターンに参加したりできる
- 外部コンテンツはツールレベルの権限で扱われ、ユーザーの承認は付与しない
- コンシューマーはそれぞれ独立したイベントストリームを受信する

### 3. resume/fork の `include_turns` などのオプション

resume/fork 時の `include_turns`、新しく開始する1つのターンに対する `turn_service_tier`、`source` メタデータが追加されました（[#44084](https://github.com/openai/codex/pull/44084)）。履歴の選択（`include_turns`）は返されるレスポンスを変えるもので、モデルのコンテキストは変えません。これらのオプションを省略した場合は既存のデフォルトが維持されます。

## 実用的な活用ポイント

### アップグレード時の移行事項

リリースノートは、アップグレード時に次の3点を確認するよう求めています。

- **`HookMetadata`**: ハンドラーが `.root` でラップされるようになりました。`hook.command` のようなアクセスは `hook.root.command` に置き換え、ハンドラー固有のフィールドを読む前に `hook.root.handler_type` を確認します。
- **通知ペイロード**: これまで未知だった一部の通知に型付きペイロードが付きました。`.params` ではなく名前付きフィールドを読みます。未知または不正なペイロードは引き続き `UnknownNotification` になります。
- **ターンハンドルのイベント**: 手動で構築したハンドルや途中から参加したハンドルは、参加した時点以降のイベントを受信します。それ以前の出力は再送されないため、収集結果が一部だけになることがあり、完了後に参加すると `TransportClosedError` が発生することがあります。保存済みの履歴は `thread.read(include_turns=True)` で取得します。`thread.turn(...)` が直接返すハンドルは、リクエスト送信時点からのイベントを保持します。

### `codex_bin` を上書きしている場合

カスタムの `codex_bin` を指定している場合、`ExternalMessage` と新しい履歴・ターン単位のオプションを使うには CLI 0.151.0 以降が必要です。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | `max` および `ultra` 推論努力レベル追加 | reasoning effort の値に `max` と `ultra` を追加（[#39662](https://github.com/openai/codex/pull/39662)） |
| Feature | `ExternalMessage` 追加 | 同期・非同期の `run()` と `turn()` に `ExternalMessage` を追加。外部コンテンツがターンを開始したり実行中の通常ターンに参加したりでき、ツールレベルの権限で扱われる（ユーザー承認は付与しない）。コンシューマーは独立したイベントストリームを受信（[#44086](https://github.com/openai/codex/pull/44086)） |
| Feature | ターン管理オプション追加 | resume/fork 時の `include_turns`、新規ターン用の `turn_service_tier`、`source` メタデータを追加。履歴の選択は返されるレスポンスを変えるもので、モデルのコンテキストは変えない。省略時は既存のデフォルトを維持（[#44084](https://github.com/openai/codex/pull/44084)） |
| Improvement | プロトコルモデルと通知の刷新 | 生成されたプロトコルモデルと通知を更新し、ターン開始レスポンス前に到着する完了イベントを保持するように改善（[#44032](https://github.com/openai/codex/pull/44032), [#44400](https://github.com/openai/codex/pull/44400)） |
| Migration | `HookMetadata` 構造変更 | ハンドラーが `.root` にラップされ、アクセス方法が変更。`hook.root.handler_type` のチェックが必要に |
| Migration | 通知ペイロードの型定義変更 | 一部の通知が型付きペイロードを持つようになり、`.params` ではなく名前付きフィールドでアクセスする必要がある |
| Migration | ターンハンドルのイベント動作変更 | 手動構築または途中参加のターンハンドルは、アタッチポイントからのイベントのみ受信。以前の出力は再生されず、完了後のアタッチは `TransportClosedError` を引き起こす可能性 |

## まとめ

Python SDK 0.154.0 では、reasoning effort の `max` / `ultra`、`ExternalMessage`、resume/fork の `include_turns` などのオプションが追加されました。`HookMetadata` の構造、通知ペイロードの型、ターンハンドルのイベント受信範囲に関する移行事項があるため、アップグレード前に該当するコードを確認してください。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)