---
title: "【AWS】2026/05/21 のアップデートまとめ"
date: 2026-05-21T08:02:01+09:00
draft: false
tags: ["aws", "security-hub", "iam", "access-analyzer", "ecs", "ebs", "fargate", "dynamodb", "postgresql", "ec2", "s3", "eks", "vpc", "direct-connect", "sagemaker", "billing-conductor", "eventbridge"]
categories: ["AWS Updates"]
summary: "2026/05/21 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260521/header.png)

# AWS 2026年5月21日のアップデート情報

## はじめに

2026年5月21日、AWSから7件のアップデートが発表されました。本日の注目ポイントは、**セキュリティとガバナンスの強化**、そして**開発体験の向上**です。特に AWS Security Hub が未使用アクセス権の検出機能を追加し、IAMのセキュリティポスチャー管理が大きく前進しました。また、DynamoDB互換のオープンソースアダプタ「ExtendDB」の発表により、ローカル開発環境での体験が大幅に改善されます。その他、ECSのGovCloudリージョンでのEBS統合対応、SageMaker HyperPodの推論データキャプチャ機能など、運用効率とコンプライアンス対応を強化するアップデートが揃っています。

## 注目アップデート深掘り

### AWS Security Hub が未使用アクセス権の検出に対応

AWS Security Hub に新たに追加された未使用アクセス権の検出機能は、組織全体のセキュリティポスチャー管理を大きく前進させるものです。従来、IAM権限の棚卸しや最小権限の原則の実装には、IAM Access Analyzer、AWS Config、各種サードパーティツールを個別に運用する必要がありましたが、この機能により**Security Hubという統一されたコンソール**で脅威検出、脆弱性管理、そしてID管理を一元的に扱えるようになります。

#### なぜこのアップデートが重要なのか

クラウド環境における権限の過剰付与は、攻撃者にとって格好の標的となります。特に複数のAWSアカウントを運用する組織では、各アカウントで使われていないIAMロールや認証情報が放置されがちです。これらは「休眠資産」として攻撃面を広げ、いざ侵害された際の被害範囲を拡大させます。本機能は**過去90日間の実際のアクセスアクティビティを分析**し、使用されていない権限を自動的に検出するため、セキュリティチームは具体的な根拠に基づいた権限削減を実施できます。

#### 実装の仕組み

この機能の背後では、IAM Access Analyzerが**サービスリンクロール**として各メンバーアカウントに自動的にデプロイされます。サービスリンクロールとは、AWSサービスが代理でアクションを実行するために使用する特殊なIAMロールで、ユーザーが手動で作成・管理する必要がありません。Security Hub Essentialsを有効化すると、このロールが自動的に作成され、IAM Access Analyzerが継続的に権限使用状況を監視します。

検出された未使用アクセスの情報は、OCSFスキーマに準拠した形式でSecurity Hubに集約され、他のセキュリティ検出結果（GuardDutyの脅威検出、AWS Configのコンプライアンス違反など）と統合表示されます。これにより、例えば「未使用のAdmin権限を持つIAMロールがアタッチされたEC2インスタンスで、同時にセキュリティグループが広く開放されている」といった複合的なリスクを一目で把握できます。

#### 最小権限ポリシーの自動生成

最も強力な機能の一つが、**実際の使用パターンに基づいた最小権限ポリシーの自動生成**です。90日間のアクセスログを解析し、実際に呼び出されたAPIアクションのみを含むポリシーを生成します。これにより、「念のため」で付与されていた過剰な権限を削ぎ落とし、攻撃面を大幅に縮小できます。

生成されたポリシーは、Security Hubのダッシュボード上で確認でき、適用前にレビューすることが可能です。段階的な展開も推奨されており、まず開発環境で検証してから本番環境に適用するといった運用が想定されています。

### ExtendDB: DynamoDB互換のオープンソースアダプタ

AWSが発表した「ExtendDB」は、DynamoDB APIを実装したオープンソースのアダプタレイヤーで、**プラグイン可能なストレージバックエンド**を持つ点が最大の特徴です。バージョン0.1のリファレンス実装ではPostgreSQLがバックエンドとして採用されており、DynamoDBのプログラミングモデルを保ちながら、ローカル開発やオンプレミス環境で動作させることができます。

#### 開発体験の大幅な改善

従来、DynamoDBを使用するアプリケーションのローカル開発では、DynamoDB LocalやLocalStackといったツールが使われてきました。しかし、これらは完全な互換性を保証するものではなく、特にストリーム機能やトランザクション処理、グローバルセカンダリインデックスの挙動などで本番環境と差異が生じることがありました。

ExtendDBは**DynamoDBのコントロールプレーンとデータプレーンのAPI**を実装しており、テーブル操作（CreateTable、UpdateTable、DeleteTableなど）、アイテム操作（PutItem、GetItem、Query、Scanなど）、そしてストリーム機能まで対応しています。これにより、本番環境との互換性が大きく向上し、ローカルでの統合テストの信頼性が高まります。

#### プラグイン設計の可能性

初期リリースではPostgreSQLがバックエンドですが、プラグイン設計により、コミュニティは新しいストレージバックエンドを追加できます。例えば、MySQLやMariaDB、あるいはSQLiteをバックエンドとして使用する実装が今後登場する可能性があります。これにより、既存のデータベースインフラストラクチャを活用しながら、DynamoDBのプログラミングモデルのメリット（シンプルなAPI、自動スケーリング思想など）を享受できます。

#### CI/CDパイプラインへの統合

ExtendDBは、CI/CDパイプラインにおける統合テストの精度を大きく向上させます。以下は、GitHub Actionsでの使用例です：

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      extenddb:
        image: aws/extenddb:0.1
        env:
          STORAGE_BACKEND: postgresql
          POSTGRES_HOST: postgres
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 8000:8000
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run integration tests
        env:
          AWS_ENDPOINT_URL: http://localhost:8000
          AWS_ACCESS_KEY_ID: dummy
          AWS_SECRET_ACCESS_KEY: dummy
          AWS_REGION: us-east-1
        run: |
          npm install
          npm test
```

この設定により、AWS環境に接続することなく、DynamoDBを使用するアプリケーションの統合テストを完全にローカルで実行できます。テストの実行速度も向上し、外部依存を排除することでCI/CDパイプラインの信頼性が高まります。

## SRE視点での活用ポイント

### Security Hubの未使用アクセス検出機能

SRE業務における権限管理は、セキュリティと運用効率のバランスを取る難しい課題です。インシデント対応やデバッグのために一時的に付与した権限が放置されたり、サービスの廃止に伴って不要になったIAMロールが残り続けたりすることは珍しくありません。

この機能を活用することで、**定期的な権限棚卸しのプロセスを自動化**できます。例えば、四半期ごとのセキュリティレビューの際に、Security Hubのダッシュボードで未使用権限を確認し、優先度の高いものから順に削除していくといった運用が可能です。CloudWatch Alarmsと組み合わせることで、新たに検出された未使用権限の数が閾値を超えた場合にアラートを発信し、Slackやメールで通知することもできます。

導入時の注意点としては、90日間の分析期間があるため、季節性のあるワークロード（年次バッチ処理など）の権限が誤って「未使用」と判定される可能性があることです。自動生成されたポリシーを適用する前に、アプリケーションの使用パターンを十分に理解し、必要に応じて例外を設定することが重要です。また、既存のTerraformやCloudFormationでIAMポリシーを管理している場合、Infrastructure as Code（IaC）との整合性を保つための運用フローを事前に設計しておくべきでしょう。

### ExtendDBの運用シナリオ

ExtendDBは、特に開発環境とCI/CD環境での活用価値が高いツールです。DynamoDBを使用するマイクロサービスのテストを、AWS環境に接続せずに完全にローカルで実行できるため、開発者の体験が大きく改善されます。インターネット接続が不安定な環境や、AWSアカウントへのアクセスが制限されている開発チームでも、フル機能のDynamoDBアプリケーションを開発できます。

障害対応のランブックに組み込む場合、例えば「本番環境で発生した問題を再現するために、特定の時点のEBSスナップショットからデータを復元し、ExtendDB上で調査する」といったシナリオが考えられます。これにより、本番データベースに影響を与えることなく、安全に問題の原因を特定できます。

リスクとしては、まだバージョン0.1の初期リリースであるため、本番環境での使用は推奨されません。あくまで開発・テスト環境での利用に留め、本番環境ではマネージドサービスのAWS DynamoDBを使用することが推奨されます。また、PostgreSQLのパフォーマンスチューニングがDynamoDBの性能特性に影響するため、適切なインデックス設計やクエリ最適化が必要になる場合があります。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Security Hub now uncovers identity risks from unused access](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-security-hub-unused-access/) | Security Hubが未使用のIAM権限、ロール、認証情報を検出し、IAM Access Analyzerを使用して過去90日間のアクセスアクティビティを分析。最小権限ポリシーの自動生成機能により攻撃面を縮小。 |
| [ECS supports native integration with Amazon EBS volumes in GovCloud Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/ecs-amazon-ebs-govcloud/) | GovCloudリージョンのECSがEBSボリュームのネイティブ統合に対応。タスク起動時にEBSボリュームを自動的にプロビジョニング・管理し、ETL、メディアトランスコーディング、ML推論などのワークロードに最適化。 |
| [Security Hub Extended expands to 21 curated partner solutions across 9 categories](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-security-hub-extended/) | Security Hub Extendedが拡張され、SentinelOne、CyberArk、Sublime、Varonis、LayerX、Native Security、Zenityなど7つの新パートナーソリューションを追加。全21ソリューションがOCSFスキーマで統一され、自動集約。 |
| [AWS Billing Conductor Improves Account Visibility with Billing Transfer Inventory](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-billing-conductor-billing-transfer/) | Billing Conductorコンソールが改善され、請求転送の招待を承認したがプロフォーマ請求データへのアクセスがないアカウントを可視化。EventBridgeとUser Notificationsによる日次通知設定に対応。 |
| [AWS announces ExtendDB, an open source DynamoDB-compatible adapter](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-extenddb-dynamodb/) | DynamoDB互換のオープンソースアダプタ「ExtendDB」v0.1を発表。プラグイン可能なストレージバックエンド設計で、初期リリースではPostgreSQLをサポート。ローカル開発、CI/テスト、オンプレミス環境でDynamoDBアプリケーションを実行可能。Apache 2.0ライセンス。 |
| [Announcing the general availability of a new AWS Local Zone in Istanbul, Türkiye](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-local-zones-istanbul-turkiye/) | トルコのイスタンブールに新しいローカルゾーンを開設。EC2（C7i、M7i、R7i）、S3、EBS、ECS、EKS、VPC、Direct Connect、ALBなどが利用可能。低遅延アクセスとデータレジデンシー要件に対応。 |
| [Amazon SageMaker HyperPod now supports data capture for inference workloads](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-hyperpod-data-capture) | SageMaker HyperPodで推論ワークロード向けのデータキャプチャ機能が利用可能に。エンドポイント、ロードバランサー、ポッドレベルでリクエスト/レスポンスを記録し、S3に非同期配信。サンプリングとKMS暗号化に対応。 |

## まとめ

本日のアップデートは、**セキュリティガバナンスの強化**と**開発者体験の向上**という2つの軸で構成されています。Security Hubの未使用アクセス検出機能は、複数アカウント運用における権限管理の課題に対する実用的な解決策を提供し、最小権限の原則の実装を大きく前進させるものです。

一方、ExtendDBのようなオープンソースツールの提供は、AWSがクラウドネイティブな開発体験の改善に積極的に取り組んでいることを示しています。ローカル開発環境での高い互換性とCI/CDパイプラインへの統合しやすさは、開発サイクルの短縮とコスト削減に直結します。

また、GovCloudリージョンでのECS-EBS統合や、イスタンブールローカルゾーンの開設は、規制要件やデータレジデンシーへの対応が引き続き重要なテーマであることを再確認させます。SageMaker HyperPodのデータキャプチャ機能は、生成AIの本番運用におけるガバナンスとコンプライアンスの重要性を反映したものといえるでしょう。

これらのアップデートを活用することで、セキュリティ、コンプライアンス、運用効率、開発体験のすべてにおいて、より成熟したクラウド環境を構築できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)