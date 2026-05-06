---
title: "【Claude Code】v2.1.128 リリースノートまとめ"
date: 2026-05-06T08:01:32+09:00
draft: false
tags: ["claude-code", "mcp", "plugins", "git", "worktree", "otel", "opentelemetry", "observability"]
categories: ["Claude Code Updates"]
summary: "v2.1.128 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260506/header.png)

# Claude Code v2.1.128 リリース解説

## はじめに

Claude Code **v2.1.128** がリリースされました（公開: 2026-05-05 08:01 JST）。本バージョンでは、**MCP の再接続時メッセージ抑制と `/mcp` UI 改善**、**`--plugin-dir` の `.zip` 受け入れ**、**`EnterWorktree` の起点ブランチ修正（未プッシュコミット保護）**、**サブプロセスへの `OTEL_*` 継承停止**、**並列シェルツール呼び出しの独立化**、**1M コンテキストモデルでの誤った "Prompt is too long" 修正**、**サブエージェントの prompt cache 修正（cache_creation 約 3 倍削減）** など、observability・MCP 連携・Git 作業の信頼性を底上げする変更が中心です。

参考: [Claude Code Releases v2.1.128](https://github.com/anthropics/claude-code/releases/tag/v2.1.128)

本記事では、特に運用への影響が大きい変更を深掘りし、活用ポイントを解説します。

## 注目アップデート深掘り

### MCP の再接続フロー刷新（`/mcp` UI 改善＋ツール再告知の要約化）

MCP（Model Context Protocol）まわりで運用に直結する3つの変更が入りました。

**1) `/mcp` がツール数を表示し、0ツールで接続したサーバーをフラグ表示**

`/mcp` の出力に各サーバーが提供するツール数が並ぶようになり、**接続したのにツールを公開していないサーバー** が即座に分かるようになりました。`mcp.json` の指定ミスや、認証/初期化失敗で空の状態で接続だけ立ち上がるケースを目視で発見しやすくなります。

**2) 再接続時のツールリスト氾濫を抑制**

従来は MCP サーバーが再接続するたびに、サーバーが公開する全ツール名が会話履歴に書き戻され、コンテキストを浪費していました。本リリースでは、再告知時のツールリストは**サーバープレフィックス単位で要約**されます。Wi-Fi の切断や MCP サーバーの再起動で会話のトークン消費が膨らんでいた環境では、明確に効きます。

**3) `workspace` が予約サーバー名に**

`workspace` という名前は内部用途で予約され、既存の `mcp.json` などに同名サーバーがあれば**警告付きでスキップ**されます。リネームが必要です。

### `EnterWorktree` の起点を `origin/<default>` から local HEAD に修正

公開リリースノートの表現は次の通りです:

> `EnterWorktree` now creates the new branch from local HEAD as documented, instead of `origin/<default-branch>` — unpushed commits are no longer dropped

これは worktree 切り替え時にコミット履歴が消えるバグ、ではなく、**`EnterWorktree` が新しいブランチを切る起点**の問題です。従来は内部的に `origin/main`（デフォルトブランチのリモート版）から派生していたため、ローカル HEAD に積んだ未プッシュのコミットが新 worktree の系譜に含まれませんでした。`/diff` などで「あれ、さっきのコミットが消えた？」と見える典型ケースがこれです。

本修正により、`EnterWorktree` はドキュメント通り**local HEAD を起点**に新ブランチを作成するようになり、未プッシュコミットも引き継がれます。サブエージェント・スキル経由で worktree を立ち上げる場面（cmux 統合、長時間タスクの分離実行など）で安全に使えるようになります。

### サブプロセスが `OTEL_*` 環境変数を継承しなくなった

Claude Code 自身が OTLP エンドポイントを叩くために設定した `OTEL_*` 系の環境変数を、**Bash ツール・hooks・MCP・LSP** が起動するサブプロセスがそのまま継承していました。その結果、Bash 経由で動かした OTel 計装済みアプリ（自前のサービス、`opentelemetry-instrumented` な npm/pip パッケージ等）が、知らずに **CLI の OTLP エンドポイントへトレースを送ってしまう** という汚染が起きていました。

本リリースで `OTEL_*` の継承が止まり、サブプロセスは自分の設定（または未設定）で動きます。CLI 利用と社内サービスの計測パイプラインを分離している環境では、誤ったトレース流入が止まり、サンプリング・コスト・ノイズの観点で改善します。

### 並列シェルツール呼び出しが互いを巻き込まない

これまでは、Claude Code が並列で投げた読み取り専用シェル（`grep` / `git diff` / `ls` 等）のうち**一つでも失敗すると、兄弟の呼び出しがキャンセルされる**問題がありました。本リリースでこの挙動が修正され、失敗した呼び出しのみがエラー扱いになります。複数ファイル・複数ディレクトリを同時に grep するような探索系タスクのスループットが、地味ながら確実に上がります。

### 1M コンテキストの "Prompt is too long" 誤検知修正

1M コンテキストモデルでも、autocompact のしきい値が小さい設定の場合、**実際の API 制限に達する前にクライアント側が "Prompt is too long" でブロック**してしまうバグが修正されました。長尺セッションを 1M 系列で運用している場合に効きます。

### サブエージェントの prompt cache が効くように

サブエージェントの進捗サマリ生成で **prompt cache を取りこぼしていた** 問題が修正され、`cache_creation` が約 3 倍削減されます。さらに、サブエージェントのトランスクリプトが静止している間にサマリが繰り返し発火していたバグも修正され、idle なサブエージェントのトークン上振れに上限が付きました。長時間走るオーケストレーション系ワークフロー（複数サブエージェントの並列実行）でコストが膨らんでいた環境で効果が大きい改善です。

## 実用的な活用ポイント

**MCP 環境の点検**: 既存の `mcp.json` を見直してください。1) `workspace` という名前のサーバーがあれば**リネーム必須**（警告でスキップされる）。2) `/mcp` で各サーバーのツール数を確認し、0 のままになっているサーバーがないか点検（多くは認証/初期化エラー）。3) 再接続のノイズが減るので、ネットワーク不安定な環境（VPN・テザリング）でのセッションコストが下がります。

**worktree ベースのワークフロー**: 自前のスキル・サブエージェントから worktree を生成している場合、未プッシュコミットを起点に作業させても**意図したコミット系譜**になります。`origin/main` 起点を前提とした自前の前処理（pull/rebase）があれば再点検すると安全です。

**OTel パイプラインの整理**: `OTEL_EXPORTER_OTLP_ENDPOINT` を Claude Code 用に設定していたチームは、これまで Bash 経由のテスト/ビルドで起動した子プロセスがその設定を引き継いでサンプル数が膨れていた可能性があります。本リリース以降は再現しなくなるため、過去のメトリクスとは断絶します。ダッシュボードのベースラインを再取得しておくと、後で「急に減った」と誤解せずに済みます。

**1M コンテキスト運用**: autocompact しきい値を絞っていて "Prompt is too long" に遭遇していた環境は、今回の修正で緩和される可能性が高いです。回避用に下げていた `--max-context` 系の運用設定があれば見直し候補。

**サブエージェント多用ワークフロー**: 進捗サマリの cache miss と idle 中の繰り返し発火が修正されたため、`subagent` を多段で走らせる構成のトークンコストが**観測可能な水準で下がる**はずです。コスト計測している場合はビフォーアフターを残しておくと、効果説明に使えます。

## 全変更点一覧

| カテゴリ | 内容 |
|---------|------|
| Improvement | `/mcp` が接続済みサーバーのツール数を表示。0ツールで繋がったサーバーをフラグ表示 |
| Improvement | MCP 再接続時のツール名リスト氾濫を抑制（サーバープレフィックスで要約） |
| Change | MCP: `workspace` が予約サーバー名に（同名サーバーは警告付きでスキップ） |
| Improvement | `--plugin-dir` がディレクトリに加え `.zip` プラグインアーカイブを受け入れ |
| Improvement | `--channels` がコンソール（API key）認証で動作。`channelsEnabled: true` の managed setting が必要 |
| Improvement | `/model` ピッカー: 重複した Opus 4.7 を統合し、現行 Opus を「Opus」と表示 |
| Improvement | サブプロセス（Bash/hooks/MCP/LSP）が `OTEL_*` を継承しなくなる |
| Improvement | SDK ホストへ Bash 権限プロンプトの `localSettings` 提案を永続化（"Always allow" が `.claude/settings.local.json` に書かれる） |
| Improvement | Auto モード: 分類器がアクションを評価できないときのエラーに retry / `/compact` / `--debug` のヒントを追加 |
| Improvement | `/color`（引数なし）でランダムな session color に |
| Fix | `EnterWorktree` が `origin/<default-branch>` ではなく local HEAD から新ブランチを作成。未プッシュコミットを保護 |
| Fix | 並列シェルツール呼び出し: 1 件の失敗が兄弟をキャンセルしない |
| Fix | 1M コンテキストモデルで autocompact ウィンドウが小さい場合の誤った "Prompt is too long" を解消 |
| Fix | サブエージェントの進捗サマリで prompt cache が効くように（`cache_creation` 約 3 倍削減） |
| Fix | サブエージェントのトランスクリプトが静止中にサマリが繰り返し発火するバグを修正 |
| Fix | MCP stdio サーバー: `CLAUDE_CODE_SHELL_PREFIX` 設定時に空白/メタ文字を含む引数が壊れる問題 |
| Fix | MCP ツール結果: structured content と content blocks 両方を返したサーバーで画像が落ちる問題 |
| Fix | 大きい入力（>10MB）を `claude -p` に stdin パイプした際のクラッシュループ |
| Fix | `/plugin` Components パネルで `--plugin-dir` ロードのプラグインに「Marketplace 'inline' not found」が出る問題 |
| Fix | `/plugin update` が npm 由来プラグインの新バージョンを検出しない問題 |
| Fix | `installed_plugins.json` の削除済みキャッシュディレクトリを指す古いエントリが PATH を汚す問題 |
| Fix | drag-and-drop 画像アップロードが「Pasting text…」でハングする問題（読み取り失敗時） |
| Fix | Remote Control: レート制限時に空の "Opening your options…" 表示。実用的な upsell に修正 |
| Fix | フォーカスモードで新プロンプト送信時に直前応答が一瞬暗くなる問題 |
| Fix | `/exit` 時に Kitty 等で OSC 9 を通知扱いする端末に「4;0;」が漏れる問題 |
| Fix | フルスクリーン時の長い URL が折り返し各行ごとにクリック可能でない問題 |
| Fix | リスト項目内の fenced code block が clipboard コピー時に先頭スペースを抱える問題 |
| Fix | `/config` 内の Tab ナビゲーションでフォーカスが取り残される問題（Tab ヘッダーが focus を保持） |
| Fix | OSC 8 ハイパーリンク非対応端末で markdown link label が消える（`label (url)` 表示にフォールバック） |
| Fix | banner の「with X effort」が effort 非対応モデルでも出る問題 |
| Fix | `/fast` が 3rd-party プロバイダで無関係なスキルにファジーマッチする問題（"not available" を表示） |
| Fix | Bedrock 既定モデルが `global.*` に解決される問題（リージョン適合 prefix に修正） |
| Fix | vim モード NORMAL の `Space` がカーソルを右に動かす標準挙動に |
| Fix | 端末プログレスインジケータ（OSC 9;4）がツール呼び出し間でちらつく問題 |
| Fix | `/rename`（引数なし）が compact 境界で終わる resume セッションで失敗する問題 |
| Fix | `--resume`/`--continue` 後に古い「remote-control is active」ステータス行が残る問題 |
| Fix | Headless `--output-format stream-json` の `init.plugin_errors` に `--plugin-dir` ロード失敗を含める |

## まとめ

v2.1.128 は派手な新機能というより、**MCP・OTel・worktree・サブエージェント** といった土台の信頼性とトークン効率を引き上げる地味で効くリリースです。特にサブエージェントの prompt cache 修正（`cache_creation` 約 3 倍削減）と OTEL 継承停止は、コストと観測の両面でこれまで黙って削られていた部分を取り戻します。MCP の `workspace` 予約は破壊的変更なので、アップデート前に既存設定だけ確認しておきましょう。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)