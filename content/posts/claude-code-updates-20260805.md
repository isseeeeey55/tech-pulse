---
title: "【Claude Code】v2.1.222・v2.1.221 リリースノートまとめ"
date: 2026-08-05T08:02:38+09:00
draft: false
tags: ["claude-code", "vscode", "focus-view", "mcp", "sandbox", "worktree", "git", "proxy", "sendmessage", "ultrareview", "vim", "vertex-ai", "stats", "bedrock", "aws-sso", "websearch", "github", "remote-control", "ultraplan"]
categories: ["Claude Code Updates"]
summary: "v2.1.222・v2.1.221 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260805/header.png)

# Claude Code v2.1.222 / v2.1.221 リリース解説 — ワークツリー隔離の権限修正、サンドボックス認証情報マスキング、VSCode Focus ビュー

## はじめに

Claude Code の **v2.1.221**（2026年8月4日）と **v2.1.222**（2026年8月5日）がリリースされました。v2.1.221 では VSCode に Focus ビューが追加され、Linux/WSL 環境でのサンドボックス認証情報マスキングが導入されました。v2.1.222 は全21項目のうち16項目が Fix で、ワークツリー隔離セッションのセキュリティ修正、MCP サーバーの使用量計測の正確化、プロキシ環境での接続安定性改善が中心です。両バージョンともセキュリティと信頼性の改善に重点が置かれています。

## 注目アップデート深掘り

### VSCode Focus ビュー機能（v2.1.221）

v2.1.221 で VSCode 向けに **Focus ビュー** 機能が追加されました。チャットメニューのトグルで、ツールアクティビティを**展開可能な**ターンごとのサマリーの背後に隠し、実行中ツールのライブインジケーターを表示します。`Ctrl+Alt+F` または "Claude Code: Toggle Focus view" コマンドで切り替えられます。

これにより、ツール呼び出しの詳細が画面を占有せず、対話の流れに集中しやすくなります。特に複数のツールが並行実行される場合や、長時間のセッションでログが増大する場合に有用です。

### サンドボックス認証情報マスキング（v2.1.221）

Linux および WSL 環境において、サンドボックス認証情報ファイルに `mode: "mask"` が追加されました。この設定では、サンドボックス化されたコマンドはセンチネルコピー（ファイル全体、または `extract` 正規表現でキャプチャされた部分）を読み取り、サンドボックスプロキシが送信時に実際の値を置換します。macOS ではファイルマスキングは `deny` にフォールバックします。

これにより、サンドボックス環境内で認証情報を安全に扱いながら、必要な場面でのみ実際の値が外部に送信される仕組みが整備されました。

### ワークツリー隔離セッションのセキュリティ強化（v2.1.222）

v2.1.222 では、ワークツリー隔離セッションおよびそのサブエージェントが、メインチェックアウトに対して破壊的な Git コマンドを実行できてしまう問題が修正されました。隔離は、すべてのセッションタイプでファイル編集と Bash に適用されるようになりました。

この修正により、並行して複数のセッションを実行する場合でも、意図しない Git 操作によるリポジトリの破壊を防ぐことができます。

### MCP サーバー使用量計測の正確化（v2.1.222）

`/usage` コマンドが MCP サーバーの使用量を過大評価していた問題が修正されました。サーバーのシェアは、実際にそのツール結果を消費したリクエストのみを反映するようになり、それ以降のすべてのターンに計上されることはなくなりました。

これにより、複数の MCP サーバーを利用する環境で、正確な使用量分析とコスト管理が可能になります。

## 実用的な活用ポイント

v2.1.221 の Focus ビュー機能は、VSCode でツールアクティビティを折りたたみ、対話フローを追いやすくします。長時間のコード生成や複雑なタスクでログが増える場合に有効です。

サンドボックス認証情報マスキングは、Linux/WSL でサンドボックス化したコマンドに認証情報ファイルを渡す際に役立ちます。`mode: "mask"` を設定すると、サンドボックス内部ではセンチネルコピーが読み込まれ、送信時にプロキシが実際の値へ置換します。

v2.1.222 のワークツリー隔離セキュリティ強化は、並行セッションや複数ブランチでの作業時に重要です。破壊的 Git コマンドの実行を防ぎ、リポジトリの整合性を保ちます。

プロキシ環境での接続安定性向上により、起動時の接続チェックが HTTPS プロキシ経由でも正しく動作し、明確なタイムアウトメッセージが表示されるようになりました。

MCP サーバーの使用量計測修正は、複数サーバーを組み合わせて利用する場合のコスト分析精度を向上させます。

## 全変更点一覧

### v2.1.222

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Fix | ワークツリー隔離セッションの Git コマンド制限 | ワークツリー隔離セッションおよびサブエージェントが、メインチェックアウトに対して破壊的 Git コマンドを実行できていた問題を修正。すべてのセッションタイプでファイル編集と Bash に隔離を適用 |
| Fix | PreToolUse auto-allow フック制限バイパス | バックグラウンドエージェントタスク（サマリー、コンパクション、リネーム）で PreToolUse auto-allow フックがツール制限をバイパスしていた問題を修正 |
| Fix | `/usage-credits` のリクエスト再送不可 | Team および Enterprise で、以前のリクエストが却下されたメンバーが「すでに usage credit リクエストを送信済み」と表示され新規送信できない問題を修正 |
| Fix | HTTPS プロキシ環境での起動接続チェック | HTTPS プロキシ環境で起動時の接続チェックがハングし失敗する問題を修正。API リクエストと同じプロキシ対応トランスポートを使用し、明確なメッセージでタイムアウト |
| Fix | "Connection closed mid-response" 誤報告 | 実際には完了しているレスポンスに対して "Connection closed mid-response" エラーが報告される問題を修正 |
| Fix | `/usage` の MCP サーバー使用量過大評価 | MCP サーバーの使用量が過大評価される問題を修正。サーバーのシェアは実際にツール結果を消費したリクエストのみを反映 |
| Fix | ブランチプッシュ後の PR リンク | ブランチプッシュ後（GitHub REST API 経由を含む）にセッションがプルリクエストにリンクされない問題を修正 |
| Fix | 組織制限モデルでのサブエージェント/チームメイトファミリーエイリアス | `model: opus` スタイルのサブエージェントおよびチームメイトファミリーエイリアスが、組織で制限されている場合に親モデルにドロップダウンする問題を修正。最新の組織許可モデルにステップダウン |
| Fix | カスタム `ANTHROPIC_BASE_URL` でのストリームタイムアウト | カスタム `ANTHROPIC_BASE_URL` ゲートウェイで、サーバーキープアライブ ping が到着しているにもかかわらずストリームアイドルタイムアウトが発火する問題を修正 |
| Fix | claude.ai コネクタの誤った認証要求 | セッショントークンが無効な場合に claude.ai コネクタが誤って認証必要とマークされる問題を修正。`/login` ヒントを表示 |
| Fix | 利用不可ツールのエラー表示 | MCP サーバー削除後など、ローカルで利用できなくなったツールのツールエラーが表示されない問題を修正 |
| Fix | `SendMessage` の長いサマリー拒否 | `SendMessage` が長いサマリーを拒否する問題を修正。文字数制限で失敗しないよう切り詰めを実施 |
| Fix | サブエージェント transcript ビューのスピナー effort ラベル | サブエージェントの transcript ビューで、スピナーの effort ラベルがサブエージェント自身の `effort:` 設定ではなくセッションの effort レベルを表示していた問題を修正 |
| Fix | ファイルウォッチャーのクラッシュ | ファイルウォッチャーがファイルシステムエラーに遭遇した場合、またはファイルウォッチャー破棄時に稀にクラッシュする問題を修正 |
| Fix | スクリーンリーダー backspace エコー | `--ax-screen-reader` モードで、backspace のたびに入力行全体が再読み上げされる問題を修正。行末削除は削除文字のみをエコー |
| Fix | ホストモデル選択キーの優先順位 | `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` 設定時に、ホストモデル選択キーがディスク上の古い `managed-settings.json` より優先されない問題を修正 |
| Improvement | auto モード安全性向上 | `SendMessage` 経由で他のエージェントセッションに送信されるメッセージが、dispatch 前に permission classifier で評価されるよう改善 |
| Improvement | `disable-model-invocation` スキルの拒否改善 | Claude がモデル呼び出し無効のスキルを実行しようとする際の拒否を改善。ワークフローを複製するのではなく、ユーザーにスキル実行を依頼するよう指示 |
| Improvement | `/diff` ビューの git blob 使用 | `/diff` ビュー、Remote Control ワークスペース差分、web セッションのファイル編集差分で、ワークスペース設定の diff ドライバーや textconv を無視し、生の git blob コンテンツを使用するよう改善 |
| Changed | Remote Control 自動起動設定変更 | Remote Control 自動起動は、リポジトリローカル設定（`.claude/settings.json` または `.claude/settings.local.json`）では有効化できなくなった（無効化は可能）。ユーザースコープで `/config` を使用して有効化 |
| Removed | ultraplan 機能削除 | ultraplan 機能を削除 |

### v2.1.221

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | [VSCode] Focus ビュー追加 | ツールアクティビティを折りたたみ、ターンごとのサマリーとライブ実行中ツールインジケーターを表示するチャットメニュートグル機能。`Ctrl+Alt+F` または "Claude Code: Toggle Focus view" コマンドで切り替え |
| Feature | Linux/WSL サンドボックス認証情報マスキング | サンドボックス認証情報ファイルに `mode: "mask"` を追加。サンドボックス化コマンドはセンチネルコピーを読み取り、プロキシが送信時に実際の値を置換。macOS では `deny` にフォールバック |
| Feature | `claude plugin validate` 警告追加 | マーケットプレイスまたはプラグイン名が Claude Desktop の管理マーケットプレイス同期で拒否される場合に警告を追加 |
| Feature | `claude-api` スキルに `prompt-audit` サブコマンド追加 | 古いモデル向けに書かれたパターンをプロンプトおよびツール記述で監査する `prompt-audit` サブコマンドを追加 |
| Fix | Bash ツール権限チェックバイパス | zsh が `[[ ]]` 正規表現条件内で隠しコマンドを実行できる権限チェックバイパスを修正。影響を受けるコマンドは権限プロンプトを表示 |
| Fix | PowerShell 権限チェックのクォート文字処理 | Windows で、引用符を含むパスを PowerShell 権限チェックが誤処理する問題を修正。該当パスは承認プロンプトを表示 |
| Fix | thinking トグル効果の持続 | thinking オフで開始したセッションで、thinking トグルが残りのセッションに効果を持たない問題を修正。MCP サーバーの接続中の無効化が暗黙的に復帰しなくなった |
| Fix | `--mcp-config` の print モード接続 | print モード（`-p`）で、`--mcp-config` からの MCP サーバーが最初のターン前に接続されず、モデルがツール呼び出しをリテラルテキストとして出力する問題を修正 |
| Fix | @メンションファイルの Esc 後消失 | Esc でプロンプトを取り下げて再送信する際、@メンションファイルが無言でドロップされる問題を修正 |
| Fix | SDK MCP ツール名のクラッシュ | `constructor` など組み込みオブジェクトプロパティと同名の SDK MCP ツールの API リクエスト準備時にクラッシュする問題を修正 |
| Fix | WebSearch の effort 高設定時エラー | thinking 無効時、effort `xhigh`/`max` で WebSearch が 400 エラーで失敗する問題を修正 |
| Fix | サンドボックス大容量アップロード TLS エラー | サンドボックスプロキシ経由のサンドボックス化大容量アップロードが TLS エラーで失敗する問題を修正 |
| Fix | Team/Enterprise 利用上限メッセージ誤表示 | Team および Enterprise の利用上限メッセージが、個人の利用上限ではなく組織の月間上限を誤って表示する問題を修正 |
| Fix | Bedrock AWS SSO 名前付きプロファイル認証 | `HOME` 環境変数が設定された Windows マシンで、AWS SSO 名前付きプロファイルを使用した Bedrock 認証が desktop 管理セッションで失敗する問題を修正 |
| Fix | `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=0` 効果 | `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=0` が中断ターン自動再開を無効化しない問題を修正。falsy 値が正しく扱われるようになった |
| Fix | スリープ復帰時の競合条件 | スリープ復帰時に 2 つの Claude Code プロセスが同時に同じ MCP コネクタまたは WIF OAuth トークンを更新し、再認証を強制する稀な競合条件を修正 |
| Fix | Desktop/claude.ai セッション名変更反映 | Claude Code Desktop または claude.ai からセッション名を変更した場合、CLI のセッション名が更新されない問題を修正。すべてのリネーム元からのセッション名がサニタイズされるようになった |
| Fix | ターミナル専用 built-in スキル呼び出し | プラグインおよび組織配信スキルのうち、`/help`、`/feedback` などターミナル専用 built-in と同名のものが、非対話セッションで呼び出せない問題を修正 |
| Fix | "Plugins changed" 通知の残存 | プラグインリロード後に "Plugins changed" 通知がクリアされず残る問題を修正 |
| Fix | Vim モードのヤンクレジスタ保持 | Vim モードで、ダイアログ、履歴検索、transcript ビュー経由後にヤンクレジスタが無言で空にされる問題を修正 |
| Fix | Vim モードの空プロンプト undo 確認 | Vim モードで、空プロンプトまで undo した際、エージェントビューに戻る前に「← をもう一度押して確認」を表示するよう修正 |
| Improvement | Google Vertex AI ツール検索再有効化 | Google Vertex AI で、Claude 4.5 世代以降のモデルに対してツール検索を再有効化 |
| Improvement | auto モード並列ツール呼び出し権限チェック | auto モードでの並列ツール呼び出しの権限チェックがキャッシュ効率的になり、チェック pending 中のモード切り替えが古い結果を適用せず確実にプロンプトを表示 |
| Improvement | auto モード権限チェックのプロンプトキャッシュコスト削減 | 決定間で会話プレフィックスのキャッシュを再利用することで、auto モード権限チェックのプロンプトキャッシュコスト削減 |
| Improvement | Stats パネルのキャッシュトークン表示 | Stats パネルでキャッシュトークンをトークン合計に含め、input、output、cache read、cache write の内訳を表示 |
| Improvement | `/ultrareview` エラーメッセージ改善 | リポジトリが base と履歴を共有しない場合の `/ultrareview` エラーメッセージを改善。ブランチのないチェックアウトは作成アドバイスとともに事前拒否され、拒否ヒントは完全なクローンに対して `git fetch --unshallow` を提案しなくなった |
| Improvement | Windows 起動プロセス読み取り | Windows 起動時のプロセス作成時刻を、PowerShell を起動せずネイティブ kernel32 呼び出しで読み取るよう改善。`powershell.exe` をゲートするエンドポイントセキュリティツールがプロンプトを出さなくなった |
| Changed | バックグラウンドセッションの挙動変更 | バックグラウンドセッションは、作業を保存するためにコミット・プッシュし、タスクが求める場合のみドラフト PR を開き、CLAUDE.md の git 指示に従い、常に作業の保存場所を報告して終了 |
| Changed | `/plugin install` のマーケットプレイスカタログ更新 | `/plugin install` は、プラグインが見つからない報告前に古いマーケットプレイスカタログを更新して再試行 |
| Changed | `/plugin` からインストールしたプラグインの即時有効化 | `/plugin` からインストールしたプラグインは、安全な場合に即座に有効化され、常に `/reload-plugins` を要求しなくなった |
| Changed | プラグイン `skills` パスでの `"."` 受け入れ | プラグインが `skills` パスとして `"."` を受け入れるようになり、ルートレベルの `SKILL.md` 検証エラーはプラグインルートの使用を提案 |
| Changed | `/status` でセッション種別表示 | `/status` がセッション種別を表示: `interactive`、または `attached` / `unattended` のバックグラウンドジョブ |
| Changed | 絵文字オートコンプリート別名対応 | 絵文字オートコンプリートが `:thumbsup:`、`:thumbsdown:`、`:love:` などの一般的な別名ショートコードを受け入れ |
| Changed | `/fork` セッションのワークツリー | `/fork` でフォークされたセッションは、元のセッションのチェックアウトではなく独自のワークツリーを作成 |
| Changed | Claude in Chrome のタブクローズ | Claude in Chrome が、不要になったブラウザタブを閉じるよう変更 |
| Changed | fast モードの usage credits 枯渇報告 | fast モードで、セッション中に usage credits が枯渇した場合、無言で失敗せずストリームで報告 |
| Changed | Monitor の出力なし終了報告 | Monitor で、出力を何も生成せずに終了した watch が "stream ended" ではなく明示的に報告 |
| Changed | Gateway `model` フィールド検証 | Gateway の `model` フィールド検証が変更され、非文字列値は転送されず 400 で拒否 |
| Removed | auto モード分類器待ちメッセージ削除 | 承認プロンプトから「Permission mode changed while the auto-mode classifier call was queued」通知の繰り返し表示を削除 |

## まとめ

v2.1.222 および v2.1.221 は、セキュリティ、接続安定性、使用量計測精度の向上に重点を置いたメンテナンスリリースです。v2.1.221 では VSCode の Focus ビュー機能とサンドボックス認証情報マスキングが導入され、開発体験と安全性が向上しました。v2.1.222 では、ワークツリー隔離セッションの権限制御強化、MCP サーバー使用量計測の修正、プロキシ環境での接続問題解決など、エンタープライズ環境での信頼性を高める多数の修正が実施されています。両バージョンとも、実際の利用シーンで報告されていた不具合に対応し、安定性と正確性を底上げする内容となっています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)