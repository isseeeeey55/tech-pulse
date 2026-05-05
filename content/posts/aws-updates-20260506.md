---
title: "【AWS】2026/05/06 のアップデートまとめ"
date: 2026-05-06T08:02:32+09:00
draft: true
tags: ["aws", "sam", "api-gateway", "lambda", "cloudwatch", "logs", "elasticache", "iam", "opensearch", "connect", "workspaces", "fsx", "iot-core", "mediatailor"]
categories: ["AWS Updates"]
summary: "2026/05/06 のAWSアップデートまとめ"
---

# 2026/05/06 AWS アップデート情報

## はじめに

2026年5月6日、AWSは13件のアップデートを発表しました。本日の注目ポイントは、**開発者体験の大幅な向上**と**運用効率化**です。特にAWS SAMがWebSocket APIとBuildKitに対応したことで、サーバーレスアプリケーションの開発生産性が飛躍的に向上しました。また、CloudWatch Logs Insightsのタグベースクエリ対応やElastiCacheの新メトリクス追加など、SREにとって日常的な運用を改善する実用的な機能強化が目立ちます。AI/ML分野では、Amazon QuickとNew Relicの統合により、インシデント対応が大きく効率化されます。本記事では、特に影響が大きい2件のアップデートを深掘りし、SRE視点での活用ポイントを解説します。

## 注目アップデート深掘り

### AWS SAMがWebSocket APIに対応 - リアルタイム通信の開発が劇的に簡単に

AWS SAM（サーバーレスアプリケーションモデル）がAmazon API GatewayのWebSocket APIに対応しました。これは、チャットアプリケーション、ライブダッシュボード、AI/LLMのストリーミング応答、IoTデバイス監視など、リアルタイム双方向通信を必要とするアプリケーション開発に大きなインパクトをもたらします。

#### なぜこのアップデートが重要なのか

従来、WebSocket APIをデプロイするには、CloudFormationで`AWS::ApiGatewayV2::Api`、`AWS::ApiGatewayV2::Integration`、`AWS::ApiGatewayV2::Route`、Lambda実行権限、ログ設定など、複数のリソースを手動で定義する必要がありました。特に厄介だったのが、Lambda関数のIAM権限設定ミスや、統合設定の不備によるエラーで、デバッグに多くの時間を費やすケースが少なくありませんでした。

今回のアップデートにより、新しいリソースタイプ`AWS::Serverless::WebSocketApi`が追加され、**最小限の設定でWebSocket APIが構築できる**ようになりました。SAMが統合設定とIAM権限を自動生成するため、開発者は本質的なビジネスロジックに集中できます。

#### 実装方法と具体例

SAMテンプレートでWebSocket APIを定義する基本的な例は以下の通りです：

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ChatWebSocketApi:
    Type: AWS::Serverless::WebSocketApi
    Properties:
      $connect:
        RouteResponseSelectionExpression: $default
      $disconnect:
        RouteResponseSelectionExpression: $default
      $default:
        RouteResponseSelectionExpression: $default
      Auth:
        Authorizers:
          LambdaAuthorizer:
            AuthorizerUri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AuthFunction.Arn}/invocations
            IdentitySource:
              - route.request.header.Auth
      RouteSettings:
        $default:
          ThrottlingBurstLimit: 500
          ThrottlingRateLimit: 1000

  ConnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.connect_handler
      Runtime: python3.11
      Events:
        ConnectRoute:
          Type: WebSocketApi
          Properties:
            ApiId: !Ref ChatWebSocketApi
            Route: $connect

  DisconnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.disconnect_handler
      Runtime: python3.11
      Events:
        DisconnectRoute:
          Type: WebSocketApi
          Properties:
            ApiId: !Ref ChatWebSocketApi
            Route: $disconnect

  DefaultFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.default_handler
      Runtime: python3.11
      Events:
        DefaultRoute:
          Type: WebSocketApi
          Properties:
            ApiId: !Ref ChatWebSocketApi
            Route: $default
```

#### 従来のCloudFormationとの比較

従来のCloudFormationでは、上記と同等の機能を実現するために以下のような冗長な定義が必要でした：

- API Gatewayリソース（1個）
- 統合リソース（3個：connect, disconnect, default）
- ルートリソース（3個）
- Lambda実行権限リソース（3個）
- デプロイメントリソース（1個）
- ステージリソース（1個）

合計で**11個以上のリソース定義**が必要でしたが、SAMでは上記のようにシンプルに記述できます。IAM権限は自動生成され、統合設定も最適化されます。

#### Globalsでの共通設定共有

複数のWebSocket APIを管理する場合、`Globals`セクションで共通設定を定義できます：

```yaml
Globals:
  WebSocketApi:
    Auth:
      Authorizers:
        LambdaAuthorizer:
          AuthorizerUri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${AuthFunction.Arn}/invocations
    RouteSettings:
      $default:
        ThrottlingBurstLimit: 500
        ThrottlingRateLimit: 1000
```

これにより、複数のマイクロサービスで一貫したセキュリティとスロットリング設定を維持できます。

### CloudWatch Logs Insightsがタグベースクエリに対応 - 動的環境での運用負荷を大幅削減

Amazon CloudWatch Logs Insightsが、ロググループのタグを使ったクエリに対応しました。この機能により、マイクロサービスやマルチテナント環境でのログ分析が劇的に効率化されます。

#### 背景：なぜタグベースクエリが必要なのか

従来のCloudWatch Logs Insightsでは、クエリ対象のロググループを名前で明示的に指定する必要がありました。しかし、マイクロサービスアーキテクチャやCI/CDパイプラインで動的にロググループが作成される環境では、以下のような課題がありました：

- 新しいロググループが追加されるたびにクエリを更新する必要がある
- 環境（本番、ステージング、開発）ごとにロググループ名の命名規則を厳密に管理しなければならない
- 複数チームが独自のロググループを持つ場合、横断的な分析が困難

タグベースクエリにより、`Environment: Production`や`Application: PaymentService`といったタグで検索できるため、**ロググループが動的に増減しても自動的にクエリ対象が更新**されます。

#### 実装例とクエリ構文

AWS CLIでロググループにタグを付与する例：

```bash
$ aws logs tag-log-group \
  --log-group-name /aws/lambda/payment-service \
  --tags Environment=Production,Application=PaymentService,Owner=TeamA

$ aws logs tag-log-group \
  --log-group-name /aws/lambda/order-service \
  --tags Environment=Production,Application=OrderService,Owner=TeamB
```

タグベースのクエリ例：

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

このクエリを実行する際、CloudWatch Logs Insightsのコンソールで「タグでフィルター」機能を使い、`Environment: Production`を選択すると、該当するすべてのロググループが自動的にクエリ対象になります。

#### Terraformでのタグ管理

Terraformで体系的にタグを管理する例：

```hcl
locals {
  common_tags = {
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_log_group" "payment_service" {
  name              = "/aws/lambda/payment-service"
  retention_in_days = 30

  tags = merge(local.common_tags, {
    Application = "PaymentService"
    Owner       = "TeamA"
  })
}

resource "aws_cloudwatch_log_group" "order_service" {
  name              = "/aws/lambda/order-service"
  retention_in_days = 30

  tags = merge(local.common_tags, {
    Application = "OrderService"
    Owner       = "TeamB"
  })
}
```

#### 動的環境での自動反映の仕組み

重要なポイントは、**タグの追加・削除が自動的にクエリ結果に反映される**ことです。例えば、新しいマイクロサービスがデプロイされ、`Environment: Production`タグが付与されたロググループが作成されると、既存のクエリに何も変更を加えることなく、自動的に新しいロググループがクエリ対象に含まれます。

逆に、サービスが廃止されてロググループが削除されたり、タグが変更されたりした場合も、自動的にクエリ対象から除外されます。これにより、**運用チームがクエリ定義をメンテナンスする負担が大幅に軽減**されます。

#### IAMポリシーとの組み合わせ

タグベースのアクセス制御と組み合わせることで、セキュリティも向上します：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:DescribeLogGroups",
        "logs:StartQuery",
        "logs:GetQueryResults"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "logs:ResourceTag/Owner": "TeamA"
        }
      }
    }
  ]
}
```

このポリシーにより、TeamAのメンバーは自分たちが所有するロググループのみクエリできます。

## SRE視点での活用ポイント

### WebSocket APIのSAM対応がもたらす運用改善

リアルタイム通信を必要とするシステムは、SREにとって運用上の挑戦が多い領域です。WebSocket接続は長時間維持されるため、接続管理、エラーハンドリング、スケーリング戦略が複雑になりがちです。SAMのWebSocket API対応により、以下のようなSRE業務が改善されます。

**インフラコードの保守性向上**：Terraformでインフラを管理している場合でも、アプリケーションレイヤーはSAMで管理する「ハイブリッド構成」を検討できます。TerraformでVPC、データベース、キャッシュなどの共有リソースを管理し、SAMで個別のマイクロサービスとそのWebSocket APIを管理することで、チーム間の責任範囲が明確になります。SAMが権限設定を自動化するため、デプロイ時の権限エラーが減り、ロールバックの信頼性が向上します。

**障害対応の迅速化**：CloudWatch Logsとの統合がSAMテンプレートで自動設定されるため、WebSocket接続のライフサイクル（connect、disconnect、メッセージ送信）ごとのログが標準化されます。これにより、障害発生時のログ分析が容易になり、「どの段階で接続が切れたのか」を迅速に特定できます。また、CloudWatch アラームと組み合わせて、`$connect`の失敗率が閾値を超えた場合に自動通知する仕組みも、SAMテンプレート内で一元管理できます。

**負荷試験とキャパシティプランニング**：SAMのRouteSettingsで`ThrottlingBurstLimit`と`ThrottlingRateLimit`を設定できるため、負荷試験の結果をもとに適切なスロットリング値を調整し、本番環境に反映する流れがコード化されます。また、Lambda関数の同時実行数制限と組み合わせることで、WebSocket接続数の急増による過負荷を防ぐ多層防御が実現します。

**注意点**：WebSocket APIは接続維持型のため、API Gatewayの接続時間制限（最大2時間）を理解した上で、クライアント側の再接続ロジックを実装する必要があります。また、既存のREST APIとWebSocket APIでは認証フローが異なるため、Lambda Authorizerの実装を慎重に設計しましょう。

### タグベースクエリがSREワークフローにもたらす効率化

CloudWatch Logs Insightsのタグベースクエリは、SREの日常業務を大きく改善します。特に、以下のシナリオで効果を発揮します。

**インシデント対応時の横断分析**：本番環境で障害が発生した際、`Environment: Production`タグでフィルターすることで、関連するすべてのマイクロサービスのログを一括検索できます。従来は各サービスのロググループ名をリストアップしてクエリに含める必要がありましたが、タグベースクエリでは「本番環境の全サービス」という概念レベルでクエリを実行できます。これにより、障害の影響範囲を迅速に把握し、根本原因の特定が早まります。

**ポストモーテムと傾向分析**：インシデント後のレビューで、過去30日間の`Application: PaymentService`のエラーログを分析する場合、タグベースクエリにより、デプロイやスケールアウトでロググループが追加・削除されていても、常に最新の構成を反映した分析が可能です。これにより、「新しいインスタンスのログが分析から漏れていた」といった見落としが防げます。

**コンプライアンスとセキュリティ監査**：金融機関やヘルスケア業界では、特定の分類（例：PCI DSS対象システム）のすべてのログを監査する必要があります。`Compliance: PCI-DSS`といったタグを付与しておけば、監査時に該当するすべてのロググループを自動的に抽出でき、手動でのリスト管理が不要になります。

**チーム間の自律性向上**：各チームが自分たちのロググループに`Owner: TeamName`タグを付与し、IAMポリシーで自チームのタグがついたログのみアクセス可能にすることで、マルチテナント環境でのログ分離が実現します。SREチームは、インシデント発生時に全体を俯瞰する権限を持ちつつ、通常時は各チームが自律的にログ分析できる体制を構築できます。

**導入時の判断基準**：タグ体系の設計には、組織全体での合意が必要です。環境（Environment）、アプリケーション（Application）、オーナー（Owner）、コスト配分（CostCenter）など、どのタグを必須とするかを事前に決めておくと、後々の運用がスムーズになります。また、タグの追加・変更はログ保持期間に影響しないため、既存環境にも安全に適用できます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS Elemental MediaTailor now provides automatic secure server-to-server integration with Google's ad platforms](https://aws.amazon.com/about-aws/whats-new/2026/05/mediatailor-automatic-google-ad-platform-integration) | MediaTailorがGoogle Ad Manager、Google Campaign Manager、Google Display & Video 360との自動サーバー間認証機能を提供開始。従来必要だった手動のホワイトリスト登録が不要になり、セットアップ時間を大幅短縮 |
| 2 | [AWS IoT Core for Device Location adds Confidence Level Configuration and Measurement Type support](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-iot-core-device-location/) | IoT Coreのデバイスロケーション解決に信頼度レベル（50%〜99%）設定機能と測定タイプメタデータ（GNSS、Wi-Fi、BLE）を追加。ユースケースに応じた精度と確実性のバランス調整が可能に |
| 3 | [AWS SAM now supports WebSocket APIs for Amazon API Gateway](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-sam-websocket-apis-api-gateway/) | SAMがWebSocket APIに対応し、最小限の設定でリアルタイム通信アプリケーションを構築可能に。統合とIAM権限が自動生成され、開発効率が飛躍的に向上 |
| 4 | [AWS SAM CLI adds BuildKit support for AWS Lambda functions packaged as container images](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-sam-cli-buildkit-aws-lambda/) | SAM CLIがBuildKitに対応し、Lambdaコンテナイメージのビルドが高速化。マルチステージビルド、並列処理、クロスアーキテクチャビルド（x86_64とarm64）をサポート |
| 5 | [Amazon Quick now integrates with New Relic for observability-driven AI agents](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-quick-new-relic/) | Amazon QuickがNew Relicと統合され、AIアシスタント内でインシデント調査、RCA生成、タスク作成が可能に。オンコールエンジニアの生産性向上と対応時間短縮を実現 |
| 6 | [Amazon ElastiCache adds thirteen new Amazon CloudWatch metrics for network capacity planning and engine diagnostics](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-elasticache-cloudwatch-metrics-network-engine-diagnostics/) | ElastiCacheが13個の新しいCloudWatchメトリクスを追加。ネットワークスロットリング、メモリフラグメンテーション、接続枯渇を検出し、キャパシティプランニングと診断を効率化 |
| 7 | [Amazon WorkSpaces now lets AI agents operate desktop applications (Preview)](https://aws.amazon.com/about-aws/whats-new/2026/05/workspaces-ai-agents/) | WorkSpacesがAIエージェントに対応し、レガシーアプリケーション（メインフレーム、ERP）の自動操作が可能に（プレビュー）。API非対応システムの業務自動化を実現 |
| 8 | [AWS IAM now provides higher maximum quotas for roles, role trust policies, instance profiles, managed policies, and identity providers](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-iam-increased-quotas/) | IAMの6つのリソースでクォータを大幅引き上げ。ロールとポリシーが5,000→10,000に、OpenID Connectプロバイダーが100→700に増加し、大規模環境のスケーリング課題を解決 |
| 9 | [Amazon OpenSearch Service expands Cluster Insights with a new insight](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-opensearch-cluster-insights/) | OpenSearch ServiceのCluster Insightsが全バージョン対応（OpenSearch 1.0以降、Elasticsearch 6.8以降）。新たに遊休インデックス検出機能を追加し、ストレージコスト削減を支援 |
| 10 | [Amazon Connect Cases now supports customer profile identity resolution](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-connect-cases-customer-profiles-id-res/) | Connect Casesが顧客プロフィールID解決機能に対応。重複プロフィールのマージ時にケースが自動再関連付けされ、エージェントが統一された履歴を参照可能に |
| 11 | [Amazon WorkSpaces Applications now supports host-to-client URL redirection](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-workspaces-applications-url/) | WorkSpaces Applicationsにホスト・ツー・クライアントURLリダイレクション機能を追加。ストリーミングセッション内のURLをローカルブラウザで開き、インフラコストを削減 |
| 12 | [Amazon FSx is now available in the AWS Asia Pacific (New Zealand) Region](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-fsx-aws-asia-pacific/) | Amazon FSxがニュージーランドリージョンで利用可能に。NetApp ONTAP、Windows File Server、Lustre、OpenZFSの4種類のファイルシステムを提供 |
| 13 | [Amazon CloudWatch Logs Insights supports querying by log group tags](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-cloudwatch-logs-query-by-tags/) | CloudWatch Logs Insightsがタグベースクエリに対応。ロググループのタグで検索でき、動的環境でのクエリメンテナンス負荷を大幅削減 |

## まとめ

本日のアップデートは、**開発者とSREの両方にとって実用的な改善**が中心でした。特にSAMのWebSocket API対応とBuildKitサポートは、サーバーレスアプリケーションの開発体験を大きく向上させます。CloudWatch Logs Insightsのタグベースクエリは、マイクロサービス環境での運用効率を劇的に改善する地味ながら強力な機能です。

また、ElastiCacheの新メトリクス、IAMクォータの引き上げ、OpenSearchのCluster Insights拡張など、**スケーラビリティと可観測性の向上**に焦点を当てたアップデートが目立ちます。これらは、成長中のシステムが直面する典型的な運用課題に対する直接的な解決策となります。

AI/ML分野では、Amazon QuickとNew Relicの統合、WorkSpacesのAIエージェント対応（プレビュー）が発表され、インシデント対応とレガシーシステムの自動化という、SREにとって重要な領域でのAI活用が進んでいることがわかります。

これらのアップデートを積極的に試し、自分たちの運用課題に適用できるか検証してみることをお勧めします。特に、SAMのWebSocket API対応とCloudWatch Logs Insightsのタグベースクエリは、比較的リスクが低く導入しやすい機能です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)