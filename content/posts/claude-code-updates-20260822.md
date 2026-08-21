---
title: "【Claude Code】v2.1.239 リリースノートまとめ"
date: 2026-08-22T08:01:56+09:00
draft: true
tags: ["claude-code", "bedrock", "vertex", "foundry", "anthropic", "mcp", "alpine", "musl", "python", "chrome", "windows", "vscode", "remote-control"]
categories: ["Claude Code Updates"]
summary: "v2.1.239 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.239 リリースノート

## はじめに

Claude Code v2.1.239 がリリースされました。本バージョンでは、コスト推定機能のデータレジデンシープレミアム対応、Python Anthropic SDK の 0.x から 1.x へのマイグレーション支援機能の追加、複数のクラウドプラットフォームでのフルスクリーンレンダラー初期提供、および 30 件以上のバグ修正と改善が含まれています。特に Bedrock のストリーミング機能、プロキシ環境下での起動問題、MCP サーバーの再接続処理など、安定性に関わる重要な修正が多数行われています。

## 注目アップデート深掘り

### コスト推定機能のデータレジデンシープレミアム対応

`/cost` コマンド、ステータスライン、`--max-budget-usd` フラグによるコスト推定が、データレジデンシーワークスペース向けの 1.1 倍の US 専用推論プレミアムを含むようになりました。これにより、データレジデンシー要件のある環境での正確なコスト予測が可能になります。

また、月次利用上限に達した際の使用制限メッセージに、セッションまたは週次制限のリセット日時が表示されるようになり、利用再開のタイミングが把握しやすくなりました。

### Python Anthropic SDK 0.x から 1.x へのマイグレーション支援

新しく `/claude-api upgrade` コマンドが追加され、Python プロジェクトで使用している `anthropic` ライブラリを 0.x から 1.x へ移行できるようになりました。スキルの Python リファレンスも 1.x 向けに更新され、タイムアウト処理が `httpx.Timeout` ではなく `anthropic.Timeout` を使用する形式に対応しています。

### Bedrock ストリーミングのプロキシ対応修正

Bedrock ストリーミング使用時に、レスポンスの Content-Type ヘッダーを削除するプロキシ環境下で、API 呼び出しが非ストリーミングで再実行され請求が 2 倍になる問題が修正されました。この修正により、プロキシ環境下でも正常にストリーミングが機能し、不要な課金が防止されます。

## 実用的な活用ポイント

本バージョンでは、プロキシ環境下での動作安定性が大幅に向上しています。Bedrock 使用時に SSO プロファイルと `awsAuthRefresh` を併用している場合の起動ハング問題が修正され、認証情報の事前チェックが `HTTPS_PROXY` を尊重するようになりました。

クラウドセッションでは、claude.ai から同期されたプラグインが `name@synced` として表示され、`claude plugin enable/disable <name>@synced` で管理できるようになり、同名のローカルインストールプラグインを上書きしなくなりました。

Alpine/musl ビルド環境では、ネイティブの画像ペースト、クリップボード、オーディオキャプチャのアドオンが読み込まれるようになり、軽量コンテナ環境での完全な機能利用が可能になりました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Improvement | コスト推定のデータレジデンシープレミアム対応 | `/cost`、ステータスライン、`--max-budget-usd` が 1.1 倍の US 専用推論プレミアムを含むように |
| Feature | フルスクリーンレンダラーの初期提供拡大 | Bedrock、Vertex、Foundry などで初回起動時にフルスクリーンで開始 |
| Feature | Python Anthropic SDK マイグレーション機能 | `/claude-api upgrade` コマンドを追加し、0.x から 1.x への移行を支援 |
| Improvement | クラウドセッションのプラグイン同期改善 | claude.ai から同期されたプラグインを `name@synced` として表示・管理 |
| Improvement | Alpine/musl ビルド対応 | ネイティブ画像ペースト、クリップボード、オーディオキャプチャが musl 環境で動作 |
| Improvement | 使用制限メッセージの改善 | 月次上限到達時にセッションまたは週次制限のリセット日時を表示 |
| Fix | Bedrock ストリーミングのプロキシ対応 | Content-Type ヘッダーを削除するプロキシ環境下での重複課金問題を修正 |
| Fix | Bedrock 起動ハング問題 | SSO プロファイルと `awsAuthRefresh` 使用時の HTTPS プロキシ環境下での起動ハングを修正 |
| Fix | 存在しないディレクトリからの起動クラッシュ | 削除されたディレクトリから起動時のクラッシュダンプを修正し、明確なメッセージを表示 |
| Fix | JetBrains IDE ターミナルの遅延 | Edit および Write 呼び出し時の約 5 秒の遅延を修正 |
| Fix | Esc キー押下時の競合状態 | プロンプトがキューイングされた状態での Esc キー押下時の早期終了を修正 |
| Fix | WebFetch のメモリリーク | 期限切れページコンテンツが 15 分ではなくセッション全体で保持される問題を修正 |
| Fix | クラウドセッションのプランモード | アイドル状態のワーカー再起動後にプランモードから抜ける問題を修正 |
| Fix | MCP elicitation フォームの表示 | フルスクリーンモードでターミナルより高いフォームが切り取られる問題を修正 |
| Fix | リモート MCP サーバーの再接続 | 一時的な 5xx エラー後に失敗状態のままになる問題を修正 |
| Fix | カスタムセッションタイトルの消失 | 約 64 KB を超える会話後にリネームしたタイトルが `/resume` から消失する問題を修正 |
| Fix | セッション選択の曖昧性 | `claude -c`/resume が `_`、`-`、`.` のみが異なるパスのセッションを誤って選択する問題を修正 |
| Fix | `/resume` の変更日時表示 | ファイルのタッチや再オープンだけで「最近変更」と表示される問題を修正 |
| Fix | 削除されたディレクトリへの cd 指示 | all-projects モードで削除された worktree への cd を指示する問題を修正 |
| Fix | dark-ansi テーマの表示 | フルスクリーンモードでツール結果のテキストが背景と同色になる問題を修正 |
| Fix | フルスクリーンレンダラープロンプト | 応答できない状況での繰り返し表示を 3 回の起動後に停止 |
| Fix | `.worktreeinclude` パターンマッチング | `**/` で始まるパターンが gitignore ディレクトリ内で何もマッチしない問題を修正 |
| Fix | UTF-8 BOM 付きファイルの認識 | BOM で始まる `.md` ファイルのエージェント、スキル、コマンドが無視される問題を修正 |
| Fix | `/insights` の出力 | 一部のモデルで literal `<message>` タグがエコーされる問題を修正 |
| Fix | marketplace `metadata.pluginRoot` | 設定が効果を持たない問題を修正 |
| Fix | ブラウザターミナルでのマウス移動 | マウスレポートが分割書き込みされた際にテキストが挿入される問題を修正 |
| Fix | カスタムテーマの status バッジ色 | effort/ultracode バッジの色オーバーライドが無視される問題を修正 |
| Fix | OpenTelemetry トレースの断片化 | `PreToolUse` フックで遅延されたツール実行が元のトレースで継続されるように修正 |
| Fix | vim モードの Escape キー | agent view で Escape キーがテキストをクリアする問題を修正 |
| Fix | `selection:copy` キーバインディング | Shift+矢印キーで拡張された選択範囲がドロップされる問題を修正 |
| Fix | `/voice` 起動ヒント | `voice.enabled` 設定で有効化後も表示される問題を修正 |
| Fix | shell-mode Tab 補完 | `./script` パスから `./` が削除される問題を修正 |
| Fix | フルスクリーンモードのクリック誤反応 | フォーカスを戻すためのクリックで許可プロンプトやボタンが押される問題を修正 |
| Fix | スラッシュコマンドパネルの表示位置 | フルスクリーンモードで最新メッセージを覆う問題を修正 |
| Fix | `/workflows` ダイアログのオーバーフロー | Claude の応答中に開いた際にヘッダーが画面外に出る問題を修正 |
| Fix | Linux サンドボックスの git 設定 | 存在しない `.git/config.worktree` が読み取り不可になる問題を修正 |
| Fix | 削除されたディレクトリでの hook 実行 | posix_spawn ENOENT エラーを修正し、プロジェクトルートまたはホームから実行 |
| Fix | `claudeMdExcludes` のシンボリックリンク | シンボリックリンクされた `.claude/rules` が除外されない問題を修正 |
| Fix | Remote Control へのタイトル同期 | 2 つのプロセスが同じバックグラウンドジョブ状態を共有する際の暴走を修正 |
| Fix | `/` で始まるセッションタイトル | `SendMessage` でアドレス不可で `ListAgents` で "(untitled)" と表示される問題を修正 |
| Fix | テキスト削除時のプレースホルダー | Ctrl+W 等でカーソルがプレースホルダー内にある場合の破損を修正 |
| Fix | マスク入力のテキスト保持 | パスワードフィールドのテキストが Ctrl+Y で貼り付け可能な問題を修正 |
| Fix | 検索ボックスの Ctrl+Backspace | 単語削除ではなく 1 文字削除される問題を修正 |
| Fix | 組織ポリシーチェック拒否時の再送信 | 拒否表示前にリクエストが再送信される問題を修正 |
| Improvement | コンパクション後のリマインダー改善 | スキルの元の引数が新しいリクエストとして再実行されないように |
| Improvement | 長いファイルパスの表示 | ツール使用行で中央切り詰めし 1 行に収まるように |
| Improvement | リモートセッションのキープアライブ | 長い `SessionStart` または `Setup` hook 実行中も送信継続 |
| Improvement | `/goal` の定期チェックイン間隔 | 30 分、1 時間、その後 2 時間ごとにバックオフ |
| Improvement | `/goal` の再開時のゴール復元 | `claude --resume` でセッションを再開した際にアクティブなゴールも復元 |
| Improvement | `ListAgents` の自己名表示 | セッションが他のピアから使用される名前を返すように |
| Improvement | `ListAgents` のチームメイト表示 | ライブチームメイトもリストに含めるように |
| Improvement | `keybindingFlavor: "readline"` の拡張 | Alt+F、Ctrl/Option+→、Alt+D などが Bash の単語キーと一致 |
| Improvement | 持続的リトライモードのエラー処理 | 組織支出上限やクレジット不足エラーで即座に失敗 |
| Improvement | Claude in Chrome の `/clear` | セッションの Chrome タブグループを閉じるように |
| Improvement | リモートセッションの画像アップロード | モバイルからアップロードされた画像に保存ファイルパスを含める |
| Improvement | Claude Code on the web のプロキシ対応 | Bash 等からの非 API anthropic.com ホストへのリクエストがプロキシを経由 |
| Improvement | Remote Control のメッセージ改善 | アカウントで有効化されていない場合の明確なメッセージと `claude doctor` 文言 |
| Feature | Windows でのクロスセッションメッセージング | `SendMessage` と `ListAgents` が Windows でも利用可能に |
| Improvement | [VSCode] usage-limit バナーのレイアウト | "View usage" リンクが警告テキストとインライン配置に |

## まとめ

v2.1.239 は、コスト推定の精度向上、クラウドプラットフォーム対応の拡大、Python SDK マイグレーション支援など、新機能と改善を含むメンテナンスリリースです。特に、プロキシ環境下での Bedrock 使用時の安定性向上、MCP サーバーの再接続処理改善、エディタ統合時の応答性改善など、エンタープライズ環境での利用に関わる重要な修正が多数含まれています。30 件を超える細かなバグ修正により、全体的なユーザー体験と信頼性が向上しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)