---
title: "【Claude Code】v2.1.110 / v2.1.109 リリースノートまとめ"
date: 2026-04-16T08:01:53+09:00
draft: false
tags: ["claude-code", "tui", "fullscreen", "focus", "traceparent", "otel", "bash", "mcp", "remote-control", "session-recap"]
categories: ["Claude Code Updates"]
summary: "v2.1.110 / v2.1.109 の変更点を解説します。`/tui fullscreen` でちらつきのない全画面モード、`/focus` コマンド新設、SDK/headless での TRACEPARENT/TRACESTATE 対応、Bash tool の最大 timeout 強制、Session recap の telemetry 無効環境対応、Remote Control からの `/autocompact` 等の呼び出しなど。"
---

![](/images/claude-code-updates-20260416/header.png)

## はじめに

Claude Code の **v2.1.110** が昨日夜（JST）にリリースされました。目玉は `/tui fullscreen` による flicker-free レンダリングの追加と、`Ctrl+O` の役割分離に伴う **`/focus` コマンドの新設** です。加えて SDK / headless セッションで **`TRACEPARENT` / `TRACESTATE` 環境変数**を使った分散トレース連携が可能になり、SRE 側の可観測性基盤と Claude Code の自動化ワークフローが一本でつながるようになりました。

一方で **v2.1.109** は「拡張思考インジケーターに rotating progress hint を追加」の 1 行だけの軽量リリースで、中身は v2.1.110 がほぼすべてです。

## 注目アップデート深掘り

### `/tui fullscreen` — ちらつきのないフルスクリーンモード

![/tui fullscreen の Before/After](/images/claude-code-updates-20260416/tui-fullscreen.png)

v2.1.110 で **`/tui` コマンド**と **`tui` 設定**が追加されました。会話の途中で `/tui fullscreen` と入力すると、同じセッションを維持したまま flicker-free のフルスクリーン表示に切り替わります。

これまでのインラインモードは、長文出力やツール実行が重なるとターミナルのスクロールと再描画が頻繁に発生し、特に大きなリファクタリングや多数のファイル編集を伴う作業で視線が散る問題がありました。フルスクリーンモードではこのちらつきが解消されます。

関連する設定として:

- **`autoScrollEnabled`**（`/config` から設定）: fullscreen mode での会話 auto-scroll を無効化。自分でスクロールしながら読みたい場面で便利
- **`Ctrl+G`**: 外部エディタで開くときに、Claude の前回レスポンスを**コメントとして含める**オプション（`/config` で有効化）

また、v2.1.110 で `Ctrl+O` の役割が整理されました。これまで「normal / verbose transcript の切り替え + focus view トグル」という複合的な働きをしていましたが、**`Ctrl+O` は transcript モードの切り替えだけ**に絞られ、focus view は新しく追加された **`/focus` コマンド**で切り替える形に分離されました。キーボードショートカットを複雑にしていたユーザーには嬉しい整理です。

### TRACEPARENT / TRACESTATE — SDK/headless セッションで分散トレース連携

![TRACEPARENT / TRACESTATE 連携の流れ](/images/claude-code-updates-20260416/traceparent-flow.png)

v2.1.110 で SDK / headless セッションが **`TRACEPARENT` / `TRACESTATE` 環境変数を読み込む**ようになりました。これは W3C Trace Context 仕様のヘッダーと同じ形式で、親トレースから引き継いだ trace context を Claude Code のセッションに紐付けるためのものです。

> **W3C Trace Context とは？**
> 分散トレーシングでサービス間の trace context を伝搬するための W3C 標準仕様です。`traceparent` には trace ID / parent span ID / sampling flag が、`tracestate` にはベンダー固有の追加情報が入ります。OpenTelemetry、AWS X-Ray、Datadog APM などほぼ全ての APM ツールがこの形式を相互運用できます。

何が嬉しいかというと、CI/CD パイプラインや Lambda 実行の中から Claude Code の SDK / headless モードを呼ぶとき、**親の trace にそのまま Claude Code のスパンを紐付けられる**点です。例えば、GitHub Actions の中で Claude Code を headless で実行して自動 PR レビューを走らせている場合、ワークフロー側で採番した trace context を環境変数で渡せば、APM 上で「PR レビュージョブ全体 → Claude Code セッション → 実行ツール」の順にフラットにトレースがつながります。

使い方の基本形:

```bash
# OpenTelemetry SDK 等で採番した context を環境変数経由で渡す
$ export TRACEPARENT="00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
$ export TRACESTATE="mycompany=span_attrs"

# SDK / headless セッションを起動
$ claude --print "このPRの差分をレビューして"
```

対象は **SDK と headless（`-p`/`--print`）セッション**で、通常の対話モードではありません。CI 自動化寄りの機能です。

## 実用的な活用ポイント

**`/plugin` Installed タブの整理**: プラグイン一覧で「要注意（更新あり等）」と「お気に入り」が上部にまとまるようになり、`f` キーで選択中の項目をお気に入り登録できます。インストール済みプラグインが多いユーザーでも重要な項目を見失いません。

**`/doctor` で MCP 設定の重複検出**: 同じ MCP サーバーが複数の config scope（プロジェクト / ユーザー / システム）で異なる endpoint で定義されているとき、警告を出してくれるようになりました。MCP の設定スコープが増えてくると混線しやすいポイントなので、ここで事前に検出できるのは助かります。

**Bash tool の max timeout 強制**: 従来、Bash tool に任意の大きな timeout 値を渡せてしまっていたのが、**ドキュメントに記載された上限を強制するように**なりました。暴走スクリプトで時間を浪費するリスクが小さくなります。既存の合理的な timeout 設定には影響しません。

**Session recap が Bedrock / Vertex / Foundry でも有効**: v2.1.108 で追加された `recap` 機能（セッション復帰時に前回のコンテキストを要約表示）が、telemetry 無効化環境でも使えるようになりました。具体的には Bedrock / Vertex / Foundry ユーザーと、`DISABLE_TELEMETRY` を設定しているユーザー向けの対応拡張です。opt out は `/config` か `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=0`。

**Remote Control 対応拡張**: モバイル / Web クライアントから `/autocompact`、`/context`、`/exit`、`/reload-plugins` が実行可能になりました。出先で動いているセッションの context を圧縮したり、プラグインを再読み込みしたりするときの選択肢が増えます。

**Write tool: IDE diff 編集の通知**: IDE 側の diff ビューでユーザーが提案内容を編集して accept したとき、**その編集内容が Claude に通知される**ようになりました。これまでは「accept ボタン押されたかどうか」しか見えていなかったので、エージェント的な挙動の精度が上がります。

**主なバグ修正**:
- MCP tool call が SSE/HTTP transport でサーバー接続が切れたとき無限 hang する問題
- non-streaming fallback のリトライで API 到達不可時に数分 hang する問題
- focus mode で session recap や local slash-command 出力が表示されない問題
- fullscreen でテキスト選択中にツール実行すると CPU 使用率が高騰する問題
- `PermissionRequest` hook の `updatedInput` が `permissions.deny` ルールで再チェックされない問題（セキュリティ関連）
- Open in editor のコマンドインジェクション対策（セキュリティ強化）

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Added (v2.1.110) | `/tui fullscreen` | flicker-free のフルスクリーンモード。`tui` 設定も追加 |
| Added (v2.1.110) | `/focus` コマンド | focus view の切り替えを `Ctrl+O` から分離 |
| Added (v2.1.110) | `Ctrl+G` で前回レスポンスをコメント化 | 外部エディタに Claude のコメントを含めて展開（`/config` で有効化） |
| Added (v2.1.110) | `TRACEPARENT` / `TRACESTATE` 対応 | SDK / headless セッションで W3C Trace Context 連携 |
| Improved (v2.1.110) | `/doctor` で MCP 重複設定警告 | 複数の config scope で異なる endpoint を警告 |
| Improved (v2.1.110) | Remote Control 対応拡張 | `/autocompact`, `/context`, `/exit`, `/reload-plugins` が利用可能 |
| Improved (v2.1.110) | Bash tool の max timeout 強制 | 任意の大きな timeout 値を弾く |
| Improved (v2.1.110) | Session recap を telemetry 無効環境でも有効化 | Bedrock / Vertex / Foundry / `DISABLE_TELEMETRY` ユーザー対応 |
| Improved (v2.1.109) | 拡張思考インジケーターに rotating progress hint | 長時間処理中の進捗表現を改善 |
| Fixed (v2.1.110) | セキュリティ・バグ修正 多数 | MCP hang、non-streaming fallback、`PermissionRequest` hook の再チェック、コマンドインジェクション対策 ほか |

## まとめ

v2.1.110 は体験面の改善と CI/CD 連携寄りの機能追加が中心です。目玉は `/tui fullscreen` のフルスクリーン表示と `TRACEPARENT` / `TRACESTATE` 対応の 2 つで、前者は普段使いのちらつきを取る純粋な UX 改善、後者は CI/CD や Lambda 内で Claude Code を headless 実行しているチーム向けの可観測性強化です。Session recap の対応環境拡張（Bedrock / Vertex / Foundry）と、MCP 設定の重複検出（`/doctor`）も、実運用で地味に効く改善です。v2.1.109 は単発の軽量リリースで、`/tui fullscreen` と合わせて progress hint が自然に効いてきます。
