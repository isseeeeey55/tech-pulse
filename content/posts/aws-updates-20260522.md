---
title: "【AWS】2026/05/22 のアップデートまとめ"
date: 2026-05-22T08:02:13+09:00
draft: true
tags: ["aws", "ec2", "rds", "aurora", "mysql", "sagemaker", "bedrock", "glue", "cloudwatch"]
categories: ["AWS Updates"]
summary: "2026/05/22 のAWSアップデートまとめ"
---

# 2026年5月22日 AWS アップデート情報

## はじめに

2026年5月22日、AWSは**6件**の重要なアップデートをリリースしました。本日のハイライトは、SageMaker AIが**OpenAI互換APIをサポート**したことで、既存の生成AIアプリケーションの移行障壁が大幅に低下した点です。また、Aurora MySQL 8.4の正式リリース、EC2の新世代インスタンス（C7i-flex/M7i-flex/M7i）のハイデラバードリージョン展開、Bedrockのリクエストレベル使用状況追跡機能の拡充など、インフラからデータ、AIまで幅広い領域でのアップデートが並びました。特に注目すべきは、**既存ツールとの互換性を重視した設計**が複数のアップデートで見られる点で、エンタープライズ環境での採用を加速させる意図が読み取れます。

---

## 注目アップデート深掘り

### Amazon SageMaker AI の OpenAI 互換 API サポート

#### なぜこのアップデートが重要なのか

生成AIアプリケーションの多くは、OpenAI APIを前提とした開発が行われています。しかし、セキュリティ要件やコスト最適化、VPC内でのデータ処理といったエンタープライズ要件を満たすために、AWS環境への移行を検討する企業が増えています。従来、この移行には大規模なコード書き換えやSDKラッパーの開発が必要でしたが、今回のアップデートにより**エンドポイントURLの変更のみ**で移行が可能になりました。

#### 具体的な移行手順

まず、従来のOpenAI APIを使用したPythonコードを見てみましょう。

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-..."
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

SageMaker Inferenceへの移行は、以下のように**初期化部分の変更のみ**で実現できます。

```python
from openai import OpenAI
import boto3

# AWS認証情報の取得（自動更新対応）
session = boto3.Session()
credentials = session.get_credentials()

client = OpenAI(
    base_url="https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/my-endpoint/openai",
    api_key=credentials.access_key  # AWS認証情報を使用
)

# 以降のコードは完全に同一
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

ストリーミングレスポンスも既存のロジックがそのまま動作します。

```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

#### LangChainでの活用例

LangChainを使用している場合も、変更は最小限です。

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

chat = ChatOpenAI(
    openai_api_base="https://runtime.sagemaker.ap-northeast-1.amazonaws.com/endpoints/my-llm-endpoint/openai",
    openai_api_key=credentials.access_key,
    model_name="llama-3-70b"  # ファインチューニング済みモデル
)

messages = [HumanMessage(content="Explain quantum computing")]
response = chat(messages)
print(response.content)
```

#### セキュリティとスケーリングのメリット

従来のOpenAI APIと異なり、SageMaker Inferenceでは以下が実現できます。

- **VPC内でのデータ処理**: すべての推論リクエストがVPC内に閉じるため、データがAWS外部に出ることがありません
- **GPU インスタンスの選択**: ワークロードに応じてml.g5.xlarge、ml.p4d.24xlargeなど最適なインスタンスタイプを選択可能
- **オートスケーリング**: トラフィック増加時に自動的にエンドポイントをスケールするポリシーを設定可能

```python
# SageMaker SDK によるオートスケーリング設定例
import boto3

client = boto3.client('application-autoscaling')

client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/my-llm-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=10
)

client.put_scaling_policy(
    PolicyName='GPUUtilizationScaling',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/my-llm-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        }
    }
)
```

#### 認証とトークン管理

AWS認証情報を使用するため、トークンの有効期限切れを意識する必要がありません。SageMaker SDKが自動的にトークンを更新します。

```python
import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

# 自動更新可能な認証情報の取得
session = boto3.Session()
credentials = session.get_credentials()

# OpenAIクライアントに渡す
client = OpenAI(
    base_url=f"https://runtime.sagemaker.{session.region_name}.amazonaws.com/endpoints/my-endpoint/openai",
    api_key=credentials.access_key
)
```

> **Note:** このアップデートは、米国東部、米国西部、アジア太平洋（東京、シンガポール）、ヨーロッパ（フランクフルト、アイルランド）、南米（サンパウロ）を含む複数リージョンで利用可能です。

---

### Amazon Bedrock のリクエストレベル使用状況帰属機能の拡張

#### なぜこのアップデートが重要なのか

マルチテナント環境やチーム横断でBedrockを利用する組織では、**誰が・どのプロジェクトで・どれだけのコストを使用したか**を正確に把握することが運用上の課題でした。従来はIAMプリンシパル単位やアプリケーション推論プロファイル単位での追跡が可能でしたが、今回のアップデートにより**個別リクエストレベル**でのメタデータ付与と追跡が可能になりました。

#### 実装方法：メタデータの付与

InvokeModel APIにメタデータを付与する実装例です。

```python
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock_runtime.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Explain SRE principles"}
        ]
    }),
    # リクエストレベルのメタデータを付与
    requestMetadata={
        'team': 'platform-engineering',
        'project': 'chatbot-v2',
        'environment': 'production',
        'experiment_id': 'exp-2026-05-22-001'
    }
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

InvokeModelWithResponseStream（ストリーミング）でも同様に対応可能です。

```python
response = bedrock_runtime.invoke_model_with_response_stream(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Write a technical blog post"}
        ]
    }),
    requestMetadata={
        'team': 'content-generation',
        'content_type': 'blog',
        'author': 'ai-assistant'
    }
)

for event in response['body']:
    chunk = json.loads(event['chunk']['bytes'])
    if chunk['type'] == 'content_block_delta':
        print(chunk['delta']['text'], end='')
```

#### ログの有効化とフィルタリング

モデル呼び出しログを有効化し、CloudWatch Logsでメタデータベースの分析を実行します。

```bash
# モデル呼び出しログの有効化（AWS CLI）
$ aws bedrock put-model-invocation-logging-configuration \
    --logging-config '{
        "cloudWatchConfig": {
            "logGroupName": "/aws/bedrock/modelinvocations",
            "roleArn": "arn:aws:iam::123456789012:role/BedrockLoggingRole",
            "largeDataDeliveryS3Config": {
                "bucketName": "my-bedrock-logs",
                "keyPrefix": "invocations/"
            }
        },
        "textDataDeliveryEnabled": true,
        "imageDataDeliveryEnabled": false,
        "embeddingDataDeliveryEnabled": true
    }'
```

CloudWatch Logs Insightsでチーム別のトークン使用量を分析するクエリ例：

```
fields @timestamp, requestMetadata.team, inputTokens, outputTokens
| filter requestMetadata.team = "platform-engineering"
| stats sum(inputTokens) as totalInput, sum(outputTokens) as totalOutput by requestMetadata.project
| sort totalInput desc
```

#### チャージバックとコスト配分

メタデータを利用して、Cost and Usage Report（CUR）と連携させることで、チーム別のコスト配分を自動化できます。

```python
import boto3
from datetime import datetime, timedelta

logs_client = boto3.client('logs')

# 過去24時間のログを取得してチーム別集計
query = """
fields requestMetadata.team, inputTokens, outputTokens
| stats sum(inputTokens) as totalInput, sum(outputTokens) as totalOutput by requestMetadata.team
"""

response = logs_client.start_query(
    logGroupName='/aws/bedrock/modelinvocations',
    startTime=int((datetime.now() - timedelta(days=1)).timestamp()),
    endTime=int(datetime.now().timestamp()),
    queryString=query
)

query_id = response['queryId']

# 結果の取得（ポーリング）
import time
while True:
    result = logs_client.get_query_results(queryId=query_id)
    if result['status'] == 'Complete':
        break
    time.sleep(1)

# チーム別コスト計算（例：Claude 3 Sonnetの料金）
INPUT_TOKEN_PRICE = 0.003 / 1000  # $per 1K tokens
OUTPUT_TOKEN_PRICE = 0.015 / 1000

for row in result['results']:
    team = next(f['value'] for f in row if f['field'] == 'requestMetadata.team')
    total_input = float(next(f['value'] for f in row if f['field'] == 'totalInput'))
    total_output = float(next(f['value'] for f in row if f['field'] == 'totalOutput'))
    
    cost = (total_input * INPUT_TOKEN_PRICE) + (total_output * OUTPUT_TOKEN_PRICE)
    print(f"Team: {team}, Cost: ${cost:.2f}")
```

#### 既存の帰属機能との使い分け

| 機能 | 粒度 | ユースケース |
|------|------|------------|
| IAMプリンシパルベース | IAMユーザー/ロール単位 | ユーザー別のアクセス制御と利用追跡 |
| アプリケーション推論プロファイル | アプリケーション単位 | アプリケーション全体のコスト追跡 |
| プロジェクトレベル追跡 | SageMaker Unified Studioプロジェクト単位 | データサイエンスプロジェクトの実験管理 |
| **リクエストレベルメタデータ（新機能）** | **個別リクエスト単位** | **A/Bテスト、実験管理、細かいコスト配分** |

> **Note:** この機能はすべてのAWSコマーシャルリージョンで利用可能です。追加のリソースやサービスは不要で、既存のBedrockエンドポイントにそのまま適用できます。

---

## SRE視点での活用ポイント

### OpenAI互換APIの運用戦略

SageMaker InferenceのOpenAI互換APIは、**既存のAIアプリケーションの段階的な移行**に最適です。まず開発環境で動作検証を行い、その後Blue/Greenデプロイメントパターンでトラフィックを徐々に切り替えることで、リスクを最小化できます。特に、CloudWatch メトリクスと組み合わせることで、レイテンシやエラー率を監視しながら、オートスケーリングポリシーを調整していく運用が考えられます。

VPC内でのデータ処理が実現できるため、金融や医療など規制の厳しい業界での生成AI導入のハードルが下がります。ただし、エンドポイントのコールドスタート時間や、オートスケーリングのトリガー設定には注意が必要です。トラフィックが急増するタイミングが予測できる場合は、CloudWatch Eventsでスケジュールベースのプリウォーミングを検討すると良いでしょう。

認証については、IAMロールベースの権限管理が利用できるため、従来のAPIキー管理よりもセキュアです。AWS Secrets Managerと組み合わせる必要がなく、インスタンスプロファイルやEKS Service Accountを活用した自動認証が可能です。

### Bedrockリクエストレベルメタデータの運用設計

リクエストレベルメタデータは、**チャージバックとコスト最適化の両面**で活用価値があります。A/Bテストでプロンプトのバリエーションを比較する際、各リクエストに`experiment_id`を付与しておけば、後からCloudWatch Logs Insightsでトークン消費量やレスポンス時間を比較分析できます。

本番環境では、`environment`タグを必ず付与し、開発環境と本番環境のコストを明確に分離することを推奨します。また、定期的にログデータをS3にエクスポートし、Amazon AthenaやQuickSightで長期的なトレンド分析を行うパイプラインを構築すると、コスト異常の早期検知に繋がります。

導入時の注意点として、メタデータの付与ルールをチーム間で統一しておかないと、後から集計が困難になります。Terraformやサービスカタログで標準テンプレートを用意し、共通のタグキー（`team`, `project`, `environment`, `cost_center`など）を事前に定義しておくと良いでしょう。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon EC2 C7i-flex, M7i-flex & M7i instances now available in Asia Pacific (Hyderabad) region](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-c7i-flex-m7i-flex-m7i-instances-HYD-region/) | Intel第4世代Xeon Scalable（Sapphire Rapids）搭載のC7i-flex、M7i-flex、M7iインスタンスがハイデラバードリージョンで利用可能に。前世代比で最大19%のコスト・パフォーマンス改善を実現。 |
| 2 | [Amazon RDS Custom now supports the latest GDR updates for Microsoft SQL Server](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-custom-sql-server-latest-gdr-updates-microsoft-sql-server/) | RDS Custom for SQL ServerがSQL Server 2019 CU32+GDRおよび2022 CU24+GDRに対応。CVE-2026-32167、CVE-2026-32176の脆弱性を修正。 |
| 3 | [Amazon Aurora MySQL 8.4 is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-aurora-mysql/8-4/) | Aurora MySQLがLTSバージョンのMySQL 8.4（8.4.7互換）に正式対応。コミュニティ版と統一されたバージョニング、TLS 1.2/1.3強制、Blue/Greenデプロイメント対応など。 |
| 4 | [Amazon SageMaker AI now supports OpenAI-compatible APIs for inference endpoints](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-ai-openai-apis/) | SageMaker InferenceがOpenAI互換APIをサポート。エンドポイントURL変更のみで、OpenAI SDK、LangChain、Strands Agentsなどが利用可能に。 |
| 5 | [Amazon Bedrock expands support for request-level usage attribution](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-bedrock-request-level-usage-attribution/) | BedrockのInvokeModelおよびInvokeModelWithResponseStream APIでリクエストレベルのメタデータ付与が可能に。チーム、プロジェクト、環境ごとの詳細なコスト追跡を実現。 |
| 6 | [Amazon SageMaker Unified Studio now supports data quality rule authoring and evaluation](https://aws.amazon.com/about-aws/whats-new/2026/05/smus-data-quality/) | SageMaker Unified StudioにAWS Glue Data Qualityが統合され、DQDLによるルール作成、静止データ・転送中データの評価、スケジュール実行が可能に。 |

---

## まとめ

本日のアップデートは、**既存ツールとの互換性**と**細かい運用制御**に焦点を当てたものが目立ちました。特にSageMaker AIのOpenAI互換API対応は、生成AIアプリケーションのAWS移行を大幅に加速させる可能性があります。コードの書き換えなしで、セキュリティ、コスト、スケーラビリティの面でエンタープライズ要件を満たせる点は、多くの組織にとって魅力的でしょう。

Bedrockのリクエストレベル帰属機能も、マルチテナント環境やチーム横断利用のガバナンスを強化する重要な機能です。Aurora MySQL 8.4のLTS対応、EC2新世代インスタンスの地理的拡大、RDS CustomのGDRアップデート対応など、安定性と選択肢の拡充も着実に進んでいます。

今後の運用では、これらの新機能を段階的に検証し、既存ワークロードへの適用可否を判断していくことが重要です。特にOpenAI互換APIとBedrockのメタデータ機能は、早期に社内標準を策定しておくことで、長期的な運用コスト削減に繋がるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)