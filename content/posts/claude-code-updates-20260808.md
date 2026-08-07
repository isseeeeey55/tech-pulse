---
title: "【Claude Code】v2.1.224 リリースノートまとめ"
date: 2026-08-08T08:01:34+09:00
draft: true
tags: ["claude-code", "self-hosted-runner", "archive", "bedrock", "sendmessage", "listagents", "mcp", "remote-control", "vscode"]
categories: ["Claude Code Updates"]
summary: "v2.1.224 のClaude Codeリリースノートまとめ"
---

## はじめに

2026年8月8日、Claude Code v2.1.224 がリリースされました。本バージョンは、セルフホステッド環境の導入、クロスセッションメッセージング、Bedrock リージョン設定の柔軟化、サンドボックスのセキュリティ強化など、エンタープライズ向け機能の拡充が中心となっています。加えて、セッションディレクトリの衝突問題、サンドボックス拒否エントリのバイパス、MCP ツールの遅延通知など、複数の重要な不具合が修正されています。

---

## 注目アップデート深掘り

### セルフホステッド環境の導入

本リリースでは、`claude self-hosted-runner` コマンドによるセルフホステッド環境が追加されました。これにより、Team および Enterprise プランのユーザーは、自社のマシンやコンテナを Claude Code の web、mobile、desktop セッションの実行環境として利用できるようになります。

オンプレミス環境やプライベートクラウドでの運用が求められる組織では、外部サービスへの依存を最小限に抑えながら Claude Code の機能を活用できるため、コンプライアンス要件への対応が容易になります。公式リリースノートには具体的な使用方法やコマンドオプションの詳細は記載されていませんが、自社インフラ内での実行環境を確立できる点が大きな変更となります。

### クロスセッションメッセージングとセキュリティ設定

本バージョンでは、Claude Code セッション間でメッセージを送受信できる `SendMessage` 機能が追加され（macOS および Linux）、`ListAgents` でセッションを発見できるようになりました。また、`crossSessionInbound` と `dialogExpiry` 設定が導入され、権限をバイパスして実行中のセッションへのクロスセッションメッセージは承認待ちとなり、他のセッションへのメッセージは自動配信されます。

さらに、サンドボックスの認証情報マスキングオプションが大幅に拡充されました。構造化された環境変数の抽出（`extract` と `onExtractNoMatch`）、JWT 対応のマスキング（`decode: "jwt"` と `maskClaims`）、AWS SigV4 再署名（`awsPairs` / `sigv4`）が追加され、これらは `network.tlsTerminate` が必要で、user、managed、または `--settings` 設定からのみ有効化されます。チーム間の連携を強化しつつ、機密情報の取り扱いを厳密に制御できる仕組みが整備されています。

---

## 実用的な活用ポイント

セルフホステッド環境は、自社インフラ内での Claude Code 実行を可能にするため、データ主権やネットワーク分離が求められる環境での利用に適しています。クロスセッションメッセージングは、複数のマシンにまたがるセッション間での情報共有を可能にし、チームでの作業効率を向上させます。

Bedrock の `ANTHROPIC_BEDROCK_REGION_PREFIX` 環境変数を設定することで、`AWS_REGION` から導出されるプロファイルよりも特定のクロスリージョン推論プロファイルを優先できるようになり、リージョン選択の柔軟性が高まります。サンドボックスの認証情報マスキング機能は、AWS 認証情報や JWT トークンを含む環境での安全な実行を支援します。

セッションディレクトリの衝突問題の修正により、長いプロジェクトパスでのセッション管理が正確になり、サンドボックス拒否エントリのバイパス修正により、意図した通りのアクセス制御が機能するようになりました。

---

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | セルフホステッド環境 | `claude self-hosted-runner` で自社マシン・コンテナを実行環境化（Team/Enterprise プラン） |
| Feature | `archive` プラグインソース | ZIP over HTTPS でプラグインをインストール、SHA-256 ピニング対応、git/npm 不要 |
| Feature | クロスセッションメッセージング | `SendMessage` と `ListAgents` でセッション間メッセージング（macOS/Linux） |
| Feature | Bedrock リージョン設定 | `ANTHROPIC_BEDROCK_REGION_PREFIX` 環境変数で特定のクロスリージョン推論プロファイルを優先 |
| Feature | セキュリティ設定 | `crossSessionInbound` / `dialogExpiry` で権限バイパス時のメッセージ承認制御 |
| Feature | サンドボックス認証情報マスキング | `extract` / `onExtractNoMatch` / `decode: "jwt"` / `maskClaims` / `awsPairs` / `sigv4` を追加（`network.tlsTerminate` 必要、user/managed/`--settings` のみ） |
| Feature | ペースト削除時の確認 | 利用不可ペーストの削除がコマンドテキストを変更する際にキャンセル・確認ステップを追加 |
| Fix | 長いプロジェクトパス | 200 文字超のパスが共有接頭辞下の別プロジェクトセッションディレクトリに解決される問題を修正 |
| Fix | `SendMessage` エラー報告 | チームメイトの inbox への書き込み失敗を「送信成功」と誤報告していた問題を修正 |
| Fix | サンドボックス拒否エントリ | 末尾スラッシュ付き（`denyRead: "~/.aws/"`）の拒否エントリが Linux/macOS でバイパス可能だった問題を修正 |
| Fix | サンドボックス違反詳細 | Bash ツール結果にサンドボックス違反詳細が表示されず、Claude が拒否理由を見られなかった問題を修正 |
| Fix | MCP ツール遅延 | ターン途中で接続した MCP ツールがツール検索で遅延され、名前がモデルに通知されなかった問題を修正 |
| Fix | プラグインインストール記録 | 同一プラグインを複数プロジェクトにインストール時に記録が破損していた問題を修正 |
| Fix | ペースト内容復元 | ペースト内容の復元時に、期限切れやプレースホルダー番号衝突で誤データ添付やテキスト喪失が発生していた問題を修正 |
| Fix | Wayland コピー | Wayland での選択時コピーがクリップボードに届かないことがあった問題を修正（2 つの選択書き込みが競合しなくなった） |
| Fix | フィードバック調査のトランスクリプト共有 | 長いセッションでトランスクリプト共有が失敗しても成功メッセージを表示していた問題を修正 |
| Fix | Remote Control 自動起動 | ログイントークンが古い状態でのコールドスタート時に "Remote credentials fetch failed" で失敗していた問題を修正 |
| Fix | Remote Control/SDK ブランクメッセージ | `/clear` など出力のないコマンド後に空白の "(no content)" メッセージを表示していた問題を修正 |
| Fix | Remote Control 履歴アップロード | サーバーセッション期限切れ後に再作成されたセッションに、以前のローカル会話履歴がアップロードされていた問題を修正 |
| Fix | VSCode Remote Control 接続表示 | 接続失敗後も Remote Control を接続中と表示していた問題を修正 |
| Fix | セッション再開時の Remote Control 再接続 | ユーザーが無効化した Remote Control が、セッション再開時に再接続されていた問題を修正（`--resume`、SDK ホスト、VSCode 拡張） |
| Fix | VSCode `remoteControlAtStartup` | 明示的に有効化した際に `remoteControlAtStartup` が無視されていた問題を修正 |
| Improvement | フルスクリーンモード | 繰り返しコンパクション後も完全な圧縮前履歴をスクロールバックに保持（直近区間のみでなく） |
| Improvement | Remote Control コンパクション | アタッチされた web/mobile クライアントにコンパクション進捗と境界を表示、`/clear` リセットを伝播 |
| Improvement | Remote Control 接続失敗表示 | 接続失敗時に詳細と再接続ショートカット付きの永続的な失敗インジケーターを表示（8 秒トーストのみでなく） |
| Breaking | サブエージェント上限削除 | セッションあたり 200 サブエージェントの生成上限を削除（並行数・深さ制限は継続） |
| Improvement | マネージド設定承認 | 組織設定が変更されていない場合、再ログインや組織切り替え後に承認プロンプトを再表示しない |
| Improvement | フィードバック調査のトランスクリプト共有 | 同意時に最終リクエストのモデル設定（システムプロンプト/`CLAUDE.md`/ツール定義/パラメータ）もアップロード。シークレット削除は継続、サイズ超過時は優先的に削除 |
| Improvement | Bash ツール説明 | コマンド出力がモデルには表示されるが、ユーザーには確実に表示されない旨を常に記載 |
| Improvement | ペーストプレースホルダー番号 | 入力に受け入れられた際にプレースホルダー番号を再採番 |
| Improvement | Remote Control セッションアーカイブ | コンパクションや `/resume` 後に新セッションが作成された際、古いサーバーセッションを死んだままリストに残さずアーカイブ |

---

## まとめ

v2.1.224 は、セルフホステッド環境、クロスセッションメッセージング、Bedrock リージョン制御、サンドボックスのセキュリティ強化など、エンタープライズ環境での利用を前提とした機能拡充が目立つリリースです。同時に、セッションディレクトリの衝突、サンドボックス拒否エントリのバイパス、MCP ツールの遅延通知など、重要な不具合が修正され、安定性と信頼性が向上しています。Remote Control やフルスクリーンモードの改善により、複数クライアント環境での利用体験も強化されています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)