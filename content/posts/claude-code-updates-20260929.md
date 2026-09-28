---
title: "【Claude Code】v2.1.284 リリースノートまとめ"
date: 2026-09-29T08:02:57+09:00
draft: true
tags: ["claude-code", "claude-sonnet-5-5", "mcp", "ultracode", "claude-tag", "vscode", "remote-control", "google-cloud", "agent-sdk"]
categories: ["Claude Code Updates"]
summary: "v2.1.284 のClaude Codeリリースノートまとめ"
---

## Claude Code v2.1.284 リリースノート

## はじめに

Claude Code v2.1.284 は、モデルの更新、UI・操作性の改善、多数のバグ修正、および Claude Tag・VSCode 拡張向けの機能追加を含む大規模リリースです。

主な変更点は以下の通りです。

- **Claude Sonnet 5.5 をデフォルト Sonnet モデルとして追加**（Anthropic API）
- **`/mcp reconnect all` コマンドを追加**（失敗した MCP サーバーの一括再接続）
- **`/usage` およびステータスラインへのドル建て支出表示を追加**
- **Ultracode を独立したトグルとして分離**（`/effort` スライダーから独立）
- レスポンスストリーム破損、エラーハンドリング、vim モードなど多数の不具合修正
- VSCode・Claude Tag・Cloud Sessions 向けの改善・修正

---

## 注目アップデート深掘り

### Claude Sonnet 5.5 がデフォルト Sonnet モデルに

Anthropic API において、Claude Sonnet 5.5（`claude-sonnet-5-5`）がデフォルトの Sonnet モデルとして追加されました。1M コンテキストウィンドウを持ち、料金は入力 $2/Mtok・出力 $10/Mtok、キャッシュ読み取りは $0.20/Mtok です。

モデル ID を明示的に指定したい場合は `claude-sonnet-5-5` を使用します。なお、マネージドポリシーの `availableModels` が空の場合や、起動時のモデルが含まれていない場合にはスタートアップ警告が出るようになったため、ポリシー設定のある環境では確認が必要です。

---

### `/mcp reconnect all` による MCP サーバー一括再接続

インタラクティブターミナルに `/mcp reconnect all` コマンドが追加されました。接続に失敗した、または認証が必要な MCP サーバーをまとめて一度に再試行できます。

> **Note:** MCP（Model Context Protocol）は、Claude Code が外部ツールやサービスと連携するためのプロトコルです。

また、再開したセッションで MCP ツールコールが「No such tool available」エラーになる不具合も修正されており、サーバーが接続中の場合は最大 10 秒待機するようになりました。

---

## 実用的な活用ポイント

- **ドル建て支出の可視化**: `/usage` やステータスラインに `$271.40 / $500.00 spent this month` のような形式でゲートウェイのスペンドリミットに対する使用額が表示されます。`rate_limits.spend_limit` には `used_usd`・`limit_usd`・`period` フィールドも追加されています（ゲートウェイが本バージョン以降を実行している場合）。

- **Ultracode の独立トグル化**: Ultracode が `/effort` スライダーから独立し、Tab キーまたは `/effort ultracode [on|off]` で切り替え可能になりました。以前は xhigh effort を強制していましたが、変更後はどの effort レベルでも Ultracode をオン/オフできます。

- **自動モードのデフォルト化**: インタラクティブターミナルおよび VS Code セッションは、`permissions.defaultMode` が設定されていない場合、すべてのプランとプロバイダーで自動モードで起動するようになりました。

- **`/rate-limit-options` が `/help` に追加**: claude.ai サブスクライバー向けに `/rate-limit-options` コマンドが `/help` とコマンドメニューに追加されました。

---

## 全変更点一覧

| カテゴリ | 内容 |
|---|---|
| Feature | Claude Sonnet 5.5（`claude-sonnet-5-5`）を追加、Anthropic API のデフォルト Sonnet モデルに（1M コンテキスト、$2/$10 per Mtok、キャッシュ読み取り $0.20/Mtok） |
| Feature | 自動モードでのワーキングディレクトリ外読み取りプロンプトに「Yes, but ask again next time」選択肢を追加 |
| Feature | `/usage` とステータスラインにドル建て支出額を表示（`$271.40 / $500.00 spent this month` 形式）、`rate_limits.spend_limit` に `used_usd`・`limit_usd`・`period` フィールドを追加 |
| Feature | `effortSlider:decreaseEffort`・`increaseEffort`・`toggleUltracode` キーバインドアクションを追加（`keybindings.json` でリバインド可能） |
| Feature | `/rate-limit-options` を `/help` とコマンドメニューに追加（claude.ai サブスクライバー向け） |
| Feature | `/mcp reconnect all` をインタラクティブターミナルに追加（失敗・認証待ちの MCP サーバーを一括再試行） |
| Feature | マネージドポリシーの `availableModels` が空、またはモデルが除外されている場合の Claude apps ゲートウェイ起動警告を追加 |
| Feature | Claude apps ゲートウェイの `telemetry.forward_to` 宛先に `auth: { google: {} }` を追加（Google Cloud の OTLP エンドポイントへ直接テレメトリ出力） |
| Feature | Claude apps ゲートウェイとアイデンティティプロバイダー間の証明書クライアント認証（`private_key_jwt`）を追加 |
| Fix | 破損したレスポンスストリームが「JSON Parse error」や「undefined is not an object」等の生エラーを表示する、または「undefined」という文字列を回答に書き込む不具合を修正（リトライまたは中断レスポンスとして報告されるように） |
| Fix | thinking ブロック直後にオーバーロードまたはサーバーエラーが発生した場合、リトライされずにエラーでターンが終了する不具合を修正 |
| Fix | コンパクト後も「Prompt is too long」エラーが続く不具合を修正（コンパクト済みリクエストが長すぎる場合、直近の会話をより少なく保持してもう一度コンパクトを実行） |
| Fix | モデルが利用不可でフォールバックもない場合に「is currently unavailable」やクラウドセッションで「Something went wrong」が表示される不具合を修正（モデル利用不可通知と Learn more リンクを表示するように） |
| Fix | Agent SDK セッションで、ユーザーメッセージに不正な `source` を持つ画像が含まれている場合のクラッシュ、および不正なドキュメントブロック以降のすべてのターンでの失敗を修正（不正な画像は説明テキストに置換） |
| Fix | 再開セッションで MCP ツールコールが「No such tool available」になる不具合を修正（サーバー接続中は最大 10 秒待機） |
| Fix | plan-usage エンドポイントがレートリミットまたはログイン拒否した後、`/usage`・`/extra-usage`・IDE 使用量ビューが繰り返し問い合わせる不具合を修正（バックオフするように） |
| Fix | `claude mcp add` がマネージド設定で MCP サーバーをプラグインに制限している場合に成功と報告する不具合を修正（拒否して対処方法を表示） |
| Fix | `/plugin` 設定画面のブール値オプションがフリーテキストになっている不具合を修正（true/false 選択肢に変更、数値オプションは無効入力を拒否、←/→ でフィールド変更に） |
| Fix | `ANTHROPIC_FOUNDRY_RESOURCE` がバリデーションなしに Foundry エンドポイントホストに補間される不具合を修正（プレーンなリソース名以外は拒否） |
| Fix | Claude Desktop が Claude apps ゲートウェイ経由で 1M コンテキストオプションを表示しない不具合を修正（ゲートウェイが 1M 対応モデルを自動マーク） |
| Fix | シェルモードで ↓ キーが非表示のバックグラウンドタスクピルを選択し、Backspace と Ctrl+U によるプロンプト編集を妨げる不具合を修正 |
| Fix | 多数のプラグインが有効な場合に Windows で Bash ツールが失敗する不具合を修正（存在しないプラグイン `bin/` ディレクトリを PATH に追加しないよう、継承エントリの重複追加も解消） |
| Fix | 古い git（2.39 未満）で `sparsePaths` プラグインマーケットプレイスが空にクローンされ、ローカルコピーを上書きする不具合を修正 |
| Fix | トランスクリプトモードで `[` が会話をスクロールバックに書き込む際、フルスクリーンレンダリングがセッション上部のターミナル出力を消去する不具合を修正（macOS・Linux） |
| Fix | 返答のストリーミング中にスクロールアップしていた場合、完了時にスクロール位置が前メッセージまたは最下部にジャンプする不具合を修正 |
| Fix | `/config` や `/plugin` などダイアログのタブバーが狭いターミナルでタイトルやラベルを途中で折り返す不具合を修正（収まらないタブは丸ごと次行に移動） |
| Fix | `/model` ピッカーで最後のモデルまでスクロール後に「+1 model」が表示される不具合を修正（非表示行のモデル数のみカウント） |
| Fix | `/keybindings` が何もしないフッターアクションの Backspace・Delete バインドを `keybindings.json` に書き出す不具合を修正 |
| Fix | エージェントパネルの閉じるキー（`footer:close`）をリバインドした場合、閲覧中エージェントの行で「x」が入力される不具合を修正 |
| Fix | vim モードで `.` が SSH 経由・tmux 等での高速入力やブラケットペーストなしの貼り付けを繰り返さない不具合、および何も入力せずに変更を繰り返した後（`cw` → Esc 等）INSERT モードのままになる不具合を修正 |
| Fix | vim モードで最後の行での `dd` またはプロンプト末尾での `yy` 後、カーソルが画像プレースホルダーの `[` 上に残り `r` や `x` で画像が壊れる・消える不具合を修正 |
| Fix | ターミナルがフォーカスを取り戻した直後にキーを押すと Remote Control 有効化プロンプトに即答してしまう不具合を修正 |
| Fix | ホームディレクトリで起動した場合にレンダラー切り替えやアップデート後にワークスペーストラスト ダイアログが 2 度表示される不具合を修正 |
| Fix | プロジェクト外から `.claude/rules` にシンボリックリンクされたルールが外部インポート承認プロンプトを表示せずスキップされる不具合を修正 |
| Fix | マーケットプレイス・claude.ai・npm からのプラグインが、マネージド `allowManagedPermissionRulesOnly` 下で `allowed-tools` により自身のツールを事前承認する不具合を修正 |
| Fix | 依存関係のバージョン範囲を解決できない場合に最初の `claude plugin install` が失敗してもプラグインが有効かつ記録されたままになる不具合を修正 |
| Fix | フックが stdout にも書き込んだ場合、デバッグログが失敗フックの stderr を失い、出力のない失敗フックが何もログしない不具合を修正（失敗フックのステータスコードもログ） |
| Fix | Elicitation および ElicitationResult フックから返された `{"decision":"block"}` が無視される不具合を修正（終了コード 2 と同様に MCP エリシテーションを拒否するように） |
| Fix | `SendMessage` ツールなしで起動したセッション（Claude Desktop など）がそれを使って他のセッションにメッセージするよう指示される不具合を修正 |
| Fix | Remote Control 経由での写真送信が、キュー済みメッセージをターミナルプロンプトに戻して編集した際に失われる不具合と、キャプションなし写真でカーソルが 1 文字移動する不具合を修正 |
| Fix | 使用量制限の自動待機中にメッセージを入力すると、そのターンで再度制限に達した場合に「Continue automatically at usage limit」設定の制御から外れる不具合を修正 |
| Fix | 使用量制限の警告が最高 Max プランのユーザーに `/upgrade` を勧める不具合を修正（`/usage-credits` が利用可能な場合はそちらを案内） |
| Fix | Explore サブエージェントが、プロキシ経由のカスタムモデル等 Claude Code が認識しないモデル ID の場合に Claude API で Opus に切り替える不具合を修正（そのモデルを継承するように） |
| Fix | `/loop` のステータス更新がセルフペースモードで reasoning 内にのみ書かれるため表示されないことが多い不具合を修正（各更新とループ停止時の結果を可視テキストで出力） |
| Fix | macOS・Linux で Claude デスクトップアプリが作成した git worktree から `/ultrareview` を起動した場合にワーキングツリーのアップロードに失敗する不具合を修正 |
| Fix | 書き込み拒否かつ読み取り拒否ディレクトリを含むワーキングディレクトリで、Linux でサンドボックス化された Bash コマンドが起動できない不具合を修正 |
| Fix | アーティファクト DB の書き込み結果が、`data/users/` サブツリーへの書き込みをすべての閲覧者に見えるとクロードに誤って伝える不具合を修正（`as_level` に「view」レベルを追加） |
| Fix | アイデンティティプロバイダーが多数のグループを列挙するサインインからのリクエストに Claude apps ゲートウェイが `431 Request Header Fields Too Large` を返す不具合を修正（リクエストヘッダーを最大 256 KiB まで受け入れる） |
| Improvement | 使用量制限待機の表示を改善（制限の状態とカウントダウンがプロンプト下の 1 ブロックに統合、カウントダウンの繰り返し表示を解消） |
| Improvement | Chrome ツールがプレフィックスなしで呼び出された場合の「No such tool available」エラーを改善（呼び出すべきツール名を明示） |
| Improvement | Monitor イベント行を改善（各イベントが出力した内容を表示、変化のない「Waiting for N … to finish」行の繰り返しを解消） |
| Improvement | Workflow ツールのサンドボックスを、async スクリプトフックのエラー処理に対して強化 |
| Improvement | 起動時間とメモリ使用量を、実際に使用している設定スキーマ部分のみをビルドすることで改善 |
| Improvement | `/claude-api` の改善（`hillclimb` が測定できないほど小さいプロンプト変更のラウンドを省略、追加ページがネットワーク読み込み不要のローカルファイルとしてビルドされる） |
| Improvement | `/tasks`・`/copy`・`/hooks` 等のリストの表示を改善（名前の後の詳細が収まる場合は 1 列に整列、収まらない場合は右端に配置） |
| Improvement | `claude plugin marketplace add` が同名で異なるソースのマーケットプレイスを置き換える際に通知し、元に戻す方法を案内するように改善 |
| Improvement | マネージド設定がサインインを要求する場合（`forceLoginMethod` や `forceLoginOrgUUID`）に API キーやトークン・`apiKeyHelper` が設定されているとき、使用中の認証情報・設定場所・削除方法を明示する起動拒否メッセージに改善 |
| Improvement | 自動メモリ読み込みを改善（`MEMORY.md` と recalled memory ノートで不可視文字および Claude Code 自身のマークアップを模倣するタグを無害化してからクロードに渡す） |
| Improvement | `claude remote-control` を改善（未トラストのフォルダーでは終了せずにターミナル上でワークスペーストラストを確認） |
| Improvement | アーティファクトページを改善（Claude が設計プランを返信ではなくページ内に書き込み、既存の名前をページタイトルとして使用） |
| Improvement | Artifact ツールを改善（claude.ai のチャット・プロジェクトリンク、チャットからのアーティファクト、アーティファクト ID 単体が渡された場合に正しいリンクまたはコンテンツを要求） |
| Improvement | `/claude-api`: 詳細は上記参照 |
| Improvement | `/artifacts` フィルタータブをタイトル横に配置し、1 語ラベル（All・Mine・Shared）に変更（`/config` や `/plugin` と同じタブバーを使用） |
| Change | インタラクティブターミナルおよび VS Code セッションは、`permissions.defaultMode` が未設定の場合、すべてのプランとプロバイダーで自動モードで起動するよう変更 |
| Change | Ultracode を `/effort` の独立したトグルに変更（Tab または `/effort ultracode [on|off]`、xhigh effort の強制をなくし、どの effort レベルでも使用可能） |
| Change | 接続断後のリトライがリクエスト全体のリトライバジェットを共有するよう変更（失敗リクエストがより早く諦める） |
| Change | Sonnet モデルのセーフガードがメッセージをフラグした際の通知を、理由の説明と編集・リトライの提案に変更 |
| Change | `ANTHROPIC_DEFAULT_OPUS_MODEL` または `modelOverrides` で Opus モデルを固定したセッションでのセーフティ関連モデル切り替えを変更（Anthropic API では固定モデルではなく API がフラグの種類に応じたモデルを選択） |
| Change | 非インタラクティブの最初のターンで、`--allowedTools` または `mcp_tool` フックで指定された MCP サーバーが `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` が `0` でも最大 2 秒待機するよう変更 |
| Change | `/recap` がチャットスレッド・ルーティン・Webhook 経由でリレーされた場合に短い通知で拒否するよう変更（ターミナル直打ち・Claude apps・Remote Control・`-p`・SDK ホストでは従来通り動作） |
| Change | アーティファクト公開がネットワーク共有上のファイル（`\\host\share` パスまたは `/net` オートマウント）を、`--add-dir` で追加したマップ済みネットワークドライブ以外では拒否するよう変更 |
| Feature (VSCode) | 各プロンプトと返答の上にオプションの時刻表示を追加（日付変更行付き。「Claude Code: Show Message Timestamps」設定、デフォルト OFF） |
| Feature (VSCode) | Manage plugins 行にプラグイン読み込みエラーと注記を追加（無効化・アンインストール・エラーコピーのポップアップ付き） |
| Feature (VSCode) | Effort スライダー下に Ultracode オン/オフスイッチを追加（スライダーの Ultracode ストップを置換、どの effort レベルでもモデルピルに「· Ultracode」表示） |
| Fix (VSCode) | Memory ダイアログからの「Reload Claude」がファイル保存前に再起動する不具合を修正 |
| Fix (VSCode) | 別の Claude プロセスが開いているタブをリストア時に確認なく開く不具合を修正 |
| Fix (VSCode) | Focus ビューのセクションが、サブエージェント動作中またはセクション最初のステップがビューから外れた場合に自動的に閉じる不具合を修正 |
| Fix (VSCode) | `/model` と Enter でチャットに使用テキストが出力される不具合を修正（モデルセレクターが開くように） |
| Fix (VSCode) | Vertex・Bedrock・Foundry での `/feedback` が送信後に拒否される不具合を修正（ターミナル同様にコンピューター上に保存） |
| Fix (VSCode) | ウィンドウリロード後にサインインが Python 拡張を最大 1 分待つ不具合を修正 |
| Fix (VSCode) | Restart Extensions 後に Claude Code タブが応答しなくなる不具合を修正（会話を再度開くように） |
| Fix (VSCode) | 送信者が記録されていない他エージェントのメッセージが生 XML で表示される不具合を修正 |
| Fix (VSCode) | 他のエージェント・セッション・チャンネルからのメッセージがリロード後に消える不具合を修正 |
| Fix (VSCode) | `/mcp`・`/config`・`/settings` コマンドが拡張のダイアログに上書きされる不具合を修正 |
| Fix (VSCode) | ターンが実行されていない状態で Escape がすべてのバックグラウンドエージェントを停止する不具合を修正 |
| Fix (VSCode) | プラグインインストールリンクが同名の既存マーケットプレイスを置き換える不具合を修正 |
| Fix (VSCode) | メッセージに大きなテキストファイルが添付されている場合のコンパクション後「Prompt is too long」エラーを修正 |
| Fix (VSCode) | パスに非 ASCII 文字・スペース・角括弧を含むファイルへのチャットリンクが開かない不具合を修正 |
| Change (VSCode) | `claudeCode.environmentVariables` 設定内の `CLAUDE_CONFIG_DIR` が絶対パスの場合のみ適用され、チャットを継続するターミナルにも渡されるよう変更 |
| Fix (Cloud Sessions) | オフライン中にルーティンの Edit と Duplicate のコントロールがまだ読み込み中と表示される不具合を修正（オフラインであることを通知するように） |
| Feature (Claude Tag) | スレッド・チャンネルデフォルト・DM 向けに「Opus (latest)」等のモデルファミリー選択を追加（最新モデルに自動追従） |
| Feature (Claude Tag) | 組織全体の上限に対するスペンドと使用率を、アナリティクスのスペンドプロジェクションチャートに追加 |
| Fix (Claude Tag) | GitHub Enterprise ホスト名にアンダースコアが含まれる場合に旧 Claude in Slack アプリのプログレスカードとリンクプレビューがリポジトリと PR 作成ボタンを省略する不具合を修正 |
| Fix (Claude Tag) | チャンネルの環境が起動を拒否した場合に Claude が沈黙する不具合を修正（1 回の通知を投稿し、@メンション時に再試行するように） |
| Change (Claude Tag) | アカウント未接続のユーザーから @メンションされるたびにプライベートサインイン通知を送信するよう変更（初回のみから変更） |
| Improvement (Claude Tag) | 「Notify members now」を改善（Enterprise Grid 全ワークスペースへの一斉通知と大規模ワークスペースでのより多くのメンバーへの到達） |
| Improvement (Claude Tag) | オンデマンドランナーを持つセルフホスト環境での待機通知を改善（ランナーが起動中・再試行中・起動しないのいずれかを表示） |
| Improvement (Claude Tag) | チャンネルマネージャー追加失敗時のエラー表示を改善（Slack ワークスペースが組織に接続済みであることを確認できない場合） |
| Improvement (Claude Tag) | 管理設定のチャンネルアクセスリストを改善（コネクター・リポジトリ・プラグインと各ソースの表示） |
| Improvement (Claude Tag) | リポジトリをチャンネルマネージャーとして追加する際、リポジトリ管理者確認ができない場合に GitHub サインインを促すよう改善 |
| Fix (Code Review) | 未提出のレビューが既に開いている場合に Code Review が完成したレビューを投稿せずに諦める不具合を修正（投稿を先に再試行するように） |

---

## まとめ

v2.1.284 は、Claude Sonnet 5.5 のデフォルト化、Ultracode トグルの独立、自動モードのデフォルト化といった動作上の変更に加え、レスポンスストリーム破損・MCP ツール・vim モード・各種 UI など多岐にわたる不具合修正を含む大規模リリースです。VSCode 拡張・Claude Tag・Cloud Sessions それぞれにも機能追加と修正が行われています。変更量が多く、広範な安定性向上を目的とした内容が中心となっています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)