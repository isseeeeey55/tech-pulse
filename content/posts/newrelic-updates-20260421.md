---
title: "【New Relic】2026/04/21 のアップデートまとめ"
date: 2026-04-21T08:01:08+09:00
draft: false
tags: ["newrelic", "infrastructure-agent"]
categories: ["New Relic Updates"]
summary: "Infrastructure Agent 1.74.1 の Go 1.25.9 ランタイム更新と Windows Docker ビルド自動化を解説"
---

![New Relic アップデートまとめ 2026/04/21](/images/newrelic-updates-20260421/header.png)

## はじめに

2026年4月21日、Infrastructure Agent 1.74.1 がリリースされました。今日のリリースは 1 件で、中身は Go ランタイムの v1.25.9 への更新と、Windows Docker イメージビルドの自動化です。Windows ホストやコンテナで Infra Agent を運用しているなら、Docker タグを 1.74.1 に更新しておくタイプの変更です。

---

## 注目アップデート深掘り

### Infrastructure Agent 1.74.1 - Go ランタイム更新と Windows ビルド自動化

![Infrastructure Agent 1.74.1 の主な変更点](/images/newrelic-updates-20260421/infra-agent-1741.png)

主な変更点は 2 つです。Go ランタイムの v1.25.9 へのアップグレードと、Windows Docker イメージビルドパイプラインの自動化。

**Go 1.25.9 更新が効く場面**

Infra Agent は常時稼働でメトリクスやログを送出する性質上、Go ランタイム側の脆弱性が監視対象ホスト全体のリスクになります。社内のコンテナスキャン（Trivy、Snyk、ECR Enhanced Scanning など）で Go の既知 CVE に引っかかって Infra Agent イメージが fail する状況が発生することがあり、ランタイム更新でこれを解消できるのが実益です。CVE 番号は GitHub Release ノートに具体的な一覧はありませんが、Go 1.25.x の直近パッチリリースには net/http と crypto 周りの修正が含まれているのが通例です。

**Windows Docker ビルドの自動化**

Windows コンテナイメージのビルドはこれまで手動ステップを含んでおり、Linux 版と比べてタグが出るタイミングが遅れがちでした。自動化により、今後はメジャー／マイナーリリースに追従して Windows 版も同じペースで出る見込みです。ECS on Windows / Service Fabric / AKS で Infra Agent を使っている環境では、タグの追随コストが下がります。

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

1.74.1 の実質的な中身は、Go 1.25.9 へのランタイム更新と Windows Docker イメージビルドの自動化の 2 点です。機能追加ではなく、ビルド・セキュリティ側の整備に寄ったリリースです。

コンテナスキャンで Go の CVE によって Infra Agent イメージが止まっていた環境や、Windows 版の追随が遅くて諦めていた環境にとっては、このタイミングでタグを更新しておく価値があります。それ以外の環境は、次回のメンテナンスウィンドウで普段どおり差し替えで問題ありません。