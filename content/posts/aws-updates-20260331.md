---
title: "【AWS】2026/03/31 のアップデートまとめ"
date: 2026-03-31T08:01:25+09:00
draft: false
tags: ["aws", "opensearch", "direct-connect", "cloudwatch", "eventbridge", "sagemaker", "mediatailor", "athena", "terraform"]
categories: ["AWS Updates"]
summary: "2026/03/31 のAWSアップデートまとめ。OpenSearch Cluster Insightsのコンソール統合、Direct ConnectのBGP監視CloudWatch対応、Athenaリージョン拡大など5件"
---

![](/images/aws-updates-20260331/header.png)

## はじめに

2026年3月31日のAWSアップデートは5件です。OpenSearch Service の Cluster Insights が AWS 管理コンソールから直接確認できるようになったことと、Direct Connect で BGP セッションの CloudWatch 監視が可能になったことが実運用に効くアップデートです。

## 注目アップデート深掘り

### OpenSearch Service Cluster Insights のコンソール統合とEventBridge連携

> **Cluster Insights とは？**
> OpenSearch クラスターのパフォーマンス、容量、セキュリティに関する推奨事項を自動生成する機能です。シャード配置やインデックスの最適化提案などを提示してくれます。

従来 OpenSearch Dashboards 経由でしかアクセスできなかった Cluster Insights が、AWS 管理コンソールから直接確認できるようになりました。さらに EventBridge との連携で、問題検知時の自動対応も組めるようになっています。

**コンソール統合で何が楽になるか**

これまでは運用チームが OpenSearch Dashboards に個別にログインして状態を確認する必要がありました。今回のアップデートで、AWS コンソール上で他のサービスと同じ画面から確認でき、EventBridge 経由で Slack 通知や PagerDuty 連携も自動化できます。

**AWS管理コンソールでの確認手順**

まず、OpenSearch Service 2.17以降のクラスターでCluster Insightsを有効化します：

```bash
$ aws opensearch update-domain-config \
    --domain-name my-opensearch-cluster \
    --cluster-config InsightsSources=Dashboards,API
```

AWS管理コンソールでは、OpenSearch Serviceのドメイン詳細ページに新しく「Cluster Insights」タブが追加されます。ここでは以下の情報を確認できます：

- **パフォーマンス推奨事項**: インデックスの最適化、シャード配置の改善提案
- **容量計画**: ストレージ使用量の予測とスケーリング推奨事項
- **セキュリティ設定**: アクセス制御や暗号化の改善点

**EventBridgeとの連携設定**

Cluster InsightsからEventBridgeへのイベント配信を設定することで、問題の自動検知が可能になります：

```json
{
  "Rules": [
    {
      "Name": "opensearch-cluster-insights",
      "EventPattern": {
        "source": ["aws.opensearch"],
        "detail-type": ["OpenSearch Cluster Insights"],
        "detail": {
          "severity": ["HIGH", "CRITICAL"]
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:sns:us-east-1:123456789012:opensearch-alerts"
        }
      ]
    }
  ]
}
```

**Terraformでの設定例**

Terraformを使用してEventBridgeルールを設定する場合：

```hcl
resource "aws_cloudwatch_event_rule" "opensearch_insights" {
  name = "opensearch-cluster-insights"
  
  event_pattern = jsonencode({
    source      = ["aws.opensearch"]
    detail-type = ["OpenSearch Cluster Insights"]
    detail = {
      severity = ["HIGH", "CRITICAL"]
    }
  })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.opensearch_insights.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.opensearch_alerts.arn
}
```

### AWS Direct Connect BGP監視のCloudWatch統合

![BGP監視 CloudWatch メトリクス構成](/images/aws-updates-20260331/bgp-monitoring-flow.png)

> **BGP（Border Gateway Protocol）とは？**
> インターネットやネットワーク間でルーティング情報を交換するプロトコルです。Direct Connect では、オンプレミスと AWS 間の経路制御に使われます。BGP セッションが切れると通信不能になるため、監視が欠かせません。

Direct Connect の BGP セッション状態を CloudWatch で直接監視できるようになりました。これまではカスタムスクリプトや API の定期実行が必要でしたが、標準の CloudWatch メトリクスとして3つの新指標が追加されています。

**新しく追加されたメトリクス**

1. **BGPSessionState**: BGPセッションの現在の状態（Established, Idle, Active等）
2. **BGPPrefixCount**: 受信している経路プレフィックス数
3. **BGPSessionUptime**: BGPセッションの稼働時間

**CloudWatch監視の設定**

AWS CLIでBGPセッションの状態を確認：

```bash
$ aws cloudwatch get-metric-statistics \
    --namespace AWS/DirectConnect \
    --metric-name BGPSessionState \
    --dimensions Name=ConnectionId,Value=dxcon-xxxxxxxxx \
    --start-time 2026-03-31T00:00:00Z \
    --end-time 2026-03-31T23:59:59Z \
    --period 300 \
    --statistics Average
```

**アラーム設定の実装**

BGPセッションダウンを検知するCloudWatchアラームをTerraformで設定：

```hcl
resource "aws_cloudwatch_metric_alarm" "bgp_session_down" {
  alarm_name          = "direct-connect-bgp-session-down"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BGPSessionState"
  namespace           = "AWS/DirectConnect"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "This metric monitors BGP session state"
  alarm_actions       = [aws_sns_topic.direct_connect_alerts.arn]

  dimensions = {
    ConnectionId = "dxcon-xxxxxxxxx"
  }
}
```

**プレフィックス数監視による経路異常検知**

BGPで受信している経路数の異常を検知するアラーム：

```hcl
resource "aws_cloudwatch_metric_alarm" "bgp_prefix_anomaly" {
  alarm_name          = "direct-connect-prefix-count-anomaly"
  comparison_operator = "LessThanLowerThreshold"
  evaluation_periods  = "3"
  threshold_metric_id = "ad1"
  alarm_description   = "Detects abnormal BGP prefix count"

  metric_query {
    id = "m1"
    metric {
      metric_name = "BGPPrefixCount"
      namespace   = "AWS/DirectConnect"
      period      = "300"
      stat        = "Average"
      dimensions = {
        ConnectionId = "dxcon-xxxxxxxxx"
      }
    }
  }

  metric_query {
    id = "ad1"
    anomaly_detector {
      metric_math_anomaly_detector {
        metric_data_queries {
          id = "m1"
        }
      }
    }
  }
}
```

> **Note:** BGPメトリクスは5分間隔で更新されます。瞬断検知には ping 監視との併用を検討してください。

## SRE視点での活用ポイント

**OpenSearch Cluster Insights の使いどころ**

複数環境（本番・ステージング・開発）や複数チームで OpenSearch を共有している場合に効きます。EventBridge 連携で Slack 通知や PagerDuty アラートを自動化し、Cluster Insights の推奨事項を Terraform 設定に反映させる判断材料にできます。小規模クラスターや開発環境のみの場合は、設定コストに見合わないかもしれません。

**Direct Connect BGP 監視の使いどころ**

ハイブリッドクラウド環境では、ping や traceroute では検知できない BGP 経路の問題（部分的な経路喪失、フラップなど）を CloudWatch で拾えるようになります。ランブックには BGP セッション状態とプレフィックス数の両方を入れておくと、接続断とルーティング異常を区別して対応できます。Terraform で Direct Connect を管理しているなら、接続作成と同時に BGP 監視も自動化してしまうのがよいでしょう。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|----------|------|
| Amazon OpenSearch Service | [Access Cluster Insights through the Amazon OpenSearch Service Console and Amazon EventBridge events](https://aws.amazon.com/about-aws/whats-new/2026/03/access-cluster-insights-opensearch/) | Cluster InsightsがAWS管理コンソールからアクセス可能になり、EventBridgeイベント連携も追加 |
| AWS Direct Connect | [AWS Direct Connect adds CloudWatch metrics for BGP monitoring](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-direct-connect-cloudwatch-bgp-monitoring/) | BGPセッションの健全性を監視する3つの新しいCloudWatchメトリクスを追加 |
| Amazon SageMaker | [Amazon SageMaker Data Agent is now available in the Amazon SageMaker Unified Studio Query Editor](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-sagemaker-data-agent-query-editor/) | SageMaker Unified Studio Query Editorで、自然言語からSQLクエリを生成するData Agentが利用可能に |
| AWS Elemental MediaTailor | [AWS Elemental MediaTailor now available in Europe (London)](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-elemental-mediatailor-london-region/) | 動的広告挿入サービスがロンドンリージョンで利用開始 |
| Amazon Athena | [Amazon Athena launches Capacity Reservations in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-athena-adding-cap-reservation-regions/) | Athena Capacity Reservationsが追加リージョンで利用可能に |

## まとめ

OpenSearch Cluster Insights と Direct Connect BGP 監視の2つは、従来カスタムスクリプトで対応していた領域が AWS 標準機能でカバーされるようになった点で、運用負荷の削減に直結します。どちらも Terraform で IaC 管理しているなら、監視設定も一緒にコード化しておくのがおすすめです。SageMaker Data Agent や MediaTailor のリージョン拡大、Athena の Capacity Reservations 拡大も含め、着実な機能拡充が続いています。