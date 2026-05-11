---
title: "【Claude Code】v2.1.139 リリースノートまとめ"
date: 2026-05-12T08:01:05+09:00
draft: false
tags: ["claude-code", "agent-view", "goal", "mcp", "hooks", "plugin"]
categories: ["Claude Code Updates"]
summary: "v2.1.139 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260512/header.png)

# Claude Code v2.1.139 リリース情報

## はじめに

2026年5月12日、Claude Code **v2.1.139** がリリースされました。本バージョンの目玉は、**全セッションを横断的に俯瞰する Agent View（Research Preview）** と、完了条件を宣言してターンを跨いで実行を継続させる **`/goal` コマンド**です。加えて hooks の機能拡張、プラグイン運用の可視化、MCP stdio サーバーへのプロジェクトパス注入など、運用上の不便を解消する地味で重要な改善が多数入っています。

主な変更点は以下の通りです：

- **Agent View（Research Preview）**: 実行中・ブロック中・完了済みのすべてのセッションを 1 つのリストで管理（`claude agents` で起動）
- **`/goal` コマンド**: 完了条件を設定し、ターンを跨いで自動継続。経過時間・ターン数・トークン数をオーバーレイ表示
- **`claude plugin details <name>`**: プラグインのコンポーネント構成と「1 セッションあたりの想定トークンコスト」を表示
- **MCP stdio サーバーへの `CLAUDE_PROJECT_DIR` 注入**: hooks と同様の挙動になり、プラグイン設定から `${CLAUDE_PROJECT_DIR}` 参照が可能に
- **Hook の機能拡張**: `args: string[]`（シェルを介さず exec する exec 形式）と PostToolUse 用 `continueOnBlock` の追加
- **`/scroll-speed` コマンド**: ホイールスクロール速度をライブプレビューで調整
- **transcript ビューのナビゲーション強化**: `?` でショートカット表示、`{` / `}` でプロンプト間ジャンプ、`v` でパネル切替

## 注目アップデート深掘り

### Agent View による横断的なセッション管理と /goal コマンド

今回のリリースの主役は、エージェント管理の抜本的な改善です。**Agent View は現時点で Research Preview** という位置付けで、`claude agents` コマンドで起動すると、実行中（running）、ユーザーの判断待ち（blocked on you）、完了済み（done）のすべての Claude Code セッションが 1 つのリストに集約されます。複数のリポジトリやチケットで並行作業しているケースでも、どのセッションが次に手を打つべき状態なのかが即座に判別できます。

セッション管理と相補的に追加された `/goal` コマンドは、**「完了条件」を宣言してエージェントに渡す**仕組みです。Claude はその完了条件が満たされるまでターンを跨いで作業を継続し、画面にはオーバーレイで**経過時間 / ターン数 / 累計トークン**をライブ表示します。インタラクティブ実行はもちろん、`-p`（print モード）と Remote Control からも利用できるため、長時間の改修やリファクタリングを「条件付きの自律実行」として走らせる運用が現実的になりました。

### Hook と MCP stdio の運用改善

hooks 周りでも実用的な改善が入りました。`args: string[]`（**exec 形式**）が追加され、シェルを介さずコマンドを直接 spawn できるため、パスのプレースホルダにクオートを足す必要がなくなります。また `PostToolUse` 向けに **`continueOnBlock` 設定**が新設され、`true` にすると hook が拒否した理由を Claude にフィードバックしつつターンを継続させる挙動が選べます。これまで「hook で止めるか・止めないか」の二択だったものが、「止めずに Claude に判断を委ねる」という第三の選択肢を持てるようになった点が実務上のメリットです。

MCP（Model Context Protocol）まわりでは、**stdio サーバーが `CLAUDE_PROJECT_DIR` を環境変数として受け取れるようになり**、hooks と同じプロジェクトパス参照が可能になりました。プラグイン設定の `commands` でも `${CLAUDE_PROJECT_DIR}` を解決できるようになっています。さらに `/mcp` の Reconnect は `.mcp.json` の編集を**再起動なしで反映**し、接続失敗時には HTTP ステータスと URL を表示するため、設定変更のフィードバックループが大幅に短縮されました。

> **Note:** MCP（Model Context Protocol）は、Claude Code が外部ツールやデータソースと連携するための標準プロトコルです。stdio は MCP がもともと対応する通信方式で、今回のリリースで新規追加されたわけではなく、**プロジェクトパスの自動注入**が追加された改善です。

### プラグイン運用とコストの可視化

プラグイン管理にも実務向きの改善が入りました。`claude plugin details <name>` で**プラグインのコンポーネント一覧と「1 セッションあたりの想定トークンコスト」**を確認できるようになり、導入前にコンテキスト消費量を見積もれます。あわせて `/context all` の per-skill トークン推定が**モデル固有のトークナイザ**を考慮し、丸めた値で表示されるようになりました。これらにより「どのプラグイン／スキルがコンテキストを食っているか」を測りながら入れ替えできるようになります。

API キーが設定されている環境では、**Remote Control・`/schedule`・claude.ai MCP コネクタ・通知設定が無効化**されるという挙動の変更も入りました。`ANTHROPIC_API_KEY` / `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` のいずれかが設定されている場合、たとえ claude.ai にもログイン済みでも上記機能は使えなくなるため、利用したい場合は API キーを外す必要があります。

## 実用的な活用ポイント

今回のアップデートにより、以下のような開発シーンで生産性の向上が期待できます：

- **長時間タスクの自律実行**: `/goal` で完了条件を宣言し、リファクタリングやテスト整備など複数ターンに跨る作業を放置気味に走らせる。経過時間・ターン数・トークン数のオーバーレイで暴走も検知できる
- **複数セッションの横断管理**: `claude agents` で Agent View を開けば、「ブロックされて待っている自分」が一目でわかるため、複数リポジトリでの並行作業の取りこぼしが減る
- **プラグインのコスト管理**: `claude plugin details <name>` と `/context all` の組合せで、プラグイン／スキルが消費するコンテキストを事前評価できる
- **hooks の段階的運用**: `args: string[]` 形式でパスのクオート問題を回避し、`continueOnBlock` で「ブロックではなくフィードバックして継続」する設計を選べる
- **API キー利用環境の注意**: API キー系の認証を使っている環境では Remote Control / `/schedule` / claude.ai MCP コネクタ等が無効化されるため、これらを併用したい場合は認証構成を見直す

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Agent View（Research Preview）追加 | `claude agents` でセッションを横断管理（running / blocked / done） |
| Feature | `/goal` コマンド | 完了条件を宣言してターン跨ぎ実行。経過時間・ターン数・トークン数を表示 |
| Feature | `/scroll-speed` コマンド | ホイールスクロール速度をライブプレビュー付きで調整 |
| Feature | `claude plugin details <name>` | コンポーネント構成と 1 セッションあたりの想定トークンコストを表示 |
| Feature | Transcript ナビゲーション | `?` でショートカット、`{`/`}` でプロンプト間ジャンプ、`v` でパネル切替 |
| Feature | Hook `args: string[]` | exec 形式でシェルを介さず spawn、パスのクオート不要 |
| Feature | Hook `continueOnBlock` | PostToolUse の拒否理由を Claude にフィードバックして継続 |
| Improvement | MCP stdio に `CLAUDE_PROJECT_DIR` 注入 | hooks と同じプロジェクトパスを参照可能 |
| Improvement | `/mcp` Reconnect | `.mcp.json` 編集を再起動なしで反映、失敗時に HTTP ステータスと URL を表示 |
| Improvement | `/context all` トークン推定 | モデル固有のトークナイザを使用し丸めた値で表示 |
| Improvement | Compaction プロンプト | 機密性の高いユーザー指示を保持するよう指示 |
| Change | API キー設定時の機能制限 | API キー利用時は Remote Control・`/schedule`・claude.ai MCP コネクタ・通知設定が無効化 |
| Fix | 各種不具合修正 | 認証デッドロック、SSE 16MB キャップ、`Skill(name *)` ワイルドカード等を多数修正 |

## まとめ

Claude Code v2.1.139 は、**「セッションの横断管理」と「完了条件付き自律実行」**という 2 軸でエージェント運用を一段引き上げるリリースです。Agent View と `/goal` の組合せで、複数の長時間タスクを同時並行で走らせつつ、ブロックされたものだけに人が介入する運用が現実味を帯びてきました。

加えて、hooks の exec 形式と `continueOnBlock`、MCP stdio への `CLAUDE_PROJECT_DIR` 注入、プラグインのコスト可視化といった改善は、いずれも「現場で運用していて気になっていたところ」を着実に潰す内容です。Agent View が Research Preview であることや、API キー使用時に Remote Control 系機能が無効化される挙動変更は導入前に押さえておくべきポイントですが、全体としては実運用での Claude Code 活用を一段進める価値のあるバージョンと言えます。

- 公式リリース: <https://github.com/anthropics/claude-code/releases/tag/v2.1.139>

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)