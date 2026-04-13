---
title: "【AWS】2026/04/14 のアップデートまとめ"
date: 2026-04-14T08:01:39+09:00
draft: true
tags: ["aws", "opensearch", "fsx", "aurora", "ec2", "elastic-disaster-recovery", "iot"]
categories: ["AWS Updates"]
summary: "2026/04/14 のAWSアップデートまとめ"
---

## はじめに

2026年4月14日のAWSアップデート情報をお届けします。今回は7件のアップデートが発表され、特にストレージ最適化、新世代EC2インスタンス、IPv6対応の拡充が注目されます。中でもAmazon OpenSearch ServerlessのDerived Source機能は大幅なストレージコスト削減を実現し、AWS GovCloud（US-West）でのR8i/M8iインスタンス提供開始は政府機関向けワークロードの性能向上に大きく貢献するでしょう。

## 注目アップデート深掘り

### Amazon OpenSearch Serverless - Derived Source機能によるストレージ最適化

OpenSearchにおけるストレージコストは、大量のログデータやメトリクスを扱う組織にとって重要な課題です。従来のOpenSearchでは、検索インデックスとは別に元のドキュメントの完全なコピー（_source フィールド）を保存する必要があり、これがストレージ使用量の大部分を占めていました。

今回発表されたDerived Source機能は、この課題を根本的に解決します。元のドキュメントを保存する代わりに、インデックスに保存されている値から動的に再構築する仕組みです。この機能により、ストレージ使用量を最大50-70%削減できる可能性があります。

実際の検証手順を見てみましょう：

```bash
# OpenSearch Serverlessコレクションの作成
$ aws opensearchserverless create-collection \
    --name "derived-source-test" \
    --type TIMESERIES \
    --description "Testing Derived Source feature"
```

インデックステンプレートでDerived Sourceを有効化：

```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "index": {
        "mode": "time_series",
        "derived_source": {
          "enabled": true
        }
      }
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "message": {
          "type": "text"
        },
        "level": {
          "type": "keyword"
        }
      }
    }
  }
}
```

Python SDKを使用した効果測定のサンプルコード：

```python
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection

def compare_storage_usage():
    # 通常のインデックスとDerived Source有効インデックスの比較
    client = OpenSearch(
        hosts=['your-collection-endpoint.us-east-1.aoss.amazonaws.com'],
        http_auth=('username', 'password'),
        use_ssl=True,
        connection_class=RequestsHttpConnection
    )
    
    # ストレージ使用量の取得
    stats_normal = client.indices.stats(index='logs-normal-*')
    stats_derived = client.indices.stats(index='logs-derived-*')
    
    normal_size = stats_normal['_all']['total']['store']['size_in_bytes']
    derived_size = stats_derived['_all']['total']['store']['size_in_bytes']
    
    reduction_rate = (normal_size - derived_size) / normal_size * 100
    
    print(f"通常のインデックス: {normal_size / (1024**3):.2f} GB")
    print(f"Derived Source: {derived_size / (1024**3):.2f} GB")
    print(f"削減率: {reduction_rate:.1f}%")
```

> **Note:** Derived Source機能は、元のドキュメント全体を取得する際に若干のレイテンシーが発生する可能性があります。読み取りパフォーマンスとストレージコストのトレードオフを十分に検証してください。

### EC2 R8i/M8iインスタンス - AWS GovCloudでの新世代性能

AWS GovCloud（US-West）でのR8iおよびM8iインスタンスの提供開始は、政府機関や規制業界におけるワークロード性能の大幅な向上を意味します。これらのインスタンスは、AWS独自のカスタムIntel Xeon 6プロセッサを搭載し、前世代と比較して15%の価格性能向上、メモリ帯域幅2.5倍の向上を実現しています。

実際の性能比較を行うためのTerraformコード例：

```hcl
# R8iインスタンスの定義
resource "aws_instance" "r8i_test" {
  ami           = "ami-12345678"  # GovCloud用AMI
  instance_type = "r8i.large"
  
  vpc_security_group_ids = [aws_security_group.test.id]
  subnet_id              = aws_subnet.test.id
  
  user_data = base64encode(templatefile("benchmark-setup.sh", {
    test_type = "memory-intensive"
  }))
  
  tags = {
    Name = "R8i-Performance-Test"
    TestType = "MemoryBandwidth"
  }
}

# 比較用R7iインスタンス
resource "aws_instance" "r7i_comparison" {
  ami           = "ami-12345678"
  instance_type = "r7i.large"
  
  vpc_security_group_ids = [aws_security_group.test.id]
  subnet_id              = aws_subnet.test.id
  
  user_data = base64encode(templatefile("benchmark-setup.sh", {
    test_type = "memory-intensive"
  }))
  
  tags = {
    Name = "R7i-Comparison-Test"
    TestType = "MemoryBandwidth"
  }
}
```

メモリ帯域幅のベンチマークスクリプト：

```bash
#!/bin/bash
# benchmark-setup.sh

# メモリ帯域幅テスト用のツールをインストール
$ sudo yum update -y
$ sudo yum install -y gcc make

# STREAM ベンチマークのダウンロードとコンパイル
$ wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c
$ gcc -O3 -fopenmp stream.c -o stream

# ベンチマーク実行
$ export OMP_NUM_THREADS=4
$ ./stream > memory_benchmark_results.txt

# PostgreSQL性能テスト用のpgbenchも実行
$ sudo amazon-linux-extras install postgresql13
$ pgbench -i -s 100 testdb
$ pgbench -c 10 -j 2 -t 1000 testdb > postgres_benchmark_results.txt
```

CloudWatchメトリクス収集の設定：

```json
{
  "metrics": {
    "namespace": "EC2/InstancePerformance",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          "cpu_usage_idle",
          "cpu_usage_iowait",
          "cpu_usage_user",
          "cpu_usage_system"
        ]
      },
      "mem": {
        "measurement": [
          "mem_used_percent",
          "mem_available_percent"
        ]
      }
    }
  }
}
```

R8i-flexインスタンスの特徴は、CPUリソースの柔軟な調整が可能な点です。ワークロードの特性に応じてvCPU数を調整し、コストを最適化できます。

## SRE視点での活用ポイント

### OpenSearch Serverless Derived Source機能

ログ管理とモニタリングを担当するSREチームにとって、このアップデートは運用コストの大幅削減を実現する重要な機能です。特に長期間のログ保持が必要な環境では、ストレージコストが運用予算の大部分を占めることが多く、50-70%の削減効果は非常に大きなインパクトがあります。

導入検討時は、まず現在のログ検索パターンを分析することが重要です。元のドキュメント全体を頻繁に取得するユースケースが多い場合は、わずかなレイテンシー増加がユーザビリティに影響する可能性があります。一方、集計クエリやメトリクス抽出が中心の運用では、ほぼ影響なくコスト削減の恩恵を受けられるでしょう。

Terraformでインフラを管理している場合は、既存のインデックステンプレートに段階的にDerived Source設定を適用し、新しいインデックスから徐々に移行していく戦略が推奨されます。CloudWatch Logsとの連携では、ログの転送設定を見直し、必要なフィールドのみをインデックス化することで、さらなる効率化が期待できます。

### EC2 新世代インスタンスの活用

R8i/M8iインスタンスの性能向上は、データベースやアプリケーションサーバーの応答性改善に直結します。特にSAPワークロードやPostgreSQLデータベースでは、メモリ帯域幅の2.5倍向上により、大幅な処理性能向上が期待できます。

Auto Scaling環境では、新世代インスタンスの高い性能を活かすことで、同じ負荷を処理するのに必要なインスタンス数を削減できる可能性があります。これは、スケールアウト時のコスト効率化だけでなく、インスタンス起動時間の短縮による障害復旧の迅速化にも貢献します。

ただし、新しいインスタンスタイプへの移行は、既存のパフォーマンスベースラインや監視閾値の見直しが必要です。CloudWatchアラームの設定値や、APMツールでの正常性判定基準を、新しい性能特性に合わせて調整することが重要です。また、マルチAZ構成での段階的な移行により、リスクを最小化しながら性能向上の効果を検証できます。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| [Amazon OpenSearch Serverless](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-opensearch-serverless-supports-derived-source/) | Derived Source機能のサポート | 元のドキュメントを保存せずにインデックス値から動的再構築、大幅なストレージ削減を実現 |
| [Amazon FSx](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-fsx-copying-backups-opt-in-regions/) | Opt-inリージョン間でのバックアップコピー対応 | ファイルシステムバックアップのクロスリージョンコピーが可能に |
| [Aurora DSQL](https://aws.amazon.com/about-aws/whats-new/2026/04/aurora-dsql-connector-for-php/) | PHP向けコネクタの提供 | PHPアプリケーションでのAurora DSQL接続を簡素化 |
| [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-r8i-instances-govcloud-us-west/) | R8i/R8i-flexインスタンスのGovCloud対応 | メモリ最適化インスタンス、Intel Xeon 6搭載で15%の性能向上 |
| [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-m8i-flex-govcloud-us-west/) | M8i/M8i-flexインスタンスのGovCloud対応 | 汎用インスタンス、前世代から15%の価格性能向上を実現 |
| [AWS Elastic Disaster Recovery](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-elastic-disaster-recovery-ipv6/) | IPv6サポート | IPv6環境での災害復旧機能が利用可能に |
| [AWS IoT](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-iot-israel-tel-aviv-europe-milan/) | イスラエル・イタリアリージョン対応 | IoTサービスの地理的拡張、レイテンシー最適化が可能 |

## まとめ

今回のアップデートは、コスト最適化と性能向上の両面でバランスの取れた内容となりました。OpenSearch ServerlessのDerived Source機能は、データ分析基盤のTCO削減に大きく貢献し、新世代EC2インスタンスは政府機関向けワークロードの性能要件をより高いレベルで満たします。また、IPv6対応の拡充やリージョン展開により、AWSエコシステム全体の柔軟性がさらに向上しています。

特に注目すべきは、ストレージ効率化への取り組みが加速している点です。データ量の爆発的な増加に対して、単純なスケールアップではなく、技術革新によるコスト削減アプローチが強化されており、今後のクラウド運用戦略においても重要な選択肢となるでしょう。