---
title: "【AWS】2026/05/15 のアップデートまとめ"
date: 2026-05-15T08:02:28+09:00
draft: false
tags: ["aws", "cloudfront", "bedrock", "sagemaker", "aurora", "lambda", "cloudformation", "cdk", "kinesis", "redshift", "s3", "opensearch", "application-recovery-controller", "iam", "glue", "athena"]
categories: ["AWS Updates"]
summary: "2026/05/15 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260515/header.png)

# 2026年5月15日 AWS アップデート情報

## はじめに

2026年5月15日、AWSから10件のアップデートが発表されました。本日の注目ポイントは、**生成AIとマルチリージョン運用の強化**です。Amazon Bedrockに新たに導入された「Advanced Prompt Optimization」は、プロンプト最適化と評価を自動化し、従来数週間かかっていた作業を大幅に効率化します。また、CloudFormationの新関数`Fn::GetStackOutput`により、マルチアカウント・マルチリージョン環境でのインフラ管理がシンプルになるなど、エンタープライズ運用の課題に対応するアップデートが目立ちます。さらに、SageMaker AI、Aurora DSQL、Application Recovery Controllerなど、データベースから災害復旧まで幅広い領域でのアップデートが含まれており、AWS基盤全体の成熟度向上が感じられる一日となりました。

## 注目アップデート深掘り

### Amazon Bedrock Advanced Prompt Optimization - プロンプト最適化の自動化がもたらす変革

Amazon Bedrockに導入された**Advanced Prompt Optimization**は、生成AIアプリケーションの開発・運用における重要な課題を解決します。従来、プロンプトの最適化と評価には数日から数週間の手作業が必要でしたが、この新機能により自動化が実現されました。

#### なぜこのアップデートが重要なのか

生成AIの性能はプロンプトの品質に大きく依存します。しかし、新しいモデルへの移行時や、既存モデルの精度向上を図る際、最適なプロンプトを見つけるプロセスは試行錯誤の連続でした。特にマルチモーダル入力（画像＋テキスト）を扱う場合や、複数の候補モデル間での比較検証は、専門知識と時間を要する作業です。Advanced Prompt Optimizationは、この課題に対して体系的なアプローチを提供します。

#### 主要機能と仕組み

この機能の核心は、**フィードバックループを通じた自動最適化**にあります。ユーザーが入力するのは以下の3要素です：

- プロンプトテンプレート
- ユーザー入力例（変数値のサンプル）
- 正解データ（任意）
- 評価指標、または自然言語による短い評価基準

システムはこれらを元に、最大5つのモデルを同時に比較しながら、最適化されたプロンプトを自動生成します。最終的には以下の情報が出力されます：

- 最適化されたプロンプト
- 評価スコア
- コスト見積もり
- レイテンシ測定値

#### マルチモーダル対応の意義

JPG、PNG、PDFといったマルチモーダル入力への対応は、実用上極めて重要です。例えば、ドキュメント分析や商品画像からの情報抽出など、画像とテキストを組み合わせたAIアプリケーションにおいて、プロンプトの最適化は複雑さを増します。Advanced Prompt Optimizationは、こうした複雑なユースケースでも一貫した手法で最適化を実行できます。

#### モデル移行シナリオでの活用

新しい大規模言語モデルへの移行を検討する際、現在のモデルとの性能差を定量的に把握することが不可欠です。この機能を使えば、以下のようなワークフローが実現できます：

```python
# Bedrock APIを使用したプロンプト最適化の概念例
# （実際のAPIは公式ドキュメントを参照してください）

import boto3

bedrock = boto3.client('bedrock')

# 最適化リクエストの構成
optimization_request = {
    'promptTemplate': 'あなたは優秀なカスタマーサポート担当です。{customer_inquiry}に丁寧に回答してください。',
    'userInputExamples': [
        {'customer_inquiry': '返品手続きについて教えてください'},
        {'customer_inquiry': '配送状況を確認したい'}
    ],
    'evaluationCriteria': [
        '回答の正確性',
        '顧客満足度',
        '応答速度'
    ],
    'targetModels': [
        'anthropic.claude-v3',
        'meta.llama3',
        'mistral.mixtral'
    ]
}
```

#### A/Bテストと本番展開への道筋

最適化されたプロンプトは、本番環境へ展開する前にA/Bテストで検証できます。評価スコアとコスト見積もりが明示されるため、ROI（投資対効果）を事前に分析し、経営判断の材料とすることも可能です。

### CloudFormation Fn::GetStackOutput - マルチアカウント環境の複雑性を解消

AWS CloudFormationに追加された新しい組み込み関数`Fn::GetStackOutput`は、マルチアカウント・マルチリージョン環境でのインフラ管理を根本的にシンプル化します。

#### 従来の課題とその影響

エンタープライズ環境では、本番・開発・ステージングなど複数のAWSアカウントが運用されるのが一般的です。例えば、ネットワーキングチームが管理するVPCの情報を、アプリケーションチームが管理するEC2やRDS環境で参照する必要がある場合、従来は以下のような手法を取らざるを得ませんでした：

- テンプレート間で値を手作業でコピー
- SSM Parameter Storeに値を保存して参照
- カスタムリソースを作成してスタック出力を取得

これらの方法は、手動調整のオーバーヘッドや設定ドリフトのリスクを伴い、大規模環境では運用負荷が増大していました。

#### Fn::GetStackOutputの仕組み

新しい関数は、以下の情報を指定するだけで、別アカウント・別リージョンのスタック出力を自動的に取得します：

- 対象スタック名
- 出力キー
- クロスアカウントアクセス用のIAMロールARN
- リージョン（オプション）

CloudFormationは指定されたIAMロールを引き受け、出力値を取得し、テンプレート処理中に解決します。

#### CloudFormationテンプレートでの使用例

```yaml
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      SubnetId: 
        Fn::GetStackOutput:
          StackName: networking-stack
          OutputKey: PublicSubnetId
          RoleArn: arn:aws:iam::123456789012:role/CrossAccountStackReader
          Region: us-west-2
      InstanceType: t3.micro
      ImageId: ami-0c55b159cbfafe1f0
```

この例では、別アカウント（123456789012）の`us-west-2`リージョンにある`networking-stack`から、`PublicSubnetId`という出力値を取得しています。

#### CDKでの自動統合

AWS CDKを使用している場合、さらに便利です。CDKではクロスアカウント・クロスリージョン参照が自動的に`Fn::GetStackOutput`を使用するため、従来必要だったカスタムリソースやSSMパラメータが不要になります。

```typescript
// CDKでのクロスアカウント参照の例
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

// 別アカウントのVPCを参照
const vpc = ec2.Vpc.fromLookup(this, 'SharedVPC', {
  vpcId: cdk.Fn.getStackOutput({
    stackName: 'networking-stack',
    outputKey: 'VpcId',
    roleArn: 'arn:aws:iam::123456789012:role/CrossAccountStackReader'
  })
});
```

#### 弱い参照によるスタック再構成の簡素化

`Fn.getStackOutput`を直接呼び出すことで、スタック間の**弱い参照**を作成できます。これは、スタックの削除や再作成時にデプロイメントデッドロックを回避する上で重要です。従来の強い依存関係では、参照先スタックを削除する前に参照元スタックを削除する必要がありましたが、弱い参照を使えばこの制約が緩和されます。

#### IAMロールの設定例

クロスアカウントアクセスには、適切なIAMロールの設定が必要です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:DescribeStacks"
      ],
      "Resource": "arn:aws:cloudformation:us-west-2:123456789012:stack/networking-stack/*"
    }
  ]
}
```

このロールの信頼ポリシーでは、参照元アカウントからのAssumeRoleを許可します。

### Aurora DSQL Change Data Capture - リアルタイムデータパイプラインの新時代

Amazon Aurora DSQLに追加されたChange Data Capture（CDC）機能（プレビュー）は、リアルタイムデータパイプラインの構築を大幅に簡素化します。

#### 従来のCDC実装の課題

データベースの変更をリアルタイムでキャプチャし、他のシステムに配信する仕組みは、イベント駆動型アーキテクチャやマイクロサービス環境で不可欠です。しかし従来、CDCの実装には以下のような課題がありました：

- Debeziumなどのサードパーティツールの導入・運用コスト
- カスタムパイプラインの構築とメンテナンス
- データベースへのパフォーマンス影響

#### Aurora DSQL CDCの特徴

新しいCDC機能は、これらの課題を解決するために以下の特性を持っています：

- **インフラ管理不要**：カスタムパイプラインの構築が不要
- **パフォーマンス影響ゼロ**：データベースのスループットやレイテンシに影響しない設計
- **ネイティブ統合**：Amazon Kinesis Data Streamsへの直接ストリーミング
- **完全な変更追跡**：INSERT、UPDATE、DELETEの全操作をキャプチャ

#### 基本的なセットアップ手順

Aurora DSQL CDCの有効化は、コンソールまたはCLIから実行できます：

```bash
$ aws dsql create-cdc-stream \
  --cluster-identifier my-aurora-dsql-cluster \
  --database-name production \
  --stream-name order-changes \
  --kinesis-stream-arn arn:aws:kinesis:us-east-1:123456789012:stream/order-events
```

このコマンドにより、`production`データベースの変更が`order-events`という名前のKinesis Data Streamsにストリーミングされます。

#### Lambda連携によるイベント駆動処理

キャプチャされた変更イベントは、AWS Lambdaで処理できます：

```python
import json
import boto3

def lambda_handler(event, context):
    """
    Aurora DSQL CDC イベントを処理する Lambda 関数
    """
    for record in event['Records']:
        # Kinesis レコードのデコード
        payload = json.loads(record['kinesis']['data'])
        
        operation = payload['operation']  # INSERT, UPDATE, DELETE
        table_name = payload['tableName']
        data = payload['data']
        
        if operation == 'INSERT' and table_name == 'orders':
            # 新規注文の通知処理
            send_order_notification(data)
        elif operation == 'UPDATE' and table_name == 'orders':
            # 注文ステータス更新の処理
            update_order_status(data)
    
    return {'statusCode': 200}

def send_order_notification(order_data):
    # SNSやSQSへの通知ロジック
    pass

def update_order_status(order_data):
    # 外部システムへの同期ロジック
    pass
```

#### Data Firehose経由でのデータレイク構築

Amazon Data Firehoseと組み合わせることで、変更データを自動的にS3、Redshift、OpenSearch Serviceに配信できます：

```bash
$ aws firehose create-delivery-stream \
  --delivery-stream-name dsql-cdc-to-s3 \
  --delivery-stream-type KinesisStreamAsSource \
  --kinesis-stream-source-configuration \
    KinesisStreamARN=arn:aws:kinesis:us-east-1:123456789012:stream/order-events,RoleARN=arn:aws:iam::123456789012:role/FirehoseRole \
  --s3-destination-configuration \
    BucketARN=arn:aws:s3:::data-lake-bucket,Prefix=aurora-cdc/,RoleARN=arn:aws:iam::123456789012:role/FirehoseRole
```

この設定により、Aurora DSQLの変更データがS3バケットに自動的にアーカイブされ、データレイクの構築やコンプライアンス要件への対応が容易になります。

#### DPU課金モデルと運用コスト

Aurora DSQL CDCの課金は、データ量に基づくDPU（Data Processing Unit）単位と、Kinesis Data Streamsの標準料金の組み合わせです。実際の運用コストは、変更データの量とKinesisのスループット設定に依存します。少量の変更であれば、従来のサードパーティCDCツールよりもコスト効率が良い可能性があります。

## SRE視点での活用ポイント

今回のアップデート群は、SREの日常業務における重要な課題に対応しています。

**Bedrock Advanced Prompt Optimization**は、生成AI基盤のSLOを維持・改善する際に有効です。例えば、カスタマーサポートチャットボットの応答品質を定量的に評価し、モデル更新時のリグレッションテストを自動化できます。複数モデル間での比較評価機能により、コスト削減とレイテンシ改善のトレードオフを数値的に検証し、意思決定の根拠とすることが可能です。ただし、プレビュー段階の機能では、本番環境への適用前に十分な検証期間を設けることが推奨されます。

**CloudFormationのFn::GetStackOutput**は、マルチアカウント環境でのインフラ管理を大幅に簡素化します。特にTerraformやCDKでIaCを実践している場合、クロスアカウント参照の実装が標準化され、設定ドリフトのリスクが低減します。障害対応のランブックにおいても、スタック出力を動的に参照することで、環境ごとの差異を吸収しやすくなります。導入時の注意点としては、IAMロールの権限設計が適切に行われているかを確認し、過度な権限付与を避けることが重要です。

**Aurora DSQL CDC**は、マイクロサービスアーキテクチャにおけるデータ同期の運用負荷を削減します。CloudWatchアラームと組み合わせてKinesisストリームの処理遅延を監視することで、データパイプラインの健全性を保つことができます。また、インフラ管理が不要な点は、オンコール対応の負担軽減に寄与します。ただし、現在プレビュー段階であるため、本番適用前にはSLA・サポート体制・機能の成熟度を慎重に評価する必要があります。

**ARC Region SwitchのLambdaイベントソースマッピング実行ブロック**は、災害復旧計画の自動化において重要な役割を果たします。フェイルオーバープランの動作確認テストを定期的に実施し、RTO（目標復旧時間）の達成可能性を検証する際に活用できます。計画外フェイルオーバーに対応する「ungraceful」モードは、障害時の意思決定プロセスを簡素化しますが、イベント重複の可能性とビジネスロジック側での冪等性確保のバランスを検討する必要があります。

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **ネットワーク** | [Amazon CloudFront announces Passthrough Mode for mutual TLS (Viewer)](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-cloudfront-mtls-passthrough/) | CloudFrontでmTLSパススルーモードが利用可能に |
| **生成AI** | [Amazon Bedrock Introduces Advanced Prompt Optimization and Migration Tool](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-bedrock-advanced-prompt-optimization-migration-tool/) | プロンプト最適化と評価を自動化し、最大5つのモデルを同時比較可能に |
| **機械学習** | [New models for image generation and text embeddings are now available in Amazon SageMaker JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/05/image-embeddings-models-on-sagemaker-jumpstart/) | FLUX.2-klein-base-4B（軽量画像生成）とQwen3-Embedding-0.6B（多言語埋め込み）がSageMaker JumpStartに追加 |
| **データベース** | [Amazon Aurora DSQL now supports change data capture (Preview)](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-aurora-dsql-change-data-capture-preview/) | Aurora DSQLがCDC機能をプレビュー提供、Kinesis Data Streamsへのリアルタイムストリーミングが可能に |
| **移行・モダナイゼーション** | [AWS Transform introduces the agent builder toolkit](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-transform-agent-builder-toolkit/) | カスタム変革エージェントを構築できるツールキットが一般公開 |
| **開発者ツール** | [AWS Transform agents now available in Kiro, Claude, Cursor, and Codex](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-transform-developer-tools/) | AWS TransformエージェントがKiro、Claude、Cursor、Codexなどの開発ツールで利用可能に |
| **機械学習** | [SageMaker AI now supports serverless model customization for Qwen3.6](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-ft-qwen3-6/) | Qwen3.6 27Bモデルのサーバーレスファインチューニング（SFT/RFT）がSageMaker AIで利用可能に |
| **IaC** | [Reference stack outputs across accounts and Regions with AWS CloudFormation and CDK](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-cloudformation-cdk-stack/) | CloudFormationに新関数Fn::GetStackOutputが追加され、アカウント間・リージョン間のスタック出力参照が可能に |
| **災害復旧** | [ARC Region switch adds Lambda event source mapping execution block](https://aws.amazon.com/about-aws/whats-new/2026/05/region-switch-lambda-esm-execution-block/) | Application Recovery Controller Region SwitchにLambdaイベントソースマッピング実行ブロックが追加され、フェイルオーバー時のイベント処理を自動化 |
| **機械学習** | [Amazon SageMaker Data Agent now available for IAM Identity Center domains](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-data-agent-idc/) | SageMaker Unified Studio の IAM Identity Center 認証ドメインで SageMaker Data Agent が利用可能に。自然言語から Python/SQL コードを自動生成 |

## まとめ

本日のアップデートは、**生成AIの実用化促進**と**エンタープライズ運用の効率化**という2つの大きなテーマで貫かれています。

Bedrockの高度なプロンプト最適化機能は、生成AIアプリケーションの品質管理とコスト最適化を同時に実現し、企業での本格導入を後押しします。SageMaker関連のアップデートも、JumpStartへの新モデル追加、Qwen3.6のファインチューニング対応、Data AgentのIAM Identity Center対応と、機械学習ワークフローの全工程における開発者体験の向上が図られています。

一方、CloudFormationの`Fn::GetStackOutput`やARC Region Switchの機能拡張は、マルチアカウント・マルチリージョン環境の運用を飛躍的にシンプル化します。特にCloudFormationの新関数は、長年のエンタープライズ課題に対する待望のソリューションであり、大規模環境でのIaC運用に大きなインパクトを与えるでしょう。

Aurora DSQL CDCは、リアルタイムデータパイプラインの構築ハードルを下げ、イベント駆動型アーキテクチャの採用を加速させる可能性があります。プレビュー段階の機能も多く含まれますが、今後の正式リリースに向けて検証を進める価値は十分にあります。

これらのアップデートは、AWSがエンタープライズ顧客の実運用における課題に真摯に向き合い、継続的に改善を重ねている証左と言えるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)