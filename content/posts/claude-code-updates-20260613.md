---
title: "【Claude Code】v2.1.176・v2.1.175・v2.1.174 リリースノートまとめ"
date: 2026-06-13T08:01:44+09:00
draft: false
tags: ["claude-code", "bedrock", "remote-control", "vscode", "mcp"]
categories: ["Claude Code Updates"]
summary: "v2.1.176・v2.1.175・v2.1.174 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260613/header.png)

# Claude Code v2.1.176・v2.1.175・v2.1.174 リリース情報

## はじめに

2026年6月13日、Claude Code の3つの連続バージョン（v2.1.176・v2.1.175・v2.1.174）がリリースされました。v2.1.176では多言語対応のセッションタイトル生成やBedrock認証情報のキャッシング改善、モデル選択の制御強化など幅広い機能改善とバグ修正が行われました。v2.1.175ではエンタープライズ環境向けの厳格なモデル管理機能 `enforceAvailableModels` が追加され、v2.1.174ではUIの操作性向上とBedrock GovCloud対応の修正、VSCode拡張機能での詳細な使用状況表示が実装されています。

## 注目アップデート深掘り

### 1. エンタープライズ向けモデル管理の厳格化（v2.1.175・v2.1.176）

v2.1.175で追加された `enforceAvailableModels` 管理設定は、エンタープライズ環境におけるモデル選択のガバナンスを強化します。この設定を有効化すると、`availableModels` 許可リストがDefaultモデルにも適用され、許可されていないモデルに解決されるDefaultは自動的に許可リスト内の最初のモデルにフォールバックします。さらに、ユーザーやプロジェクトの設定で管理者が定めた `availableModels` リストを拡大することができなくなります。

v2.1.176ではこの仕組みをさらに強化し、`availableModels` の強制適用が改善されました。エイリアスモデルの選択が `ANTHROPIC_DEFAULT_*_MODEL` 環境変数を通じてブロックされたモデルへリダイレクトされることを防止し、`/fast` トグルが許可リスト外のモデルへの切り替えを試みる場合は操作を拒否するようになりました。

### 2. Bedrock認証情報のキャッシング改善とGovCloud対応修正（v2.1.176・v2.1.174）

v2.1.176では、Bedrock認証情報のキャッシング動作が改善されました。従来は固定の1時間でキャッシュされていましたが、`awsCredentialExport` から取得した認証情報に含まれる `Expiration` フィールドに基づいてキャッシュが保持されるようになり、不要な再認証を削減できます。

v2.1.174では、Bedrock GovCloudリージョン（`us-gov-*`）において誤った推論プロファイルプレフィックスが導出されていた問題が修正されました。従来は `global` プレフィックスが使用されていましたが、正しく `us-gov` が使われるようになり、400エラーが解消されました。

## 実用的な活用ポイント

エンタープライズ管理者は、`enforceAvailableModels` 設定を有効化することで、組織のコンプライアンス要件に沿ったモデル利用を徹底できます。この設定により、ユーザーが個別に設定を変更して許可されていないモデルを使用するリスクを排除できます。

Bedrock認証情報のキャッシング改善により、一時的な認証情報を使用する環境では、認証情報の有効期限まで再取得が不要となり、APIリクエストの効率が向上します。GovCloudリージョンを利用する組織では、v2.1.174以降で正常に推論プロファイルが解決されるようになります。

多言語チームでは、v2.1.176の `language` 設定を使用することで、会話の言語に合わせたセッションタイトルが自動生成されます。また、`footerLinksRegexes` 設定を活用すれば、フッター行に正規表現でマッチするリンクバッジを表示し、プロジェクト固有のリソースへ素早くアクセスできます。

## 全変更点一覧

| バージョン | カテゴリ | 内容 | 概要 |
|-----------|---------|------|------|
| v2.1.176 | Feature | Session titles language support | セッションタイトルが会話の言語で生成される。`language` 設定で言語を固定可能 |
| v2.1.176 | Feature | `footerLinksRegexes` setting | フッター行に正規表現マッチするリンクバッジを表示する設定を追加 |
| v2.1.176 | Improvement | Bedrock credential caching | `awsCredentialExport` の認証情報が `Expiration` まで（従来の固定1時間ではなく）キャッシュされるように改善 |
| v2.1.176 | Fix | `availableModels` enforcement | エイリアスモデルが `ANTHROPIC_DEFAULT_*_MODEL` 環境変数でブロックされたモデルにリダイレクトされる問題と、`/fast` が許可リスト外モデルに切り替わる問題を修正 |
| v2.1.176 | Fix | Auto mode Fable 5 fallback | Opus 4.8が有効でない組織でFable 5の自動モードが失敗する問題を修正。分類器が利用可能な最良のOpusモデルにフォールバックするように |
| v2.1.176 | Fix | Hook `if` conditions for tool paths | `Edit(src/**)`, `Read(~/.ssh/**)`, `Read(.env)` などのパターンが正しくマッチするように修正 |
| v2.1.176 | Fix | Linux sandbox with symlinked settings | `.claude/settings.json` が絶対パスのシンボリックリンクの場合にLinuxサンドボックスが起動しない問題を修正 |
| v2.1.176 | Fix | `/copy` and clipboard in tmux/SSH | tmux over SSHで `/copy` やマウス選択コピーがシステムクリップボードに届かない問題と、tmux 3.2未満でペーストバッファがロードされない問題を修正 |
| v2.1.176 | Fix | Remote Control model switching | Web/モバイルからRemote Control接続時にセッションのモデルが無言で切り替わる問題を修正 |
| v2.1.176 | Fix | Remote Control disconnect notifications | 切断通知が数値コードではなく人間が読める理由を表示するように修正。接続失敗時の重複行も修正 |
| v2.1.176 | Fix | Remote Control account switching | 別アカウントにサインインした際にRemote Controlセッションが切断されない問題を修正 |
| v2.1.176 | Fix | `/cd` and git branch reporting | `/cd` やworktree移動後にセッションが前ディレクトリのgitブランチを報告し続ける問題を修正 |
| v2.1.176 | Fix | `claude agents` navigation | 1つのウィンドウで戻る操作をすると、同じセッションに接続された他のウィンドウがデタッチされる問題を修正 |
| v2.1.176 | Fix | Backgrounded sessions "Working" status | `/bg` でターン途中にバックグラウンド化し、続行すべき内容がない場合に "Working" が永久に表示される問題を修正 |
| v2.1.176 | Fix | Background agent search by PR URL | スケジュールされたウェイクアップ中やジョブブロック中に開かれたPRが `claude agents` 検索に表示されない問題を修正 |
| v2.1.176 | Fix | Agents view text cursor on Windows | Windowsでエージェントビューの入力欄にテキストカーソルが表示されない問題を修正 |
| v2.1.176 | Fix | `claude --bg -cn <name>` name seeding | セッション名がシードされない問題を修正 |
| v2.1.176 | Fix | Background sessions Windows network paths | Windowsネットワークパスが永続化された状態で再起動前に正規化されるように修正 |
| v2.1.176 | Fix | Background-session respawn with malformed IDs | 破損した状態ファイルからの不正なresume IDで再起動が拒否される問題を修正 |
| v2.1.176 | Fix | Windows daemon startup with ReadOnly attribute | `~/.claude/daemon` にReadOnly属性が設定されているとWindowsバックグラウンドサービスデーモンが起動しない問題を修正 |
| v2.1.176 | Fix | Cloud sessions authentication timeout | 長時間アイドル後にクレームされたクラウドセッションが "Could not resolve authentication method" で失敗する問題を修正 |
| v2.1.176 | Improvement | Background session auto-update guidance | 自動更新をまたいだウィンドウで返信を送信できない場合のガイダンスを明確化。`claude daemon status` がバージョンスキュー動作を説明 |
| v2.1.175 | Feature | `enforceAvailableModels` managed setting | 有効時、`availableModels` 許可リストがDefaultモデルも制約し、ユーザー/プロジェクト設定で管理された `availableModels` リストを拡大できなくなる |
| v2.1.174 | Feature | `wheelScrollAccelerationEnabled` setting | フルスクリーンモードでマウスホイールスクロール加速を無効化する設定を追加 |
| v2.1.174 | Fix | `/model` picker model family visibility | Defaultが解決するモデルファミリーが非表示になる問題を修正。Max/Team Premium/EnterpriseではOpusが独立行に、Pro/TeamではSonnetが、従量課金APIアカウントではOpusが表示される |
| v2.1.174 | Fix | `/model` picker Sonnet version label | `ANTHROPIC_DEFAULT_SONNET_MODEL` が異なるSonnetを指定している場合にハードコードされたSonnetバージョンラベルが表示される問題を修正 |
| v2.1.174 | Fix | Fable 5 usage credits banner | 使用量ベース課金のエンタープライズアカウントで誤ってFable 5の使用量クレジット消費バナーが表示される問題を修正 |
| v2.1.174 | Fix | Bedrock GovCloud inference profile prefix | GovCloudリージョン（`us-gov-*`）で誤った推論プロファイルプレフィックス（`us-gov` ではなく `global`）が導出され、400エラーが発生する問題を修正 |
| v2.1.174 | Fix | Background sessions env inheritance | バックグラウンドセッションがデーモンを起動したシェルから他セッションの `ANTHROPIC_*` プロバイダ環境変数（ゲートウェイURL、カスタムヘッダー、`/model` エイリアス）を継承する問題を修正 |
| v2.1.174 | Fix | macOS/Linux exit pause after interrupted command | macOS/Linuxでシェルコマンドが中断/終了された直後にClaude Codeを終了する際の1〜2秒の停止を修正 |
| v2.1.174 | Fix | Git commit co-author model name | 一部のモデルでgitコミットの共同著者アトリビューションに誤ったモデル名が表示される問題を修正 |
| v2.1.174 | Fix | `/advisor` dialog blocked model pre-selection | `availableModels` 許可リストでブロックされた保存済みアドバイザーモデルが `/advisor` ダイアログで事前選択される問題を修正 |
| v2.1.174 | Fix | Skill hot-reload efficiency | スキルのホットリロード時に単一スキルの変更でもスキルリスト全体が再送信される問題を修正。変更されたスキルのみが再通知されるように |
| v2.1.174 | Fix | Workflow tool subagent attribution headers | Workflow tool の `agent()` サブエージェントがエージェントごとのアトリビューションヘッダーを欠落していた問題を修正 |
| v2.1.174 | Feature | [VSCode] Usage attribution dialog | アカウント＆使用状況ダイアログ（`/usage`）に、過去24時間/7日間のキャッシュミス、ロングコンテキスト、サブエージェント、スキル/エージェント/プラグイン/MCPごとの内訳を表示する使用状況アトリビューション機能を追加 |
| v2.1.174 | Fix | Pre-warmed background workers authentication | アイドル状態で待機した後にクレームされたプリウォーム済みバックグラウンドワーカーが "Could not resolve authentication method" で失敗する問題を修正 |

## まとめ

今回の3バージョンでは、エンタープライズ環境でのモデル管理の厳格化（v2.1.175の `enforceAvailableModels`、v2.1.176の強制適用改善）が最も重要な変更です。組織のガバナンス要件に応じた柔軟かつ厳密なモデル制御が可能になりました。

v2.1.176では多言語対応のセッションタイトル生成やBedrock認証情報のキャッシング改善といった機能強化に加え、Remote Control、バックグラウンドセッション、Hookパターンマッチング、tmux/SSH環境でのクリップボード操作など、多岐にわたる不具合が修正されています。v2.1.174ではBedrock GovCloudリージョンの対応修正やVSCode拡張での詳細な使用状況トラッキング機能が追加され、操作性とモニタリング能力が向上しました。

全体として、エンタープライズ環境での統制機能の強化と、日常的な開発ワークフローにおける細かな不具合の解消が進んでおり、安定性と管理性が大きく改善されたリリースといえます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)