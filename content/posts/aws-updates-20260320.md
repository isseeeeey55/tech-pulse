---
title: "【AWS】2026/03/20 のアップデートまとめ"
tags: ["aws", "lambda", "ec2", "graviton", "direct-connect", "efa"]
date: "2026-03-20T08:00:00+09:00"
categories: ["AWS Updates"]
summary: "LambdaのAZメタデータ取得対応と、Graviton4搭載のC8gnインスタンスの新リージョン対応が目を引く7件のアップデート。"
draft: false
---

![](/tech-pulse/images/aws-updates-20260320/header.png)

## はじめに

2026年3月20日のAWSアップデートは7件。LambdaのAZメタデータ取得対応と、Graviton4搭載のC8gnインスタンスの新リージョン対応が目を引きます。ほかにDirect Connectのシドニー拠点追加、EC2 FleetのCapacity Reservations対応、EFAのNIXLサポートなど。

## 注目アップデート深掘り

### AWS Lambdaのアベイラビリティゾーンメタデータサポート

Lambda関数が、自身の実行AZ IDを取得できるようになりました。これまでLambdaはどのAZで動いているかを知る手段がなく、RDSやElastiCacheへのアクセスでクロスAZ通信が発生しても制御できませんでした。

![Lambda AZメタデータによる同一AZ内通信の最適化](/tech-pulse/images/aws-updates-20260320/lambda-az-metadata.png)

**これで何ができるか**

AZ IDがわかれば、同一AZ内のRDSリードレプリカやElastiCacheノードに優先接続できます。クロスAZ通信はデータ転送料金が発生するうえレイテンシーも増えるため、高頻度で呼ばれるLambda関数では無視できないコスト要因でした。

**具体的な実装方法**

メタデータエンドポイントへHTTPリクエストを送るだけです：

```pythonimport urllib.request
import json

def lambda_handler(event, context):
    # メタデータエンドポイントからAZ IDを取得
    metadata_url = "http://169.254.169.254/latest/meta-data/placement/availability-zone-id"

    try:
        with urllib.request.urlopen(metadata_url) as response:
            az_id = response.read().decode('utf-8')

        # AZ IDに基づいてRDSエンドポイントを選択
        if az_id == "use1-az1":
            rds_endpoint = "database-az1.cluster-xxx.us-east-1.rds.amazonaws.com"
        elif az_id == "use1-az2":
            rds_endpoint = "database-az2.cluster-xxx.us-east-1.rds.amazonaws.com"
        else:
            rds_endpoint = "database-default.cluster-xxx.us-east-1.rds.amazonaws.com"

        return {
            'statusCode': 200,
            'body': json.dumps({
                'az_id': az_id,
                'selected_endpoint': rds_endpoint
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

Powertools for AWS Lambdaを使う場合：

```pythonfrom aws_lambda_powertools import Logger
import urllib.request

logger = Logger()

def get_az_id():
    metadata_url = "http://169.254.169.254/latest/meta-data/placement/availability-zone-id"
    with urllib.request.urlopen(metadata_url) as response:
        return response.read().decode('utf-8')

@logger.inject_lambda_context
def lambda_handler(event, context):
    current_az = get_az_id()
    logger.info(f"Lambda executing in AZ: {current_az}")

    # AZ情報を使ったルーティング
    return process_with_az_awareness(current_az, event)
```

**クロスAZ通信コストの確認**

```bash
$ aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=my-function \
    --start-time 2026-03-20T00:00:00Z \
    --end-time 2026-03-20T23:59:59Z \
    --period 3600 \
    --statistics Average
```

### EC2 C8gnインスタンスの新リージョン対応

Graviton4搭載のC8gnインスタンスが、東京リージョンを含む追加リージョンで使えるようになりました。C7gn（Graviton3）比で約30%の性能向上、最大600 Gbpsのネットワーク帯域幅を持つネットワーク集約型のインスタンスです。

**Terraformでの定義例**

```terraformresource "aws_instance" "c8gn_compute" {
  ami           = "ami-0abcdef1234567890"  # Amazon Linux 2023 ARM64
  instance_type = "c8gn.xlarge"

  # ネットワーク最適化を有効化
  ena_support = true
  sriov_net_support = "simple"

  # 配置グループでネットワーク性能を最大化
  placement_group = aws_placement_group.cluster.name

  tags = {
    Name = "high-performance-compute"
    InstanceFamily = "C8gn-Graviton4"
  }
}

resource "aws_placement_group" "cluster" {
  name     = "compute-cluster"
  strategy = "cluster"
}
```

**ベンチマーク手順**

```bash#!/bin/bash
# C8gn vs C7gn 性能比較スクリプト

# CPU性能テスト
echo "Running CPU benchmark..."
sysbench cpu --cpu-max-prime=20000 --threads=8 run

# ネットワーク帯域幅テスト
echo "Testing network performance..."
iperf3 -c target-server -t 60 -P 4

# メモリ帯域幅テスト
echo "Memory bandwidth test..."
sysbench memory --memory-total-size=10G run
```

公式の数値としては以下が示されています：

- ネットワーク仮想アプライアンス: 30%のスループット向上
- データ分析処理: 25%の処理時間短縮
- AI/ML推論: 20%のレイテンシー削減

## SRE視点での活用ポイント

**Lambda AZメタデータの使いどころ**

TerraformでLambda + RDSの構成を管理しているなら、AZメタデータを使った接続先の最適化は検討する価値があります。CloudWatchアラームと組み合わせれば、AZ単位での障害検知やフェイルオーバーの自動化にも使えます。

注意点として、メタデータ取得にはHTTPリクエストが1回走ります。高頻度で実行される関数では、初回取得時にキャッシュする実装にしておくのが無難です。

**C8gnへの移行判断**

マイクロサービス間で大量のデータをやり取りする構成では、ネットワーク帯域幅がボトルネックになりがちです。C8gnの600 Gbpsは、そういった構成で効いてきます。ただしGraviton4はARM64なので、移行前にアプリケーションの互換性検証は必須です。段階的に移行して、ベンチマークで比較しながら進めるのが安全です。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|----------|------|
| Amazon Redshift | [Redshift supports federated permissions with IAM Identity Center in multiple AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/03/redshift-federated-permissions-idc-mrr/) | マルチリージョンでのIAM Identity Centerフェデレーション認証 |
| AWS Direct Connect | [AWS Direct Connect announces new location in Sydney, Australia](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-direct-connect-sydney-sy5/) | シドニーに新しいDirect Connect拠点を追加 |
| Amazon EC2 Fleet | [Amazon EC2 Fleet now supports interruptible Capacity Reservations](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ec2-fleet-interruptible-capacity-reservations/) | 中断可能なCapacity Reservationsに対応 |
| AWS EFA | [AWS adds support for NIXL with EFA to accelerate LLM inference at scale](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-support-nixl-with-efa/) | LLM推論を高速化するNIXLのEFAサポート |
| AWS Lambda | [AWS Lambda now supports Availability Zone metadata](https://aws.amazon.com/about-aws/whats-new/2026/03/lambda-availability-zone-metadata/) | Lambda関数のAZ ID取得が可能に |
| Amazon EC2 | [Amazon EC2 C8gn instances are now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ec2-c8gn-instances-additional-regions/) | Graviton4搭載C8gnが東京を含む新リージョンで利用可能 |
| Amazon RDS | [Amazon RDS Custom for SQL Server adds ability to view and schedule new operating system updates](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-rds-custom-sql-server-operating-system-updates/) | RDS Custom for SQL ServerにOSアップデート管理機能を追加 |

## まとめ

LambdaのAZメタデータ取得は、地味だけどコスト最適化に直結するアップデートです。クロスAZ通信コストが月数万円に達している環境なら、導入する理由は十分あります。C8gnの東京リージョン対応は、Graviton4への移行を検討していたチームにとっては待望のリリースでしょう。ARM64互換の検証さえ済んでいれば、すぐに試せます。
