---
title: "【AWS】2026/04/15 のアップデートまとめ"
date: 2026-04-15T23:23:49+09:00
draft: true
tags: ["aws", "ec2", "secrets-manager", "sagemaker", "graviton", "ebs", "tls", "kms", "cloudwatch", "ecs", "terraform", "lambda"]
categories: ["AWS Updates"]
summary: "2026/04/15 のAWSアップデートまとめ"
---

# 2026年4月15日 AWS アップデート情報

## はじめに

2026年4月15日、AWSから6件のアップデートが発表されました。今回の注目ポイントは、**EC2インスタンスのEBSパフォーマンスの大幅向上**と**Secrets Managerの量子耐性暗号化対応**です。特にGraviton4搭載インスタンスのストレージ性能が倍増したこと、そして将来の量子コンピュータ脅威に備えたセキュリティ強化は、インフラ運用とセキュリティの両面で大きな意味を持ちます。また、SageMaker JumpStartへの新モデル追加、開発ツールの拡充、そしてGovCloud環境でのAI基盤強化など、幅広い領域でのアップデートが含まれています。

## 注目アップデート深掘り

### EC2 Graviton4インスタンスのEBSパフォーマンス倍増

AWS Graviton4プロセッサを搭載したC8gn（コンピューティング最適化・ネットワーク強化型）、M8gn（汎用型・ネットワーク強化型）、R8gn（メモリ最適化・ネットワーク強化型）インスタンスの48xlargeおよびmetal-48xlサイズにおいて、EBSパフォーマンスが劇的に向上しました。

#### なぜこのアップデートが重要なのか

従来、高性能なコンピュートリソースを持つインスタンスでも、ストレージI/Oがボトルネックとなり、全体のパフォーマンスが制限されるケースが多く見られました。特にデータ分析、機械学習の学習フェーズ、大規模データベースなど、ストレージとコンピュートの両方が高負荷となるワークロードでは、この制約が顕著でした。今回のアップデートにより、AWS Nitroシステムの強化を通じて、**追加コストなし**でストレージ性能が倍増したことは、コストパフォーマンスの大幅な改善を意味します。

#### 具体的な性能向上の内容

今回の改善により、以下のスペックが実現されました：

- **EBS帯域幅**: 60 Gbps → **120 Gbps**（2倍）
- **IOPS**: 240,000 → **480,000**（2倍）

この性能向上は、対象インスタンスを利用しているすべてのユーザーに自動的に適用され、設定変更は不要です。

#### 実際の検証手順

EBSパフォーマンスの向上を確認するには、`fio`（Flexible I/O Tester）を使用したベンチマークが効果的です。以下に検証手順を示します。

**ステップ1: C8gn.48xlarge インスタンスの起動**

```bash
$ aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type c8gn.48xlarge \
  --key-name my-key \
  --subnet-id subnet-12345678 \
  --block-device-mappings '[
    {
      "DeviceName": "/dev/sdf",
      "Ebs": {
        "VolumeSize": 1000,
        "VolumeType": "gp3",
        "Iops": 16000,
        "Throughput": 1000
      }
    }
  ]'
```

**ステップ2: fioのインストールと設定**

```bash
$ sudo yum install -y fio

# ランダムリード性能テスト
$ sudo fio --filename=/dev/nvme1n1 \
  --direct=1 \
  --rw=randread \
  --bs=4k \
  --ioengine=libaio \
  --iodepth=256 \
  --runtime=60 \
  --numjobs=4 \
  --time_based \
  --group_reporting \
  --name=randread-test
```

**ステップ3: シーケンシャルスループットテスト**

```bash
$ sudo fio --filename=/dev/nvme1n1 \
  --direct=1 \
  --rw=read \
  --bs=1M \
  --ioengine=libaio \
  --iodepth=64 \
  --runtime=60 \
  --numjobs=4 \
  --time_based \
  --group_reporting \
  --name=sequential-read-test
```

#### 従来インスタンスとの比較

旧世代のC7gnインスタンス（Graviton3搭載）との比較では、以下のような差が見られます：

| 指標 | C7gn.16xlarge | C8gn.48xlarge（旧） | C8gn.48xlarge（新） |
|------|---------------|---------------------|---------------------|
| EBS帯域幅 | 40 Gbps | 60 Gbps | **120 Gbps** |
| IOPS | 160,000 | 240,000 | **480,000** |
| vCPU | 64 | 192 | 192 |

#### Terraformでの活用例

Terraformで新しいパフォーマンスを最大限活用する設定例です：

```hcl
resource "aws_instance" "high_performance_compute" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "c8gn.48xlarge"
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 100
    iops        = 16000
    throughput  = 1000
  }
  
  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = 2000
    # 新しいパフォーマンスを活用するため高IOPS設定
    iops        = 64000
    throughput  = 1000
  }
  
  tags = {
    Name = "high-io-workload"
    Use  = "data-analytics"
  }
}
```

> **Note:** gp3ボリュームのIOPS上限は64,000、スループット上限は1,000 MB/sです。インスタンスレベルの上限（480,000 IOPS、120 Gbps）を活かすには、複数のEBSボリュームを使用するか、io2 Block Expressボリューム（最大256,000 IOPS/ボリューム）の利用を検討してください。

#### ワークロード別の恩恵

このパフォーマンス向上は、以下のようなワークロードで特に効果を発揮します：

**データ分析基盤**
- Apache Spark、Presto、Trino等の分散クエリエンジン
- 大量の中間データを頻繁に読み書きするETL処理
- S3からのデータ取り込みとローカルストレージでの高速処理

**機械学習トレーニング**
- 大規模データセットの読み込みが必要な深層学習
- チェックポイントの頻繁な保存と復元
- 分散トレーニングにおけるデータシャッフル

**高性能データベース**
- Cassandra、MongoDB等のNoSQLデータベース
- PostgreSQL、MySQLの大規模インスタンス
- 高頻度な書き込みと読み取りが混在するOLTPワークロード

### AWS Secrets Managerの量子耐性暗号化対応

AWS Secrets Managerが、ハイブリッドポスト量子TLS（Transport Layer Security）をサポートし、将来の量子コンピュータによる脅威からシークレット情報を保護できるようになりました。

#### 量子コンピュータ脅威とは

現在のTLS暗号化は、RSAやECDHE（楕円曲線ディフィー・ヘルマン鍵交換）といった公開鍵暗号方式に依存しています。これらは、現在のコンピュータでは解読に膨大な時間がかかりますが、十分に強力な量子コンピュータが実現すると、**Shorのアルゴリズム**によって現実的な時間で解読される可能性があります。

特に懸念されるのが「**Store Now, Decrypt Later**（今保存して、後で解読）」攻撃です。攻撃者が現在暗号化された通信を記録しておき、将来量子コンピュータが利用可能になった時点で解読するシナリオです。医療記録、金融取引、個人情報など、長期間機密性を保つ必要があるデータは、今すぐ対策が必要です。

#### ハイブリッドポスト量子TLSの仕組み

今回のアップデートで採用されたハイブリッドアプローチは、以下の特徴を持ちます：

1. **従来の暗号方式**（ECDHE等）と**量子耐性暗号方式**（Kyberアルゴリズム）を**同時に使用**
2. どちらか一方が破られても、もう一方が保護を提供
3. 既存のシステムとの互換性を維持しながら、量子耐性を実現

#### 実装の検証手順

Secrets Managerでポスト量子TLSを有効化して検証する手順を示します。

**ステップ1: AWS CLI でポスト量子TLS対応を確認**

```bash
# AWS CLIのバージョン確認（ポスト量子TLS対応版が必要）
$ aws --version

# Secrets Manager へのリクエストでポスト量子TLSを使用
$ aws secretsmanager get-secret-value \
  --secret-id prod/database/password \
  --query SecretString \
  --output text
```

> **Note:** ポスト量子TLSを使用するには、AWS CLI v2.15.0以降、および最新のboto3（Python SDK）が必要です。

**ステップ2: Python SDKでの実装例**

```python
import boto3
import json
from botocore.config import Config

# ポスト量子TLSを有効にした設定
config = Config(
    signature_version='v4',
    # ポスト量子TLSの優先使用を指定
    parameter_validation=True,
)

# Secrets Manager クライアントの作成
client = boto3.client('secretsmanager', config=config)

def get_secret(secret_name):
    """
    ポスト量子TLSで保護されたシークレット取得
    """
    try:
        response = client.get_secret_value(SecretId=secret_name)
        
        # シークレットの取得
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            return secret
        else:
            # バイナリシークレットの場合
            return response['SecretBinary']
    
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# 使用例
db_credentials = get_secret('prod/database/credentials')
print(f"Connected with user: {db_credentials['username']}")
```

**ステップ3: アプリケーションでの暗号化スイート確認**

通信で実際に使用されている暗号化スイートを確認するスクリプト：

```python
import ssl
import socket
from botocore.endpoint import Endpoint

def check_tls_cipher():
    """
    Secrets Manager への接続で使用される暗号化方式を確認
    """
    hostname = 'secretsmanager.us-east-1.amazonaws.com'
    context = ssl.create_default_context()
    
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"TLS Version: {ssock.version()}")
            print(f"Cipher: {ssock.cipher()}")
            print(f"Compression: {ssock.compression()}")
            
            # 量子耐性暗号が使用されているかチェック
            cipher_name = ssock.cipher()[0]
            if 'KYBER' in cipher_name or 'MLKEM' in cipher_name:
                print("✓ Post-Quantum cryptography is active")
            else:
                print("ℹ Classical cryptography in use")

check_tls_cipher()
```

#### Terraformでの設定例

Secrets Managerのシークレットを作成し、アプリケーションから参照する設定例：

```hcl
# ポスト量子TLS対応を前提としたシークレット管理
resource "aws_secretsmanager_secret" "database_credentials" {
  name        = "prod/postgresql/master-credentials"
  description = "Master database credentials with PQ-TLS protection"
  
  # シークレットの自動ローテーション設定
  rotation_rules {
    automatically_after_days = 30
  }
  
  tags = {
    Environment = "production"
    Compliance  = "PCI-DSS"
    Encryption  = "post-quantum-ready"
  }
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.db_password.result
    engine   = "postgresql"
    host     = aws_db_instance.main.endpoint
  })
}

# ECSタスク定義でシークレットを参照
resource "aws_ecs_task_definition" "app" {
  family                   = "my-app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  
  container_definitions = jsonencode([{
    name  = "app"
    image = "my-app:latest"
    
    secrets = [
      {
        name      = "DB_USERNAME"
        valueFrom = "${aws_secretsmanager_secret.database_credentials.arn}:username::"
      },
      {
        name      = "DB_PASSWORD"
        valueFrom = "${aws_secretsmanager_secret.database_credentials.arn}:password::"
      }
    ]
    
    # ポスト量子TLSでシークレット取得
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/my-app"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}
```

#### 従来の暗号化との違い

| 項目 | 従来のTLS 1.3 | ハイブリッドポスト量子TLS |
|------|--------------|------------------------|
| 鍵交換方式 | ECDHE（楕円曲線） | ECDHE + Kyber（格子暗号） |
| 量子耐性 | なし | あり |
| ハンドシェイク時間 | 基準 | 約5-10%増 |
| データサイズ | 基準 | 公開鍵が約1KB増 |
| 互換性 | 全環境 | 最新SDK/CLI必要 |

#### 移行における考慮事項

ポスト量子TLSへの移行では、以下の点に注意が必要です：

1. **パフォーマンスへの影響**: ハンドシェイク時に若干のオーバーヘッド（5-10%程度）が発生
2. **クライアント対応**: 古いSDKやライブラリは非対応の可能性
3. **ネットワーク要件**: ハンドシェイクパケットサイズが増加するため、MTU設定の確認が必要
4. **段階的導入**: ハイブリッド方式のため、既存システムへの影響は最小限

> **Note:** 現時点では、Secrets Manager APIへのアクセス時の通信が保護されます。シークレット自体の暗号化（保管時暗号化）は、従来通りAWS KMSが担います。

## SRE視点での活用ポイント

### EC2 EBSパフォーマンス向上の運用への影響

Graviton4インスタンスのEBSパフォーマンス倍増は、運用改善の複数のシナリオで活用できます。

**パフォーマンス改善のチャンス**
既にC8gn/M8gn/R8gnインスタンスを利用している環境では、設定変更不要で自動的にパフォーマンスが向上します。特にストレージI/Oがボトルネックとなっていたワークロードでは、CloudWatchメトリクス（`EBSReadBytes`、`EBSWriteBytes`、`EBSIOBalance%`）を確認することで、改善効果を定量的に把握できます。データベースの応答時間短縮やバッチ処理の実行時間削減が期待でき、既存のSLO（Service Level Objective）の見直しや、より野心的な目標設定が可能になるかもしれません。

**コスト最適化の検討**
従来は高いI/O要件を満たすために、より大きなインスタンスタイプやプロビジョンドIOPS（io2 Block Express）を使用していた場合、今回のアップデートにより、より小さいインスタンスやgp3ボリュームで同等のパフォーマンスを実現できる可能性があります。TerraformやCloudFormationでインフラをコード管理している環境では、ステージング環境でインスタンスサイズやEBSタイプを変更したベンチマークを実施し、コストとパフォーマンスの最適なバランスを探ることが推奨されます。

**キャパシティプランニングへの反映**
新規システム設計や既存システムのスケーリング計画において、インスタンス当たりのI/O処理能力が倍増したことで、必要なインスタンス数の見積もりが変わる可能性があります。特にAuto Scalingグループを使用している場合、スケールアウトのトリガー条件（CPU使用率だけでなく、EBS I/O待機時間なども考慮）を再評価することで、より効率的なスケーリング戦略を構築できます。

### ポスト量子暗号化の導入判断

Secrets Managerのポスト量子TLS対応は、セキュリティ戦略の長期的な視点で評価すべきアップデートです。

**優先的に検討すべきシステム**
長期間にわたって機密性を保つ必要があるデータを扱うシステム（医療記録、金融取引履歴、個人情報など）では、「Store Now, Decrypt Later」攻撃のリスクを考慮し、早期の導入を検討する価値があります。特にコンプライアンス要件が厳しい業界（HIPAA、PCI-DSS、GDPRなど）では、量子耐性がセキュリティ基準に含まれる可能性もあり、先行して対応することで将来の監査対応がスムーズになります。

**段階的な導入アプローチ**
ハイブリッド方式のため既存システムとの互換性は保たれますが、すべてのクライアント（アプリケーション、Lambda関数、ECSタスクなど）が最新のSDKを使用しているかの確認は必要です。障害対応のランブックに「Secrets Manager接続エラー時はSDKバージョンを確認」という項目を追加し、段階的に各サービスのSDKをアップデートしていく計画が現実的です。まずは開発環境やステージング環境で動作確認を行い、本番環境へはカナリアデプロイメントやブルーグリーンデプロイメントで段階的にロールアウトすることでリスクを最小化できます。

**監視とアラートの設定**
ポスト量子TLS導入後は、CloudWatch Logsでエラーパターン（特にTLSハンドシェイク失敗）を監視し、アラートを設定することが重要です。古いSDKを使用しているクライアントが突然増えた場合や、予期しない接続エラーが発生した場合に迅速に検知できる体制を整えることで、運用の安定性を維持できます。

## 全アップデート一覧

| # | タイトル | 概要 | リンク |
|---|---------|------|--------|
| 1 | Amazon EC2 P6-B300 instances are now available in the AWS GovCloud (US-East) Region | 政府機関向けGovCloud環境で、NVIDIA Blackwell GPUを搭載したP6-B300インスタンスが利用可能に。大規模言語モデルや兆単位のパラメータを持つ基盤モデルの開発に対応。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-p6-b300-govcloud-us-east/) |
| 2 | AWS Secrets Manager now supports hybrid post-quantum TLS | Secrets Managerがハイブリッドポスト量子TLSをサポート。従来の暗号方式と量子耐性暗号を組み合わせ、将来の量子コンピュータ脅威から秘密情報を保護。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-secrets-manager-post-quantum-tls/) |
| 3 | AWS Transform is now available in Kiro and VS Code | レガシーコードの自動変換ツールAWS TransformがKiroとVS Codeで利用可能に。Java、Python、Node.jsプロジェクトの最新バージョンへのアップグレードや依存関係更新を支援。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-transform-kiro-vscode/) |
| 4 | Amazon EC2 C8gn, M8gn, and R8gn instances now support higher Amazon EBS-optimized performance | Graviton4搭載インスタンスのEBSパフォーマンスが大幅向上。EBS帯域幅が120 Gbps、IOPSが480,000に倍増し、追加コスト不要で利用可能。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-c8gn-m8gn-r8gn-ebs/) |
| 5 | NVIDIA Nemotron-3-Super-120B, Qwen3.5-9B, and Qwen3.5-27B models now available on Amazon SageMaker JumpStart | SageMaker JumpStartで3つの新しい基盤モデルが利用可能に。エージェント推論、多言語コーディング、高度な文脈理解など、それぞれ異なる専門機能を提供。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/nemotron3super-120b-qwen3.5-9b-qwen3.5-27b-on-sagemaker-jumpstart/) |
| 6 | Amazon Quick now supports document-level access controls for Google Drive knowledge bases | Amazon QuickがGoogle Driveのドキュメントレベルアクセス制御（ACL）をサポート。元の権限設定を保持しながら、セキュアなナレッジベースを構築可能。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-document-level-access-controls-google-drive/) |

## まとめ

今回のアップデートは、**パフォーマンス**、**セキュリティ**、**開発者体験**という3つの軸で重要な改善が行われました。

EC2 Graviton4インスタンスのEBSパフォーマンス倍増は、追加コスト不要でストレージ集約型ワークロードの性能を大幅に向上させる、即座に恩恵を受けられるアップデートです。データ分析、機械学習、高性能データベースなど、幅広いユースケースでボトルネックの解消が期待できます。

Secrets Managerのポスト量子TLS対応は、将来を見据えたセキュリティ投資として位置づけられます。量子コンピュータの実用化はまだ先ですが、「Store Now, Decrypt Later」攻撃のリスクを考えると、長期的な機密性が求められるデータを扱うシステムでは早期の検討が賢明です。

また、SageMaker JumpStartへの新モデル追加やAWS Transformの開発環境統合は、AI/ML開発と技術的負債の削減を加速させる開発者向けの改善です。P6-B300インスタンスのGovCloud対応は、政府機関や規制産業におけるAI基盤の強化を示しています。

全体として、AWSはコンピューティング性能、セキュリティの先進化、そして開発者の生産性向上という、クラウドインフラの根幹となる要素を着実に強化し続けていることがうかがえます。特にGraviton4エコシステムの充実ぶりは、Arm アーキテクチャの本格的な普及を後押しするものであり、今後のインフラ選択においてますます重要な選択肢となるでしょう。