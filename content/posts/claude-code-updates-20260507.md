---
title: "【Claude Code】v2.1.132・v2.1.131・v2.1.129 リリースノートまとめ"
date: 2026-05-07T08:01:27+09:00
draft: false
tags: ["claude-code", "plugin", "manifest", "vscode", "windows", "ssh", "terminal", "homebrew", "winget", "otel", "mantle", "oauth"]
categories: ["Claude Code Updates"]
summary: "v2.1.132・v2.1.131・v2.1.129 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260507/header.png)

# Claude Code v2.1.129〜v2.1.132 リリース情報

## はじめに

2026年5月6日（JSTで5月7日早朝）、Claude Code の3バージョン（v2.1.129、v2.1.131、v2.1.132）が立て続けにリリースされました。新機能の追加よりも、安定性向上と回帰修正が大半を占める「地固め」リリースです。

v2.1.129 は `--plugin-url` フラグ追加・パッケージマネージャー連携・OAuth/キャッシュ周りの修正を中心とした幅広い改善、v2.1.131 は Windows 版 VS Code 拡張の起動回帰と Mantle エンドポイント認証の修正に絞った緊急パッチ、v2.1.132 はセッション関連環境変数の追加に加え、グレースフル終了・Unicode 入力・ペースト周りの細かなターミナルバグを多数修正した内容となっています。

## 注目アップデート深掘り

### `--plugin-url` フラグ追加とプラグインマニフェストの仕様変更（v2.1.129）

v2.1.129 で追加された `--plugin-url <url>` フラグは、URL から `.zip` 形式のプラグインアーカイブを取得し、現在のセッションだけで利用できる仕組みです。プラグインの試験導入や、社内 GitHub Releases などに置いた配布物の検証で、グローバル設定を汚さずに動作確認したいケースに直結します。

同時にプラグインマニフェストの仕様も整理されました。`themes` と `monitors` は `"experimental": { ... }` の下で宣言する形に変更され、トップレベル宣言は引き続き動作するものの `claude plugin validate` で警告が出るようになります。実験的機能の境界をマニフェスト上で明示することで、安定 API との切り分けが明確になり、将来の破壊的変更時の影響範囲を把握しやすくなる狙いです。

> **Note:** プラグインは Claude Code の機能を拡張するサードパーティ製モジュールで、`themes`（カラースキーム）や `monitors`（状態監視フック）といった実験的な拡張ポイントを提供しています。

### Windows 版 VS Code 拡張の起動修正と Mantle 認証修正（v2.1.131）

v2.1.131 は2件のみの緊急修正リリースです。1件目は VS Code 拡張機能が Windows でアクティブ化に失敗する問題で、原因は bundled SDK 内 `createRequire` ポリフィルにビルド時のパスがハードコードされていたことでした。Windows のパス区切り（バックスラッシュ）と Unix 形式の差異が解決されず、拡張機能の初期化段階でモジュール解決に失敗していたかたちです。

2件目は Mantle エンドポイントへの認証が `x-api-key` ヘッダー欠落で失敗していた問題の修正です。サードパーティ経由で Claude Code を運用しているチームでは、この2点を含む v2.1.131 への更新が必須となります。

### セッション系環境変数の追加とグレースフル終了の修正（v2.1.132）

v2.1.132 では、Bash ツールが起動するサブプロセスに対して、フックに渡される `session_id` と同値の `CLAUDE_CODE_SESSION_ID` 環境変数が渡されるようになりました。フック内のスクリプトと Bash ツール側で同じセッション ID を参照できるため、セッション単位のロック・ログ振り分け・キャッシュキーといった処理が組み立てやすくなります。

加えて `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` を指定すると、フルスクリーンの代替画面レンダラーをオプトアウトし、ターミナルのスクロールバックに会話を残せるようになりました。スクリーンキャプチャやログ取りでスクロールバック前提のワークフローを組んでいる人向けの設定です。

ターミナル安定性の面では、IDE の停止ボタンや `kill -INT` などの外部 SIGINT でグレースフル終了が走らずターミナルモードが復元されない問題が修正されたほか、ネイティブビルドで SSH 切断時に未捕捉例外が出ていた問題、`--resume` が絵文字混入で `no low surrogate in string` エラーになる問題なども解消しています。

## 実用的な活用ポイント

### パッケージマネージャー経由での自動更新（v2.1.129）

`CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` を設定しておくと、Homebrew または WinGet で導入した Claude Code がバックグラウンドでアップグレードコマンドを実行し、再起動を促すプロンプトを出すようになりました。デフォルトでは無効なオプトイン挙動なので、自動更新を許容する個人環境と、固定バージョンで運用したい CI/共有環境を明確に分けられます。

`/v1/models` を使ったゲートウェイ側のモデルディスカバリーも `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` でのオプトインに戻されました（v2.1.126〜v2.1.128 では自動有効）。Bedrock や Vertex、`ANTHROPIC_BASE_URL` 経由のゲートウェイを使う環境では、意図しない一覧取得が走らなくなる点を確認しておくとよいでしょう。

### Ctrl+R 履歴検索とターミナル互換性

Ctrl+R の履歴検索は、v2.1.124 以前と同じく「全プロジェクトの履歴を横断検索」する挙動に戻り、現在のプロジェクト／セッションに絞り込みたい場合は Ctrl+S で切り替える形に変更されました。プロジェクトをまたいで同じコマンドを呼び出す機会が多い SRE・インフラ系の運用で恩恵が大きい変更です。

ターミナル互換性では、Emacs の `eat` のように同期出力の自動検出に乗らないターミナル向けに `CLAUDE_CODE_FORCE_SYNC_OUTPUT=1` の上書きが追加されました。あわせて v2.1.132 では Indic 言語の連結文字や ZWJ 絵文字が行をまたいだときのカーソル位置ずれ、NFD 分解された合字が vim 操作で壊れる問題、`/` で始まるテキストのペーストが暗黙に飲まれる問題などが修正されており、日本語・絵文字・各種スクリプトを混在して使う環境での安定度が一段上がっています。

### MCP / OTel / OAuth 周辺の地味だが効く修正

v2.1.129 では、stdio MCP サーバーが非プロトコルデータを stdout に書いた際にメモリが 10GB 以上まで膨らむバグが修正されました。長時間セッションを張る MCP サーバーを運用している場合は更新必須の項目です。`tools/list` に失敗する MCP サーバーは1回リトライした上で `/mcp` 上に「connected · tools fetch failed」と表示されるようになり、無言で 0 ツールになる問題も解消しています。

OTel メトリクス `claude_code.pull_request.count` が、シェル経由だけでなく MCP ツール経由で作成された PR/MR もカウントするようになった点も、計測基盤側で集計の連続性を確認しておきたい変更です。OAuth まわりではスリープ復帰直後のリフレッシュ競合で全セッションがログアウトする問題、1時間 TTL のプロンプトキャッシュが暗黙に5分に降格していた問題なども修正されています。

## 全変更点一覧

| バージョン | カテゴリ | 変更内容 | 概要 |
|-----------|---------|---------|------|
| v2.1.132 | Feature | `CLAUDE_CODE_SESSION_ID` 追加 | Bash ツールのサブプロセスにフック同値の session_id を環境変数で渡す |
| v2.1.132 | Feature | 代替画面オプトアウト | `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` でスクロールバック維持 |
| v2.1.132 | Fix | グレースフル終了 | 外部 SIGINT 時のターミナルモード復元と `--resume` ヒント表示 |
| v2.1.132 | Fix | SSH 切断時例外 | ネイティブビルドで SSH 断・ターミナルクローズ時の未捕捉例外を修正 |
| v2.1.132 | Fix | `--resume` 復元 | 絵文字断片による `no low surrogate in string` エラーを修正 |
| v2.1.132 | Fix | Unicode 編集 | Indic 連結・ZWJ 絵文字でのカーソル位置ずれ／NFD 文字の vim 操作破損を修正 |
| v2.1.132 | Fix | ペースト処理 | `/` 始まりテキストの欠落・エスケープ列混入・MCP/IDE 周辺多数を修正 |
| v2.1.131 | Fix | Windows 起動問題 | VS Code 拡張で `createRequire` ポリフィルのビルドパス問題を解消 |
| v2.1.131 | Fix | Mantle 認証 | Mantle エンドポイントへの `x-api-key` ヘッダー欠落を修正 |
| v2.1.129 | Feature | `--plugin-url` フラグ | URL の `.zip` プラグインを現セッション限定で読み込み |
| v2.1.129 | Feature | パッケージマネージャー自動更新 | `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` で Homebrew/WinGet 更新を自動化 |
| v2.1.129 | Feature | プラグインマニフェスト整理 | `themes`/`monitors` を `experimental` 配下で宣言、トップレベルは警告 |
| v2.1.129 | Feature | ゲートウェイモデル discovery | `/v1/models` 探索を `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` でオプトイン化 |
| v2.1.129 | Improvement | Ctrl+R 履歴検索 | デフォルトを全プロジェクト横断に戻し、Ctrl+S で絞り込み |
| v2.1.129 | Improvement | ターミナル互換性 | `CLAUDE_CODE_FORCE_SYNC_OUTPUT=1` で Emacs eat 等の同期出力を強制 |
| v2.1.129 | Improvement | OTel 拡張 | `claude_code.pull_request.count` が MCP 経由 PR/MR も計測 |
| v2.1.129 | Fix | MCP メモリリーク | stdio MCP サーバーの非プロトコル stdout でメモリ 10GB+ になる問題を修正 |
| v2.1.129 | Fix | OAuth リフレッシュ競合 | スリープ復帰時の競合で全セッションがログアウトする問題を修正 |
| v2.1.129 | Fix | プロンプトキャッシュ TTL | 1時間 TTL が暗黙に5分へ降格していた問題を修正 |

## まとめ

3バージョンを通して見ると、目玉機能は `--plugin-url` とパッケージマネージャー自動更新の2つに絞られ、残りは仕様整理（マニフェストの `experimental` 化、モデル discovery のオプトイン化）と回帰・安定性修正が中心です。とりわけ Windows VS Code 拡張の起動不能、stdio MCP のメモリリーク、SSH 切断時の例外、外部 SIGINT でのモード復元失敗あたりは運用に直接刺さる修正なので、v2.1.128 以前で停まっている環境はまとめて v2.1.132 まで上げておくと安全です。

国際化文字や絵文字を含む編集・ペースト周りの改善も積み重なっており、日本語環境やマルチバイトを多用するチームでも違和感が減っています。プラグイン・MCP・OTel まわりはエンタープライズ寄りの変更が多いので、組織導入で運用している場合は環境変数のデフォルト変更（モデル discovery のオプトイン化など）を中心にチェックしておくとよいでしょう。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code v2.1.129 リリースノート](https://github.com/anthropics/claude-code/releases/tag/v2.1.129)
- [Claude Code v2.1.131 リリースノート](https://github.com/anthropics/claude-code/releases/tag/v2.1.131)
- [Claude Code v2.1.132 リリースノート](https://github.com/anthropics/claude-code/releases/tag/v2.1.132)
