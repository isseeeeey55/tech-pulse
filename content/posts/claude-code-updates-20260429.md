---
title: "【Claude Code】v2.1.122・v2.1.121 リリースノートまとめ"
date: 2026-04-29T08:01:25+09:00
draft: false
tags: ["claude-code", "mcp", "bedrock", "vertex-ai", "opentelemetry", "mtls", "oauth", "sessions", "tools", "ui-improvement"]
categories: ["Claude Code Updates"]
summary: "v2.1.122・v2.1.121 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260429/header.png)

## はじめに

2026年4月29日、Claude Code の v2.1.122 および v2.1.121 が相次いでリリースされました。今回のアップデートでは、**MCP サーバーの安定性向上**と**クラウドプロバイダー連携の強化**が大きな柱となっています。

主な変更点は以下の通りです：

- **MCP サーバーの起動時自動リトライ（最大3回）** により、一時的なエラーで切断されたままになる問題を解消
- **`ANTHROPIC_BEDROCK_SERVICE_TIER` 環境変数**追加により、Bedrock のサービスティア（`default` / `flex` / `priority`）を明示選択可能に
- **`/resume` 検索ボックスへの PR URL 貼り付け対応**で、GitHub / GitHub Enterprise / GitLab / Bitbucket の PR を作成したセッションを呼び戻せる
- **Vertex AI の X.509 証明書ベース Workload Identity Federation（mTLS ADC）対応**で、エンタープライズ向けの認証選択肢が拡大
- **OpenTelemetry の `api_request` / `api_error` 数値属性**が文字列ではなく数値として送出されるよう修正
- **`/skills` のインクリメンタル検索**、**ダイアログのスクロール対応**、**`alwaysLoad` MCP オプション**など、開発体験の細部改善が多数

これらのアップデートは、エンタープライズ環境での運用安定性とセキュリティを重視した内容となっており、特に複数のクラウドプロバイダーを活用する組織にとって有益な機能強化が含まれています。

---

## 注目アップデート深掘り

### MCP サーバーの起動時リトライと claude.ai コネクタ重複表示

今回のリリースで最も注目すべきは、**MCP サーバーの安定性向上**に関する一連の改善です。v2.1.121 で起動時の自動リトライが実装され、v2.1.122 で claude.ai コネクタとの重複検出 UI が改善されました。

MCP（Model Context Protocol）サーバーは、Claude Code が外部ツールやデータソースと連携する際の中核的なコンポーネントです。しかし、ネットワークの一時的な不安定性やサーバー側の遅延により、起動時の接続が失敗するケースは実運用では避けられません。**v2.1.121 では、起動時に一過性のエラーが発生した MCP サーバーに対して最大3回まで自動リトライを行うようになりました**。従来は1回失敗するとそのまま `disconnected` 状態に留まっていたため、ユーザーが手動で再接続する必要がありました。

この変更がもたらす実質的なメリットは、**長時間稼働するセッションでの信頼性向上**です。特に CI/CD パイプラインに組み込んだ自動化タスクや、夜間バッチ処理など、人間の介入が難しいシナリオでの安定性が大幅に改善されます。あわせて v2.1.121 では、claude.ai コネクタが同一 URL で重複表示されていた問題を解消する重複排除も入っています。

さらに v2.1.122 では、**手動追加した MCP サーバーと同一 URL の claude.ai コネクタが隠蔽されていた問題**が改善されました。`/mcp` 上で隠れていたコネクタが「重複している手動エントリを削除してください」というヒント付きで表示されるようになり、設定が競合した際の原因特定が容易になります。また、`alwaysLoad: true` を MCP サーバー設定に指定すると、そのサーバーの全ツールがツール検索の遅延ロード対象から外れ、常に即時利用可能になる新オプションも v2.1.121 で追加されました。

### Bedrock サービスティアを環境変数で選択可能に

AWS Bedrock を利用しているユーザーにとって重要なアップデートが、**`ANTHROPIC_BEDROCK_SERVICE_TIER` 環境変数の追加**です（v2.1.122）。値として `default` / `flex` / `priority` の3種を取り、リクエスト時に `X-Amzn-Bedrock-Service-Tier` ヘッダーとして AWS 側に送出されます。

AWS Bedrock は用途に応じて複数のサービスティアを提供しており、`flex` はコスト効率重視、`priority` はスループットと低レイテンシ重視といった特性を持ちます。従来は Claude Code 側からティアを指定する手段がなく、AWS 側のデフォルト挙動に任せるしかありませんでしたが、今回のヘッダー連携により呼び出し単位での明示制御が可能になりました。

```bash
# 開発環境ではコスト重視
export ANTHROPIC_BEDROCK_SERVICE_TIER=flex

# 本番環境では低レイテンシ重視
export ANTHROPIC_BEDROCK_SERVICE_TIER=priority
```

この変更が重要な理由は、**ワークロード特性に応じたコスト・性能のバランス調整**が、コード変更なしで運用可能になる点です。シェルプロファイルや CI 環境の env で切り替えるだけで適用できるため、SRE やインフラエンジニアが環境ごとの予算管理・リソース配分を制御しやすくなります。なお、Bedrock application inference profile ARN を使う場合の不具合（`/model` の Effort オプションが表示されない、`output_config: Extra inputs are not permitted` エラー、`thinking.type.enabled is not supported` エラー）も今回まとめて修正されています。

---

## 実用的な活用ポイント

今回のアップデートを日常の開発ワークフローに活かすためのポイントをいくつか紹介します。

**PR URL でのセッション検索**は、コードレビュープロセスの効率化に直結します。`/resume` の検索ボックスに PR URL を貼り付けるだけで、その PR を作成した元セッションを呼び戻せます。GitHub に加え GitHub Enterprise・GitLab・Bitbucket にも対応しているため、企業内 Git ホスティングを使うチームでも横断的に利用できます。

**Vertex AI の mTLS 対応**は、X.509 証明書ベースの Workload Identity Federation（mTLS ADC）に対応する形で実装されました。サービスアカウントキーを発行せずに、ワークロード証明書で Vertex AI に認証できるようになり、長期クレデンシャル不要の運用が可能になります。あわせて、プロキシゲートウェイ越しに `count_tokens` エンドポイントが 400 を返していた不具合も修正されています。

**OpenTelemetry のログ出力改善**により、監視とトラブルシューティングの精度が向上しました。`api_request` / `api_error` の数値属性（トークン数やレイテンシなど）が文字列ではなく数値型で送出されるようになったため、Grafana や Datadog 側で数値集計・閾値アラートが正しく機能します。さらに `@`-mention 解決のための `claude_code.at_mention` ログイベントが追加され、`stop_reason` / `gen_ai.response.finish_reasons` / `user_system_prompt`（`OTEL_LOG_USER_PROMPTS` でゲート）も LLM リクエストスパンに含まれるようになりました。

**`/skills` の type-to-filter 検索ボックス**追加により、長いスキル一覧をスクロールせずに目的のものに到達できます。また、フルスクリーンモードでプロンプトに入力してもスクロール位置がボトムにジャンプしなくなり、ターミナル幅を超えるダイアログが矢印キー / PgUp / PgDn / マウスホイールでスクロール可能になるなど、ターミナル UI の細かなストレスが解消されました。`--dangerously-skip-permissions` 利用時に `.claude/skills/` `.claude/agents/` `.claude/commands/` への書き込みでもう確認を求められなくなった点も、ヘビーユーザーには嬉しい変更点でしょう。

---

## 全変更点一覧

| バージョン | カテゴリ | 変更内容 |
|---|---|---|
| 2.1.122 | Feature | `ANTHROPIC_BEDROCK_SERVICE_TIER`（`default`/`flex`/`priority`）で Bedrock サービスティアを選択、`X-Amzn-Bedrock-Service-Tier` ヘッダー送出 |
| 2.1.122 | Feature | `/resume` 検索ボックスに PR URL を貼ると、その PR を作成したセッションが見つかる（GitHub / GHE / GitLab / Bitbucket） |
| 2.1.122 | Feature | `/mcp` で手動追加サーバーに隠された claude.ai コネクタを表示し、重複削除を促すヒントを追加 |
| 2.1.122 | Improvement | OpenTelemetry: `api_request`/`api_error` の数値属性を文字列ではなく数値として送出 |
| 2.1.122 | Improvement | OpenTelemetry: `@`-mention 解決のための `claude_code.at_mention` ログイベント追加 |
| 2.1.122 | Fix | `/branch` がリワインド済みタイムラインを含むセッションで「tool_use ids without tool_result」を出していた問題 |
| 2.1.122 | Fix | Bedrock application inference profile ARN で `/model` の Effort オプションが出ない／`output_config` エラーを解消 |
| 2.1.122 | Fix | Vertex AI `count_tokens` エンドポイントがプロキシ越しに 400 を返していた不具合 |
| 2.1.122 | Fix | ToolSearch がセッション開始後に接続した MCP ツールを取りこぼしていた問題（nonblocking モード） |
| 2.1.122 | Fix | 新モデル向け画像が誤って 2576px にリサイズされていたのを正規の 2000px 上限に |
| 2.1.122 | Fix | `tmux -CC` 制御パイプがリモート制御セッションのアイドル状態再描画でフラッディングする問題 |
| 2.1.122 | Fix | 不正な hooks エントリで `settings.json` 全体が無効化されていた挙動を改善 |
| 2.1.121 | Feature | MCP サーバー設定の `alwaysLoad: true` で全ツールをツール検索の遅延ロード対象から除外 |
| 2.1.121 | Feature | `claude plugin prune` で孤立した自動インストール依存を削除、`plugin uninstall --prune` でカスケード削除 |
| 2.1.121 | Feature | `/skills` に type-to-filter 検索ボックスを追加 |
| 2.1.121 | Feature | PostToolUse hooks の `hookSpecificOutput.updatedToolOutput` で全ツールの出力を置換可能に |
| 2.1.121 | Feature | Vertex AI: X.509 証明書ベース Workload Identity Federation（mTLS ADC）対応 |
| 2.1.121 | Feature | MCP サーバーの起動時一過性エラーで最大3回まで自動リトライ |
| 2.1.121 | Improvement | フルスクリーンモードでプロンプトへの入力でスクロールが下に飛ばなくなった |
| 2.1.121 | Improvement | 行送りで折り返した URL を任意の行クリックでフルオープン |
| 2.1.121 | Improvement | `--dangerously-skip-permissions` が `.claude/skills/`・`agents/`・`commands/` の書き込みを再確認しなくなった |
| 2.1.121 | Improvement | `/terminal-setup` が iTerm2 の "Applications in terminal may access clipboard" を有効化（`/copy` が tmux 越しでも動作） |
| 2.1.121 | Fix | 多数画像処理時のメモリ無制限増加（マルチGB RSS）を修正 |
| 2.1.121 | Fix | `/usage` が大規模履歴で最大 ~2GB のメモリリーク |
| 2.1.121 | Fix | 起動ディレクトリが消えると Bash ツールが永続的に使用不能になる問題 |
| 2.1.121 | Fix | `--resume` が大規模セッションで破損した行で失敗 → 当該行をスキップして継続 |

---

## まとめ

v2.1.122 および v2.1.121 のリリースは、**安定性・セキュリティ・運用性**の三軸での着実な改善が特徴です。派手な新機能の追加よりも、日々の運用で直面する課題への丁寧な対応が目立ちます。

特に MCP サーバー周りの改善は、Claude Code をプロダクション環境で安心して運用するための基盤強化と言えます。自動リトライと重複検出により、長時間稼働や複雑な設定環境でのトラブルが減少するでしょう。

また、AWS Bedrock と Google Cloud Vertex AI という二大クラウドプロバイダーへの対応強化は、マルチクラウド戦略を採用する組織にとって朗報です。各クラウドの特性を活かした最適な運用が可能になります。

細かな UI 改善やバグ修正も多数含まれており、総合的な開発体験の向上が期待できるリリースと言えるでしょう。既存ユーザーは早めのアップデートを検討する価値があります。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code CHANGELOG (anthropics/claude-code)](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)