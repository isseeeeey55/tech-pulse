---
title: "【Claude Code】v2.1.84 / v2.1.85 リリースノートまとめ"
date: 2026-03-27T08:01:19+09:00
draft: false
tags: ["claude-code", "powershell", "mcp", "worktree", "hooks", "bedrock", "vertex-ai", "streaming", "otel"]
categories: ["Claude Code Updates"]
summary: "v2.1.84/v2.1.85 のClaude Codeリリースノートまとめ。PowerShellツール、3Pモデル制御環境変数、Hooks条件フィルタ等"
---

![](/images/claude-code-updates-20260327/header.png)

## はじめに

Claude Code v2.1.84 および v2.1.85 がリリースされました。v2.1.84では、Windows環境でのPowerShellツール（opt-inプレビュー）、Bedrock/Vertex AI向けの環境変数による詳細なモデル制御、フック機能の拡張が主な変更点です。v2.1.85ではフック条件フィルタの追加やMCP OAuth改善など、運用品質の向上が図られています。

## 注目アップデート深掘り

### PowerShell ツール（opt-in プレビュー）

v2.1.84で最も注目すべき新機能が、Windows向けPowerShellツールのopt-inプレビューです。従来のClaude CodeはBashツールのみでLinux/macOS環境が前提でしたが、PowerShellツールの追加によりWindows Server環境でも直接コマンド実行が可能になります。

**有効化方法**

PowerShellツールはopt-inのため、明示的に有効化が必要です：

```json
{
  "permissions": {
    "allow": ["PowerShell"]
  }
}
```

> **PowerShellツールとは？**
> Claude CodeがWindows環境でPowerShellコマンドを直接実行できるようにする新しいツールです。Bashツールと同様の位置づけで、ファイル操作、プロセス管理、Azure CLI呼び出しなどが可能になります。

Windows ServerでIaCを管理しているチームや、Azure環境との連携が必要なSREにとって、これまでWSL経由で行っていた作業をネイティブなPowerShellで実行できるようになる点が大きなメリットです。

詳細: https://code.claude.com/docs/en/tools-reference#powershell-tool

### 3Pモデル制御の環境変数拡張

Bedrock、Vertex AI、Foundry経由でClaude Codeを利用している企業向けに、モデル制御の環境変数が大幅に拡張されました。

```bash
# デフォルトモデルの能力検出をオーバーライド
$ export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTS="effort,thinking"
$ export ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTS="effort,thinking"

# /model ピッカーのラベルをカスタマイズ
$ export ANTHROPIC_DEFAULT_OPUS_MODEL_NAME="Claude Opus (Bedrock)"
$ export ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION="us-east-1 endpoint"
```

3Pプロバイダー経由ではモデルのバージョンがピン留めされることがあり、能力検出が正しく動作しないケースがありました。これらの環境変数により、`effort`（推論コスト制御）や`thinking`（拡張思考）の対応状況を明示的に指定できるようになります。

### Hooks の条件フィルタ（v2.1.85）

![フック条件フィルタ Before/After](/images/claude-code-updates-20260327/hooks-filter.png)

v2.1.85で追加された`if`フィールドにより、フックの発火条件をパーミッションルール構文で指定できるようになりました。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "if": "Bash(git *)",
        "command": "echo 'git command detected'"
      }
    ]
  }
}
```

従来はmatcherでツール名を指定するだけでしたが、`if`フィールドで`Bash(git *)`のように引数パターンまで絞り込めるようになりました。全てのBash実行でフックプロセスが起動されていた状況が改善され、プロセス生成のオーバーヘッドを大幅に削減できます。

## 実用的な活用ポイント

**ストリーミングタイムアウトの調整**: `CLAUDE_STREAM_IDLE_TIMEOUT_MS`環境変数（デフォルト90秒）で、ストリーミングのアイドル監視閾値を設定できます。ネットワークが不安定な環境や、レスポンスが遅い3Pプロバイダー利用時に値を大きくすることで、不要な切断を防げます。

**リクエストIDによるデバッグ**: APIリクエストに`x-client-request-id`ヘッダーが付与されるようになりました。タイムアウトやエラー発生時にAnthropicサポートへ共有することで、問題の特定が格段に容易になります。

**バックグラウンドタスクの通知**: Bashのバックグラウンドタスクが対話プロンプトで停止している場合、約45秒後に通知が表示されるようになりました。`sudo`待ちなどでタスクが固まっている状況を早期に検知できます。

**MCP説明文の2KB制限**: MCPツールの説明文とサーバー指示が2KBにキャップされました。OpenAPI生成されたMCPサーバーがコンテキストを圧迫する問題が解消されます。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | PowerShell ツール（v2.1.84） | Windows向け opt-in プレビュー |
| Feature | 3Pモデル制御環境変数（v2.1.84） | `ANTHROPIC_DEFAULT_{OPUS,SONNET,HAIKU}_MODEL_SUPPORTS/NAME/DESCRIPTION` |
| Feature | `CLAUDE_STREAM_IDLE_TIMEOUT_MS`（v2.1.84） | ストリーミングアイドル監視の閾値設定 |
| Feature | `TaskCreated` フック（v2.1.84） | タスク作成時に発火するフックイベント |
| Feature | `WorktreeCreate` HTTP フック（v2.1.84） | ワークツリー作成時にHTTPフック対応 |
| Feature | `allowedChannelPlugins`（v2.1.84） | 管理者向けチャンネルプラグイン許可リスト |
| Feature | フック条件フィルタ `if`（v2.1.85） | パーミッションルール構文でフック発火条件を制御 |
| Feature | MCPサーバー環境変数（v2.1.85） | `CLAUDE_CODE_MCP_SERVER_NAME/URL` を headersHelper に提供 |
| Improvement | `x-client-request-id` ヘッダー | APIリクエストのデバッグ追跡 |
| Improvement | MCP説明文 2KB キャップ | コンテキスト圧迫防止 |
| Improvement | ディープリンクのターミナル選択 | 優先ターミナルで開くように改善 |
| Improvement | Rules/Skills `paths:` YAML対応 | glob のYAMLリスト形式をサポート |
| Fix | IME入力（CJK）のインライン描画 | 日本語入力がカーソル位置に正しく表示 |
| Fix | macOS キーチェーン一時エラー | "Not logged in" 誤表示を修正 |
| Fix | Partial clone リポジトリ起動性能 | Scalar/GVFS での大量blob ダウンロード回避 |
| Fix | `/compact` のコンテキスト超過 | 大規模会話でのコンパクト失敗を修正（v2.1.85） |
| Fix | MCP OAuth スコープ再認可 | リフレッシュトークン存在時の昇格フロー修正（v2.1.85） |

## まとめ

v2.1.84/v2.1.85は「マルチプラットフォーム対応」と「運用精度の向上」が2大テーマです。PowerShellツールによるWindows対応、3Pモデル制御環境変数によるBedrock/Vertex AI環境でのカスタマイズ性向上は、企業環境でのClaude Code活用範囲を広げます。

v2.1.85のフック条件フィルタ（`if`フィールド）は、PreToolUseフックを多用しているユーザーにとって大きな改善です。不要なプロセス生成を削減し、フックのパフォーマンスオーバーヘッドを最小化できます。

バグ修正面では、日本語入力（IME）のインライン描画修正やmacOSキーチェーンの一時エラー対応など、日常的な使用感を改善する修正が多く含まれています。