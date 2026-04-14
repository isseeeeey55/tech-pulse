---
title: "【AWS】2026/04/15 のアップデートまとめ"
date: 2026-04-15T08:01:25+09:00
draft: true
tags: ["aws", "secrets-manager", "ec2", "sagemaker", "quicksight", "redshift", "cloudwatch", "transform"]
categories: ["AWS Updates"]
summary: "2026/04/15 のAWSアップデートまとめ"
---

# AWS アップデート情報 (2026/04/15)

## はじめに

2026年4月15日、AWSから7件のアップデートが発表されました。特に注目すべきは、AWS Secrets Managerが量子コンピュータ脅威に対応した post-quantum TLS をサポートしたことと、EC2の最新インスタンスファミリーでEBSパフォーマンスが大幅に向上したことです。また、CloudWatch Logs Insightsにパラメータ機能が追加され、運用効率の向上が期待されます。

## 注目アップデート深掘り

### Amazon EC2 C8gn/M8gn/R8gn インスタンスの EBS パフォーマンス向上

AWS Graviton4プロセッサを搭載したEC2インスタンスファミリー（C8gn: コンピューティング最適化・ネットワーク強化型、M8gn: 汎用バランス型・ネットワーク強化、R8gn: メモリ最適化・ネットワーク強化型）の48xlargeおよびmetal-48xlサイズにおいて、EBSパフォーマンスが劇的に向上しました。

#### 性能向上の詳細比較

従来と比較した性能向上は以下の通りです：

- **EBS帯域幅**: 60 Gbps → 120 Gbps（2倍）
- **IOPS**: 240,000 → 480,000（2倍）

この改善は AWS Nitro システムの強化によるもので、追加コストなしで利用できます。

#### 実際の検証手順

EBSパフォーマンスの向上を検証するには、以下のステップで実測できます：

```bash
# C8gn.48xlargeインスタンスでEBSボリュームのIOPS性能をテスト
$ aws ec2 run-instances \
    --image-id ami-12345678 \
    --instance-type c8gn.48xlarge \
    --block-device-mappings '[{
        "DeviceName": "/dev/sdf",
        "Ebs": {
            "VolumeSize": 1000,
            "VolumeType": "gp3",
            "Iops": 16000,
            "Throughput": 1000
        }
    }]'

# インスタンス起動後、fioツールでベンチマーク実行
$ sudo fio --name=random-write --ioengine=libaio --rw=randwrite \
    --bs=4k --size=10g --numjobs=16 --iodepth=64 \
    --runtime=300 --group_reporting --filename=/dev/nvme1n1
```

Terraformでの実装例：

```hcl
resource "aws_instance" "high_performance_compute" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "c8gn.48xlarge"
  
  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = 1000
    iops        = 16000
    throughput  = 1000
  }

  tags = {
    Name = "high-iops-workload"
  }
}

# EBS最適化インスタンスの設定
resource "aws_ebs_volume" "high_performance" {
  availability_zone = aws_instance.high_performance_compute.availability_zone
  size             = 2000
  type             = "io2"
  iops             = 64000  # 新しい上限を活用
  
  tags = {
    Name = "high-performance-storage"
  }
}
```

この性能向上により、データベースワークロード、大規模なログ処理、リアルタイム分析などの用途で大幅な処理時間短縮が期待できます。特に、I/Oバウンドなワークロードにおいては、従来の半分の時間で処理が完了する可能性があります。

### CloudWatch Logs Insights の保存クエリパラメータ機能

CloudWatch Logs Insightsに、最大20個のパラメータを持つ保存クエリ機能が追加されました。これまでは類似したクエリを複数管理する必要がありましたが、テンプレート化により運用効率が大幅に改善されます。

#### パラメータ付きクエリの実装例

従来は異なるログレベルごとに個別のクエリを保存していましたが、今回のアップデートでパラメータ化が可能になりました：

```sql
-- パラメータ付きクエリの例
fields @timestamp, @message, level, service
| filter level = ?{log_level}
| filter service like ?{service_pattern}
| filter @timestamp >= ?{start_time}
| sort @timestamp desc
| limit ?{result_limit}
```

AWS CLIでのパラメータ付きクエリ実行：

```bash
# パラメータ付きクエリの保存
$ aws logs put-query-definition \
    --name "service-error-analysis" \
    --query-string 'fields @timestamp, @message, level, service
| filter level = ?{log_level}
| filter service like ?{service_pattern}
| sort @timestamp desc
| limit ?{result_limit}' \
    --log-group-names "/aws/lambda/my-function"

# パラメータを指定してクエリ実行
$ aws logs start-query \
    --log-group-names "/aws/lambda/my-function" \
    --start-time 1735689600 \
    --end-time 1735693200 \
    --query-string 'fields @timestamp, @message, level, service
| filter level = "ERROR"
| filter service like "payment-*"
| sort @timestamp desc
| limit 100'
```

Python SDKでの実装例：

```python
import boto3
from datetime import datetime, timedelta

def execute_parameterized_query(log_level="ERROR", service_pattern="*", hours_back=1, limit=50):
    client = boto3.client('logs')
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)
    
    query_string = f"""
    fields @timestamp, @message, level, service
    | filter level = "{log_level}"
    | filter service like "{service_pattern}"
    | sort @timestamp desc
    | limit {limit}
    """
    
    response = client.start_query(
        logGroupNames=['/aws/lambda/my-function'],
        startTime=int(start_time.timestamp()),
        endTime=int(end_time.timestamp()),
        queryString=query_string
    )
    
    return response['queryId']

# 使用例
query_id = execute_parameterized_query(
    log_level="WARN", 
    service_pattern="auth-*", 
    hours_back=24, 
    limit=100
)
```

このパラメータ機能により、1つのクエリテンプレートで複数のシナリオに対応でき、クエリ管理の複雑さが大幅に軽減されます。

## SRE視点での活用ポイント

### EBSパフォーマンス向上の運用改善効果

C8gn/M8gn/R8gnインスタンスのEBS性能向上は、SREにとって以下の運用改善をもたらします。データベースのバックアップ・復旧時間が半減することで、RTOの大幅な短縮が期待できます。また、ログ集約基盤やメトリクス収集システムでは、より多くのデータを同時処理できるため、監視の粒度を向上させながらコストを抑制できます。

Terraformでインフラ管理している環境では、インスタンスタイプの変更により追加コストなしで性能向上の恩恵を受けられます。ただし、アプリケーションがI/Oバウンドでない場合、性能向上の効果は限定的であるため、事前にボトルネックの特定が重要です。移行時は段階的なロールアウトを行い、CloudWatchメトリクスでEBS使用率とレイテンシーを継続監視することを推奨します。

### CloudWatchパラメータクエリによる障害対応効率化

保存クエリのパラメータ機能は、障害対応のランブック標準化に大きく貢献します。従来は障害レベルやサービスごとに個別のクエリを管理していましたが、パラメータ化により一つのテンプレートで多様な調査パターンに対応できます。

特に、オンコール対応では時間範囲やログレベルを動的に変更しながら原因調査を行うため、この機能により調査時間の短縮が期待できます。CloudWatchアラームと連携し、アラート発生時に自動でパラメータ付きクエリを実行するワークフローを構築すれば、初動対応の自動化も可能です。導入時は既存のクエリをパラメータ化し、チーム内でテンプレートを共通化することで、属人性を排除した運用体制を構築できます。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Secrets Manager now supports hybrid post-quantum TLS](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-secrets-manager-post-quantum-tls/) | 量子コンピュータ脅威に対応したpost-quantum TLSをサポート、機密情報の長期的保護を強化 |
| [AWS Transform is now available in Kiro and VS Code](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-transform-kiro-vscode/) | レガシーアプリケーションの最新化とSDKマイグレーションを支援するツールを拡張 |
| [Amazon EC2 C8gn, M8gn, and R8gn instances now support higher Amazon EBS-optimized performance](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-c8gn-m8gn-r8gn-ebs/) | Graviton4搭載インスタンスでEBS帯域幅とIOPSを2倍に向上、追加コストなし |
| [NVIDIA Nemotron-3-Super-120B, Qwen3.5-9B, and Qwen3.5-27B models now available on Amazon SageMaker JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/04/nemotron3super-120b-qwen3.5-9b-qwen3.5-27b-on-sagemaker-jumpstart/) | 3つの新しい基盤モデルを追加、エージェント推論と多言語コーディング能力を強化 |
| [Amazon Quick now supports document-level access controls for Google Drive knowledge bases](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-document-level-access-controls-google-drive/) | Google Driveとの統合でドキュメントレベルのアクセス制御をサポート |
| [Amazon Redshift introduces key performance optimization for Top-K queries](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-redshift-topk-optimization/) | Top-Kクエリの性能最適化により、大規模データから上位K件の抽出を高速化 |
| [Amazon CloudWatch Logs Insights now supports saved queries with parameters](https://aws.amazon.com/about-aws/whats-new/2026/03/cloudwatch-logs-insights-query-params/) | 保存クエリに最大20個のパラメータをサポート、クエリテンプレート化により運用効率を向上 |

## まとめ

本日のアップデートは、性能向上とセキュリティ強化の両面で重要な進歩を示しています。特にEC2インスタンスのEBS性能向上は、I/O集約的なワークロードに immediate な恩恵をもたらし、CloudWatchのパラメータクエリ機能は日々の運用効率を大幅に改善するでしょう。量子コンピュータ脅威への対応も含め、AWSが長期的な視点でサービスを強化し続けていることが伺えます。これらのアップデートを活用することで、より効率的で安全なクラウド運用が実現できそうです。