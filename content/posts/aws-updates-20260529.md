---
title: "【AWS】2026/05/29 のアップデートまとめ"
date: 2026-05-29T08:02:35+09:00
draft: false
tags: ["aws", "resilience-hub", "iot-core", "billing-and-cost-management", "opensearch", "partner-central", "connect", "organizations", "cloudtrail", "sagemaker", "bedrock", "elemental", "dynamodb", "glue", "ec2"]
categories: ["AWS Updates"]
summary: "2026/05/29 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260529/header.png)

# 2026年5月29日 AWS アップデート情報

## はじめに

2026年5月29日に公開されたAWSアップデートは全17件で、AIと機械学習基盤の大幅な拡充が目立つ日となりました。特に注目すべきは、次世代AWS Resilience Hubの一般提供開始による組織全体のレジリエンシー管理の高度化と、SageMaker Notebook InstancesへのP5en、P6-B200といった最新GPU搭載インスタンスの展開によるAI開発基盤の強化です。また、AWS IoT CoreへのMQTT接続管理API追加、AWS OrganizationsとCloudTrailの統合強化といった運用管理機能の改善も含まれています。生成AI分野では、Claude Opus 4.8のリリースやAmazon Bedrock、OpenSearch Serverlessの次世代版提供開始など、エンタープライズ向けAI活用を加速する内容が揃いました。

## 注目アップデート深掘り

### AWS Resilience Hub 次世代版による組織レベルのレジリエンシー強化

AWS Resilience Hubの次世代版が全AWSリージョンで一般提供開始されました。このアップデートは、プラットフォームエンジニアリングとSREチームにとって、ワークロードの耐障害性を組織規模で管理する能力を根本的に変える可能性を秘めています。

**3階層アプリケーションモデルの導入**

従来のシンプルなリソース単位の管理から、システム→ユーザージャーニー→サービスという3階層でアプリケーションを構造化できるようになりました。これにより、技術的なコンポーネントとビジネス価値の提供方法を直接結びつけられます。例えば、ECサイトであれば「購入フロー」というユーザージャーニーに対して、商品検索サービス、決済サービス、在庫管理サービスを紐付け、それぞれのレジリエンシーがビジネスに与える影響度を可視化できます。

**依存関係の自動検出機能**

最も実用的な改善点は、AWS内部サービス、内部エンドポイント、サードパーティエンドポイントの依存関係を継続的に自動検出する機能です。マイクロサービスアーキテクチャが複雑化するほど、手動での依存関係管理は困難になります。この機能により、新しいサービスデプロイ時やアーキテクチャ変更時に、影響範囲を自動で把握できるようになります。

**生成AIによる障害モード分析**

AWS Well-ArchitectedフレームワークとAWS Resilience Analysis Frameworkに基づき、生成AIが障害モードを分析し、優先度付きの実行可能な提案を生成します。これにより、膨大なベストプラクティスドキュメントを個別に確認する手間が削減され、現在のシステム構成に即した具体的な改善策を得られます。

**AWS Organizations統合による一元管理**

複数アカウント・リージョンのレジリエンシー状況を単一ダッシュボードで監視できるようになりました。これは、エンタープライズ環境で複数チームが並行して開発・運用している場合に特に有効です。組織レベルのポリシーをモジュール化して定義し、各チームに一貫して適用できるため、全社的なレジリエンシーガバナンスが実現します。

既存ユーザーは現在の環境を継続使用しながら段階的に移行できるため、リスクを最小化して新機能の恩恵を受けられます。

### AWS IoT CoreのMQTT接続管理API追加による運用効率化

AWS IoT CoreにGetConnection APIとListSubscriptions APIが追加され、IoTデバイスフロートの接続管理が大幅に改善されました。

**GetConnection APIによる詳細な接続情報取得**

GetConnection APIは、MQTT接続の詳細情報をプログラマティックに取得できます。接続ステータス、MQTTセッション詳細に加えて、送信元・宛先IPアドレス、ポート番号、クライアントVPCエンドポイントIDといったソケットレベルの情報まで含まれます。

デバイスが突然切断された場合、従来はCloudWatchメトリクスやログを手動で調査する必要がありましたが、このAPIにより接続問題の根本原因を即座に特定できます。例えば、特定のネットワーク経路での問題やファイアウォール設定の不備などを、IPアドレスとポート情報から診断できます。

IAMポリシーによる細粒度アクセス制御が可能なため、セキュリティチームとデバイス管理チームで権限を分離できます。

**ListSubscriptions APIによるサブスクリプション監視**

ListSubscriptions APIは、MQTTセッションのすべてのトピックサブスクリプションとQoSレベルを返します。接続中のデバイスだけでなく、永続セッションを持つオフラインクライアントにも対応しています。

大規模なIoTフロート運用では、デバイスが不要なトピックを購読し続けることでメッセージング料金が増加するケースがあります。このAPIにより、全デバイスのサブスクリプション状態を一覧化し、重複や不要な購読を特定してクリーンアップできます。

**既存のDeleteConnection APIとの組み合わせ**

これらの新APIは既存のDeleteConnection APIと組み合わせることで、包括的なMQTT接続ライフサイクル管理が可能になります。問題のある接続を検出（GetConnection）し、サブスクリプションを確認（ListSubscriptions）した上で、必要に応じて接続を切断（DeleteConnection）するという完全な運用フローを自動化できます。

これらの API は SDK や CLI からプログラマティックに呼び出せます。公式発表時点では具体的なコマンド構文は明示されていないため、実際の呼び出し方法は最新の API リファレンスを参照してください。IAM ポリシーで呼び出し可能なプリンシパルとアクションを制限できるため、自動化基盤には最小権限のみを、運用担当者には調査用途の権限を付与する、といった権限分離が可能です。

### Amazon OpenSearch Serverless 次世代版の性能とコスト革新

次世代Amazon OpenSearch Serverlessは、AIエージェント構築用に最適化された完全マネージド検索・ベクトルエンジンです。前世代比で20倍高速なオートスケーリング、数秒でのリソースプロビジョニング、スケール・ツー・ゼロ対応により、ピーク時の従来型クラスタ運用と比べて最大60%のコスト削減が可能です。

**コンピュートとストレージの完全分離アーキテクチャ**

共有ストレージレイヤーの採用により、コンピュートとストレージが独立してスケールします。これは特にトラフィックパターンが予測不可能なAIアプリケーションで威力を発揮します。検索リクエストが急増した場合、数秒でコンピュートリソースを拡張できる一方、夜間や週末などの低トラフィック時にはスケール・ツー・ゼロでコストを最小化できます。

従来のクラスタ型アーキテクチャでは、ストレージ容量のためにノードを増やすとコンピュート能力も増えてしまい、コスト効率が悪化していました。新アーキテクチャでは、データ量が大きくてもクエリ頻度が低いワークロードでは、ストレージのみを確保しコンピュートを最小限に抑えられます。

**ネットワーク接続の簡素化**

コレクションレベルとリージョンレベルの2種類のリソースベースエンドポイントにより、マルチVPCやオンプレミス環境との接続が標準VPC APIで容易になりました。従来は複雑なネットワーク設定が必要でしたが、これらのエンドポイントを使用することで、VPCピアリングやTransit Gatewayの設定が大幅に簡素化されます。

**開発プラットフォームとのネイティブ統合**

VercelやKiroといったAI開発プラットフォームとのネイティブ統合により、自然言語コマンドで開発環境から直接検索インフラをプロビジョニングできます。また、Claude CodeやCursor、CodexなどのコーディングプラットフォームではOpenSearch Agent Skillsとして利用でき、エージェント機能に検索機能を直接組み込めます。

これにより、AIエージェント開発者はインフラ構築の複雑さから解放され、アプリケーションロジックに集中できます。

## SRE視点での活用ポイント

### Resilience Hubによる障害対策の体系化

次世代Resilience Hubは、SREチームが組織全体のレジリエンシーを体系的に管理する強力なツールです。依存関係の自動検出機能により、新サービスのデプロイ前に影響範囲を把握でき、障害時のブラストラジアス（影響範囲）を事前に制限する設計判断ができます。

生成AIによる優先度付き提案は、限られたリソースで最も効果的な改善から着手する判断材料になります。例えば、複数のシングルポイントオブフェイラー（SPOF）が存在する場合、ビジネスインパクトの大きいものから順に対応できます。

AWS Organizationsとの統合は、複数チームが並行して運用する環境で、組織レベルのレジリエンシーポリシーを一貫して適用する場面で有効です。各チームが個別に判断するのではなく、全社的な基準に基づいた設計を促せます。

導入時は、まず重要度の高い1〜2システムでパイロット運用し、依存関係検出の精度やAI提案の妥当性を検証することをおすすめします。段階的移行が可能なため、既存の運用プロセスを維持しながら新機能を評価できます。

### IoT Core APIによるデバイスフロート運用の自動化

新しいMQTT接続管理APIは、大規模IoTデバイスフロートの運用自動化に直結します。CloudWatch Alarmと組み合わせて、接続断が一定閾値を超えたら自動でGetConnection APIを呼び出し、接続失敗の原因（ネットワーク、認証、設定ミスなど）を分類する自動診断システムを構築できます。

EventBridgeルールでListSubscriptions APIの結果を定期的に集計し、不要なサブスクリプションを検出して自動クリーンアップするワークフローも実現できます。これにより、メッセージング料金の予期しない増加を防げます。

Lambda関数と組み合わせることで、特定パターンの接続異常を検出した際に自動でチケット作成や通知を行う仕組みも構築できます。IAM権限の細粒度制御により、自動化スクリプトには最小権限のみを付与し、人間のオペレーターはより広範な権限で操作する、といった権限分離も可能です。

導入にあたっては、まず既存のトラブルシューティング手順を棚卸しし、手動で行っている調査をAPI呼び出しに置き換えられる部分から自動化することをおすすめします。

### OpenSearch Serverless次世代版によるコスト最適化

スケール・ツー・ゼロ対応は、検索機能を持つが常時利用されないシステムのコスト削減に直結します。例えば、業務時間のみ利用される社内検索システムや、夜間バッチ処理時のみクエリが発生するデータ分析基盤などでは、非稼働時間帯のコストをほぼゼロにできます。

CloudWatch メトリクスでクエリレイテンシとコンピュートリソース使用率を監視し、パフォーマンス要件を満たす最小限のリソース構成を見極めることが重要です。20倍高速なオートスケーリングにより、トラフィック急増時のレイテンシ悪化リスクは大幅に低減されていますが、ビジネスクリティカルなワークロードでは初期段階で十分な負荷テストを実施すべきです。

マルチVPC環境での接続簡素化により、開発・ステージング・本番環境を同一OpenSearch Serverlessクラスタで統合し、環境ごとのコレクション分離と適切なアクセス制御を組み合わせることで、インフラ管理コストを削減できます。

導入時の注意点として、前世代からの移行パスやデータマイグレーション手順を事前に確認し、段階的な移行計画を立てることをおすすめします。

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| レジリエンシー | [AWS Resilience Hub次世代版GA](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-announces-next-gen-aws-resilience-hub/) | 3階層アプリケーションモデル、依存関係自動検出、生成AI障害モード分析、AWS Organizations統合 |
| IoT | [AWS IoT Core MQTT接続管理API](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-iot-core-apis-mqtt/) | GetConnection APIとListSubscriptions APIによる接続詳細とサブスクリプション管理 |
| コスト管理 | [BCMダッシュボードBudgetsウィジェット](https://aws.amazon.com/about-aws/whats-new/2026/05/monitor-aws-budgets-using-dashboards) | 予算監視とコスト分析を単一ダッシュボードで実行、CSV/PDF/メール配信対応 |
| 検索 | [OpenSearch Serverless次世代版GA](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-opensearch-serverless-next-generation-generally-available/) | 20倍高速スケーリング、最大60%コスト削減、コンピュート・ストレージ分離 |
| パートナー | [Partner Central TCV対応](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-partner-central-opportunity-deal-sizing-tcv/) | 総契約価値(TCV)から月次経常収益(MRR)への自動変換 |
| コンタクトセンター | [Amazon Connect多言語サマリー](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-connect-summary-languages/) | ポストコンタクトサマリーが8言語に拡張（日本語、中国語、韓国語など） |
| ガバナンス | [Organizations CloudTrailイベント](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-organizations-cloudtrail/) | AccountJoinedOrganization/AccountDepartedOrganizationイベント自動記録 |
| ML | [SageMaker P4de東京リージョン](https://aws.amazon.com/about-aws/whats-new/2026/04/p4de-region-expansion-sagemaker-notebook-instances/) | 8×NVIDIA A100 GPU (640GB)、最大60%性能向上、20%コスト削減 |
| ML | [SageMaker P5.48xl東京リージョン](https://aws.amazon.com/about-aws/whats-new/2026/05/p5-48xl-region-expansion-sagemaker-notebook-instances/) | NVIDIA H100搭載、最大4倍高速化、40%コスト削減 |
| AI | [Claude Opus 4.8 on AWS](https://aws.amazon.com/about-aws/whats-new/2026/05/claude-opus-4.8-aws/) | Anthropic最新モデル、コーディング・エージェント・知識業務で大幅改善 |
| メディア | [Elemental Inference Smart Subtitles](https://aws.amazon.com/about-aws/whats-new/2026/05/elemental-inference-subtitles) | AI駆動ライブ字幕自動生成、7言語対応、カスタム辞書対応 |
| データベース | [DynamoDB Streams PrivateLink FIPS](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-dynamodb-streams-privatelink-fips-govcloud/) | GovCloudでPrivateLink FIPS対応、VPC内通信でコンプライアンス強化 |
| AI | [Bedrock Service Quotas対応](https://aws.amazon.com/about-aws/whats-new/2026/5/amazon-bedrock-service-quotas/) | bedrock-mantleエンドポイントのトークン/分クォータ一元管理 |
| ML | [SageMaker P6-B200バージニア](https://aws.amazon.com/about-aws/whats-new/2026/06/p6-b200-region-expansion-sagemaker-notebook-instances/) | 8×NVIDIA Blackwell GPU (1440GB)、P5en比2倍性能向上 |
| ETL | [Glue大規模ワーカースペイン](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-glue-larger-memory-intensive-workers-spain) | G.12X/16XとR.1X/2X/4X/8Xワーカータイプ追加 |
| ML | [SageMaker P5en.48xl GA](https://aws.amazon.com/about-aws/whats-new/2026/02/p5en-new-instance-launch-sagemaker-notebook-instances/) | H200 GPU、GPUメモリ1.7倍、帯域幅1.4倍、通信遅延35%削減 |
| ML | [SageMaker P5.4xl GA](https://aws.amazon.com/about-aws/whats-new/2026/03/p5-4xl-new-instance-launch-sagemaker-notebook-instances/) | H100 Tensor Core GPU、最大4倍高速化、40%コスト削減 |

## まとめ

2026年5月29日のアップデートは、組織レベルのレジリエンシー管理、AI/ML開発基盤の強化、運用自動化の3つの軸で大きな進展がありました。

次世代Resilience Hubは、複雑化するクラウドアーキテクチャの耐障害性を組織規模で管理する新しいアプローチを提示しています。依存関係の自動検出と生成AIによる分析により、SREチームはより戦略的な障害対策に時間を割けるようになるでしょう。

SageMaker Notebook Instancesへの最新GPU（P5en、P6-B200、P4de）の展開は、AI開発の民主化を加速します。特にアジア太平洋リージョンでの提供開始により、データ所在地要件を満たしながら最先端のAI開発が可能になります。Claude Opus 4.8やOpenSearch Serverless次世代版といったAIサービスの進化も相まって、エンタープライズでの生成AI活用が本格化する基盤が整いました。

IoT Core MQTT管理APIやOrganizations CloudTrailイベントといった運用管理機能の改善は、地味ながら日々の運用効率に直結します。これらのAPIを活用した自動化により、手動オペレーションを削減し、より高度な運用課題に取り組む時間を確保できます。

全体として、エンタープライズのクラウド活用を「規模」と「自動化」の両面で支援する内容が揃った、充実したアップデート日となりました。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)