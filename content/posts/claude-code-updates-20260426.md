---
title: "【Claude Code】v2.1.120 リリースノートまとめ"
date: 2026-04-26T08:01:43+09:00
draft: true
tags: ["claude-code", "powershell", "ultrareview", "ci-cd", "skills", "claude-effort", "windows", "git-bash", "bash", "iac", "terraform", "cloudformation", "json", "mcp"]
categories: ["Claude Code Updates"]
summary: "v2.1.120 のClaude Codeリリースノートまとめ"
---

## はじめに

2026年4月26日、Claude Code **v2.1.120** がリリースされました。Feature 3件、Fix 1件、Improvement 2件の構成で、Windows 対応と CI 統合まわりの変更が中心です。

本記事で深掘りするのは次の 3 つ。

- **PowerShell をデフォルトシェルとして使用可能（Windows）** — Git Bash 不要、Windows 標準環境で動作
- **`/ultrareview` の CI/スクリプト統合対応** — `--json` オプションで CI パイプラインへの組み込みが可能
- **Skills 内で `${CLAUDE_EFFORT}` 変数参照が可能** — Skill 実行時に作業精度を動的に制御

Fix では危険な `rm` 操作の誤検知を修正、Improvement ではマルチライン Bash コマンドの権限プロンプト改善と UI 操作性の向上が含まれます。

---

## 注目アップデート深掘り

### PowerShellのデフォルトシェル化：Windows環境の開発体験を刷新

Windows環境におけるClaude Codeの利用がより自然になりました。従来はGit Bashなど外部シェル環境の導入が推奨されていましたが、v2.1.120からはPowerShellがデフォルトシェルとしてネイティブサポートされるようになりました。

**従来の問題：Bash 前提での Windows ギャップ**

Windows 環境では、開発者が標準で利用できるシェルは PowerShell またはコマンドプロンプトです。これまでClaude CodeがBash前提の挙動をしていた場合、Windows上でのスクリプト実行やコマンド生成にギャップが生じ、手動での変換作業や環境構築の手間が発生していました。今回の対応により、PowerShell 環境での AWS CLI、Azure CLI、Terraform などのインフラ管理ツールとの連携がシームレスになります。生成コードをそのまま Windows 端末で実行できるため、Bash 構文への手動変換や WSL 経由での実行といった迂回が不要になります。

**実務への影響**

たとえば、AWS環境のリソース状態確認やデプロイ自動化スクリプトを作成する際、Claude CodeがPowerShellの構文に沿ったコマンドやスクリプトを生成できるようになります。これにより、生成されたコードをそのままWindows端末で実行可能になり、Bash環境への変換やWSL経由での実行といった迂回策が不要になります。特に企業環境では、セキュリティポリシー上Git BashやWSLのインストールが制限されているケースもあり、標準のPowerShellで完結できる意義は大きいと言えます。

---

### `ultrareview`のCI/スクリプト統合対応：コードレビューの自動化基盤が完成

> **`/ultrareview` とは？**
> Claude Code のマルチエージェントコードレビュー機能を起動するスラッシュコマンドです。変更差分を元にセキュリティリスク・設定ミス・コード品質などを自動でレビューします。`--json` オプションを付けると結果が JSON 形式で出力され、CI パイプラインへの組み込みが容易になります。

`/ultrareview` コマンドが CI 環境やスクリプトからの呼び出しに対応しました。これにより、Claude Codeのコードレビュー機能をGitHub Actions、GitLab CI、Jenkins等のパイプラインに組み込み、プルリクエストやマージリクエストの品質チェックを自動化できるようになります。

**IaC レビューの見落としを自動検知する**

Infrastructure as Code（IaC）の文脈では、Terraform やクラウドネイティブなデプロイメント定義ファイル（CloudFormation、Helm charts、Kubernetes manifests など）のレビューは、セキュリティリスクや設定ミスを防ぐプロセスです。しかし、手動レビューだけでは見落としが発生しやすく、また専門知識を持つレビュアーのリソースも限られています。`ultrareview`をCI/CD統合することで、すべてのコード変更に対して一貫した品質基準でのレビューを自動実行でき、ヒューマンエラーを削減しつつレビュアーの負担も軽減できます。

**CI統合の実例**

リリースノートに明示的なコマンド例はありませんが、CI/スクリプト統合対応により、以下のようなワークフローが実現可能になります：

```bash
$ claude ultrareview --json
```

この`--json`オプションにより、レビュー結果が構造化されたJSON形式で出力されるため、CIパイプラインのステップとして組み込み、外部ツールやレポートシステムへ結果を連携しやすくなります。たとえば、TerraformのPRに対して自動レビューを実行し、検出された問題をGitHub Issueとして起票する、あるいは重大度に応じてマージをブロックする、といった運用が可能です。

**SRE業務での実践**

SREチームがCloudFormationやSAMテンプレートの変更をレビューする際、セキュリティグループの過度な開放、IAMロールの過剰権限、バックアップ設定の欠如など、見落としやすい設定ミスを`ultrareview`が自動検出できます。これをCI/CDパイプラインに組み込むことで、本番環境へのデプロイ前に問題を検知し、障害を未然に防ぐ仕組みが構築できます。

---

### Skills内での`${CLAUDE_EFFORT}`変数参照：動的な精度制御が可能に

Skills（Claude Codeの再利用可能なタスク定義機能）内で、`${CLAUDE_EFFORT}`変数を参照できるようになりました。この変更により、Skill実行時にEffort level（作業の精度・詳細度を制御するパラメータ）を動的に渡し、状況に応じて処理の深さを調整できるようになります。

> **Note:** Skillsは、Claude Codeで繰り返し使うタスクやワークフローを定義・再利用する機能です。`${CLAUDE_EFFORT}`は、Claude Codeが作業にかける精度や詳細度を制御する変数です。

**状況に応じた精度調整が必要な理由**

SRE 業務では、同じタスク（ログ分析、障害調査、パフォーマンス診断など）でも、状況によって求められる精度が異なります。たとえば、軽微なアラートの初動調査では迅速な概要把握が優先されますが、本番障害の根本原因分析では詳細かつ多角的な分析が必要です。従来、Skillを使う場合は固定された精度設定で実行されていたため、用途ごとに別のSkillを用意するか、実行後に手動で追加分析を行う必要がありました。`${CLAUDE_EFFORT}`を参照できるようになったことで、同じSkillを状況に応じて柔軟に使い分けられるようになります。

**実務への応用**

たとえば、「Kubernetesクラスタの異常ログ調査」Skillを定義しておき、通常のアラート対応では低いEffort levelで迅速に実行、一方で重大なインシデント発生時には高いEffort levelで詳細分析を実行する、といった運用が可能です。これにより、インシデント対応の初動速度を保ちながら、必要に応じて深掘り分析も同じSkillで実施できるため、運用スクリプトの管理が簡素化されます。

---

## 実用的な活用ポイント

今回のリリースは、日常の開発ワークフローと運用自動化の両面で実務上の利便性を高めています。

**Windows環境での開発効率化**

PowerShell ネイティブサポートにより、Windows 端末でのインフラ管理作業の手戻りが減ります。AWS CLI や Azure CLI を使ったリソース管理スクリプト、Terraform の実行スクリプトなどを Claude Code に生成・実行させる際、そのまま PowerShell で動作するコードが得られます。企業環境で標準支給 PC が Windows の場合、特に効果が出やすいです。

**CI/CDパイプラインへの統合**

`ultrareview`のCI/スクリプト統合対応により、GitHub ActionsやGitLab CIのワークフロー定義に`claude ultrareview --json`を組み込み、すべてのインフラコード変更に対して自動レビューを実施できます。JSON出力を利用すれば、レビュー結果をSlackに通知する、問題があればマージをブロックする、といった柔軟な連携が可能です。これにより、レビュープロセスの標準化と品質の底上げが実現できます。

**誤検知修正による安全性向上**

危険な`rm`操作の誤検知が修正されたことで、パイプラインや条件分岐を含む複雑なシェルスクリプトを実行する際の誤ったブロックが減少します。SREが本番環境のログローテーションスクリプトやクリーンアップタスクを実行する際、安全な操作が不当に警告されることなく、スムーズに作業を進められます。また、マルチラインbashコマンドの権限プロンプト改善により、複数行にわたるスクリプト実行時の確認が一度で済むようになり、対話的な操作の手間も削減されます。

**Effort制御の実践Tips**

Skills内で`${CLAUDE_EFFORT}`を活用する際は、インシデント管理ツール（PagerDuty、Opsgenie等）からのアラート重要度をEffort levelにマッピングする運用が考えられます。たとえば、SEV1インシデントではEffort=highで詳細分析、SEV3アラートではEffort=lowで迅速な初動対応、といった形でSkillを呼び出すことで、対応の迅速性と精度のバランスを最適化できます。

---

## 全変更点一覧

| カテゴリ       | 変更内容                                                                 | 概要                                                                                           |
|----------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Feature        | PowerShellをデフォルトシェルとして使用可能（Windows環境）                | Git Bash不要、Windows標準環境でClaude Codeが動作                                               |
| Feature        | `/ultrareview`コマンドのCI/スクリプト統合対応                            | `--json`オプション等によりCI/CDパイプラインへの組み込みが可能                                  |
| Feature        | Skills内で`${CLAUDE_EFFORT}`変数参照が可能                               | Skill実行時にEffort level（作業精度）を動的に制御可能                                          |
| Fix            | 危険な`rm`操作の誤検知を修正                                             | 安全なパイプライン処理が誤ってブロックされる問題を解消                                         |
| Improvement    | マルチラインbashコマンドの権限プロンプト改善                             | 複数行スクリプト実行時の確認が効率化                                                           |
| Improvement    | UI操作性の向上                                                           | 詳細は明示されていないが、全般的な使い勝手の向上                                               |

---

## まとめ

PowerShell 対応と `ultrareview` の CI 統合が今回の目玉です。PowerShell ネイティブサポートは、企業支給端末が Windows のチームで Git Bash や WSL の導入を回避していた手間を解消します。`ultrareview --json` の CI 統合は、IaC の PR レビューをパイプラインで継続実行できる基盤になります。

`${CLAUDE_EFFORT}` 変数は地味な変更ですが、インシデント対応の初動調査と深掘り分析を同じ Skill で使い分けたい SRE チームには効いてきます。危険な `rm` 操作の誤検知修正は、複雑なパイプライン処理を書く際の余計なブロックを解消する実用的な Fix です。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)