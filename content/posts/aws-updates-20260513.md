---
title: "【AWS】2026/05/13 のアップデートまとめ"
date: 2026-05-13T08:02:05+09:00
draft: true
tags: ["aws", "lambda", "eventbridge", "sagemaker", "redshift", "eks", "ec2"]
categories: ["AWS Updates"]
summary: "2026/05/13 のAWSアップデートまとめ"
---

# 2026年5月13日 AWS アップデート解説

## はじめに

2026年5月13日、AWSから7件のアップデートが発表されました。本日の注目ポイントは、**Lambda Managed Instancesへのスケジュール済みスケーリング対応**と、**EventBridge Schedulerの大幅な機能拡張**です。予測可能なトラフィックパターンに対して事前にキャパシティを調整できるようになり、運用自動化の選択肢が大きく広がりました。また、Redshiftの新世代RGインスタンス、KarpenterのARC対応、ENA ExpressのAZ間通信対応など、パフォーマンスと可用性に関する重要なアップデートも含まれています。

## 注目アップデート深掘り

### AWS Lambda Managed Instancesのスケジュール済みスケーリング

#### なぜこのアップデートが重要なのか

Lambda Managed Instancesは、マネージドEC2インスタンス上でLambda関数を実行できる機能で、ルーティング、ロードバランシング、オートスケーリングが組み込まれています。これまで、営業時間アプリケーションやマーケティングイベントなど予測可能なトラフィックパターンを持つワークロードでは、需要変化の前に手動でキャパシティを調整するか、カスタムオートメーションを構築する必要がありました。

今回のアップデートにより、Amazon EventBridge Schedulerを使用して、期待されるトラフィックの前に事前にキャパシティ制限を調整するスケジュールを定義できるようになりました。これにより、ピーク時間前にパフォーマンス目標を達成しながら、アイドル期間のコストを削減できます。

#### スケジュール設定の実装手順

まず、EventBridge Schedulerでスケジュールを作成する基本的な手順を見ていきます。営業時間（平日9時〜18時）にキャパシティを段階的に増加させ、終業後はゼロにスケールダウンする例を考えます。

AWS CLIを使用した設定例：

```bash
# 営業開始30分前（8:30）にキャパシティを増加
$ aws scheduler create-schedule \
  --name "lambda-scale-up-weekday" \
  --schedule-expression "cron(30 8 ? * MON-FRI *)" \
  --schedule-expression-timezone "Asia/Tokyo" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:lambda:ap-northeast-1:123456789012:function:my-function",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeSchedulerRole",
    "Input": "{\"ReservedConcurrentExecutions\": 100}"
  }'

# 営業終了後（18:30）にキャパシティをゼロに削減
$ aws scheduler create-schedule \
  --name "lambda-scale-down-weekday" \
  --schedule-expression "cron(30 18 ? * MON-FRI *)" \
  --schedule-expression-timezone "Asia/Tokyo" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:lambda:ap-northeast-1:123456789012:function:my-function",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeSchedulerRole",
    "Input": "{\"ReservedConcurrentExecutions\": 0}"
  }'
```

#### 従来の手動調整との比較

従来の運用では、以下のような対応が必要でした：

- **手動調整**: 管理者が毎日/毎週決まった時間にコンソールまたはCLIでキャパシティを変更
- **Lambda Insights + CloudWatch Alarms**: メトリクスベースのリアクティブなスケーリング（閾値到達後に反応）
- **カスタムオートメーション**: 独自のLambda関数やStep Functionsを組み合わせたスケジューラー構築

スケジュール済みスケーリングは、これらと比較して以下の利点があります：

- **予測可能なトラフィックに対するプロアクティブな対応**: ピーク前にキャパシティを確保
- **運用負荷の削減**: 手動操作が不要
- **標準機能としての信頼性**: カスタムコードのメンテナンス不要
- **タイムゾーン対応**: グローバル展開時に各リージョンの時間帯を考慮した設定が容易

#### 実践的な設定パターン

マーケティングキャンペーンの例として、キャンペーン開始予定時刻の数時間前にキャパシティを拡大し、終了後に段階的に縮小する設定を考えます：

```bash
# キャンペーン開始4時間前に準備
$ aws scheduler create-schedule \
  --name "campaign-prep" \
  --schedule-expression "at(2026-05-20T06:00:00)" \
  --schedule-expression-timezone "UTC" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:campaign-processor",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeSchedulerRole",
    "Input": "{\"ReservedConcurrentExecutions\": 500}"
  }'

# キャンペーン終了2時間後に削減
$ aws scheduler create-schedule \
  --name "campaign-scale-down" \
  --schedule-expression "at(2026-05-20T14:00:00)" \
  --schedule-expression-timezone "UTC" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:campaign-processor",
    "RoleArn": "arn:aws:iam::123456789012:role/EventBridgeSchedulerRole",
    "Input": "{\"ReservedConcurrentExecutions\": 50}"
  }'
```

> **Note:** スケジュール実行が失敗した場合、EventBridge Schedulerは自動的にリトライを行います。Dead Letter Queue（DLQ）を設定することで、失敗したスケジュール実行を追跡し、SNS通知と組み合わせることで運用チームへのアラートを実現できます。

### EventBridge Schedulerの大幅な機能拡張

#### 619個の新規SDK APIアクション追加の意義

今回のアップデートで、EventBridge Schedulerは新たに13個のAWSサービスと統合され、合計619個の新しいSDK APIアクションが利用できるようになりました。特にAWS Lambda Managed Instancesへの対応により、時間ベースのスケジュールで直接スケーリング制御が可能になります。

従来、カスタム統合コードを書く必要があった複雑な操作が、EventBridge Schedulerから直接実行可能になったことで、開発の手間が大幅に削減されます。これにより、270以上のAWSサービスへの直接呼び出しが可能になり、インフラストラクチャの自動化がより包括的になります。

#### 従来のカスタム統合との比較

従来の方法では、EventBridge RuleからLambda関数をトリガーし、そのLambda関数内でBoto3などのSDKを使用してターゲットサービスのAPIを呼び出す必要がありました：

**従来の方法（カスタムLambda関数が必要）:**

```python
# Lambda関数のコード例（従来）
import boto3

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    
    # Lambda Managed Instancesのキャパシティを更新
    response = lambda_client.put_function_concurrency(
        FunctionName='my-function',
        ReservedConcurrentExecutions=100
    )
    
    return response
```

**新しい方法（EventBridge Schedulerから直接呼び出し）:**

```bash
# カスタムコード不要、Schedulerから直接API呼び出し
$ aws scheduler create-schedule \
  --name "direct-api-call" \
  --schedule-expression "rate(1 hour)" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:lambda:putFunctionConcurrency",
    "RoleArn": "arn:aws:iam::123456789012:role/SchedulerExecutionRole",
    "Input": "{\"FunctionName\": \"my-function\", \"ReservedConcurrentExecutions\": 100}"
  }'
```

この変更により、Lambda関数のデプロイ、バージョン管理、エラーハンドリング、ログ管理といった運用負荷が不要になります。

#### 実装例：マルチリージョン展開の自動化

EventBridge Schedulerの拡張機能を活用して、マルチリージョンでの定期処理を一元管理する例を示します：

```bash
# 各リージョンの営業時間に合わせたスケジューリング
$ aws scheduler create-schedule \
  --name "apac-business-hours-scale" \
  --schedule-expression "cron(0 9 ? * MON-FRI *)" \
  --schedule-expression-timezone "Asia/Tokyo" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:lambda:putFunctionConcurrency",
    "RoleArn": "arn:aws:iam::123456789012:role/SchedulerExecutionRole",
    "Input": "{\"FunctionName\": \"apac-processor\", \"ReservedConcurrentExecutions\": 200}",
    "RetryPolicy": {
      "MaximumEventAge": 86400,
      "MaximumRetryAttempts": 3
    }
  }'
```

> **Note:** 新しいAPI統合は、すべてのEventBridge Scheduler利用可能リージョンで提供されています。リージョンごとの対応状況は、AWSドキュメントで最新情報を確認してください。

## SRE視点での活用ポイント

### Lambda Managed Instancesスケジューリングの運用改善

予測可能なトラフィックパターンを持つシステムでは、スケジュール済みスケーリングが大きな運用改善をもたらします。営業時間アプリケーションであれば、営業開始前に段階的にキャパシティを増加させ、終業後はゼロにスケールダウンすることで、アイドル期間のコストを削減できます。

Terraformでインフラを管理している場合、EventBridge Schedulerリソースをコード化することで、環境ごとに異なるスケーリングポリシーを宣言的に管理できます。開発環境では最小限のキャパシティ、本番環境ではピーク時の需要に対応したキャパシティをそれぞれ定義し、同じテンプレートから展開可能です。

CloudWatch Alarmsと組み合わせることで、スケジュールベースのプロアクティブなスケーリングと、メトリクスベースのリアクティブなスケーリングを両立できます。予期しないトラフィック急増にはアラームベースで対応し、通常のピークパターンにはスケジュールで対応するハイブリッド戦略が有効です。

導入時の注意点として、スケジュール実行の失敗を監視する仕組みが必要です。Dead Letter QueueとSNS通知を組み合わせ、スケジュール実行が失敗した場合に運用チームへアラートを送る設計を推奨します。また、タイムゾーンの設定ミスによる意図しない時間帯でのスケーリングを防ぐため、テスト環境での十分な検証が重要です。

### EventBridge Scheduler拡張によるオーケストレーション簡素化

619個の新規API統合により、複数のAWSサービスにまたがる定期処理を、カスタムコードなしで実装できるようになりました。CI/CDパイプラインの自動トリガーや、定期的なデータパイプラインの実行と必要に応じたリソース調整を、一つのスケジューラーから管理できます。

障害対応のランブックに組み込む際は、EventBridge Schedulerの`RetryPolicy`設定を活用し、一時的な障害に対する自動リトライを構成することで、運用の堅牢性が向上します。最大イベント保持期間と最大リトライ回数を適切に設定し、失敗した実行はDLQに送信して後続の分析に活用できます。

導入判断の基準として、既存のカスタムLambda関数ベースのスケジューラーと比較し、保守コスト削減効果を評価することをおすすめします。Lambda関数のデプロイパイプライン、ユニットテスト、ログ分析といった運用コストが削減される一方、EventBridge Schedulerの制限事項（スケジュール数、入力ペイロードサイズなど）を考慮する必要があります。

## 全アップデート一覧

| タイトル | 概要 | リンク |
|---------|------|--------|
| AWS Lambda supports scheduled scaling for functions on Lambda Managed Instances | Lambda Managed Instances上で実行される関数に対して、EventBridge Schedulerを使用したスケジュール済みスケーリング機能をサポート。予測可能なトラフィックパターンに対して事前にキャパシティを調整可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-lambda-managed-instances/) |
| Amazon SageMaker Feature Store now supports SageMaker Python SDK V3 | SageMaker Feature StoreがPython SDK v3に対応。Lake Formationによるカラムレベル・行レベルのアクセス制御と、Apache Icebergテーブルプロパティ設定が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-feature-store-pyv3/) |
| Amazon EventBridge Scheduler adds 619 new SDK API actions, including Lambda Managed Instances | EventBridge Schedulerが619個の新規SDK APIアクションをサポート。13個の新サービスと統合し、Lambda Managed Instancesのスケーリング制御に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-eventbridge-sdk-integrations/) |
| Karpenter now supports Amazon Application Recovery Controller zonal shift | KarpenterがARCゾーナルシフト・ゾーナルオートシフトに対応。AZ障害時に自動的にトラフィックを健全なAZへ転向し、障害AZでのキャパシティプロビジョニングを停止 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/karpenter-arc-zonal-shift/) |
| Amazon Redshift launches RG instances powered by AWS Graviton | AWS Graviton搭載の新世代RGインスタンスを一般提供開始。RA3と比べて最大2.4倍高速で、vCPUあたり30%低価格。カスタム構築のベクトル化データレイククエリエンジンを搭載 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-redshift-rg-instances-powered-by-graviton) |
| Announcing Region Expansion of P6-B200 instances on SageMaker Studio notebooks | SageMaker Studio notebooksでP6-B200インスタンスがUS Eastリージョンで一般提供開始。8個のNVIDIA Blackwell GPU搭載、AIトレーニングでP5enと比べて最大2倍のパフォーマンス向上 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/p6-b200-region-expansion-sagemaker-studio-notebooks/) |
| ENA Express for Amazon EC2 instances now supports traffic between Availability Zones | ENA ExpressがAZ間通信に対応。独自プロトコルSRDにより、単一フロー当たり最大25 Gbpsの帯域幅を実現（従来の5 Gbpsから5倍向上） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/ena-express-availability-zones/) |

## まとめ

本日のアップデートは、**運用自動化**と**パフォーマンス向上**という2つの軸で大きな進展がありました。Lambda Managed InstancesとEventBridge Schedulerの組み合わせにより、予測可能なワークロードの運用が大幅に簡素化されます。カスタムコードを書かずに、宣言的なスケジュール定義だけで複雑な運用シナリオを実現できるようになりました。

また、Redshiftの新世代RGインスタンス、P6-B200のリージョン拡大、ENA ExpressのAZ間対応など、パフォーマンスと可用性に関する重要な機能強化も含まれています。KarpenterのARC統合は、EKSクラスタの高可用性運用において自動化の新たな選択肢を提供します。

SageMaker Feature StoreのSDK v3対応は、Lake Formationとの統合により、機械学習ワークロードにおけるデータガバナンスを強化します。全体として、運用効率とシステム信頼性の両面で、エンタープライズ利用を強く意識したアップデートとなっています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)