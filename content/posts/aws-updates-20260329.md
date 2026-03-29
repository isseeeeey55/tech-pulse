---
title: "【AWS】2026/03/29 のアップデートまとめ"
date: 2026-03-29T08:01:09+09:00
draft: false
tags: ["aws", "cloudwatch", "timestream", "influxdb", "opensearch"]
categories: ["AWS Updates"]
summary: "2026/03/29 のAWSアップデートまとめ。CloudWatch Logs IAクラスにPPL/SQL・データ保護が追加、Timestream for InfluxDBに高度なメトリクス機能"
---

![](/tech-pulse/images/aws-updates-20260329/header.png)

## はじめに

2026年3月29日のAWSアップデートは2件です。CloudWatch Logs の低頻度アクセス（IA）クラスに OpenSearch PPL/SQL とデータ保護機能が追加されたことと、Amazon Timestream for InfluxDB に高度なメトリクス機能が入ったことです。どちらもコスト最適化と運用監視に直結するアップデートになっています。

## 注目アップデート深掘り

### CloudWatch Logs IAクラスの機能強化

![低頻度アクセスクラスの機能比較](/tech-pulse/images/aws-updates-20260329/ia-class-comparison.png)

> **OpenSearch PPL（Piped Processing Language）とは？**
> OpenSearchが提供するパイプライン形式のクエリ言語。Unix のパイプのように `source=... | where ... | stats ...` と処理を連結して書ける。SQLより直感的にログ分析ができるのが特徴。

Amazon CloudWatch Logsの低頻度アクセス（IA）クラスに、データ保護機能と OpenSearch PPL/SQL サポートが追加されました。これまで標準ログクラスでしか使えなかった分析・保護機能が、IAクラスでも利用可能になります。

**IAクラスの制約が緩和されました**

Logs IAクラスは取り込み料金が標準クラスの50%で済む反面、クエリ機能に制限がありました。今回の追加で、セキュリティ監査やコンプライアンス対応のログ分析をIAクラスのままで実行できるようになっています。

**具体的な検証手順**

まず、既存のログストリームをIAクラスに設定し、新機能を検証してみましょう。

```bash
# ログストリームをIAクラスで作成
$ aws logs create-log-stream \
    --log-group-name "/aws/lambda/security-logs" \
    --log-stream-name "security-events-ia" \
    --log-class INFREQUENT_ACCESS
```

データ保護機能を設定するには、機密データの識別パターンを定義します：

```bash
# データ保護ポリシーの作成
$ aws logs put-data-protection-policy \
    --log-group-identifier "/aws/lambda/security-logs" \
    --policy-document '{
        "Version": "2021-01-01",
        "Statement": [{
            "Sid": "MaskPII",
            "DataIdentifier": [
                "arn:aws:dataprotection::aws:data-identifier/EmailAddress",
                "arn:aws:dataprotection::aws:data-identifier/CreditCardNumber"
            ],
            "Operation": {
                "Audit": {
                    "FindingsDestination": {
                        "CloudWatchLogs": {
                            "LogGroup": "DataProtectionAuditLogs"
                        }
                    }
                },
                "Deidentify": {
                    "MaskConfig": {}
                }
            }
        }]
    }'
```

OpenSearch PPLクエリの実行例：

```bash
# PPLクエリでセキュリティイベントを分析
$ aws logs start-query \
    --log-group-name "/aws/lambda/security-logs" \
    --start-time 1709251200 \
    --end-time 1709337600 \
    --query-string 'source=table | where event_type="login_failed" | stats count() by user_id | sort count desc | head 10'
```

**標準クラスとの比較**

| 項目 | 標準クラス | IAクラス（今回の追加後） |
|------|-----------|----------------------|
| 取り込み料金 | 100% | 50% |
| PPL/SQL クエリ | ○ | ○（NEW） |
| データ保護 | ○ | ○（NEW） |
| リアルタイムアラート | ○ | × |

### Timestream for InfluxDBの高度なメトリクス

> **Amazon Timestream for InfluxDBとは？**
> InfluxDB 2のフルマネージド版。IoTセンサーやアプリのメトリクスなど、時系列データの保存・クエリに特化したサービス。OSS版InfluxDBとAPIレベルで互換性がある。

InfluxDB 2インスタンスの詳細な運用メトリクスが、追加設定なしで自動的にCloudWatchへ送信されるようになりました。

**何が変わるか**

InfluxDBはセンサーデータやメトリクスを大量に処理するため、DB自体の健全性監視が欠かせません。これまでは自前でメトリクス収集の仕組みを用意する必要がありましたが、有効化するだけでCloudWatchに流れるようになります。

**実際の設定手順**

Terraformを使用してTimestream for InfluxDBインスタンスを作成し、高度なメトリクスを有効化：

```hcl
resource "aws_timestreaminfluxdb_db_instance" "monitoring_db" {
  name               = "production-metrics"
  db_instance_type   = "db.influx.medium"
  allocated_storage  = 20
  bucket             = "monitoring-bucket"
  organization       = "production-org"
  username          = "admin"
  password          = var.admin_password
  
  # 高度なメトリクス機能を有効化
  publicly_accessible = false
  vpc_subnet_ids     = [aws_subnet.private.id]
  vpc_security_group_ids = [aws_security_group.timestream.id]
  
  tags = {
    Environment = "production"
    Purpose     = "metrics-monitoring"
  }
}
```

CloudWatchダッシュボードでメトリクスを可視化：

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/TimestreamInfluxDB", "QueryExecutionTime", "DBInstanceIdentifier", "production-metrics"],
          [".", "WriteLatency", ".", "."],
          [".", "ReadLatency", ".", "."],
          [".", "CPUUtilization", ".", "."]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "Timestream InfluxDB Performance"
      }
    }
  ]
}
```

Python SDKを使用したメトリクス監視の自動化：

```python
import boto3
from datetime import datetime, timedelta

def check_timestream_health():
    cloudwatch = boto3.client('cloudwatch')
    
    # 過去1時間のCPU使用率を取得
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/TimestreamInfluxDB',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'DBInstanceIdentifier',
                'Value': 'production-metrics'
            }
        ],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average', 'Maximum']
    )
    
    # 異常値の検出とアラート
    for datapoint in response['Datapoints']:
        if datapoint['Maximum'] > 80:
            print(f"High CPU detected: {datapoint['Maximum']}% at {datapoint['Timestamp']}")
```

## SRE視点での活用ポイント

**CloudWatch Logs IA の使いどころ**

月次レポートや四半期レビューでしか参照しないログは、IAクラスへの移行候補になります。Terraform でログストリームの `log_class` を `INFREQUENT_ACCESS` に変えるだけで取り込みコストが半減し、PPL/SQLでの分析もデータ保護も使えます。PCI DSS や GDPR 対応のログも対象にできます。

ただし、リアルタイムアラートが必要なログは標準クラスのまま残してください。判断基準は「そのログに即時性が求められるかどうか」です。

**Timestream for InfluxDB メトリクスの使いどころ**

CloudWatch アラームと組み合わせれば、InfluxDB の異常を早期検知してランブックに組み込めます。これまで自前で構築していた監視パイプラインが不要になるのは地味に効きます。

注意点として、メトリクス送信分の CloudWatch 料金が加算されます。不要なメトリクスは送信対象から外す設定を入れておくとよいでしょう。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|----------|----------|------|
| CloudWatch Logs | [Amazon CloudWatch Logs now supports data protection, OpenSearch PPL and OpenSearch SQL for the Infrequent Access ingestion class](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-cloudwatch-infrequent-access-log-class/) | 低頻度アクセスログクラスにデータ保護機能とOpenSearch PPL/SQLサポートを追加。コスト効率的なログ分析と機密データ保護を実現 |
| Timestream | [Amazon Timestream for InfluxDB Now Supports Advanced Metrics](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-timestream-for-influxdb-advanced-metrics/) | InfluxDBインスタンスの詳細な運用メトリクスを自動的にCloudWatchに公開。追加設定不要でリアルタイムモニタリングが可能 |

## まとめ

2件ともコスト最適化と運用監視がテーマです。CloudWatch Logs IA は「安いけど機能が足りない」という従来の弱点が解消され、より多くのログをIAクラスに寄せられるようになりました。Timestream for InfluxDB の高度なメトリクスは、有効化するだけで CloudWatch に流れるので導入コストが低いです。週明けにでも設定を見直してみてはいかがでしょうか。