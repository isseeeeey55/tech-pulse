---
title: "【AWS】2026/05/08 のアップデートまとめ"
date: 2026-05-08T08:02:17+09:00
draft: true
tags: ["aws", "ec2", "rds", "aurora", "kms", "bedrock", "sagemaker", "opensearch", "mediatailor", "iam"]
categories: ["AWS Updates"]
summary: "2026/05/08 のAWSアップデートまとめ"
---

# 2026/05/08 AWS アップデート情報

## はじめに

2026年5月8日は、11件のAWSアップデートが発表されました。本日の注目トピックは、**Amazon Bedrock AgentCoreへの決済機能の追加**と**AWS Advanced JDBC Wrapperのクライアント側暗号化対応**です。前者はAIエージェントが自律的に課金処理を行える画期的な機能であり、後者はJavaアプリケーションのセキュリティを大幅に強化するものです。また、EC2インスタンスの地域拡大（G7e、X8i、P6-B200）やAmazon OpenSearch ServiceのVPCプライベート接続対応など、インフラストラクチャとネットワークセキュリティの改善も多数含まれています。

---

## 注目アップデート深掘り

### Amazon Bedrock AgentCore に決済機能が追加（プレビュー）

Amazon Bedrock AgentCoreに**Payments機能**が追加され、AIエージェントが自律的に有料APIやリソースにアクセスし、決済を実行できるようになりました。この機能はCoinbaseとStripeとの協業により実現し、HTTP 402レスポンス（Payment Required）を受け取った際に、x402プロトコルを使用して自動的に決済処理を行います。

#### なぜこのアップデートが重要なのか

従来、AIエージェントが外部の有料APIやサービスを利用する際は、開発者が事前に課金契約を結び、APIキーを手動で設定する必要がありました。これでは動的なリソース発見や、エージェント間の自律的な取引が困難です。AgentCore Paymentsは、ウォレット認証から取引実行、予算管理、可視化までを統合的に提供することで、**エージェントの自律性を飛躍的に高める**インフラストラクチャとなります。

#### 技術的な仕組みと実装

AgentCore Paymentsは、以下のような決済ライフサイクルを自動化します：

1. エージェントがAPIにアクセスし、HTTP 402レスポンスを受信
2. x402プロトコルに従い、ウォレット（Coinbase CDP / Stripe Privy）から自動決済
3. ステーブルコインでの支払いと証明書の返送
4. セッションレベルの支出制限チェック（インフラ層で強制）
5. すべてのトランザクションをCloudWatch経由でログ・監査

開発者は以下のように、セッションレベルで支出上限を設定できます：

```python
import boto3

bedrock = boto3.client('bedrock-agent-runtime')

response = bedrock.invoke_agent(
    agentId='your-agent-id',
    agentAliasId='your-alias-id',
    sessionId='session-123',
    inputText='Find and purchase the latest market data from premium APIs',
    sessionConfiguration={
        'paymentConfiguration': {
            'walletType': 'COINBASE_CDP',  # または 'STRIPE_PRIVY'
            'spendingLimitPerSession': 10.00,  # USD相当
            'currency': 'USDC'
        }
    }
)
```

Coinbase x402 Bazaar MCP サーバーを通じて、10,000以上のx402対応エンドポイントに即座にアクセス可能です。エージェントは自律的にこれらのサービスを発見し、必要に応じて決済を実行します。

#### 従来の方法との比較

| 項目 | 従来の方法 | AgentCore Payments |
|------|-----------|-------------------|
| API利用の事前準備 | 手動契約・APIキー管理 | 自動発見・自動決済 |
| 課金統合の開発 | 個別に実装が必要 | プロトコルレベルで統合済み |
| 支出管理 | アプリケーション層で実装 | インフラ層で強制 |
| 監査・可視化 | 独自ログ実装 | CloudWatch標準統合 |

#### 動作確認のステップ

1. **ウォレット接続**: Coinbase CDP Walletを設定
2. **エージェント設定**: セッションレベルの支出上限を設定
3. **MCP サーバー接続**: Coinbase x402 Bazaar経由で有料エンドポイントにアクセス
4. **決済フロー検証**: HTTP 402レスポンス受信時の自動決済を確認
5. **監査ログ確認**: CloudWatchでトランザクション履歴を可視化

対応リージョンは US East (N. Virginia)、US West (Oregon)、Europe (Frankfurt)、Asia Pacific (Sydney) です。

---

### AWS Advanced JDBC Wrapper にクライアント側暗号化機能が追加

AWS Advanced JDBC Wrapperに**KMS暗号化プラグイン**が追加され、カラムレベルのクライアント側暗号化が可能になりました。この機能により、Javaアプリケーションから機密データをデータベースに送信する前に暗号化し、**アプリケーションコードの変更なし**でエンドツーエンドの暗号化を実現します。

#### なぜこのアップデートが重要なのか

データベースの転送中暗号化（TLS）と保存時暗号化は基本的なセキュリティ対策ですが、これらではデータがデータベースエンジン内で復号化されます。認証情報の漏洩、管理者権限の悪用、SQLインジェクション攻撃により、プレーンテキストのデータが露出する可能性があり、**PCI DSS、HIPAA、GDPR**などのコンプライアンス要件に抵触します。

KMS暗号化プラグインは、JDBCドライバレベルで動作することで、この課題を解決します。プレーンテキストはアプリケーションにのみ見え、データベースは暗号化された値のみを保持します。データベース管理者やSQLインジェクション攻撃者も、暗号化キーにアクセスできなければデータを読み取れません。

#### 技術的な仕組みと実装

KMS暗号化プラグインは、以下のような動作を行います：

1. **書き込み時**: アプリケーションが暗号化対象カラムに値を書き込む際、JDBCドライバがデータベース到達前にKMSで暗号化
2. **読み込み時**: 暗号化されたデータを取得し、アプリケーション側で復号化
3. **データ整合性**: HMAC検証でデータ改ざんを検知（データベース側で暗号化キーなしに検証可能）

以下は、JDBC接続文字列での設定例です：

```java
String jdbcUrl = "jdbc:aws-wrapper:postgresql://mydb.region.rds.amazonaws.com:5432/mydb"
    + "?wrapperPlugins=kms_encryption"
    + "&kmsKeyId=arn:aws:kms:us-east-1:123456789012:key/abc-def-ghi"
    + "&encryptedColumns=users.credit_card,users.ssn";

Connection conn = DriverManager.getConnection(
    jdbcUrl, 
    "username", 
    "password"
);

// 既存のSQLコードはそのまま使用可能
PreparedStatement stmt = conn.prepareStatement(
    "INSERT INTO users (name, credit_card) VALUES (?, ?)"
);
stmt.setString(1, "John Doe");
stmt.setString(2, "4111-1111-1111-1111");  // 自動的に暗号化される
stmt.executeUpdate();
```

Spring BootやHibernateとの統合も、DataSource設定を変更するだけで完了します：

```yaml
spring:
  datasource:
    url: jdbc:aws-wrapper:postgresql://mydb.region.rds.amazonaws.com:5432/mydb?wrapperPlugins=kms_encryption&kmsKeyId=arn:aws:kms:us-east-1:123456789012:key/abc-def-ghi&encryptedColumns=users.credit_card,users.ssn
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    driver-class-name: software.amazon.jdbc.Driver
```

#### 既存の暗号化手法との比較

| 項目 | TLS/保存時暗号化 | アプリ層暗号化 | KMS暗号化プラグイン |
|------|----------------|--------------|-------------------|
| DB管理者からの保護 | ✗ | ✓ | ✓ |
| コード変更の必要性 | なし | 大規模 | なし |
| SQLクエリ互換性 | 完全 | 制限あり | 完全 |
| キー管理 | AWS管理 | 独自実装 | AWS KMS統合 |
| データ整合性検証 | なし | 独自実装 | HMAC自動検証 |

#### 実装時の注意点

- 暗号化対象カラムは、インデックスを使った検索ができなくなる（暗号化された値での比較になるため）
- HMAC検証により、データ改ざんは検知できるが、データベース側でのソートや範囲検索は不可
- Amazon RDS/Aurora（PostgreSQL、MySQL互換）でのみ動作確認済み

Apache 2.0ライセンスのオープンソースプロジェクトとして提供されるため、企業内での検証や拡張も可能です。

---

## SRE視点での活用ポイント

### AgentCore Paymentsの運用シナリオ

AgentCore Paymentsは、**マイクロサービス間の自律的な課金処理**や**動的なサードパーティAPI利用**において、運用の柔軟性を大幅に向上させます。例えば、障害発生時にエージェントが自動的に有料の診断APIを呼び出し、根本原因を特定するといったシナリオが考えられます。

ただし、セッションレベルの支出上限設定は必須です。予期しないループや攻撃による予算超過を防ぐため、CloudWatch Alarmsと連携して支出異常を検知する仕組みを整えることが推奨されます。また、すべてのトランザクションがCloudWatchに記録されるため、監査要件を満たしやすい一方、ログ保管コストの見積もりも必要です。

### KMS暗号化プラグインの導入判断

KMS暗号化プラグインは、**レガシーJavaアプリケーションのセキュリティ強化**において非常に有効です。Hibernateや既存のコネクションプール（HikariCP、C3P0）との互換性が高いため、コード変更を最小限に抑えつつ、PCI DSSやHIPAA準拠を達成できます。

導入時の判断基準として、以下を検討すると良いでしょう：

- **暗号化対象カラムの検索頻度**: 頻繁に検索・ソートするカラムは暗号化に不向き（パフォーマンス影響大）
- **キー管理の要件**: KMS利用によるAPI呼び出しコストとレイテンシの許容範囲
- **データベース管理者の権限範囲**: 管理者からもデータを保護する必要があるか

Terraformでインフラをコード化している環境では、KMSキーの作成と権限設定を自動化し、環境ごとに異なるキーを使用することで、セキュリティレベルをさらに高めることができます。既存のRDS/Auroraインスタンスに対しても、接続文字列の変更だけで適用できるため、段階的なロールアウトが可能です。

### OpenSearch Service VPC Egressの活用

OpenSearch ServiceのVPC egress対応により、**Lambda関数やSageMakerモデルとのプライベート接続**が容易になります。これまではNATゲートウェイやインターネット経由での通信が必要でしたが、VPC内で完結することで、レイテンシの削減とセキュリティの向上が同時に実現します。

導入時は、セキュリティグループとNACLの設定を慎重に行う必要があります。特に、OpenSearchドメインからのアウトバウンドトラフィックを適切に制限し、意図しないリソースへのアクセスを防ぐことが重要です。また、VPC egress有効化により追加されるENI（Elastic Network Interface）には、追加料金が発生する場合があるため、コスト見積もりも忘れずに実施しましょう。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon EC2 G7e instances now available in Europe (London) region](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-g7e-london-region/) | G7eインスタンス（GPU最適化型）がロンドンリージョンで利用可能に |
| 2 | [Amazon EC2 X8i instances are now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-ec2-x8i-instances-BOM-DUB-region/) | X8iインスタンス（メモリ最適化型、Intel Xeon 6搭載）がアイルランドとムンバイで利用可能。X2i比でパフォーマンス43%向上、メモリ容量1.5倍、メモリ帯域幅3.3倍。SAP HANA等のメモリ集約ワークロードに最適 |
| 3 | [AWS Advanced JDBC Wrapper now provides client-side encryption](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-advanced-jdbc-wrapper-encryption/) | KMS暗号化プラグインによるカラムレベルのクライアント側暗号化に対応。アプリケーションコード変更なしでエンドツーエンド暗号化を実現 |
| 4 | [AWS Elemental MediaTailor launches Monetization Functions](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-elemental-mediatailor-monetization-functions) | MediaTailorに広告決定サーバー（ADS）リクエストのカスタマイズ機能が追加。外部API呼び出しやデータ変換をインライン実行可能に |
| 5 | [Amazon SageMaker HyperPod now supports AMI-based node lifecycle configuration for Slurm clusters](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-hyperpod-ami-based-node/) | HyperPodがAMIベースのノードライフサイクル設定に対応。Docker、Enroot、Pyxis等が事前設定され、クラスター作成時間を大幅短縮 |
| 6 | [Amazon SageMaker Unified Studio adds identity and user management features](https://aws.amazon.com/about-aws/whats-new/2026/05/smus-identity-user-management/) | IAMドメインでIAM Identity Center SSO対応、Identity CenterドメインでフェデレーションIAMロール経由アクセスに対応。複数ユーザーの同一ロール共有時もセッション分離と個別監査が可能に |
| 7 | [AWS Capabilities by Region now supports availability notifications](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-regional-planning-tool-notification) | AWS Builder Center内の「AWS Capabilities by Region」で、サービス・機能の利用可能性通知に対応。1,500以上のサービス・機能を37リージョンで追跡し、アプリ内アラートと週次メールで通知 |
| 8 | [Amazon EC2 P6-B200 instances are now available in the AWS GovCloud (US-West) Region](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-p6-b200-aws-govcloud) | P6-B200インスタンス（NVIDIA Blackwell GPU搭載）がGovCloud US-Westで利用可能。P5en比で最大2倍のAI学習・推論性能、GPU メモリ帯域幅60%向上 |
| 9 | [AWS India customers can now use UPI Scan and Pay for sign-up and payments](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-india-upi-scanandpay/) | インド顧客がUPI Scan and PayでAWS登録・支払いが可能に。QRコード読み取りで支払い完結、UPI AutoPayで月次請求自動化にも対応 |
| 10 | [Amazon OpenSearch Service now supports VPC egress for private connectivity to resources in your VPC](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-opensearch-service-vpc) | OpenSearch ServiceがVPC egress対応。VPC内リソース（ML モデル、Lambda、カスタムアプリ等）へのプライベート接続が可能に。インターネット経由のトラフィック露出を排除 |
| 11 | [Agents that transact: Amazon Bedrock AgentCore now includes Payments (preview)](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-agentcore-payments-preview) | Bedrock AgentCoreに決済機能が追加（プレビュー）。CoinbaseとStripeと協業し、AIエージェントが自律的に有料API・リソースにアクセスして決済を実行可能に。x402プロトコル対応、セッションレベル支出制限、CloudWatch統合 |

---

## まとめ

本日のアップデートは、**AIエージェントの自律性向上**（Bedrock AgentCore Payments）と**セキュリティ強化**（JDBC Wrapper暗号化、OpenSearch VPC egress）が大きなテーマとなっています。特にAgentCore Paymentsは、エージェントが自律的に経済活動を行える基盤を提供する画期的な機能であり、今後のAIエコシステムの進化を加速させるでしょう。

また、EC2インスタンスの地域拡大（X8i、P6-B200、G7e）により、グローバルな高性能コンピューティング環境の選択肢が広がっています。特にX8iはSAP HANA認定を受け、メモリ集約ワークロードにおいて前世代比43%の性能向上を実現しており、大規模データベースやAI推論パイプラインの運用において有力な選択肢となります。

SageMaker関連では、HyperPodのAMIベース設定とUnified Studioのユーザー管理強化により、AI/ML環境の構築・運用効率が向上しています。インドのUPI Scan and Pay対応は、地域特化型の決済手段をクラウドサービスに統合する好例であり、今後他地域でも同様の展開が期待されます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)