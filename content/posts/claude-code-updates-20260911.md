---
title: "【Claude Code】v2.1.268 リリースノートまとめ"
date: 2026-09-11T08:03:26+09:00
draft: true
tags: ["claude-code", "gateway", "self-hosted-runner", "webfetch", "mcp", "oauth", "vscode", "slack", "code-review"]
categories: ["Claude Code Updates"]
summary: "v2.1.268 のClaude Codeリリースノートまとめ"
---

## はじめに

Claude Code v2.1.268 がリリースされました。このバージョンでは、Claude apps ゲートウェイの価格管理機能とアクセス制御の強化、セッション状態管理オプションの追加、WebFetch のタイムアウト設定、そして CPU 使用率の最適化が行われました。また、サードパーティ Anthropic 互換エンドポイントでの不具合修正、シンボリックリンクディレクトリの権限制御の改善、VSCode 拡張と Claude in Slack の機能改善など、多数のバグ修正と改善が含まれています。

## 注目アップデート深掘り

### Claude apps ゲートウェイの価格管理とアクセス制御の強化

`gateway.yaml` に `pricing:` を設定することで、サインイン済みの Claude Code クライアントが管理設定を通じて同じレートを受け取り、`/cost` とテレメトリーが使用量メーターと一致するようになりました。これにより、組織全体でのコスト管理の透明性が向上します。

同時に、セキュリティ面でも改善が加えられています。`access_control.allow_cidrs` が空の場合、ゲートウェイ起動時に警告が表示されるようになり、初めてパブリックアドレスからリクエストが到着した際にも一度だけ警告が表示されます。さらに、新たに追加された `gatewayInternalNetworks` 管理設定により、管理者は組織自身のパブリック IPv4 ブロック上での `/login` を許可できるようになりました。これらの機能により、セルフホスト環境でのアクセス制御がより細やかに行えるようになっています。

### サードパーティ Anthropic 互換エンドポイントの互換性修正

v2.1.265 以降、サードパーティの Anthropic 互換エンドポイント（`ANTHROPIC_BASE_URL`）を使用する際に、すべてのターンが HTTP 400 で失敗する不具合が修正されました。原因は Artifact ツールの入力スキーマに含まれる正規表現を、これらのエンドポイントが拒否していたことでした。この修正により、カスタムエンドポイントを使用する環境でも安定した動作が保証されます。

### WebFetch のタイムアウト設定と CPU 使用率の最適化

WebFetch が応答を開き続けたままサーバーが完了しない場合に無限にハングする問題が修正され、フェッチは 300 秒後に失敗するようになりました。タイムアウト値は `CLAUDE_CODE_WEBFETCH_DEADLINE_MS` 環境変数で上書き可能（0 に設定すると無効化）です。

また、アイドル状態のセッションでのビジーループが CPU コアを占有しなくなり、セッション要約中の頻繁なターミナルフォーカスレポートによる CPU 高使用率の問題も解消されました。これらの改善により、長時間実行されるセッションでのリソース効率が大幅に向上しています。

## 実用的な活用ポイント

### セッション状態の管理

新たに追加された `claude self-hosted-runner --remove-session-state` オプション（デフォルトはオフ）を使用すると、セッション終了時に `<base-dir>/_sessions/` 配下の各セッションごとのディレクトリを削除できます。長期運用時のディスク使用量管理に有効です。

### CLI の JSON 出力拡張

`claude auth status --json` の出力に `configDirectory` が追加され、`claude plugin install`、`uninstall`、`update`、`enable`、`disable` コマンドに `--json` オプションが追加されました。また、`claude plugin list --json` の各行に `errorDetails` と `noteDetails` が含まれるようになり、プラグイン管理の自動化やスクリプト化が容易になりました。

### シンボリックリンクディレクトリの権限制御

macOS の `/etc`、`/tmp`、`/var` や Linux の `/bin` などのシンボリックリンクディレクトリに対する deny および ask パーミッションルールが、実際のパス位置で指定された場合にも適用されるようになり、Bash コマンドがシンボリックリンクパスで書かれた deny ルールを無視する問題も修正されました。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | Claude apps ゲートウェイの価格管理 | `gateway.yaml` の `pricing:` 設定により、サインイン済みクライアントが同じレートを受け取り、`/cost` とテレメトリーが一致 |
| Feature | ゲートウェイのアクセス制御警告 | `access_control.allow_cidrs` が空の場合の起動時警告と、パブリックアドレスからの初回リクエスト時の警告を追加 |
| Feature | gatewayInternalNetworks 管理設定 | 組織のパブリック IPv4 ブロック上での `/login` を管理者が許可可能に |
| Feature | セッション状態削除オプション | `claude self-hosted-runner --remove-session-state` でセッション終了時にディレクトリを削除 |
| Feature | configDirectory の JSON 出力 | `claude auth status --json` に `configDirectory` を追加 |
| Feature | プラグインコマンドの JSON 出力 | `claude plugin` コマンド群に `--json` オプションを追加、`errorDetails`/`noteDetails` を含む |
| Feature | アーティファクトのブラウザタブアイコン | 公開されたアーティファクトに、各ページに合わせて Claude が選んだアイコンを追加 |
| Fix | サードパーティエンドポイントの HTTP 400 | v2.1.265 以降、`ANTHROPIC_BASE_URL` でのターン失敗を修正（Artifact ツールの正規表現が原因） |
| Fix | WebFetch のハング | 応答を開き続けるサーバーで無限ハングする問題を修正、300 秒後にフェッチ失敗（`CLAUDE_CODE_WEBFETCH_DEADLINE_MS` で上書き可能） |
| Fix | リスポーンされたチームメイトの信頼問題 | 信頼していないフォルダの同名エージェントファイルからツールやシステムプロンプトを取得する問題を修正 |
| Fix | 高 CPU 使用率 | アイドルセッションのビジーループとターミナルフォーカスレポートによる CPU 占有を修正 |
| Fix | MCP ツール呼び出し後の空メッセージ | Claude が "your message came through empty" と返信する問題を修正 |
| Fix | シンボリックリンクディレクトリの権限ルール | macOS の `/etc`、`/tmp`、`/var` や Linux の `/bin` に対する deny/ask ルールが実際のパス位置で適用されない問題を修正 |
| Fix | Read/Edit deny ルールの適用漏れ | `env -C`、`eval` などの解析不可能なコマンドが同じ行にある場合に deny ルールが適用されない問題を修正 |
| Fix | プラグインとマーケットプレイスのシークレット露出 | git ソース URL からのトークンやパスワードがエラー表示される問題を修正 |
| Fix | MCP 設定のシークレット露出 | `/mcp` や `/plugin` サーバー詳細、`claude mcp list`/`get`、MCP ログインエラーで `${VAR}` プレースホルダーから解決されたシークレットが表示される問題を修正 |
| Fix | SDK セッションのプロンプトキャッシング | `excludeDynamicSections` 使用時に最初のメッセージが毎回再レンダリングされ、プロンプトキャッシングと拡張思考が途中で壊れる問題を修正 |
| Fix | モデルアクセス拒否のキャッシュ | キャッシュされたモデルアクセス拒否が古い場合に、再起動後や Desktop Code タブで制限メッセージが表示される問題を修正 |
| Fix | 実行中セッションのモデル切り替え | 別の Claude Code プロセスがモデルアクセスエントリを更新した際に、組織のデフォルトモデルに暗黙的に切り替わる問題を修正 |
| Fix | Fable モデルの 429 エラー表示 | Pro および Team プランで長コンテキスト 429 エラー時に、使用クレジット同意プロンプトではなく 1M コンテキストメッセージを表示 |
| Fix | ワークロード ID フェデレーション | プロファイル共有時に `401 … jti reused` で失敗する問題を修正（claude-code-action の設定） |
| Fix | MCP サーバー OAuth サインイン | ローカルコールバックポート範囲がバインドできない場合の "No available ports for OAuth redirect" エラーを修正 |
| Fix | /compact の会話要約 | `$` シーケンスを含むテキストが壊れる問題を修正 |
| Fix | /compact 後の会話再開 | 復元されたファイルノートが毎回同じ順序で読み込まれるように修正 |
| Fix | SDK のコンパクション前会話送信 | プロンプト提案、サイド質問、`/rename` がコンパクション前の会話を送信する問題を修正 |
| Fix | `@` ファイルと `/` コマンド提案 | 上矢印でプロンプトを呼び出して編集後に提案が表示されない問題を修正 |
| Fix | claude agents の戻る操作 | ← キーを自然なペースで押してエージェントリストに戻る際、1 秒以上停止するまで無視される問題を修正 |
| Fix | claude agents のセッション削除スタック | ワークツリーが削除できない場合にスタックする問題を修正、原因と次のステップを表示、git ワークツリーでは Ctrl+X で強制削除可能に |
| Fix | エージェントパネルの行拡張 | 改行を含むテキストでバックグラウンドエージェントとワークフロー行が複数行に拡張される問題を修正 |
| Fix | Claude in Slack の MCP ツール消失 | 組織管理設定で MCP 許可リストが設定されると Slack ツールが失われる問題を修正 |
| Fix | Claude in Chrome のホスト解析 | ナビゲーション URL にスキームはあるがホストが解析できない場合に "https" ホストの許可を求める問題を修正 |
| Fix | スピナーの折り返し | 現在のタスクラベルが長い場合に複数行に折り返す問題を修正、ラベルと "Next:" 行が 1 行に収まるように |
| Fix | /bug と /feedback のカーソル | ネイティブカーソル有効時に説明フィールドでカーソルが表示されない問題を修正 |
| Fix | Remote Control セッション名 | `claude remote-control` が提供するセッションが `ListAgents` でセッションタイトルではなく生成された名前を表示する問題を修正 |
| Fix | claude plugin validate のパス拒否 | ディレクトリ名が 2 つのドットで始まるプラグインパスを拒否する問題を修正（プラグインローダーは受け入れる） |
| Fix | プラグインのデフォルトモニター/SKILL.md | チェックできないデフォルトモニターファイルやルート SKILL.md を暗黙的にスキップする問題を修正 |
| Fix | WebFetch の localhost エラー | localhost などドットのないホスト名に対するエラーメッセージを改善、URL が拒否される理由と curl の使用を提案 |
| Fix | PermissionRequest フック | `--print` モードで発火しない問題を修正 |
| Fix | policy-helper 警告 | ヘッドレス（`-p`）実行時に表示されない問題を修正 |
| Fix | /resume のフォーク名表示 | `/fork` バックグラウンドセッションが親の名前ではなく `⑂` フォーク名で表示されるように修正 |
| Fix | claude.ai ゲートコマンドのログイン提案 | サインアウト時に Enterprise 移行メッセージではなく `/login` を提案するように修正 |
| Fix | SessionEnd フックタイムアウト | `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` がフックごとの `timeout` がない SessionEnd フックを拡張しない問題を修正（1.5 秒後にキャンセルされていた） |
| Fix | /autofix-pr などのクラウドセッションコマンド | GitHub アカウント未接続時の再試行/アプリインストール指示を改善、`/web-setup` や Web 接続ページを案内 |
| Fix | クラウドセッションコマンドのポリシー説明 | `/teleport` や `/remote-env` などで組織ポリシーにより無効化されている場合の説明を追加、"Unknown command" ではなく理由を表示 |
| Fix | Bash サンドボックス説明の過剰表現 | ファイルシステム分離がオフの場合に未強制パスリストを削除、strict モードがコマンドを決して非サンドボックスで実行できないと主張する記述を修正 |
| Improvement | フルスクリーンモードの再描画 | プロンプト行の追加/削除（Shift+Enter）が文字入力と同じ速度で再描画されるように改善 |
| Improvement | --continue / --resume の起動速度 | 会話が即座に表示され、最初のメッセージがトランスクリプト全体を再読み込みしないように改善 |
| Improvement | ツール集約ターンの応答性 | ツールバッチごとの非表示リマインダーでトランスクリプトを再描画しないように改善 |
| Improvement | ワークフロースクリプト検出の起動時間 | `.claude/workflows/` のスクリプトをリストする際に各スクリプトを解析しないように改善 |
| Improvement | オートモード拒否メッセージ | Claude が受け取るメッセージにアクションをブロックしたルールを明記し、より安全な方法を試すよう促すように改善 |
| Improvement | Claude in Chrome の長いページ読み取り | ファイルに保存して読み戻す代わりにインラインで維持するように改善 |
| Improvement | MEMORY.md の切り詰め警告 | 切り詰められた行数と開始位置を表示するように改善 |
| Improvement | アーティファクトのターミナル権限プロンプト | 質問を先頭に配置するように改善 |
| Improvement | プロンプトフッター | エディターや `/diff` 選択をプロンプト入力内に表示、フルスクリーンモードではフッターではなくヘッダーに Remote Control ステータスを表示 |
| Improvement | 使用クレジット必要メッセージ | セッション途中で使用クレジットを有効にした場合、Claude Code 再起動後に有効になることを明記 |
| Improvement | /plugin の即時適用 | プラグインのインストール、有効化、無効化がメニューを閉じた時点で有効になり、その後の `/reload-plugins` が不要に |
| Breaking | Bedrock、Vertex、Foundry のシステムプロンプト | 環境、モデル、設定の詳細を添付ファイルとして配信するように変更、ファーストパーティセッションと一致 |
| Breaking | Bedrock、Vertex、Foundry のツールリスト | 会話全体でツールリストのバイト安定性を維持（後から接続されたツールは遅延ロード）、ファーストパーティセッションと一致 |
| Breaking | タスク追跡ツールの提供条件 | TaskCreate/Get/Update/List、TodoWrite を Claude 3.x、Opus 4.0–4.7、Sonnet 4.0–4.6、Haiku 4.5 のみで提供、他では `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` で有効化 |
| Breaking | アーティファクトデータ編集プロンプト | ターミナルでドキュメント数とアーティファクト公開範囲を表示するカードに変更 |
| Breaking | ローカル Cowork セッションのアーティファクト制限 | すべての承認をスキップする設定でも、Artifact ツールがセッションフォルダ外のローカルファイルやシンボリックリンクを拒否 |
| Breaking | WebFetch 拒否ルールのスコープ変更 | プレーンな `WebFetch` deny/ask ルールが Artifact ツールの読み取り/更新に適用されなくなり、`Artifact` ルール（または `WebFetch(domain:claude.ai)`）を使用 |
| Breaking | MCP サーバー認証通知 | 各サーバーを一度だけ通知し、起動ごとに表示しないように変更 |
| Feature (VSCode) | CLAUDE_CONFIG_DIR 設定時の UI 対応 | 設定ファイルや `environmentVariables` に `CLAUDE_CONFIG_DIR` が設定されている場合にセッションリスト、設定トグル、チャットタブが動作するように修正 |
| Fix (VSCode) | ログイン/ログアウト後の UI 空白 | ログイン、ログアウト、アカウント切り替え後にモデルピル、モデルピッカー、コマンドメニューが数秒間空白になる問題を修正 |
| Fix (VSCode) | Auto モードの表示 | プロジェクトやローカル設定が `~/.claude/settings.json` のモデルを上書きする場合に、新規タブやリロード直後の会話でモードピッカーから Auto が消える問題を修正 |
| Fix (VSCode) | SessionStart フック後のセッション名 | SessionStart フックが設定されている場合に、ウィンドウリロード後にセッション名が最後のプロンプトに戻る問題を修正 |
| Fix (VSCode) | フッターの待機時間 | 別のタブが既に起動している場合に、新規タブの Claude プロセス起動を待たずにモデルピルと Remote Control ピルを表示するように修正 |
| Fix (VSCode) | 二重プロセス起動 | セッションタブの起動が設定読み取りから 0.5 秒以上遅れた場合に 2 つ目の Claude プロセスが完全起動する問題を修正 |
| Fix (VSCode) | preferredLocation 設定の無視 | セッションリストからの再開が `claudeCode.preferredLocation: "sidebar"` を無視する問題（常にパネルを開いていた）を修正、プログラム的な開きが設定を "panel" にリセットする問題も修正 |
| Fix (VSCode) | Windows の問題 | WSL 未インストール機器での WSL インストールプロンプト表示を修正、WSL インストール時に Windows ファイルの IDE 診断が正しく返されるように修正 |
| Fix (VSCode) | CLAUDE_CONFIG_DIR 設定時のカスタムスタイル保存 | CLI が読み取らないフォルダにユーザーレベルスタイルを保存する問題を修正 |
| Feature (VSCode) | 権限ルール保存場所の矢印キー操作 | 常時許可権限ルールの保存場所を左右矢印キーで変更可能に、キーボードとスクリーンリーダーユーザー向け |
| Feature (VSCode) | Focus last message コマンド | 会話の最新メッセージにキーボードフォーカスを移動する "Claude Code: Focus last message" コマンドを追加、キーボードとスクリーンリーダーユーザー向け |
| Improvement (VSCode) | プラグイン管理ダイアログの即時適用 | インストール、有効化、無効化、アンインストールが再起動なしで開いているセッションに適用されるように変更 |
| Breaking (VSCode) | アーティファクト権限プロンプトの変更 | 一部のアーティファクト権限プロンプトで "don't ask again" 選択肢を省略、ターミナルと一致 |
| Fix (Web) | 長時間実行セッションのファイル保存消失 | 約 6 時間以上実行するクラウドセッションで、永続セッションフォルダに保存されたファイルが暗黙的に消失する問題を修正、最大 1 日間保持 |
| Fix (Web) | ルーチンのエフォートレベルエラー | 管理者がモデルのエフォートを制限している組織で、ルーチンがセッションを再開またはエフォート未設定でセッションを開始する際の "Invalid effort level" エラーを修正 |
| Improvement (Web) | ルーチン作成時の説明改善 | 会話からルーチンを作成し、コネクタがない場合に、コネクタがないことと追加方法を説明、確認のみではなく |
| Fix (Claude Tag) | 管理設定ページのローディング | 一時的な読み込み失敗後にスケルトンで固まるまたは空白になる問題を修正、失敗したセクションに Retry ボタンを表示 |
| Feature (Claude Tag) | Slack チャンネル設定へのリンク | Slack チャンネルの設定ページから組織の Claude in Slack 管理設定へのリンクを追加 |
| Fix (Claude Tag) | Enterprise Grid チャンネルの設定消失 | Slack 管理者がチャンネルを別のワークスペースに移動した後に Claude 設定（リポジトリ、環境、アクセス）が失われる問題を修正 |
| Improvement (Claude Tag) | ブロックされたアクションの説明改善 | 権限チェック、Claude 自身の確認判断、アクセス不足のいずれがアクションを停止したかを説明 |
| Improvement (Claude Tag) | 応答速度の向上 | 読み取り専用ルックアップ（Slack 検索、スレッド読み取り、人物検索）を順次ではなく同時実行 |
| Improvement (Claude Tag) | 比較のフォーマット改善 | 文レベルの比較をワイドテーブルではなくリストで表示、横スクロールを回避、長いテーブルセルを折り返し |
| Fix (Claude Tag) | スレッドの !restart コマンド | 独自セッションを持つスレッドで `@Claude !restart` が矛盾する "this thread is handled by the channel session" 通知も投稿する問題を修正 |
| Improvement (Claude Tag) | 異なる組織のアカウントメッセージ | Claude アカウントが Slack ワークスペースと異なる組織にある場合の説明を改善、ワークスペースを組織に接続する方法を説明 |
| Fix (Claude Tag) | Markdown リンクの括弧表示 | URL が山括弧で囲まれている Markdown リンクがクリック可能リンクではなくリテラル括弧テキストとして表示される問題を修正 |
| Fix (Claude Tag) | ワークスペースゲストのメンション | ゲストが Claude を使用できるチャンネルでのワークスペースゲストのトップレベル @mention が、回答ではなく "your Slack account isn't connected" 応答を受け取る問題を修正 |
| Fix (Claude Tag) | チャンネルセッションのリフレッシュ | チャンネルの長時間実行セッションが会話途中で新しいものに置き換えられる問題を修正、スケジュールされたリフレッシュはチャンネルとスレッドが静かになるまで待機 |
| Fix (Claude Tag) | チャンネル設定カードの重複結果 | 複数回クリックされたチャンネル設定カードが、変更が既に適用された後に拒否されたと提案セッションに通知する問題を修正、結果は一度だけ送信 |
| Breaking (Claude Tag) | パブリックチャンネルのメモリ分離 | 各チャンネルが独自のノートを保持し、Claude が他のパブリックチャンネルに保存したノートを想起しなくなり、ワークスペースノートは共有のまま |
| Feature (Code Review) | 未解決の発見事項の注記 | フォローアップレビューで未解決の発見事項リストの下に、発見事項のスレッドを解決する（返信するだけでなく）ことで後続レビューでカウントされなくなる旨の注記を追加 |
| Fix (Code Review) | 発見事項検証エージェント失敗時の不完全終了 | 発見事項を検証するエージェントの 1 つが途中で失敗した場合にレビューが不完全で終了する問題を修正、エージェントを置き換えて評決に到達 |
| Fix (Code Review) | ドラフト変換後のレビュー投稿 | 実行中レビューの後ろにキューされたプッシュトリガーレビューが、プルリクエストがドラフトに変換された後も投稿される問題を修正 |
| Fix (Code Review) | ルートファイル編集時の CLAUDE.md 無視 | PR がルートファイル（例: README.md）を編集した場合に、CLAUDE.md がリストするファイルと名前のみが一致する場合にディレクトリの CLAUDE.md 規約を無視する問題を修正 |

## まとめ

v2.1.268 は、Claude apps ゲートウェイの価格管理とアクセス制御の強化、セッション状態管理オプションの追加、WebFetch のタイムアウト設定、CPU 使用率の最適化など、セルフホスト環境とリソース管理面での改善が目立つリリースとなっています。サードパーティエンドポイントとの互換性修正、シンボリックリンクディレクトリの権限制御改善、VSCode 拡張の安定性向上、Claude in Slack の応答速度とメモリ管理の改善など、幅広い領域での品質向上が図られました。また、CLI の JSON 出力拡張により、自動化スクリプトやプラグイン管理のプログラム的な操作がより容易になっています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)