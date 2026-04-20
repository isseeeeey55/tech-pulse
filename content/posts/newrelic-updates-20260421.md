---
title: "【New Relic】2026/04/21 のアップデートまとめ"
date: 2026-04-21T08:01:08+09:00
draft: true
tags: ["newrelic", "infrastructure-agent", "security", "windows", "aws", "ecs", "ec2"]
categories: ["New Relic Updates"]
summary: "2026/04/21 のNew Relicアップデートまとめ"
---

## はじめに

2026年4月21日、New Relic から Infrastructure Agent のアップデートがリリースされました。今回は1件のアップデートですが、セキュリティ強化と運用自動化の観点で重要な内容を含んでいます。Infrastructure Agent 1.74.1 では、Windows Docker イメージ作成プロセスの自動化、Go言語ランタイムのバージョンアップによるセキュリティパッチ適用が行われており、特に Windows 環境で New Relic を運用している SRE にとって見逃せない更新となっています。

---

## 注目アップデート深掘り

### Infrastructure Agent 1.74.1 - セキュリティと運用自動化の強化

Infrastructure Agent 1.74.1 は、一見マイナーアップデートに見えますが、実は運用の信頼性とセキュリティ面で重要な改善が施されています。主な変更点は Go 言語ランタイムの v1.25.9 へのアップグレードと、Windows Docker イメージビルドプロセスの自動化です。

**なぜこのアップデートが重要なのか**

Go 言語のアップデートには、通常複数のセキュリティパッチとパフォーマンス改善が含まれています。Infrastructure Agent は常時稼働し、システムメトリクスやログを収集する性質上、エージェント自体の脆弱性は監視対象システム全体のセキュリティリスクに直結します。特に AWS 環境では、エージェントが IAM ロールを通じてクラウドリソースにアクセスするケースも多く、エージェントの安全性確保は最優先事項です。

また、Windows Docker イメージ作成の自動化は、リリースサイクルの短縮化とビルド品質の均一化に貢献します。これにより、今後の Windows 環境向けアップデートがより迅速に提供されることが期待できます。

**SRE日常業務への具体的な影響**

監視設定面では、エージェントの安定性向上により、メトリクス収集の欠損リスクが低減します。特に長時間稼働する Windows EC2 インスタンスや ECS の Windows コンテナでは、エージェントのメモリリークや予期しないクラッシュが監視ブラインドスポットを生む原因となるため、こうした安定性改善は障害検知の信頼性向上に直結します。

パフォーマンスチューニングの観点では、Go ランタイムの改善により、エージェント自体のリソース消費が最適化される可能性があります。Infrastructure Agent は CPU とメモリの使用率が比較的低いものの、大量のログやメトリクスを処理する環境では、わずかな改善でもホストリソースの節約につながります。

**アップグレード手順**

Linux 環境（Amazon Linux 2、Ubuntu 等）での標準的なアップグレード手順は以下の通りです。

```bash
# yum ベースのディストリビューション（Amazon Linux 2 等）
$ sudo yum update newrelic-infra

# apt ベースのディストリビューション（Ubuntu 等）
$ sudo apt-get update
$ sudo apt-get install --only-upgrade newrelic-infra

# アップグレード後のバージョン確認
$ newrelic-infra --version
```

Windows 環境では、PowerShell から以下のように実行します。

```powershell
# Chocolatey を使用している場合
PS> choco upgrade newrelic-infra

# MSI インストーラーを使用している場合は、新しいバージョンをダウンロードして上書きインストール
```

ECS on EC2 や ECS Fargate で Windows コンテナを使用している場合は、タスク定義のコンテナイメージタグを更新します。

```yaml
# ECS タスク定義（JSON 抜粋）
{
  "containerDefinitions": [
    {
      "name": "newrelic-infra",
      "image": "newrelic/infrastructure:1.74.1-windows",
      "essential": false,
      "environment": [
        {
          "name": "NRAA_LICENSE_KEY",
          "value": "YOUR_LICENSE_KEY"
        }
      ]
    }
  ]
}
```

**Before/After の比較**

- **Before（1.74.0 以前）**: Go 1.25.8 ランタイムを使用。既知の脆弱性を含む可能性があり、セキュリティスキャンでアラートが出るケースも
- **After（1.74.1）**: Go 1.25.9 ランタイムに更新。セキュリティパッチ適用済みで、コンプライアンス要件を満たしやすくなる

> **Note:** Infrastructure Agent は New Relic の基盤となるエージェントで、ホストやコンテナからシステムメトリクス、プロセス情報、ネットワーク統計を収集し、New Relic プラットフォームに送信します。オンホストインテグレーション（MySQL、Nginx、Redis 等）や flex integration と組み合わせることで、多様な監視シナリオに対応できます。

---

## SRE視点での活用ポイント

**監視・アラート・ダッシュボードの改善**

Infrastructure Agent の安定性向上は、監視データの連続性を保証します。特にアラート設定において、エージェントのクラッシュによる「データ欠損」を原因とする誤検知が減少するため、アラート疲れ（alert fatigue）の軽減につながります。NRQL を使用したカスタムアラート条件では、`SystemSample` や `ProcessSample` といったイベントデータの欠損が SLO 計算に影響を与えることがありますが、エージェントの信頼性向上によりこうしたリスクが低減します。

**AWS 環境での運用における影響**

EC2 インスタンスで Infrastructure Agent を運用している場合、セキュリティグループやネットワーク ACL の設定により、エージェントが New Relic エンドポイント（`https://infra-api.newrelic.com`）と通信できることを確認してください。また、ECS タスクで使用する場合、タスクロールに適切な権限（CloudWatch Logs へのログ出力権限など）が付与されていることを確認しましょう。

Lambda 環境では Infrastructure Agent は直接使用しませんが、Lambda Extension を通じて類似の機能を提供します。今回のアップデートは Infrastructure Agent のみですが、今後の Extension アップデートにも同様のセキュリティ改善が反映される可能性があります。

**すぐに試せる Tips**

まず、非本番環境（dev/staging）で新バージョンのエージェントを展開し、24〜48時間のメトリクス収集が正常に行われることを確認してください。New Relic UI で `Infrastructure > Hosts` から該当ホストを選択し、CPU、メモリ、ディスク I/O のグラフに異常なギャップがないかチェックします。

```sql
-- NRQL でエージェントバージョンを確認するクエリ
SELECT latest(agentVersion) 
FROM SystemSample 
FACET hostname 
SINCE 1 day ago
```

**アップグレード時の注意点とリスク**

Infrastructure Agent のアップグレードは通常、サービスの再起動を伴います。Linux 環境では `systemctl restart newrelic-infra`、Windows 環境では `Restart-Service newrelic-infra` が実行されます。この間、数秒〜数十秒のメトリクス収集の中断が発生しますが、データは再起動後に再開されるため、履歴データへの影響はありません。

ただし、カスタム統合（flex integration や オンホストインテグレーション）を多数設定している場合、設定ファイルの互換性を事前に確認してください。特に `integrations.d` ディレクトリ配下の YAML 設定に依存している場合、エージェントのアップグレード前にバックアップを取得しておくことを推奨します。

また、Auto Scaling Group や ECS サービスで Infrastructure Agent を含むイメージを使用している場合、新しいインスタンスやタスクが起動する際に自動的に新バージョンが適用されるよう、AMI や Docker イメージの更新を計画してください。

> **Note:** NRQL（New Relic Query Language）は、New Relic に保存されたテレメトリデータをクエリするための SQL ライクな言語です。`SystemSample` はホストのシステムメトリクス、`ProcessSample` はプロセスメトリクスを格納するイベントタイプです。

---

## 全アップデート一覧

| カテゴリ | バージョン | 概要 |
|---------|-----------|------|
| Infrastructure Agent | 1.74.1 | Windows Docker イメージ作成の自動化、Go 言語を v1.25.9 にアップグレード、セキュリティパッチ、バグ修正による安定性向上 |

---

## まとめ

今回のアップデートは件数こそ1件ですが、New Relic の監視基盤を支える Infrastructure Agent の品質と信頼性を向上させる重要な内容でした。特に Go ランタイムのアップグレードによるセキュリティ強化は、AWS 環境でコンプライアンスを重視する組織にとって必須の対応となります。

SRE の日常業務では、こうした「地味だが重要な」アップデートを見落とさず、計画的にエージェントを更新していくことが、長期的な監視品質の維持につながります。Windows 環境での Docker イメージビルドプロセス自動化は、今後のリリースサイクル短縮の予兆とも言えるため、次回以降の更新頻度の変化にも注目していきましょう。

Infrastructure Agent を最新状態に保つことで、より正確なメトリクス収集、迅速な障害検知、そして安全な運用環境を実現できます。非本番環境での検証を経て、本番環境へのロールアウトを進めてください。