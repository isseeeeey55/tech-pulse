---
title: "【AWS】2026/05/19 のアップデートまとめ"
date: 2026-05-19T08:02:17+09:00
draft: false
tags: ["aws", "glue", "redshift", "sam", "sagemaker", "lightsail", "cloudformation", "dynamodb", "athena", "emr", "lambda", "lake-formation", "evs", "local-zones"]
categories: ["AWS Updates"]
summary: "2026/05/19 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260519/header.png)

# 2026/05/19 AWS アップデート情報

## はじめに

2026年5月19日は、7件のAWSアップデートが発表されました。本日のアップデートは、データ基盤・分析領域とサーバーレス開発環境の改善に焦点が当てられています。特に、**AWS Glue zero-ETL のムンバイリージョン対応**と**Amazon Redshift の Iceberg テーブルサポート強化**は、データレイク構築とマルチエンジン分析基盤において大きな価値を提供します。また、**SAM CLI の CloudFormation Language Extensions 対応**は、ローカル開発体験を大きく改善するものです。

今回は、データエンジニアリングとサーバーレス開発の両面で注目度の高いアップデートを深掘りしていきます。

## 注目アップデート深掘り

### AWS Glue zero-ETL のムンバイリージョン対応とデータパイプライン運用の変革

AWS Glue zero-ETL がアジア太平洋（ムンバイ）リージョンで利用可能になりました。このサービスは、DynamoDB、Oracle Database@AWS、自社管理データベース（Oracle、SQL Server、MySQL、PostgreSQL）、そしてSalesforce、SAP、Zendesk、Zoho CRMといったSaaSアプリケーションから、分析用データストアへのデータレプリケーションを**完全マネージドサービス**として提供します。

#### なぜこのアップデートが重要なのか

従来のETLパイプライン構築では、データソースからの変更データキャプチャ（CDC）の実装、スキーママッピングの定義、増分レプリケーションの制御、エラーハンドリング、リトライロジックなど、多くのインフラコードを開発・運用する必要がありました。AWS Glue zero-ETL は、これらすべてを自動化し、データエンジニアがパイプラインのメンテナンスではなく、データから価値を引き出す作業に集中できるようにします。

ムンバイリージョンでの展開により、インド地域に拠点を置く企業は、低レイテンシでのデータレプリケーションが実現可能になります。特に金融、eコマース、SaaS企業など、リアルタイム性の高い分析が求められる領域で、データ移動の遅延を最小化できる点が重要です。

#### 従来のETLパイプラインとの比較

従来のAWS Glue ETLジョブでは、以下のようなPythonスクリプトを記述し、変更検知やエラーハンドリングを実装する必要がありました：

```python
# 従来のGlue ETL Jobの例（簡略化）
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# データソースからの読み込み、変換、書き込みロジックを実装
datasource = glueContext.create_dynamic_frame.from_catalog(...)
transformed = ApplyMapping.apply(frame = datasource, mappings = [...])
glueContext.write_dynamic_frame.from_options(...)

job.commit()
```

一方、AWS Glue zero-ETL では、コンソールまたはAWS CLIで統合を定義するだけで、スキーママッピング、CDC、増分レプリケーションがすべて自動化されます：

```bash
$ aws glue create-integration \
  --integration-name salesforce-to-redshift \
  --source-arn arn:aws:glue:ap-south-1:123456789012:connection/salesforce-connection \
  --target-arn arn:aws:redshift-serverless:ap-south-1:123456789012:namespace/analytics-namespace \
  --region ap-south-1
```

このコマンド一つで、Salesforceからの顧客データがRedshift Serverlessへ自動的にレプリケートされ、ほぼリアルタイムで分析可能になります。スキーマ変更も自動的に追従され、パイプラインの保守作業が劇的に削減されます。

#### リージョン固有の利点とコスト効率

ムンバイリージョンでの展開により、インド国内のデータレジデンシー要件を満たしながら、他のリージョンにデータを転送する際のデータ転送コストを削減できます。また、DynamoDBやOracle Database@AWSが同一リージョン内にある場合、ネットワークレイテンシが最小化され、レプリケーションのリアルタイム性が向上します。

従来のGlue ETLジョブと比較した場合、zero-ETLではGlue DPU（Data Processing Unit）の継続的な課金が不要になるため、小規模から中規模のデータ量では大幅なコスト削減が期待できます。ただし、大規模なバッチ処理や複雑な変換ロジックが必要な場合は、従来のGlue Jobの方が柔軟性とコスト効率で優位な場合もあるため、ユースケースに応じた選択が重要です。

---

### Amazon Redshift の Iceberg テーブルサポート強化によるデータレイクの柔軟性向上

Amazon Redshift が Apache Iceberg テーブルへの直接書き込みと ALTER TABLE DDL ステートメントのサポートを追加しました。AWS Glue Data Catalog（awsdatacatalog）マウント経由で、外部スキーマを作成することなくRedshiftの変換結果をデータレイクに直接保存できるようになります。

#### 背景：なぜ ALTER TABLE が重要なのか

Apache Iceberg は、大規模なデータレイクテーブル向けのオープンテーブルフォーマットで、スキーマの進化（Schema Evolution）、タイムトラベル、パーティション管理といった高度な機能を提供します。しかし、従来のRedshiftからIcebergテーブルへのアクセスは読み取り専用に近く、スキーマ変更やパーティション戦略の調整には、テーブル全体を削除してデータを再ロードする必要がありました。

このアップデートにより、Icebergテーブルの構造を段階的に進化させることができ、ビジネス要件の変化に柔軟に対応できるようになります。

#### 具体的な ALTER TABLE の操作例

以下は、Redshift から Iceberg テーブルのスキーマを変更する具体例です：

```sql
-- Iceberg テーブルに新しいカラムを追加
ALTER TABLE awsdatacatalog.sales_db.transactions
ADD COLUMN customer_segment VARCHAR(50);

-- カラム名を変更
ALTER TABLE awsdatacatalog.sales_db.transactions
RENAME COLUMN customer_id TO client_id;

-- パーティション戦略を追加（日次から月次に変更）
ALTER TABLE awsdatacatalog.sales_db.transactions
DROP PARTITION FIELD day(order_date);

ALTER TABLE awsdatacatalog.sales_db.transactions
ADD PARTITION FIELD month(order_date);

-- 圧縮タイプをカスタマイズ
ALTER TABLE awsdatacatalog.sales_db.transactions
SET TBLPROPERTIES ('write.parquet.compression-codec' = 'zstd');
```

これらの操作は、従来のようにテーブル削除とデータ再ロードを伴わず、既存データを保持したまま適用されます。ダウンタイムなしでスキーマを進化させることができるのは、運用上の大きなメリットです。

#### マルチエンジン分析基盤との相互運用性

Redshift で変更したIcebergテーブルは、Amazon Athena や Amazon EMR からも同じスキーマで即座にクエリ可能です。以下はAthenaからのクエリ例です：

```sql
-- Athena から同じ Iceberg テーブルをクエリ
SELECT client_id, customer_segment, SUM(amount) as total_sales
FROM sales_db.transactions
WHERE month(order_date) = 5
GROUP BY client_id, customer_segment;
```

この相互運用性により、データエンジニアリングチームはRedshiftで複雑なETL処理を実行し、データサイエンスチームはAthenaやEMR Sparkで機械学習向けの特徴量抽出を行うといった、役割分担が可能になります。

#### AWS Lake Formation との統合

AWS Lake Formation を使用すると、Icebergテーブルへのアクセス権限を一元管理できます。Redshiftからの書き込みもLake Formationのポリシーに従うため、セキュリティとガバナンスを維持しながらデータレイクを運用できます：

```bash
$ aws lakeformation grant-permissions \
  --principal DataLakePrincipalIdentifier=arn:aws:iam::123456789012:role/RedshiftRole \
  --resource '{"Table": {"DatabaseName": "sales_db", "Name": "transactions"}}' \
  --permissions "INSERT" "ALTER" \
  --region us-east-1
```

このアップデートは、データレイクを中心とした統合分析基盤の構築において、Redshiftの役割を大きく拡張するものです。

---

### AWS SAM CLI の CloudFormation Language Extensions 対応によるローカル開発体験の向上

AWS SAM CLI が CloudFormation Language Extensions に正式対応し、ローカル開発でのDRY（Don't Repeat Yourself）原則をサポートするようになりました。これにより、Lambda関数やDynamoDBテーブル、SNSトピックなど、複数の類似リソースを単一の定義から生成できます。

#### 従来の課題とLanguage Extensionsによる解決

従来のSAMテンプレートでは、複数の類似リソースを定義する際、すべてのリソースを個別に記述する必要がありました。例えば、複数のLambda関数を作成する場合：

```yaml
# 従来の方法：重複コードが多い
Resources:
  UserServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: app.lambda_handler
      CodeUri: user-service/
      Environment:
        Variables:
          SERVICE_NAME: user

  OrderServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: app.lambda_handler
      CodeUri: order-service/
      Environment:
        Variables:
          SERVICE_NAME: order

  PaymentServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: app.lambda_handler
      CodeUri: payment-service/
      Environment:
        Variables:
          SERVICE_NAME: payment
```

CloudFormation Language Extensions の `Fn::ForEach` を使用すると、これを以下のように簡潔に記述できます：

```yaml
# Language Extensions を使用した方法
Transform: AWS::LanguageExtensions
Resources:
  Fn::ForEach::Services:
    - ServiceName
    - [user, order, payment]
    - ${ServiceName}ServiceFunction:
        Type: AWS::Serverless::Function
        Properties:
          Runtime: python3.11
          Handler: app.lambda_handler
          CodeUri: !Sub ${ServiceName}-service/
          Environment:
            Variables:
              SERVICE_NAME: !Ref ServiceName
```

このテンプレートは、従来の3倍の記述量を削減しながら、同じ3つのLambda関数を生成します。

#### ローカル実行の流れ

今回のアップデートにより、SAM CLI は Language Extensions をメモリ内で自動的に展開し、ローカル実行します：

```bash
# テンプレートのビルド（拡張機能を展開）
$ sam build

# ローカルでLambda関数を呼び出し
$ sam local invoke UserServiceFunction -e events/user-event.json

# ローカルAPIサーバーを起動
$ sam local start-api

# テンプレートの検証（拡張機能の構文エラー検出）
$ sam validate
```

元のテンプレートはそのまま維持され、`sam deploy` でCloudFormationにデプロイする際も、CloudFormation側で拡張機能が処理されます。これにより、ローカルテストとクラウドデプロイの一貫性が保証されます。

#### 開発イテレーションサイクルの短縮

従来、Language Extensions を使用したテンプレートは、CloudFormationにデプロイして初めてエラーが検出されることがありました。例えば、`Fn::ForEach` の記述ミスやパラメータ参照エラーは、デプロイ時に初めて発覚し、修正後に再度デプロイする必要がありました。

今回の対応により、これらのエラーは `sam validate` や `sam build` の段階でローカルに検出できるため、クラウドへのデプロイ回数が削減され、開発スピードが大幅に向上します。

> **Note:** `Fn::Length`、`Fn::ToJsonString`、条件付き DeletionPolicy/UpdateReplacePolicy といった他の Language Extensions もサポートされています。

---

## SRE視点での活用ポイント

### データパイプラインの運用自動化とアラート設計

AWS Glue zero-ETL をデータ基盤に導入する際、SREとしてはレプリケーションの健全性監視が重要になります。CloudWatch メトリクスを使用して、レプリケーション遅延やエラー率を追跡し、閾値を超えた場合にアラートを発報する仕組みを構築するとよいでしょう。例えば、Terraformで以下のようなアラームを定義できます：

```hcl
resource "aws_cloudwatch_metric_alarm" "glue_zero_etl_lag" {
  alarm_name          = "glue-zero-etl-replication-lag"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReplicationLag"
  namespace           = "AWS/Glue"
  period              = 300
  statistic           = "Average"
  threshold           = 600  # 10分以上の遅延で警告
  alarm_description   = "Glue zero-ETL replication lag exceeds 10 minutes"
  dimensions = {
    IntegrationName = "salesforce-to-redshift"
  }
}
```

また、Redshift の Iceberg テーブルに対する ALTER TABLE 操作は、スキーマ変更の監査ログとして CloudTrail で記録されます。Terraform で管理しているインフラであれば、スキーマ変更を IaC に反映するプロセスを確立し、手動変更による構成ドリフトを防ぐことが推奨されます。

### サーバーレス開発のCI/CDパイプライン統合

SAM CLI の Language Extensions 対応は、CI/CDパイプラインにおけるテスト工程を充実させます。GitHub Actions や AWS CodePipeline で、`sam validate` と `sam build` をデプロイ前のステージに組み込むことで、構文エラーや依存関係の不足を早期に検出できます：

```yaml
# GitHub Actions の例
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: aws-actions/setup-sam@v2
      - name: Validate SAM template
        run: sam validate --lint
      - name: Build SAM application
        run: sam build
      - name: Run local tests
        run: sam local invoke --event test-events/event.json
```

また、マイクロサービス構成で多数のLambda関数を管理している場合、Language Extensions によるテンプレート記述量削減は、長期的な保守性向上につながります。ただし、チーム全体が `Fn::ForEach` の記法に習熟している必要があるため、ドキュメント整備や勉強会の実施が導入判断の一部となるでしょう。

SageMaker Flexible Training Plans による GPU 容量予約は、定期的な機械学習トレーニングを実行するチームにとって、予算管理とリソース確保の両面でメリットがあります。オンデマンドに比べ最大65%のコスト削減が見込まれるため、月次・四半期ごとのGPU利用予測を立て、予約期間と割引率のバランスを評価するとよいでしょう。予約期間終了の事前通知機能により、更新忘れのリスクも軽減されます。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Lightsail CDN distributions now support IPv6-only instances as origins](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-lightsail-cdn-ipv6/) | Lightsail CDN が IPv6 専用インスタンスをオリジンとしてサポート開始 |
| 2 | [AWS Glue zero-ETL is now available in Asia Pacific (Mumbai) region](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-glue-zero-etl-mumbai-region) | AWS Glue zero-ETL がムンバイリージョンで利用可能に。DynamoDB、Oracle、SaaS アプリケーションからの完全マネージドなデータレプリケーションを提供 |
| 3 | [AWS Management Console now displays AWS Local Zones in the Region Selector](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-local-zones-region-selector/) | AWS Management Console のリージョンセレクターに Local Zones が表示され、複数の Local Zones にまたがるリソース管理が効率化 |
| 4 | [Amazon Redshift adds ALTER TABLE for Iceberg tables and writes via the AWS Glue Data Catalog mount](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-redshift-alter-table-iceberg/) | Redshift が Iceberg テーブルへの直接書き込みと ALTER TABLE DDL をサポート。スキーマ、パーティション、プロパティの柔軟な変更が可能に |
| 5 | [Amazon EVS enables support for 32 hosts per environment](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-evs-32-hosts) | Amazon EVS の環境ごとの ESXi ホスト上限が 16 から 32 に倍増。VMware Cloud Foundation の柔軟な構成設計が可能に |
| 6 | [Amazon SageMaker Studio now supports GPU capacity reservation through SageMaker Flexible Training Plans](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-training-plan-support-for-studio/) | SageMaker Studio が Flexible Training Plans による GPU 容量予約に対応。オンデマンドと比較して最大 65% のコスト削減を実現 |
| 7 | [AWS SAM CLI adds AWS CloudFormation Language Extensions support to accelerate local serverless development](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-sam-cli-cloudformation/) | SAM CLI が CloudFormation Language Extensions に対応。ローカル開発での DRY 原則をサポートし、イテレーションサイクルを短縮 |

---

## まとめ

本日のアップデートは、**データ基盤の統合性**と**開発者体験の向上**という2つのテーマで構成されています。AWS Glue zero-ETL のムンバイ対応と Redshift の Iceberg サポート強化は、マルチエンジン分析基盤の構築において、データパイプラインの運用コストを削減し、スキーマの柔軟性を高めるものです。一方、SAM CLI の Language Extensions 対応は、サーバーレスアプリケーション開発におけるローカルテストの充実度を大きく向上させます。

また、SageMaker Flexible Training Plans の GPU 容量予約や Amazon EVS のホスト数拡張など、計算リソースの計画的な確保とコスト最適化を支援する機能も充実しています。これらのアップデートは、いずれも運用効率とコスト効率の両立を追求する SRE やデータエンジニアにとって、実務で即座に活用できる内容となっています。

今後も引き続き、各リージョンでのサービス展開や新機能のアップデートに注目していきましょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)