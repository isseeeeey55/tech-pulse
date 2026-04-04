---
title: "【AWS】2026/04/04 のアップデートまとめ"
date: 2026-04-04T08:01:16+09:00
draft: false
tags: ["aws", "glue", "emr", "bedrock", "sagemaker", "secretsmanager", "marketplace", "cloudwatch", "kms", "prometheus", "opentelemetry", "spark"]
categories: ["AWS Updates"]
summary: "2026/04/04 のAWSアップデートまとめ。CloudWatch Query StudioでPromQLネイティブサポート、EMRにKiro powersでSparkトラブルシューティング、Bedrock Guardrailsクロスアカウント保護のGA化など8件"
---

![](/tech-pulse/images/aws-updates-20260404/header.png)

## はじめに

2026年4月4日のAWSアップデートは8件です。CloudWatch Query StudioがPromQLをネイティブサポート（プレビュー）、EMRにKiro powersによるSparkトラブルシューティングエージェントが追加、Bedrock Guardrailsのクロスアカウント保護がGAになりました。監視まわりの統合が進んだ一日です。

## 注目アップデート深掘り

### Amazon CloudWatch Query Studio Preview - PromQLネイティブサポート

> **PromQLとは？**
> Prometheusが採用しているクエリ言語です。Kubernetesの監視で広く使われており、`rate()`や`avg_over_time()`といった関数でメトリクスを柔軟に集計できます。CloudWatch Metrics Insightsとは構文が異なるため、これまでは使い分けが必要でした。

![CloudWatch Query Studio：監視統合のBefore/After](/tech-pulse/images/aws-updates-20260404/query-studio-comparison.png)

CloudWatchにPromQLネイティブサポートが入りました。PrometheusベースのメトリクスとCloudWatchメトリクスを併用している環境では、別々の画面とクエリ言語を使い分ける必要があった。Query Studioでは両方を1つのインターフェースで扱えます。

対応リージョンは現時点で5つ（バージニア、オレゴン、シドニー、シンガポール、アイルランド）。東京リージョンはまだプレビュー対象外ですが、今後の追加に期待です。

**検証ポイント**

PromQLでEC2のCPU使用率を5分間の平均で取得する例：

```promql
# CloudWatch Metrics Insights
SELECT AVG(CPUUtilization) FROM "AWS/EC2" WHERE InstanceId = 'i-1234567890abcdef0'

# PromQL
avg_over_time(aws_ec2_cpuutilization{instance_id="i-1234567890abcdef0"}[5m])
```

OpenTelemetryメトリクスとAWSメトリクスを同一クエリで扱えるのが実用上のポイントです。アプリのリクエスト数とEC2のCPU使用率を相関分析するケース：

```promql
rate(http_requests_total[5m]) / on() group_left aws_ec2_cpuutilization
```

従来は画面を行き来して手動で突き合わせていた作業が、ワンクエリで済みます。

### Amazon EMR - Spark トラブルシューティング with Kiro Powers

> **Kiro powersとは？**
> AWSのAIコーディングアシスタント「Kiro」のプラグイン機能です。IDE上でKiroをインストールし、各種powersを追加することで特定ドメインのAI支援が受けられます。MCP Proxy for AWS経由でIAMロールベースの認証を行い、操作はCloudTrailに記録されます。

Sparkジョブのトラブルシューティングは、ログを追ってメモリ設定やパーティション戦略を手動で調整する地道な作業でした。Kiro powersはログ・メトリクス・設定を横断的に分析し、根本原因の特定から修正案の提示まで自動化してくれます。

対応環境はEMR on EC2とEMR Serverless。PySpark向けには具体的なコード改善案も出力されます。

**トラブルシューティングの例**

メモリ不足エラーが発生した場合、従来は手動でログを追う必要がありました：

```bash
$ aws emr describe-step --cluster-id j-1234567890ABC --step-id s-1234567890ABC
$ aws logs get-log-events --log-group-name /aws/emr/j-1234567890ABC/spark
```

Kiroはこれらを自動解析し、以下のような改善案を提示します：

```python
# Kiro が提案する修正例
spark = SparkSession.builder \
    .appName("OptimizedExample") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

large_df = spark.read.parquet("s3://bucket/large-dataset/") \
    .repartition(200)  # 最適なパーティション数をKiroが提案
result = large_df.groupBy("category").agg({"amount": "sum"}) \
    .write.mode("overwrite").parquet("s3://output-bucket/")
```

Sparkバージョンのアップグレード支援も別のpowerとして提供されています。EMR 6.5 → 7.12 のような大きなジャンプでも、コード変換・依存関係の解決・データ品質比較まで対応。全商用リージョンで利用可能です。

## SRE視点での活用ポイント

**CloudWatch Query Studioの運用活用**

Kubernetesクラスター上のマイクロサービス監視では、PrometheusでアプリケーションメトリクスをCloudWatchでAWSリソースメトリクスを別々に見ていたケースが多いはずです。Query Studioで統合できれば、障害対応時の根本原因分析がシンプルになります。

レスポンス時間の劣化が起きた際、アプリのレイテンシとRDSの接続数、EC2のCPU使用率を同時に分析して相関を特定できる。PromQLベースの複雑な条件でCloudWatchアラートを設定することも可能です。ただしプレビュー段階なので、本番アラートへの組み込みはGA後が無難でしょう。

**EMR Spark運用の自動化**

データパイプラインのSparkジョブ失敗は深夜や休日に起きがちです。Kiro powersの自動診断をオンコールランブックに組み込めば、一次対応の負荷を減らせます。「Kiroに初期診断を実行させ、提案された修正案を確認する」というステップを加えるイメージ。

ただし本番環境への導入は段階的に。まずdev/staging環境でKiroの提案精度を検証し、誤った修正が適用されるリスクを把握しておくべきです。

**セキュリティとコンプライアンス**

Bedrock GuardrailsのクロスアカウントGA化で、Organizations配下でのAIモデル利用ポリシーを一元管理できるようになりました。有害コンテンツの最大88%をブロックできるとされています。Secrets ManagerのカスタムKMSキー対応と合わせて、暗号化ポリシーの柔軟化にも活用できます。

## 全アップデート一覧

> **SageMaker Data Agentとは？**
> Amazon Bedrockのモデルと連携して、構造化・非構造化データに対する推論を実行するマネージドサービスです。データソースへの接続とプロンプト実行をサーバーレスで処理します。

| サービス | アップデート内容 |
|---------|------------------|
| [AWS Glue](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-gsr-3-more-regions/) | Schema Registry が新たに3リージョンで利用可能に |
| [Amazon EMR](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-emr-spark-troubleshooting-upgrade-kiro-power/) | Kiro powers による Spark トラブルシューティング・アップグレードエージェント |
| [Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/04/bedrock-guardrails-cross-account-safeguards/) | Guardrails のクロスアカウント保護が GA |
| [Amazon SageMaker](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-sgmkr-dataagent-chart-mv/) | Data Agent にチャート機能とマテリアライズドビューを追加 |
| [AWS Secrets Manager](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-secrets-manager-console-custom-kms-key-input/) | コンソールでカスタムKMSキーの入力が可能に |
| [AWS Marketplace](https://aws.amazon.com/about-aws/whats-new/2026/04/partner-revenue-supports-mp-metering/) | Partner Revenue Measurement で Marketplace Metering をサポート |
| [AWS Partner](https://aws.amazon.com/about-aws/whats-new/2026/04/partner-revenue-measurement-user-agent-support/) | 特定サービスで User Agent 文字列をサポート |
| [Amazon CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudwatch-query-studio-preview/) | Query Studio で PromQL ネイティブサポート（プレビュー） |

## まとめ

8件中、CloudWatch Query StudioのPromQLサポートとEMRのKiro powersが実務へのインパクトが大きいです。前者はPrometheus + CloudWatchの二重管理から脱却できる可能性があり、後者はSparkジョブの障害対応を自動化する手段を提供しています。Bedrock Guardrailsのクロスアカウント保護GA化も、マルチアカウント環境でAIを運用しているチームに効くアップデートです。
