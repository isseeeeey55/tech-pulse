---
title: "【AWS】2026/06/09 のアップデートまとめ"
date: 2026-06-09T08:02:16+09:00
draft: false
tags: ["aws", "documentdb", "msk", "kafka", "compute-optimizer", "dynamodb", "elasticache", "memorydb", "workspaces", "sagemaker", "cost-anomaly-detection", "cloudtrail", "aurora", "dsql", "savings-plans", "redshift", "application-migration-service", "opensearch"]
categories: ["AWS Updates"]
summary: "2026/06/09 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260609/header.png)

# 2026年6月9日 AWS アップデート情報

## はじめに

2026年6月9日、直近に公開されたAWSのアップデートから9件をまとめてお届けします。本日のハイライトは、Amazon MSK Express Brokers が Kafka Streams でのトピック自動作成に対応したこと、AWS Compute Optimizer がアイドルリソース検出機能を6つの新しいリソースタイプに拡張したこと、そして AWS Cost Anomaly Detection に AI を活用したコスト調査機能が追加されたことです。これらのアップデートは、開発者の運用負荷軽減とコスト最適化の自動化という、AWS が注力している領域を反映しています。また、Amazon OpenSearch Serverless の Agentic Search や Amazon Redshift の手動スナップショットコスト削減など、AI 活用と経済性向上に関する機能強化も目立ちます。

## 注目アップデート深掘り

### Amazon MSK Express Brokers が Kafka Streams でのトピック自動作成に対応

Amazon MSK Express Brokers に、Kafka Streams アプリケーションで必要なトピックを自動作成する機能が追加されました。これまで Kafka Streams アプリケーションを Express Brokers にデプロイする際、ステートフル操作（リモートステートストア、ウィンドウ操作、結合処理など）で使用される内部トピックを手動で事前作成・管理する必要があり、デプロイメントの複雑さと運用オーバーヘッドが課題となっていました。

**なぜこのアップデートが重要なのか**

Kafka Streams は状態管理やウィンドウ集計のために複数の内部トピックを利用します。従来はこれらのトピックを手動で作成し、パーティション数やレプリケーション設定を適切に構成する必要がありました。設定ミスやトピック不足はアプリケーションの起動失敗や不安定な動作につながるため、特に複雑なストリーム処理パイプラインでは大きな運用コストとなっていました。今回のアップデートにより、アプリケーション起動時にこれらのトピックが自動的に作成されるため、デプロイメント作業が大幅に簡素化されます。

**MSK Express Brokers の性能特性**

MSK Express Brokers は、従来の MSK Brokers と比較して以下の性能特性を持ちます。

| 項目 | MSK Express Brokers | 従来の MSK Brokers との比較 |
|------|---------------------|---------------------------|
| スループット | ブローカーあたり高スループット | **3倍** |
| スケールアップ速度 | 高速スケーリング | **20倍** |
| 復旧時間 | 障害時の自動復旧 | **90%短縮** |

これらの特性により、リアルタイムストリーム処理アプリケーションやイベント駆動型アーキテクチャにおいて、高いパフォーマンスと可用性が実現されます。

**自動作成されるトピックの種類**

Kafka Streams のステートフル操作では、以下のような内部トピックが自動的に作成されます。

- **Changelog トピック**: ステートストア（ウィンドウ集計の状態を含む）の変更履歴を保持
- **Repartition トピック**: 結合やキー変更に伴うデータの再分散に使用

従来はこれらを個別に管理する必要がありましたが、新機能により自動管理されるため、開発者はビジネスロジックに集中できます。

**利用方法と可用性**

この機能は MSK Express Brokers が利用可能なすべての AWS リージョンで即座に利用可能で、追加設定なしで利用開始できます。既存の Kafka Streams アプリケーションをデプロイする際、必要なトピックが自動的に作成されるため、手動のトピック管理作業が不要になります。

### AWS Cost Anomaly Detection に AI を活用したコスト調査機能が追加

AWS Cost Anomaly Detection に、Amazon Q を使用した AI 駆動のコスト調査機能が実装されました。この機能は、検出されたコスト異常の根本原因を数分で自動分析し、自然言語による説明を提供します。

**従来の課題と新機能による改善**

通常、コスト変動の調査には AWS CloudTrail イベントとリソースアクティビティの相関関係を手動で調べる必要があり、複数のサービスやアカウントにまたがる場合、数時間かかることもありました。FinOps チームやセキュリティチームは、以下のような作業を手動で実施していました。

1. Cost Explorer でコスト異常の発生時刻とサービスを特定
2. CloudTrail でその時間帯の API コールを検索
3. リソースの作成・変更イベントを抽出
4. IAM プリンシパル（ユーザー・ロール）を特定
5. 影響範囲を評価し、対応チームに連絡

新機能では、Amazon Q がこれらのステップを自動化し、以下の情報を自然言語で提供します。

- **コスト変化の分類**: 使用量ベースの変化か、料金ベースの変化か
- **影響範囲の特定**: 影響を受けたサービス、アカウント、リージョン
- **根本原因の特定**: 特定の API コールと IAM プリンシパル
- **後続質問への対応**: パターン分析やリソースの詳細確認

**Organization Trail との連携**

Organization Trail を導入している組織では、全メンバーアカウント全体で自動的に調査が機能します。これにより、マルチアカウント環境でどのメンバーアカウントのどの操作がコスト異常を引き起こしたかを組織全体で追跡できます。

**料金とクロスアカウント調査**

この機能はすべての商用 AWS リージョンで追加料金なしで利用できます。ただし、Organization Trail を使用したクロスアカウント調査では、CloudWatch Logs Insights の標準料金が適用される場合があります。

**実践的な活用シナリオ**

例えば、開発チームが意図しないリソースプロビジョニングを行った場合、従来は以下のような手順で調査していました。

1. Cost Explorer で EC2 の急激なコスト増加を確認
2. CloudTrail で `RunInstances` API コールを検索
3. 大量のインスタンスを起動した IAM ロールを特定
4. そのロールを使用しているアプリケーションを調査

新機能では、Amazon Q に「このコスト異常の原因は何ですか？」と質問するだけで、「開発環境用の IAM ロール `dev-deployment-role` が、2026年6月9日 14:23 UTC に `us-east-1` リージョンで 50 台の `m5.xlarge` インスタンスを起動しました」といった具体的な回答が得られます。

### Amazon OpenSearch Serverless が Agentic Search に対応

Amazon OpenSearch Serverless に *Agentic Search* という新機能が追加されました。これは自然言語を使ってデータを検索できる機能で、ユーザーが「東京への $800 以下の航空券を見つけて」といった自然言語で質問すると、システムが意図を理解し、最適な検索戦略を立案し、DSL（ドメイン固有言語）クエリを自動生成して結果を返します。

**技術的な仕組み**

裏側では LLM（大規模言語モデル）を搭載した QueryPlanningTool が自然言語を DSL クエリに変換し、必要なツールを連携させて結果を取得します。このアーキテクチャにより、複雑な検索条件（範囲検索、集計、複合条件など）を自然言語で表現でき、SQL や DSL の知識がないユーザーでも高度な検索を実行できます。

**カスタマイズと可視性**

ユーザーは API または OpenSearch Dashboards を通じて動作をカスタマイズでき、OpenSearch UI ではエージェント作成と検索実行をガイドされた形で実行できます。AWS コンソールから各コレクションへアクセス可能なアプリケーションが用意されています。

**実践的なユースケース**

- EC サイトやマーケットプレイスで「予算内の商品」や「人気商品」を自然言語で検索
- ログ分析・監視システムで「本日のエラー件数が多いサービス」といった複雑なクエリを簡単に実行
- チャットボット・AI アシスタントのバックエンドとして、複雑な検索要求を処理
- ファイナンス・マーケティング部門が集計データを「昨月対比で売上が増加した商品」のような質問で取得

## SRE視点での活用ポイント

### MSK Express Brokers のトピック自動作成機能

Kafka Streams を使ったリアルタイム監視やメトリクス集計パイプラインを構築する際、従来はステートフルアプリケーションのデプロイ前にインフラチームがトピックを準備する必要がありました。この事前準備作業は、新しいストリーム処理ロジックの追加や変更のたびに発生し、デプロイメントのリードタイムを長期化させる要因となっていました。

自動作成機能により、CI/CD パイプラインに組み込むランブックや手順書からトピック作成ステップを削除でき、デプロイメント自動化の度合いが向上します。特に、マイクロサービスアーキテクチャで複数のストリーム処理アプリケーションを管理している環境では、トピック管理の運用負荷が大幅に軽減されるでしょう。

一方で、自動作成されるトピックのパーティション数やレプリケーション設定が要件を満たしているか、初期デプロイ時に確認する必要があります。本番環境への導入前に、開発環境で自動作成されたトピックの設定値を CloudWatch メトリクスで確認し、必要に応じてトピック設定をオーバーライドする手順を整備しておくことを推奨します。

### AI 駆動のコスト調査機能

コスト異常の調査は、オンコール対応やインシデント対応の一環として発生することがあります。特に夜間や休日に突発的なコスト増加が検出された場合、迅速に根本原因を特定し、必要に応じてリソースをスケールダウンまたは削除する判断が求められます。

従来は CloudTrail ログを手動で検索し、どのチームのどの操作が原因かを特定する作業に時間がかかっていましたが、Amazon Q による自動分析により、オンコールエンジニアが数分で状況を把握し、適切なエスカレーションや対応を実施できます。これは MTTR（Mean Time To Resolve）の短縮に直結します。

また、定期的なコストレビューやポストモーテムの際にも、過去のコスト異常の根本原因を自然言語で取得できるため、再発防止策の立案や予算計画の精度向上に貢献します。Organization Trail と組み合わせることで、複数アカウントにまたがるコスト異常をシングルペインで調査でき、マルチアカウント戦略を採用している組織での運用効率が大幅に向上するでしょう。

導入時の注意点として、CloudWatch Logs Insights の料金が発生する可能性があるため、クロスアカウント調査の頻度とコストのバランスを事前に評価しておくことが推奨されます。

### Agentic Search の運用シナリオ

ログ分析や障害調査において、OpenSearch を活用している環境では、複雑な検索条件を DSL で記述する必要がありました。Agentic Search により、オンコールエンジニアが自然言語で「過去1時間のエラーログで最も頻度の高いエラーメッセージは？」といった質問を投げることで、迅速にインシデントの影響範囲を把握できます。

また、ランブックやプレイブックに「特定のエラーパターンを検索するための DSL クエリ」を記載する代わりに、「こういう質問をすればよい」という自然言語の例を記載することで、ドキュメントの可読性と再利用性が向上します。

ただし、LLM が生成するクエリの精度や意図認識の正確性は、データスキーマやフィールド名に依存するため、事前に代表的な検索パターンをテストし、期待通りの結果が得られるかを確認しておく必要があります。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon DocumentDB now supports engine minor version starting with 5.0.1](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-documentdb-engine-minor-version-5-0-1/) | Amazon DocumentDB がエンジンマイナーバージョン 5.0.1 をサポート |
| 2 | [Amazon MSK Express Brokers now support automatic topic creation with Kafka Streams](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-msk-express-topic-support-kstreams/) | MSK Express Brokers が Kafka Streams のステートフル操作で必要なトピックを自動作成。スループット 3 倍、スケール速度 20 倍、復旧時間 90% 短縮の高性能ブローカーで運用負荷を削減 |
| 3 | [AWS Compute Optimizer now supports idle recommendations for six additional resource types](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-compute-optimizer-six-new-idle) | Compute Optimizer がアイドルリソース検出機能を DynamoDB、ElastiCache、MemoryDB、DocumentDB、WorkSpaces、SageMaker エンドポイントに拡張。利用率メトリクスから未使用リソースを自動検出し、コスト削減機会を提示 |
| 4 | [AWS now provides AI-powered cost investigations for cost anomalies](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-ai-powered-cost-investigations/) | Cost Anomaly Detection に Amazon Q を活用した根本原因分析機能を追加。CloudTrail と連携し、数時間かかっていたコスト調査を数分で完了。Organization Trail 環境ではクロスアカウント調査に対応 |
| 5 | [Amazon Aurora DSQL now supports the JSONB data type with compression](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-aurora-dsql-supports-jsonb/) | Aurora DSQL が PostgreSQL の JSONB データ型をサポート。圧縮機能がデフォルトで有効化され、セミ構造化データを効率的に保存可能。PostgreSQL 互換性が向上 |
| 6 | [AWS Savings Plans Purchase Analyzer now supports target coverage analysis](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-savings-plans-coverage/) | Savings Plans Purchase Analyzer にターゲットカバレッジ分析機能を追加。On-Demand 支出のカバレッジ目標を設定し、過去の利用データから必要な購入額を自動推奨。複数シナリオの比較分析が可能 |
| 7 | [Amazon Redshift reduces manual snapshot cost for Serverless and RG instances](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-redshift-incremental-manual-snapshots/) | Redshift の手動スナップショット課金モデルを刷新。複数スナップショット間の重複データブロックを除外し、ユニークなデータブロックのみを課金対象に。既存スナップショットにも自動適用され、大幅なコスト削減を実現 |
| 8 | [AWS Application Migration Service is now AWS Transform MGN](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-transform-mgn-rebrand/) | AWS Application Migration Service（MGN）が AWS Transform MGN に名称変更。手動制御型と自動化型（エージェントワークフロー）の2つの利用方法を提供。FedRAMP High、HIPAA、PCI DSS などのコンプライアンス認定を保有 |
| 9 | [Amazon OpenSearch Serverless now supports Agentic Search](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-opensearch-serverless-next-generation-generally-available/) | OpenSearch Serverless に Agentic Search 機能を追加。自然言語による検索が可能に。LLM を搭載した QueryPlanningTool が DSL クエリを自動生成し、API と OpenSearch Dashboards でカスタマイズ可能 |

## まとめ

本日のアップデートは、**運用自動化**と**コスト最適化**、そして **AI 活用**という3つの軸で構成されています。MSK Express Brokers のトピック自動作成や Compute Optimizer のアイドルリソース検出拡張は、手動運用作業を削減し、インフラチームの負荷を軽減します。一方、AI を活用したコスト調査や Agentic Search は、従来の手動分析作業を自動化し、迅速な意思決定を支援します。

また、Redshift の手動スナップショットコスト削減や Savings Plans Purchase Analyzer のターゲットカバレッジ分析など、経済性向上に関する機能強化も目立ちます。これらは、AWS が顧客のコスト最適化を支援するための継続的な取り組みの一環と言えるでしょう。

特に注目すべきは、Amazon Q や LLM を活用した機能が複数のサービスに展開されている点です。コスト調査や検索といった従来は専門知識を必要としていた領域が、自然言語インターフェースによってアクセス可能になることで、より多くのエンジニアが高度な分析を実施できるようになります。

今後もこのような AI 活用と自動化の流れは加速していくと予想されます。SRE やインフラエンジニアとしては、これらの新機能を積極的に検証し、運用業務の効率化とコスト最適化に活用していくことが求められるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)