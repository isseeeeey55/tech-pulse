---
title: "【AWS】2026/04/22 のアップデートまとめ"
date: 2026-04-22T08:02:49+09:00
draft: true
tags: ["aws", "lambda", "s3", "aurora", "athena", "sagemaker", "backup", "redshift", "ec2", "connect", "iam", "privatelink", "cloudformation", "organizations", "marketplace"]
categories: ["AWS Updates"]
summary: "2026/04/22 のAWSアップデートまとめ"
---

# 2026年4月22日 AWS アップデート情報

## はじめに

2026年4月22日、AWSから10件のアップデートが発表されました。本日は特にデータベース・Lambda・SageMaker といったサービスを中心に、エンタープライズ運用の効率化とセキュリティ強化に直結するアップデートが目立ちます。

中でも注目すべきは **Lambda が S3 バケットをファイルシステムとしてマウントできる新機能**（S3 Files）と、**Aurora Serverless の最大30%のパフォーマンス向上**です。Lambda と S3 の統合はこれまで SDK 経由のダウンロード・アップロード処理が一般的でしたが、今回のアップデートでファイルシステム形式の直接アクセスが可能になり、特に AI/ML ワークロードの実装パターンが大きく変わる可能性があります。Aurora Serverless のアップグレードは、AI エージェント等のバースト型ワークロードへの最適化が進み、運用コスト削減とパフォーマンス改善を同時に実現します。

その他にも、Athena Spark の PrivateLink 対応、SageMaker のマルチリージョンレプリケーション、Connect のプライオリティダイヤリング機能など、エンタープライズ利用における利便性と安全性を高めるアップデートが揃っています。

---

## 注目アップデート深掘り

### 1. Lambda が S3 バケットをファイルシステムとしてマウント可能に（S3 Files）

#### なぜ重要なのか

従来、Lambda 関数から S3 上のファイルを扱う場合、AWS SDK を用いた明示的なダウンロード・アップロード処理が必要でした。この方式では、ファイルサイズが大きい場合に `/tmp` の容量制限（最大10GB）に引っかかったり、複数の Lambda 関数間でファイルを共有する際にカスタムな同期ロジックの実装が求められるといった課題がありました。

今回発表された **S3 Files** は、Lambda 関数が S3 バケットをファイルシステムとして直接マウントできる機能です。Amazon EFS をベースに構築されており、ファイルシステムとしての使いやすさと S3 のスケーラビリティ・耐久性・コスト効率を併せ持っています。これにより、標準的な POSIX ファイル操作（`open()`, `read()`, `write()` など）をそのまま使ってデータにアクセスでき、複数の Lambda 関数が同じファイルシステムを共有できるようになります。

特に AI/ML ワークロードや大規模なファイル処理パイプラインにおいて、以下のような恩恵が期待できます：

- **エージェントの状態管理**：AI エージェントが会話履歴やメモリを S3 Files に保存し、複数の呼び出しにまたがって状態を維持できる
- **パイプライン間のデータ共有**：前処理・推論・後処理といった複数ステップで中間結果を共有ワークスペースに書き込み、次ステップが参照
- **ダウンロード不要の直接処理**：機械学習モデルや大容量データセットに対して、ダウンロードせずにストリーミング形式でアクセス

#### 実装手順

S3 Files を Lambda 関数で利用するには、以下の手順を実施します。

**1. S3 バケットの作成と S3 Files ファイルシステムの準備**

まず、マウント対象となる S3 バケットを用意します。S3 Files は Amazon EFS をベースにしているため、Lambda コンソールまたは AWS CLI で S3 Files ファイルシステムを作成します。

```bash
$ aws s3 mb s3://my-lambda-shared-workspace
```

**2. Lambda 関数の設定で S3 Files をマウント**

Lambda コンソールまたは AWS SAM テンプレートで、関数に S3 Files ファイルシステムをマウントする設定を追加します。

AWS SAM テンプレート例：

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  MyLambdaFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: app.handler
      MemorySize: 1024
      Timeout: 300
      FileSystemConfigs:
        - Arn: arn:aws:elasticfilesystem:us-east-1:123456789012:access-point/fsap-xxxxxxxxxxxx
          LocalMountPath: /mnt/data
      Policies:
        - Statement:
          - Effect: Allow
            Action:
              - elasticfilesystem:ClientMount
              - elasticfilesystem:ClientWrite
            Resource: arn:aws:elasticfilesystem:us-east-1:123456789012:file-system/fs-xxxxxxxxxxxx
```

**3. Lambda 関数コードで標準ファイル操作を実行**

Python の例：

```python
import os

def handler(event, context):
    # S3 Files マウントポイントへのアクセス
    workspace = "/mnt/data"
    
    # ファイル書き込み（他の Lambda からも参照可能）
    with open(f"{workspace}/agent_memory.json", "w") as f:
        f.write('{"session_id": "abc123", "state": "processing"}')
    
    # ファイル読み込み
    if os.path.exists(f"{workspace}/shared_model.bin"):
        with open(f"{workspace}/shared_model.bin", "rb") as f:
            model_data = f.read()
            # モデルを直接メモリにロードして推論処理
    
    return {"statusCode": 200, "body": "Processed"}
```

**4. Lambda Durable Functions との組み合わせ**

新たに GA となった Lambda Durable Execution SDK for Java と組み合わせることで、長時間実行ワークフローの途中状態を S3 Files に永続化し、複数ステップにまたがる AI パイプラインを構築できます。

```java
import software.amazon.awssdk.services.lambda.durable.*;

public class WorkflowHandler implements RequestHandler<Input, Output> {
    @Override
    public Output handleRequest(Input input, Context context) {
        DurableExecutionContext durable = DurableExecutionContext.builder().build();
        
        // Step 1: データ前処理を実行し、S3 Files に結果保存
        durable.invokeFunction("preprocess", input);
        
        // Step 2: 外部 API 呼び出しを待機（最大1年間）
        durable.waitForCallback("external-api-callback");
        
        // Step 3: S3 Files から前処理結果を読み込んで最終処理
        durable.invokeFunction("finalize", input);
        
        return new Output("Workflow completed");
    }
}
```

#### 従来方式との比較

| 項目 | 従来方式（SDK 経由） | S3 Files |
|------|---------------------|----------|
| **ファイルアクセス方法** | `boto3.client('s3').download_file()` 等 | 標準 POSIX 操作（`open()`, `read()`） |
| **複数関数間の共有** | カスタム同期ロジックが必要 | 自動的に共有、ロック不要 |
| **/tmp 容量制限** | 10GB（ダウンロードサイズに制約） | マウントポイント経由でほぼ無制限 |
| **コスト** | S3 API リクエスト料金 + データ転送料金 | S3 料金のみ（追加料金なし） |
| **レイテンシ** | ダウンロード時間が必要 | ストリーミングアクセス可能 |

#### 活用シナリオ

- **AI エージェントのメモリ管理**：LangChain や LlamaIndex で構築したエージェントが、会話履歴やベクトル埋め込みを S3 Files に保存し、セッションをまたいで状態を維持
- **データパイプライン**：Lambda で大規模ログファイルを前処理 → 中間結果を S3 Files に保存 → 別の Lambda が後処理
- **機械学習推論**：学習済みモデル（数GB）を S3 Files に配置し、複数の Lambda 関数が同時にロードして推論処理を実行

---

### 2. Aurora Serverless が最大30%のパフォーマンス向上とスマートスケーリングを実現

#### なぜ重要なのか

Amazon Aurora Serverless は、使用量に応じて自動的にデータベース容量をスケールし、アイドル時にはゼロにスケールダウンしてコストを削減する機能を持つサービスです。これまでも開発環境やバースト型ワークロードに適していましたが、今回のアップデート（プラットフォームバージョン4）では、**最大30%のパフォーマンス向上**と**ワークロード理解型のスマートスケーリング**が導入されました。

特に注目すべきは、AI エージェントアプリケーションに最適化された点です。AI エージェントは通常、ユーザーリクエスト時に集中的なデータベース処理を実行し、その後は長時間アイドル状態になるという特性があります。新しいスケーリングアルゴリズムは、こうした不規則なパターンを学習し、必要なタイミングで迅速にスケールアップし、不要になればすぐにスケールダウンします。

また、Web アプリケーションや API サービスのように、複数のタスクが同時にリソースを競合する環境でも、より適切に容量を配分できるようになりました。従来はこうした要求の厳しいワークロードでは Aurora Provisioned が推奨されるケースもありましたが、v4 では Serverless のまま運用できる範囲が広がります。

#### パフォーマンス検証手順

プラットフォームバージョン3と4のパフォーマンス差を実測するには、以下の手順でベンチマークを実施します。

**1. 既存クラスターのバージョン確認**

```bash
$ aws rds describe-db-clusters \
    --db-cluster-identifier my-aurora-serverless \
    --query 'DBClusters[0].EngineVersion'
```

**2. v4 へのアップグレード（Blue/Green デプロイメント推奨）**

```bash
$ aws rds create-blue-green-deployment \
    --blue-green-deployment-name aurora-v4-upgrade \
    --source-arn arn:aws:rds:us-east-1:123456789012:cluster:my-aurora-serverless \
    --target-engine-version 8.0.mysql_aurora.4.0.0
```

Blue/Green デプロイメントを使用することで、本番環境への影響を最小限に抑えながら、新バージョンでのパフォーマンステストが可能です。

**3. 負荷テストの実施**

Apache Bench や Locust を使用して、同一のワークロードを v3 と v4 に対して実行し、スループットとレイテンシを比較します。

```bash
# v3 クラスターに対する負荷テスト
$ ab -n 10000 -c 100 https://api.example.com/v3/endpoint

# v4 クラスターに対する負荷テスト
$ ab -n 10000 -c 100 https://api.example.com/v4/endpoint
```

**4. CloudWatch メトリクスでの確認**

Aurora のパフォーマンスメトリクスを CloudWatch で可視化し、以下の指標を比較します：

- `DatabaseConnections`：同時接続数
- `CommitThroughput`：トランザクションスループット
- `SelectLatency`：SELECT クエリのレイテンシ
- `ACUUtilization`：Aurora Capacity Units の使用率

```python
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# v3 と v4 のレイテンシを取得して比較
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/RDS',
    MetricName='SelectLatency',
    Dimensions=[{'Name': 'DBClusterIdentifier', 'Value': 'my-aurora-v4'}],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=60,
    Statistics=['Average']
)

for datapoint in response['Datapoints']:
    print(f"Time: {datapoint['Timestamp']}, Latency: {datapoint['Average']} ms")
```

#### スマートスケーリングの動作確認

新しいスケーリングアルゴリズムの挙動を確認するには、以下のようなバースト型ワークロードを実行します。

**AI エージェントシミュレーション**

```python
import time
import mysql.connector

# Aurora Serverless v4 に接続
conn = mysql.connector.connect(
    host='my-cluster.cluster-xxxx.us-east-1.rds.amazonaws.com',
    user='admin',
    password='password',
    database='agents'
)

cursor = conn.cursor()

# バースト処理：短時間に大量のクエリを実行
for i in range(1000):
    cursor.execute("INSERT INTO conversations (session_id, message) VALUES (%s, %s)", 
                   (f"session-{i}", f"User message {i}"))
    cursor.execute("SELECT * FROM conversations WHERE session_id = %s", (f"session-{i}",))
    result = cursor.fetchall()

conn.commit()

# 長時間アイドル（スケールダウンを観察）
print("Waiting for scale-down...")
time.sleep(600)  # 10分間待機

# 再度バースト処理（スケールアップの速度を確認）
for i in range(1000, 2000):
    cursor.execute("INSERT INTO conversations (session_id, message) VALUES (%s, %s)", 
                   (f"session-{i}", f"User message {i}"))

conn.close()
```

CloudWatch で `ServerlessDatabaseCapacity` メトリクスを確認し、スケールアップ・ダウンのタイミングと速度を可視化します。

#### コスト試算

Aurora Serverless v4 のコストメリットを試算するには、以下の要素を考慮します：

- **ACU（Aurora Capacity Units）の最小・最大設定**：アイドル時の最小 ACU を 0.5 に設定することで、ほぼ使用していない時間帯のコストをほぼゼロにできる
- **実際の稼働パターン**：1日のうち業務時間（8時間）のみ高負荷、それ以外はアイドルの場合、従来の Provisioned インスタンス（24時間稼働）と比較して約70%のコスト削減が可能

```python
# コスト試算例（us-east-1 リージョン）
acu_price_per_hour = 0.12  # USD per ACU-hour

# シナリオ1: Provisioned (r6g.xlarge 相当 = 常時8 ACU)
provisioned_cost = 8 * acu_price_per_hour * 24 * 30  # 月額
print(f"Provisioned monthly cost: ${provisioned_cost:.2f}")

# シナリオ2: Serverless v4 (業務時間8h は8 ACU、その他16h は0.5 ACU)
serverless_cost = (8 * acu_price_per_hour * 8 + 0.5 * acu_price_per_hour * 16) * 30
print(f"Serverless v4 monthly cost: ${serverless_cost:.2f}")
print(f"Cost reduction: {(1 - serverless_cost / provisioned_cost) * 100:.1f}%")
```

---

## SRE視点での活用ポイント

### S3 Files の運用シナリオ

Lambda の S3 Files 機能は、SRE の観点からいくつかの重要な運用改善につながります。

**障害対応ランブックの自動化**では、複数の Lambda 関数が協調して障害復旧処理を実行する際、S3 Files を共有ワークスペースとして利用できます。たとえば、インシデント発生時に第一段階の Lambda が診断ログを S3 Files に書き込み、第二段階の Lambda がそれを読み込んで復旧スクリプトを実行するといったフローが、カスタムな同期処理なしで実装可能です。Lambda Durable Functions と組み合わせることで、長時間にわたる復旧処理のチェックポイントを S3 Files に保存し、途中で失敗しても再開できる仕組みを構築できます。

**コスト最適化の観点**では、従来の SDK 経由のダウンロード・アップロード処理では、S3 API リクエスト数とデータ転送量に応じた課金が発生していましたが、S3 Files ではファイルシステム形式のアクセスにより、こうした細かいリクエストが不要になります。特に大量の小ファイルを処理するワークロードでは、API リクエスト数の削減により運用コストを抑えられる可能性があります。

ただし、**導入時の注意点**として、S3 Files は Amazon EFS をベースにしているため、Lambda 関数が VPC 内に配置される必要があります。VPC Lambda の場合、コールドスタート時間が若干増加する可能性があるため、レイテンシ要件が厳しいリアルタイム処理では、事前に性能検証を実施することが推奨されます。また、複数の Lambda 関数が同じファイルに同時書き込みを行う場合、適切なロック機構を実装する必要があることも留意すべき点です。

### Aurora Serverless v4 のスケーリング戦略

Aurora Serverless v4 のスマートスケーリング機能は、SRE がオンコール対応を減らし、運用の自動化を進める上で有効です。

**アラート疲れの軽減**という点では、従来の Provisioned インスタンスではリソース逼迫時に手動でのスケールアップが必要でしたが、Serverless v4 では自動的にスケールするため、深夜のアラートやエスカレーションが減少します。CloudWatch アラームを `ACUUtilization` メトリクスに設定し、一定の閾値を超えた場合にのみ通知するようにすることで、真に対応が必要な異常事態のみに集中できます。

**本番環境への適用判断基準**としては、以下のようなワークロード特性を持つシステムで特に有効です：

- 業務時間帯とそれ以外で負荷が明確に異なる（例：社内向け管理画面）
- バースト的なトラフィックが発生する（例：キャンペーン時のアクセス集中）
- 開発・ステージング環境で常時稼働させる必要がない

一方、常に一定の高負荷が予想されるシステム（24時間稼働の顧客向け API など）では、Provisioned インスタンスの方がコストパフォーマンスが良い場合もあるため、CloudWatch のコスト最適化ダッシュボードで実際の ACU 使用量を可視化し、定期的に見直すことが重要です。

**Terraform での管理**を検討する場合、Aurora Serverless v4 のスケーリング設定は以下のように記述できます：

```hcl
resource "aws_rds_cluster" "aurora_serverless_v4" {
  cluster_identifier      = "my-aurora-serverless-v4"
  engine                  = "aurora-mysql"
  engine_version          = "8.0.mysql_aurora.4.0.0"
  database_name           = "mydb"
  master_username         = "admin"
  master_password         = var.db_password
  
  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 16
  }
  
  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
```

---

## 全アップデート一覧

| # | タイトル | 概要 | リンク |
|---|----------|------|--------|
| 1 | **SageMaker が IAM Identity Center のマルチリージョンレプリケーションをサポート** | SageMaker Unified Studio ドメインを IdC インスタンスとは異なるリージョンにデプロイ可能に。データレジデンシー要件を満たしながら一元化された SSO アクセスを維持。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/smus-identity-center/) |
| 2 | **AWS Transform custom が6つの追加リージョンで利用可能** | 東京、ムンバイ、ソウル、シドニー、カナダ中部、ロンドンで提供開始。大規模なコード現代化をカスタムトランスフォーメーションで実現。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-atx-custom-additional-regions/) |
| 3 | **Athena Spark が AWS PrivateLink に対応** | VPC 内のクライアントからパブリックインターネットを経由せずに Athena Spark の全エンドポイントにアクセス可能に。Spark Connect、Live UI、History Server すべてに対応。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-athena-spark-aws-privatelink/) |
| 4 | **AWS Backup が Redshift Serverless と Aurora DSQL をサポート** | AWS Organizations のバックアップポリシーで、Redshift Serverless と Aurora DSQL をリソースタイプとして直接指定可能に。組織全体のバックアップガバナンスを強化。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/backup-policies-aurora-dsql-redshift-serverless/) |
| 5 | **AWS Marketplace が EU・ノルウェー・英国での VAT 支払いを自動化** | デジタルサービス販売における VAT 処理を自動化。請求書を提出すると自動検証・振込を実施。複数取引の統合請求と監査対応レポート機能を提供。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-marketplace-vat/) |
| 6 | **EC2 G7e インスタンスがロサンゼルスの Local Zones で利用可能** | NVIDIA RTX PRO 6000 Blackwell Server Edition GPU と第5世代 Intel Xeon を搭載。VFX 編集・LLM 推論・エッジ AI など、低レイテンシが求められるワークロードに対応。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-g7e-instances-local-zones/) |
| 7 | **Lambda Durable Execution SDK for Java が GA** | 長時間実行ワークフローを構築可能に。進捗の自動チェックポイント、最大1年間の実行一時停止機能を提供。Java 17+ 対応、ローカルテストエミュレーター搭載。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/lambda-durable-execution-java-ga/) |
| 8 | **Lambda が S3 バケットをファイルシステムとしてマウント可能に** | S3 Files により、Lambda 関数が S3 をファイルシステムとして直接マウント。複数の Lambda 関数が共有ワークスペースを通じてデータを共有可能。AI/ML ワークロードに最適。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-lambda-amazon-s3/) |
| 9 | **Aurora Serverless が最大30%のパフォーマンス向上とスマートスケーリングを実現** | プラットフォームバージョン4で提供。ワークロード理解型スケーリング、AI エージェント最適化、ゼロスケール対応。追加料金なし。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aurora-serverless-smarter-scaling/) |
| 10 | **Amazon Connect Outbound Campaigns が連絡先優先順位付けをサポート** | 最大10個のプロフィール属性に基づいて架電順序を設定可能。顧客 LTV、アカウント階級、予約日時などでセグメントをソート。追加コストなし。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-priority-dialing/) |

---

## まとめ

本日のアップデートは、**サーバーレス技術の成熟**と**エンタープライズ運用の効率化**という2つの大きなテーマが浮かび上がりました。

Lambda と S3 Files の統合、Lambda Durable Execution SDK for Java の GA、Aurora Serverless v4 のパフォーマンス向上は、いずれもサーバーレスアーキテクチャの適用範囲を大きく広げるものです。特に AI/ML ワークロードにおいて、これまで ECS や EKS で構築していた処理を Lambda ベースに移行できるケースが増えるでしょう。Lambda の実行時間制限（最大15分）や /tmp 容量制限といった課題が、S3 Files と Durable Functions により緩和され、より複雑なワークフローをサーバーレスで実現できるようになります。

一方、SageMaker のマルチリージョンレプリケーション、Athena Spark の PrivateLink 対応、AWS Backup の新サービス対応など、エンタープライズ環境でのガバナンス・コンプライアンス要件に応えるアップデートも充実しています。データレジデンシー要件が厳しい金融・ヘルスケア業界での AWS 活用が、さらに進むことが期待されます。

SRE の観点では、これらのアップデートを活用することで、手動運用の削減、コスト最適化、セキュリティ強化を同時に進められます。特に Aurora Serverless v4 のスマートスケーリングは、オンコール対応の負担を軽減し、より戦略的な業務に集中できる環境を提供します。Terraform や CloudFormation でこれらの新機能を IaC 化し、継続的に改善していくことが、今後の SRE 運用の鍵となるでしょう。