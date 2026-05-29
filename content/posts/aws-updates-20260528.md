---
title: "【AWS】2026/05/28 のアップデートまとめ"
date: 2026-05-28T08:06:33+09:00
draft: false
tags: ["aws", "sagemaker", "ec2", "emr", "spark", "guardduty", "s3", "backup", "lake-formation", "connect", "hyperpod", "iceberg", "glue"]
categories: ["AWS Updates"]
summary: "2026/05/28 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260528/header.png)

# 2026年5月28日 AWS アップデート解説

## はじめに

2026年5月28日、AWSから6件のアップデートが発表されました。本日の注目ポイントは、**機械学習・データ分析基盤の性能とセキュリティの大幅強化**です。SageMaker Studio notebooks では NVIDIA H100 搭載の P5.4xl インスタンスが利用可能になり、LLM 開発の高速化とコスト削減が期待できます。また、Amazon EMR が Apache Spark 4.0.2 に対応し、ANSI SQL サポートや細粒度アクセス制御が強化されました。セキュリティ面では、GuardDuty が S3 継続的バックアップのマルウェアスキャンに対応し、ランサムウェア攻撃後の安全な復旧ポイント特定が可能になっています。

本記事では、特に影響範囲の大きい **Amazon EMR の Apache Spark 4.0.2 対応**と **GuardDuty の S3 継続的バックアップ対応**を深掘りし、SRE 視点での活用シナリオを解説します。

## 注目アップデート深掘り

### Amazon EMR が Apache Spark 4.0.2 に対応 - データエンジニアリングの民主化と強化されたセキュリティ

Amazon EMR で Apache Spark 4.0.2 の一般提供が開始されました。このアップデートは、データパイプラインの構築方法を大きく変える可能性を秘めています。

#### なぜこのアップデートが重要なのか

従来の Spark 3.x では、SQL エンジニアが複雑なデータ変換を扱う際に Python や Scala の知識が必要でした。また、機密データを含むデータレイクでは、テーブル単位のアクセス制御しかできず、行・列レベルの細かい制御には外部ツールやカスタムロジックが必要でした。Spark 4.0.2 では、**ANSI SQL 標準のサポート強化**と **VARIANT データ型**により、SQL だけで半構造化データを扱えるようになり、**Apache Lake Formation との統合**によって行・列レベルのきめ細かいアクセス制御（FGAC）が実現します。

#### ANSI SQL と VARIANT データ型の実装

Spark 4.0.2 では、ANSI SQL モードがデフォルトで有効化され、標準 SQL の動作により近くなりました。特に注目すべきは、JSON や API レスポンスなどの半構造化データを扱うための **VARIANT データ型**です。

```sql
-- VARIANT データ型を使った JSON データの処理例
CREATE TABLE api_responses (
  id STRING,
  response_data VARIANT,
  timestamp TIMESTAMP
) USING iceberg;

-- ネストされた JSON データのクエリ
SELECT 
  id,
  response_data:user.name::STRING AS user_name,
  response_data:metadata.request_id::STRING AS request_id,
  response_data:results[0].score::DOUBLE AS top_score
FROM api_responses
WHERE response_data:status::STRING = 'success';
```

従来の Spark 3.x では、JSON データを扱うために `from_json()` 関数や明示的なスキーマ定義が必要でしたが、VARIANT 型を使うことで、より直感的な SQL 構文でデータにアクセスできます。

#### Lake Formation による細粒度アクセス制御

Spark 4.0.2 では、AWS Lake Formation と統合された行レベル・列レベルのアクセス制御が可能になりました。これにより、データエンジニアは単一のテーブルを複数チームで共有しながら、機密情報を適切に保護できます。

```python
# PySpark での Lake Formation 統合例
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Spark4-FGAC-Demo") \
    .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.my_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
    .getOrCreate()

# Lake Formation のポリシーが自動的に適用される
df = spark.table("my_catalog.database.customer_data")

# ユーザーの権限に応じて、見える行・列が自動的にフィルタリングされる
df.show()
```

金融機関や医療機関など、コンプライアンス要件が厳しい環境では、この機能によってデータガバナンスを維持しながら、データ活用を加速できます。

#### Apache Iceberg v3 と S3 Tables 統合

Spark 4.0.2 は Apache Iceberg v3 テーブル形式をサポートし、Iceberg テーブルでの VARIANT データ型や AWS S3 Tables との統合を利用できます。半構造化データを含む分析テーブルを Iceberg で管理しやすくなるため、データレイクの標準化やテーブル形式の統一を進めている組織では移行検証の価値があります。

```sql
-- Iceberg v3 テーブルの作成例
CREATE TABLE customer_transactions (
  transaction_id STRING,
  customer_id STRING,
  amount DECIMAL(10,2),
  transaction_date DATE
) USING iceberg
TBLPROPERTIES (
  'format-version' = '3',
  'write.metadata.metrics.default' = 'full',
  'commit.manifest.min-count-to-merge' = '10'
);

-- テーブル履歴やスナップショットの確認
SELECT * FROM customer_transactions.history;
SELECT * FROM customer_transactions.snapshots;
```

#### ストリーミング機能の強化

Spark 4.0.2 では、ストリーミング処理の性能と機能が拡張されました。リアルタイム不正検知やパーソナライゼーションエンジンなど、レイテンシに敏感なアプリケーションのデプロイが迅速化されます。

```python
# Structured Streaming の拡張機能を活用した例
from pyspark.sql.functions import window, col

streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "transactions") \
    .load()

# リアルタイム集計とウィンドウ処理
windowed_counts = streaming_df \
    .selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*") \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("customer_id")
    ) \
    .count()

query = windowed_counts.writeStream \
    .outputMode("update") \
    .format("console") \
    .start()
```

### GuardDuty Malware Protection が S3 継続的バックアップに対応 - ランサムウェア対策の新標準

Amazon GuardDuty Malware Protection for AWS Backup が、Amazon S3 の継続的バックアップ（Point-in-Time Recovery）に対応しました。この機能は、ランサムウェア攻撃後の復旧戦略を根本から変える可能性があります。

#### なぜこのアップデートが重要なのか

ランサムウェア攻撃を受けた場合、バックアップからの復旧が最後の砦となります。しかし、従来の方法では「どの時点のバックアップが感染前のクリーンな状態か」を特定することが困難でした。攻撃者がシステムに潜伏している期間中に取得されたバックアップには、既にマルウェアが混入している可能性があります。S3 継続的バックアップのマルウェアスキャン機能により、バックアップタイムライン全体から安全な復旧ポイントを科学的に特定できるようになりました。

#### フルスキャンと増分スキャンの実装

AWS Backup のバックアッププラン内で、S3 継続的バックアップに対してフルスキャンまたは増分スキャンを設定できます。初回や重要データの棚卸しではフルスキャン、継続的な監視では変更分を対象にする増分スキャンを組み合わせることで、復旧前検証の実効性とコストのバランスを取りやすくなります。

運用設計では、次の点をバックアッププランやランブックに明記しておくと扱いやすくなります。

- **フルスキャンのタイミング**: 初回有効化時、重要な構成変更後、または定期的な基準点の確認
- **増分スキャンの対象**: 日常的な変更分の確認と、復旧候補時刻の絞り込み
- **オンデマンドスキャン**: インシデント対応時に、復旧したい任意の時点がクリーンかを確認

#### GetPITRMalwareScanResults API による復旧前検証

新しい `GetPITRMalwareScanResults` API を使用することで、特定の復旧時刻（Point-in-Time）がクリーンであることを復旧前に検証できます。

```python
import boto3
from datetime import datetime, timedelta

backup_client = boto3.client('backup')
guardduty_client = boto3.client('guardduty')

# 復旧候補となる時刻のマルウェアスキャン結果を確認
recovery_point_time = datetime.now() - timedelta(hours=48)

response = backup_client.get_pitr_malware_scan_results(
    ResourceArn='arn:aws:s3:::my-critical-bucket',
    RecoveryPointTime=recovery_point_time.isoformat()
)

if response['ScanStatus'] == 'COMPLETED':
    if response['MalwareDetected'] == False:
        print(f"復旧時刻 {recovery_point_time} はクリーンです。復旧を開始できます。")
    else:
        print(f"警告: 復旧時刻 {recovery_point_time} にマルウェアが検出されました。")
        print(f"検出されたマルウェア: {response['ThreatNames']}")
        # より古い時点を検証
else:
    print(f"スキャン状態: {response['ScanStatus']}")
```

#### インシデント対応フローへの組み込み

ランサムウェア攻撃を検知した際の典型的な復旧フローは以下のようになります。

1. 継続的バックアップの対象バケットと保持期間を確認
2. 攻撃検知時刻の前後で複数の復旧候補時刻を選定
3. オンデマンドスキャンと `GetPITRMalwareScanResults` で候補時刻のスキャン状態を確認
4. マルウェア検出がない最新の時点を復旧候補として承認
5. 復旧後にアプリケーション整合性、アクセスログ、GuardDuty / Security Hub の検知状況を再確認

このフローにより、「感染前の最新クリーン状態」への復旧が、推測ではなく科学的根拠に基づいて実行できます。

## SRE視点での活用ポイント

### Apache Spark 4.0.2 の運用シナリオ

Spark 4.0.2 の ANSI SQL と VARIANT データ型は、データエンジニアリングチームと SQL エンジニアの協業を促進します。Terraform でデータパイプラインインフラを管理している場合、EMR クラスタのバージョンアップグレードは段階的に実施できます。

```hcl
resource "aws_emr_cluster" "data_pipeline" {
  name          = "spark-4-data-pipeline"
  release_label = "emr-spark-8.0.0"  # Spark 4.0.2 を含む EMR Spark リリース
  applications  = ["Spark", "Hadoop", "Hive"]

  ec2_attributes {
    instance_profile = aws_iam_instance_profile.emr_profile.arn
    subnet_id        = aws_subnet.main.id
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 2
  }

  # Lake Formation 統合の有効化
  configurations_json = jsonencode([{
    "Classification" : "spark-hive-site",
    "Properties" : {
      "hive.metastore.client.factory.class" : "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
    }
  }])
}
```

既存の Spark 3.x ワークロードからの移行では、まずテスト環境で互換性を検証し、ANSI SQL モードでの挙動変更を確認することが推奨されます。特に、NULL 値の扱いや型変換の厳密性が変更されているため、既存の SQL クエリが意図した結果を返すか検証が必要です。

Lake Formation の FGAC 機能を導入する際は、IAM ロールと Lake Formation パーミッションの関係を整理し、「誰がどのデータにアクセスできるか」のポリシー設計が重要です。CloudWatch アラームと組み合わせて、アクセス拒否エラーが急増した場合に通知を受け取る仕組みを構築すると、権限設定ミスを早期に検知できます。

コスト面では、VARIANT データ型の使用により、複雑な JSON パース処理が不要になるため、Spark ジョブの実行時間が短縮され、EMR クラスタの稼働時間削減につながる可能性があります。パフォーマンステストで実行時間を計測し、コスト削減効果を定量化することが推奨されます。

### GuardDuty S3 継続的バックアップスキャンの運用シナリオ

ランサムウェア対策のランブック（障害対応手順書）に、GuardDuty のマルウェアスキャン機能を組み込むことで、復旧時間（RTO）と復旧ポイント（RPO）の両立が可能になります。

通常、S3 バケットの継続的バックアップは AWS Backup で自動化されていますが、「どの時点が安全か」の判断は人間が行う必要がありました。GetPITRMalwareScanResults API を使用することで、この判断プロセスを自動化し、スクリプト化できます。

```python
# ランブックに組み込むスクリプト例
def find_clean_recovery_point(resource_arn, max_lookback_hours=72):
    """
    指定されたリソースのクリーンな復旧ポイントを検索
    """
    backup_client = boto3.client('backup')
    current_time = datetime.now()
    
    for hours_back in range(0, max_lookback_hours, 6):
        check_time = current_time - timedelta(hours=hours_back)
        response = backup_client.get_pitr_malware_scan_results(
            ResourceArn=resource_arn,
            RecoveryPointTime=check_time.isoformat()
        )
        
        if response['ScanStatus'] == 'COMPLETED' and not response['MalwareDetected']:
            return check_time
    
    return None
```

CloudWatch Logs にスキャン結果を記録し、Security Hub と統合することで、組織全体のバックアップセキュリティ状態を可視化できます。

コスト面では、増分スキャンを活用することで、日次バックアップの継続的なマルウェア監視を低コストで実現しやすくなります。ただし、フルスキャンとのバランスを取るため、定期的に基準点を再確認する運用が現実的です。

導入判断としては、クリティカルなデータを S3 に保管している場合、特に規制要件がある業界（金融、医療、官公庁）では、この機能の導入がコンプライアンス対応として推奨されます。既存の AWS Backup 設定に対して、API または CLI でマルウェアスキャンを有効化するだけで利用開始できるため、導入ハードルは低いと言えます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon SageMaker Studio notebooks now support P5.4xl instance types](https://aws.amazon.com/about-aws/whats-new/2026/01/p5.4xl-new-launch-sagemaker-studio-notebooks/) | SageMaker Studio notebooks で NVIDIA H100 搭載の P5.4xl インスタンスが利用可能に。前世代比で最大 4 倍の高速化と最大 40% のコスト削減が期待でき、LLM や拡散モデルの学習・デプロイに活用可能。7つのリージョンで利用可能。 |
| 2 | [Amazon EMR now supports Apache Spark 4.0.2 in general availability](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark800-release.html) | Amazon EMR Spark 8.0.0 が Apache Spark 4.0.2 の一般提供を開始。ANSI SQL、VARIANT データ型、SQL PIPE 構文、SQL scripting、SQL UDF、ストリーミング機能拡張、Iceberg v3、Native FGAC / FTA をサポート。 |
| 3 | [Amazon Connect Customer now uses generative AI to automatically evaluate self-service interactions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-connect-customer-gen-AI-evaluations-self-service) | Amazon Connect Customer に生成AI による自動評価機能が追加。自然言語でカスタム評価基準を定義し、AI エージェントのセルフサービスインタラクション品質を自動評価。詳細な理由説明とトランスクリプト参照を提供。7つのリージョンで利用可能。 |
| 4 | [Amazon SageMaker HyperPod Slurm clusters now support specifying minimum capacity requirements with continuous provisioning](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-hyperpod-mincount/) | SageMaker HyperPod で Slurm クラスタの最小キャパシティ要件（MinCount）指定が可能に。分散学習ワークロードで必要な最小ノード数を保証し、クラスタが InService になるタイミングを制御。3時間のロールバック機構を実装。 |
| 5 | [Amazon EC2 X8i instances are now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-ec2-x8i-instances-SIN-SYD-PDT-region/) | EC2 X8i インスタンス（メモリ最適化型、カスタム Intel Xeon 6 搭載）がアジア太平洋（シンガポール、シドニー）と GovCloud（US-West）で利用可能に。前世代 X2i 比で最大 43% の性能向上、メモリ容量 1.5 倍（最大 6TB）、メモリ帯域幅 3.3 倍を実現。SAP HANA 認定取得。 |
| 6 | [Amazon GuardDuty Malware Protection for AWS Backup supports Amazon S3 continuous backups](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-guardduty-aws-backup-s3-continuous/) | GuardDuty Malware Protection が S3 継続的バックアップに対応。バックアップタイムライン全体から安全な復旧ポイントを特定可能に。フル/増分スキャンの選択、任意時点でのオンデマンドスキャン、新しい GetPITRMalwareScanResults API による復旧前検証を提供。 |

## まとめ

本日のアップデートは、**機械学習とデータ分析の性能向上**、**データガバナンスとセキュリティ強化**、そして**運用自動化の促進**という3つの軸で整理できます。

SageMaker の P5.4xl インスタンス対応と HyperPod の MinCount 機能により、大規模 AI/ML ワークロードの開発効率とコスト最適化が進みます。EMR の Spark 4.0.2 対応は、データエンジニアリングチームの生産性を向上させるとともに、Lake Formation 統合によってエンタープライズグレードのデータガバナンスを実現します。

セキュリティ面では、GuardDuty の S3 継続的バックアップ対応が、ランサムウェア対策の新しい標準を確立します。「感染前のクリーンな状態」を科学的に特定できることは、インシデント対応における意思決定の質を大きく向上させます。

これらのアップデートは、SRE チームがシステムの信頼性、セキュリティ、効率性を高めるための強力なツールとなります。特に、既存のインフラ自動化（Terraform、AWS CLI）や監視基盤（CloudWatch、Security Hub）と組み合わせることで、その効果を最大化できるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)
