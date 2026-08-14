---
title: "【Claude Code】v2.1.233・v2.1.232 リリースノートまとめ"
date: 2026-08-15T08:02:58+09:00
draft: true
tags: ["claude-code", "gitlab", "sendmessage", "subagent", "mcp", "remote-control", "bash", "powershell", "windows", "linux", "git", "oauth", "fable", "vertex", "bedrock", "aws", "notification", "desktop", "vs-code", "slack", "cygwin"]
categories: ["Claude Code Updates"]
summary: "v2.1.233・v2.1.232 のClaude Codeリリースノートまとめ"
---

## はじめに

2026年8月15日、Claude Code v2.1.233 および v2.1.232 がリリースされました。v2.1.232 では subagent のフォーク機能がデフォルト有効化され、セッション間の直接メッセージング機能（`@` メンション）が導入されました。GitLab のトークン保護とプラグインマーケットプレイス対応も実装され、エンタープライズ向けのゲートウェイ設定検証が強化されています。v2.1.233 では GitLab マージリクエスト URL のサポート、Anthropic アップストリームでのユーザー ID 転送機能、Linux での Bash コマンドメモリ制限機能が追加されました。また、MCP v2 接続の無限再接続問題や Windows のパス検証に関するセキュリティ脆弱性の修正が含まれています。

## 注目アップデート深掘り

### セッション間の直接メッセージング機能（v2.1.232）

v2.1.232 では、プロンプトで `@` を入力することで他の Claude セッションを名前で参照できるようになりました。Claude は `SendMessage` を使用してそのセッションに直接到達します。`SendMessage` は、実行中のセッションと完全に一致する単一の名前に対しては、最初に参照確認を求めることなく直接配信します。同一マシン上の対話型セッションは一意の名前を維持するようになり、既に使用中の名前でセッションを開始または名前変更すると、`name-word-word` 形式の変種が付与されます。`/config` には「Dialog expiry」と「Messages from your other sessions」（クロスセッションのインバウンド受け入れ/保留/拒否）の設定行が追加されました。これにより、複数のセッションを並行実行しながら、セッション間で直接通信できる柔軟なワークフローが可能になります。

### GitLab マージリクエスト対応と Bash メモリ制限（v2.1.233）

v2.1.233 では、`--worktree` フラグと `claude agents` ビューに GitLab マージリクエスト URL のサポートが追加されました（マージリクエストは `!N` として表示されます）。また、Linux での Bash ツールコマンドに対するオプトインのメモリ cgroup サポート（`CLAUDE_CODE_TOOL_MEMORY_LIMIT`）が追加され、暴走したビルドがセッションを停止させないようになりました。さらに、Anthropic アップストリームに対するオプトインの `forward_user_identity` アプリゲートウェイ設定が追加され、サインイン済みユーザーの ID をヘッダーとして送信することで、ゲートウェイの背後にあるプロキシがユーザーごとの支出を記録できるようになりました。これらの機能は、チーム開発環境での可視性とリソース管理の向上に寄与します。

## 実用的な活用ポイント

v2.1.232 の subagent フォーク機能により、`subagent_type: "fork"` を設定した subagent は完全な会話とプロンプトキャッシュを継承できるようになりました。対話型セッションでの非チームメイトエージェントのスポーンはデフォルトでバックグラウンド実行されます。GitLab サポートでは、`glrt-`、`gloas-`、`glptt-`、`glagent-`、`glimt-`、`glsoat-`、`glcbt-`、`glft-`、`glffct-` トークンファミリーの秘密編集と、ルーティング可能な `glpat-`/`gldt-` トークンの完全編集が実装されています。プラグインマーケットプレイスでは、`gitlab.com` リポジトリ URL（ネストされたサブグループを含む）が `github.com` URL と同様にクローンできるようになり、`additionalMarketplaces` と `allowedMarketplaces` が `extraKnownMarketplaces` と `strictKnownMarketplaces` の使いやすいエイリアスとして受け入れられます。

v2.1.233 では、WebFetch セッション URL キャッシュ TTL を設定する `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` 環境変数が追加されました（デフォルトは 15 分のまま変更なし）。Opus 4.8、Sonnet 5、Fable 5、Mythos 5 以降のモデルでは、タスク/TODO トラッキングツール（TaskCreate/Get/Update/List、TodoWrite）が利用できなくなりましたが、`CLAUDE_CODE_ENABLE_TODO_TOOLS=1` を設定することで復元できます。

## 全変更点一覧

| カテゴリ | バージョン | 変更内容 | 概要 |
|---------|-----------|---------|------|
| Feature | v2.1.232 | Subagent フォークのデフォルト有効化 | `subagent_type: "fork"` subagent が完全な会話とプロンプトキャッシュを継承、対話型セッションでの非チームメイトエージェントスポーンがデフォルトでバックグラウンド実行 |
| Feature | v2.1.232 | セッション間メッセージング | プロンプトで `@` 入力により他の Claude セッションを名前で参照、`SendMessage` による直接到達 |
| Feature | v2.1.232 | セッション名の一意性保証 | 同一マシン上の対話型セッションが一意の名前を維持、重複時は `name-word-word` 変種を付与 |
| Feature | v2.1.232 | `/config` 設定行追加 | "Dialog expiry" と "Messages from your other sessions"（クロスセッションのインバウンド受け入れ/保留/拒否）設定 |
| Feature | v2.1.232 | GitLab トークン秘密編集 | `glrt-`、`gloas-`、`glptt-`、`glagent-`、`glimt-`、`glsoat-`、`glcbt-`、`glft-`、`glffct-` トークンファミリーの秘密編集と、ルーティング可能な `glpat-`/`gldt-` トークンの完全編集を実装 |
| Feature | v2.1.232 | GitLab プラグインマーケットプレイス対応 | `gitlab.com` リポジトリ URL（ネストされたサブグループを含む）が `github.com` URL と同様にクローン可能 |
| Feature | v2.1.232 | 設定エイリアス追加 | `additionalMarketplaces` と `allowedMarketplaces` が `extraKnownMarketplaces` と `strictKnownMarketplaces` のエイリアスとして受け入れ |
| Feature | v2.1.232 | Fable 5 アドバイザー復活 | Fable アクセス権を持つ組織で `/advisor` に Fable 5 が再度提供、`/model fable` で利用クレジット同意を設定 |
| Feature | v2.1.233 | GitLab マージリクエスト URL サポート | `--worktree` フラグと `claude agents` ビューに GitLab マージリクエスト URL サポートを追加（MR は `!N` として表示） |
| Feature | v2.1.233 | ユーザー ID 転送機能 | Anthropic アップストリームにオプトインの `forward_user_identity` アプリゲートウェイ設定を追加、サインイン済みユーザーの ID をヘッダーとして送信 |
| Feature | v2.1.233 | Bash メモリ制限機能 | Linux での Bash ツールコマンドに対するオプトインのメモリ cgroup サポート（`CLAUDE_CODE_TOOL_MEMORY_LIMIT`）を追加 |
| Feature | v2.1.233 | WebFetch キャッシュ TTL 設定 | `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` 環境変数を追加、WebFetch セッション URL キャッシュ TTL を設定可能（デフォルトは 15 分のまま） |
| Fix | v2.1.232 | PowerShell パラメータ変数書き込みバイパス | 変数書き込みパラメータが `$PSDefaultParameterValues` を静かに上書きして後続コマンドのファイルアクセスをリダイレクトできた問題を修正 |
| Fix | v2.1.232 | Windows Cygwin スタイルシンボリックリンク | Git Bash が Cygwin スタイルシンボリックリンクをフォローしてパス検証が通常ファイルと見なしていた問題を修正、書き込みに承認が必要に |
| Fix | v2.1.232 | ネストされた git リポジトリの信頼継承 | ネストされた git リポジトリが親ディレクトリから信頼を継承していた問題を修正、各リポジトリで独自の信頼確認が必要に |
| Fix | v2.1.232 | MCP 接続のハング | サーバーが応答しない、またはプロトコルバージョンプローブに不正な返信を送信した際、MCP 接続が 30 秒の接続タイムアウト全体でハングしていた問題を修正 |
| Fix | v2.1.232 | Remote Control セッションのトランスクリプト/認証情報継承 | クラウドセッション内のブリッジによってホストされた Remote Control セッションがそのセッションのトランスクリプトまたは認証情報を継承していた問題を修正 |
| Fix | v2.1.232 | Remote Control セッションの再接続 | Claude Desktop または IDE から開始された Remote Control セッションが、ローカルセッション再開のたびに新しい claude.ai セッションとして表示されていた問題を修正、既存のセッションに再接続 |
| Fix | v2.1.232 | Remote Control セッションのアイドル時到達不能 | Remote Control セッションがアイドル中に新たに接続されたクライアントから到達不能に見えていた問題を修正 |
| Fix | v2.1.232 | Remote Control ブリッジセッションの履歴復元 | セッションワーカー再起動時に Remote Control ブリッジセッションが会話履歴を復元しなかった問題を修正 |
| Fix | v2.1.232 | Remote Control 削除セッションの再開 | claude.ai またはアプリから削除されたセッションの会話を再開する際、ログインに関するメッセージで失敗していた問題を修正、代替セッションを開始するように（v2.1.227 でのリグレッション） |
| Fix | v2.1.232 | Cloud ゲートウェイ `/login` の静かな終了 | 管理設定の読み込み失敗時に "Press Enter to continue" 後に Cloud ゲートウェイ `/login` が静かに終了または応答しないターミナルを残していた問題を修正、理由を表示 |
| Fix | v2.1.232 | ネイティブビルドの音声モード | 音声サービスが接続を拒否した際にネイティブビルドの音声モードが "listening…" で停止していた問題を修正、拒否を即座に表示 |
| Fix | v2.1.232 | mTLS クライアント証明書ローテーション | mTLS クライアント証明書のローテーションに再起動が必要だった問題を修正、接続エラー時にローテーションされた証明書とキーを自動リロード |
| Fix | v2.1.232 | AWS または Vertex リージョン値の不正な形式 | 不正な形式の AWS または Vertex リージョン値がリクエスト URL の構築に使用されていた問題を修正、デフォルトリージョンにフォールバック |
| Fix | v2.1.232 | ストリームアイドルタイムアウトエラー | Bedrock、Vertex、ゲートウェイデプロイメントでストリームアイドルタイムアウトエラーがリクエスト失敗を引き起こし回復しなかった問題を修正 |
| Fix | v2.1.232 | コンテンツサイズオーバーレイのレンダリング幅 | 切り詰められたテキストを含むコンテンツサイズオーバーレイが 1 列広くレンダリングされ、先頭切り詰めテキストが省略記号に折りたたまれていた問題を修正 |
| Fix | v2.1.232 | 絵文字の途中で切れた文字 | 長いシェルコマンドまたはエージェント説明プレビューが絵文字の途中で切れた際に生じていた文字化けを修正 |
| Fix | v2.1.232 | プラグインマーケットプレイス登録解除の競合 | `known_marketplaces.json` への同時書き込みによりプラグインマーケットプレイスが静かに登録解除される可能性があった起動時の競合を修正 |
| Fix | v2.1.232 | `/update` と `/tui` の再起動拒否 | 再起動後も存続する作業が実行中の際に `/update` と `/tui` が再起動を拒否していた問題を修正 |
| Fix | v2.1.232 | SDK およびリモートセッションでの使用制限ガイダンス | 使用制限ガイダンスが SDK およびリモートセッションで利用できないスラッシュコマンドを提案していた問題を修正 |
| Fix | v2.1.232 | 対話型 `--advisor fable` 起動の同意メッセージ | 対話型 `--advisor fable` 起動の同意メッセージが、終了したばかりの対話型セッションで `/model fable` を実行するよう指示していた問題を修正 |
| Fix | v2.1.233 | クラウドセッションの喪失マーク | Claude が承認プロンプトを待機中に環境がシャットダウンした際、クラウドセッションが時折喪失とマークされていた問題を修正 |
| Fix | v2.1.233 | MCP v2 接続の無限再接続 | 固定タイムアウトで長時間保持ストリームを終了するサーバー（サーバーレスホストなど）に対して MCP v2 接続が subscriptions/listen ストリームを無限に再オープンしていた問題を修正 |
| Fix | v2.1.233 | Notification フックの不発火 | Claude Desktop または VS Code 下で実行中に承認プロンプトに対して Notification フックが発火しなかった問題を修正 |
| Fix | v2.1.233 | Linux でのアイドルセッションの CPU 使用率 | サンドボックスが有効な際に Linux でのアイドルセッションが時折 1 つの CPU コアを 100% 維持していた問題を修正 |
| Fix | v2.1.233 | バンドルスキルエイリアスの "Unknown command" | `/checkup` や `/review` などのバンドルスキルエイリアスが、`-p` モードまたはプラグイン/MCP 読み込み時にユーザーまたはプロジェクトスキルがバンドルスキルをシャドウすると "Unknown command" を報告していた問題を修正 |
| Fix | v2.1.233 | スキル/コマンド引数置換 | 引数値がテンプレートマーカーとして再展開されないよう、スキル/コマンド引数置換を修正 |
| Fix | v2.1.233 | Windows NT デバイスパスのバイパス | NT `\??\` デバイスプレフィックスで綴られた Windows パスが UNC パス検証をバイパスし、NTLM 認証情報リークベクターを開いていた問題を修正 |
| Fix | v2.1.233 | Windows 自動モードの繰り返し停止 | 通常の `cd <dir> && <command> > file` Bash コマンドに対して Windows の自動モードが手動承認のために繰り返し停止していた問題を修正（v2.1.232 でのリグレッション） |
| Improvement | v2.1.232 | フルスクリーンストリーミング | 長いセッションでも応答性を維持、更新のたびに会話全体を再正規化しなくなった |
| Improvement | v2.1.232 | 管理設定承認ダイアログ | エンドポイント URL を表示、テレメトリのみの変更に対してより明確な表現を使用、定型的な OpenTelemetry オプションをスキップ、サーバー管理のサンドボックスバイナリオーバーライド（`sandbox.bwrapPath`、`sandbox.socatPath`、`sandbox.ripgrep`）に承認を要求 |
| Improvement | v2.1.232 | `/feedback` と `/bug` の即座オープン | Claude 応答中に呼び出された際に `/feedback` と `/bug` がターンの終了を待たずに即座にオープン |
| Improvement | v2.1.232 | `/plugin install` のマーケットプレイス更新 | `/plugin install plugin@marketplace` が最初にマーケットプレイスを更新、新規公開プラグインが手動マーケットプレイス更新なしでインストール可能 |
| Improvement | v2.1.232 | `/code-review` のバックグラウンドエージェント | high、xhigh、max 努力レベルでの `/code-review` が他のレベルと同様にバックグラウンドエージェントで実行 |
| Improvement | v2.1.232 | 画像読み込みの非ブロッキング | ペーストおよびクリップボード画像がイベントループをブロックせずに読み込まれる |
| Improvement | v2.1.232 | Remote Control の再接続時間延長 | ネットワーク障害後約 30 分間再接続を継続、1 時間にわたる複数回の障害後も切断されなくなった |
| Improvement | v2.1.232 | Remote Control の会話再開 | 同じマシン上の別の Claude Code が Remote Control を保持している場合、会話再開が静かに Remote Control を奪わなくなった、`/remote-control` を実行して移動 |
| Improvement | v2.1.232 | エージェントパネル更新 | 完了した subagent が `/tasks` フッターヒントとともに即座に非表示、"↓ N more" オーバーフロー表示が視認性のために左に移動 |
| Improvement | v2.1.232 | Remote Control ターミナルメッセージ | セッションが別のデバイスに引き継がれたか、別のアプリから終了されたか、削除されたかをターミナルで表示、それを元に戻す再接続を提案しなくなった |
| Improvement | v2.1.232 | Bash 入力リダイレクションの承認チェック | すべてのプラットフォームで Bash 入力リダイレクション（`< file`）が引数表記と同様に承認チェック |
| Improvement | v2.1.232 | 完了バックグラウンドエージェントの再開メッセージ短縮 | 完了したバックグラウンドエージェントを再開する際に表示されるメッセージを短縮 |
| Improvement | v2.1.232 | Cowork セッションの @-import 非インライン化 | Cowork セッションがユーザースコープメモリファイルからの外部 @-import をインライン化しなくなった |
| Improvement | v2.1.232 | クロスセッションメッセージングソケットディレクトリの強化 | 共有 `/tmp` 上の自動生成クロスセッションメッセージングソケットディレクトリを強化、事前に配置されたシンボリックリンクや他のユーザーのディレクトリを使用せず拒否 |
| Improvement | v2.1.232 | Linux ファイルシステムサンドボックスの強化 | 保護パスバイパスに対して Linux ファイルシステムサンドボックスを強化 |
| Improvement | v2.1.233 | セルフホストランナーのセッション起動時間 | セッションブランチが作業ツリーを書き直さずに作成され、2 つのサーバーラウンドトリップがエージェント起動をブロックしなくなった |
| Improvement | v2.1.233 | アプリゲートウェイエラー転送 | Vertex、Foundry、AWS 上の Claude Platform からの 400/413 エラーがアップストリーム自身のメッセージを伝達、アプリゲートウェイの auto-compact に関するバグを修正 |
| Improvement | v2.1.233 | `claude plugin validate` のチェック強化 | `.claude/skills` ディレクトリを単体でチェック、frontmatter のパースに失敗した SKILL.md ファイルを報告 |
| Improvement | v2.1.233 | スクリーンリーダーモード | `/effort` セレクターが番号付きリストとして入力番号プロンプトでレンダリング、ヒントとダイアログテキストがクリップされなくなった |
| Improvement | v2.1.233 | プリントモード診断 | Claude Code が認識しないモデル ID に対してリクエストが送信された際、`[claude-code:unrecognized_model]` 行が stderr に書き込まれる、`modelOverrides` でマップしてサイレンス化 |
| Breaking | v2.1.232 | エンタープライズポリシー | url-typed の `blockedMarketplaces` エントリが、CLI が git クローンとして分類した際にその URL のブロックを維持 |
| Breaking | v2.1.232 | ゲートウェイ `desktop:` オーバーレイ | リリース済みのすべての Desktop 設定を受け入れ（以前は 11 の手動リストキー）、起動時に Desktop 自身のスキーマに対して検証、不明または無効なキーで起動失敗 |
| Breaking | v2.1.232 | ゲートウェイ空エントリとドメイン値の検証 | 空の `managed.policies[].match.groups`/`admin.admin_groups` エントリと不正な形式の `email_domain` 値（空、または `@`、空白、カンマを含む）が起動時に失敗、誰にもマッチしないか管理者アクセスを付与することが無くなった |
| Breaking | v2.1.232 | `sandbox.ripgrep` の設定範囲制限 | `sandbox.ripgrep` がユーザー、管理、`--settings` 設定からのみ尊重されるように変更、プロジェクト設定でサンドボックスの ripgrep バイナリを上書きできなくなった |
| Breaking | v2.1.232 | サブエージェント作成の起動ヒントとツアー削除 | カスタム subagent 作成を提案する起動ヒントと `/powerup` ツアー内の対応するナッジを削除 |
| Breaking | v2.1.233 | GitHub アプリセットアップヒントの表示変更 | GitHub アプリセットアップヒントが、origin リモートが gitlab.com または bitbucket.org 上にあるリポジトリで表示されなくなった、エンタープライズマーケットプレイスヒントが非 GitHub 内部 git ホストをカバー |
| Breaking | v2.1.233 | TODO/タスクトラッキングツールの無効化 | Opus 4.8、Sonnet 5、Fable 5、Mythos 5 以降のモデルで TODO/タスクトラッキングツール（TaskCreate/Get/Update/List、TodoWrite）が利用不可、`CLAUDE_CODE_ENABLE_TODO_TOOLS=1` で復元可能 |
| Breaking | v2.1.233 | Windows の Cygwin スタイルシンボリックリンクと入力リダイレクションの承認変更取り消し | v2.1.232 の Windows での Cygwin スタイルシンボリックリンクと入力リダイレクション（`< file`）に対する Bash 承認変更を取り消し、より狭い範囲のバージョンが後のリリースで復帰予定 |

## まとめ

v2.1.232 および v2.1.233 は、セッション間通信機能の導入、GitLab サポートの強化、リソース管理機能の追加を中心としたリリースです。セッション間の直接メッセージング機能と subagent のフォーク機能により、複数セッションを並行実行するワークフローが大幅に改善されました。GitLab トークンの秘密保護とプラグインマーケットプレイス対応により、GitLab ユーザーの開発環境統合が進展しています。Linux でのメモリ制限機能とユーザー ID 転送機能は、チーム環境でのリソース管理と支出追跡の可視性を向上させます。一方で、複数の権限バイパスに関する修正（PowerShell パラメータ変数書き込み、Windows Cygwin スタイルシンボリックリンク、NT デバイスパスのバイパス）により、セキュリティが強化されました。MCP v2 接続の無限再接続問題やクラウドセッションの喪失マークなどの安定性問題も解決され、全体としてエンタープライズ環境での信頼性と運用性が向上しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)