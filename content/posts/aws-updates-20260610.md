---
title: "【AWS】2026/06/10 のアップデートまとめ"
date: 2026-06-10T08:02:15+09:00
draft: false
tags: ["aws", "backup", "eks", "sagemaker", "emr", "s3", "bedrock", "cost-explorer", "cloudwatch", "rds", "postgresql"]
categories: ["AWS Updates"]
summary: "2026/06/10 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260610/header.png)

# 2026年6月10日 AWS アップデート情報

## はじめに

今回は、直近で発表された9件のAWSアップデートを紹介します。今回のアップデートは、**データ主権とコンプライアンス対応の強化**、**AI/MLエージェントの実用化**、そして**開発者体験の向上**という3つの軸で展開されています。

特に注目すべきは、AWS European Sovereign Cloud（ドイツ）リージョンでの機能拡充（AWS Backup for EKS、S3 Access Grants）と、コスト管理を支援する2つの新しいAI機能（AWS FinOps AgentとCost ExplorerのAmazon Q分析）です。また、データエンジニアリング領域では、EMR ServerlessのSpark Connect対応により、インタラクティブな開発体験が大幅に向上しています。PostgreSQL 19 Beta 1のプレビュー提供や、CloudWatch Logs Insightsへの23個の新機能追加など、運用効率化に直結するアップデートも目立ちます。

## 注目アップデート深掘り

### Amazon EMR ServerlessがSpark Connectに対応 - インタラクティブ開発の新時代

Amazon EMR Serverlessが**Spark Connect**をサポートし、データエンジニアとアナリストの開発体験が大きく変わります。このアップデートにより、Amazon SageMaker Unified Studio、Jupyter、Visual Studio Codeなど、任意のノートブック環境からApache Sparkアプリケーションを対話的に開発・実行できるようになりました。

#### Spark Connectが解決する課題

従来のEMRクラスタ方式では、開発者はクラスタに直接接続してジョブを実行する必要があり、開発環境とSpark実行環境が密結合していました。Spark Connectは**クライアント-サーバーアーキテクチャ**を採用することで、この課題を解決します。アプリケーションクライアントとSparkドライバーが分離されることで、開発者は好みのIDE環境を維持しながら、Sparkインフラは独立してEMR Serverless上で動作します。

この分離により、ローカルのPythonコード実行とリモートSpark操作を統一環境で組み合わせることが可能になります。たとえば、ノートブックのあるセルでPandasによるローカル分析を実行し、次のセルでPySparkによる大規模分散処理を実行する、といった柔軟なワークフローが実現します。

#### 運用監視と可視化の強化

EMRコンソール、Spark UI、Spark History Serverからセッションの監視とデバッグが可能で、個別セッション単位での詳細なコスト・使用状況の可視化も実現されています。これにより、部門別やプロジェクト別のチャージバック対応が容易になり、FinOps実践の観点からも有用です。

インタラクティブセッションの利用により、ad hoc分析やプロトタイピングの段階から本番デプロイまでのサイクルが短縮され、データエンジニアリングの生産性向上が期待できます。EMRリリース7.13で利用でき、EMR Serverlessが利用可能なすべてのリージョンで提供されています。

> **Note:** Amazon SageMaker Unified Studioと組み合わせることで、EMR ServerlessとAthena Sparkの両方をランタイムとして選択でき、ワークロードの特性に応じた最適なエンジン選択が可能になります。

### AWS FinOps Agent - AIによるコスト最適化の自動化

AWS FinOps Agentは、FinOps実践者とエンジニアリングチーム向けのAIエージェントで、コスト管理業務を大幅に効率化します。現在プレビュー段階で米国東部（バージニア北部）リージョンで提供されていますが、全リージョンのコスト・使用量データをカバーしています。

#### AIエージェントがもたらす運用改革

FinOps Agentの最大の特徴は、**自然言語によるコスト質問への回答**と**異常検知時の自動調査**です。従来、コスト異常が発生した際には、エンジニアが手動でコストエクスプローラーやCloudWatchログを調査し、原因を特定する必要がありました。FinOps Agentは、コスト異常を検出すると自動的に根本原因を調査し、Slackに通知します。これにより、エンジニアチームは手動トリアージなしに対応できます。

#### 既存AWS最適化サービスとの統合

FinOps Agentは、AWS Cost Optimization HubやAWS Compute Optimizerと統合されており、ライトサイジング、アイドルリソース、Savings Plansの推奨事項を自動的に提示します。さらに、Jiraチケットの自動作成機能により、最適化タスクを運用フローに組み込むことができます。

たとえば、スケジュール実行されるワークフローでアイドルリソースの推奨事項を定期的に確認し、Jiraチケットを自動生成してエンジニアに割り当てる、といった運用が可能になります。プレビュー期間は無料で利用できるため、早期に試用して自社のFinOpsプロセスへの統合可能性を評価することをおすすめします。

### CloudWatch Logs Insightsに23個の新機能 - ログ分析の表現力が大幅拡張

Amazon CloudWatch Logs Insightsのクエリ言語が**23個の新しいコマンドと関数**に対応し、ログ分析の表現力が劇的に向上しました。この拡張により、従来は複雑な回避策や外部ツールが必要だった処理を、Logs Insights内で完結できるようになります。

#### 追加された主要機能カテゴリ

新機能は以下のカテゴリに分類されます：

**セキュリティ関連**：ハッシュ関数（md5、sha256）により、ログの改ざん検証やセキュリティ監査が可能になりました。また、IP処理関数（isPrivateIP、isPublicIP、isReservedIP）により、プライベートIPとパブリックIPを自動判別して不正アクセス検知を実装できます。

**データ処理**：型変換関数（toNumber、toInt、toLong、toDouble）により、ログ内の数値文字列を適切な型に変換して統計処理を実行できます。文字列関数では、strcontainsが大文字小文字を区別しない検索に対応し、より柔軟なログ検索が可能になりました。

**時系列分析**：rate、count_over_time、sum_over_timeなどの分析関数により、APIレスポンスタイムのrate計算やイベント発生頻度の時系列監視が容易になります。histogram関数を使えば、価格帯別の分布やレスポンスタイムの分布を可視化できます。

**データパース**：CSV・XML形式のログファイルを自動パースできるようになり、アプリケーションログやアクセスログの構造化データ抽出が簡単になりました。

**クエリ制御**：「limit any N」で先頭N件を取得でき、最大10個のstatsコマンドが使用可能になったことで、複雑な多段階集計が1つのクエリで実現できます。

これらの新機能は全商用AWSリージョンで利用可能です。

## SRE視点での活用ポイント

今回のアップデートをSREの観点から見ると、**運用自動化**と**オブザーバビリティ強化**という2つの軸で活用できます。

EMR ServerlessのSpark Connect対応により、データエンジニアリングチームとSREの連携が強化されます。たとえば、障害発生時のログ分析パイプラインをノートブック環境で対話的に構築し、検証後にバッチジョブとしてスケジュール実行する、といったワークフローが実現できます。セッション単位のコスト可視化により、分析クエリのコストを追跡し、非効率なクエリを特定して最適化するFinOps活動もやりやすくなります。

AWS FinOps AgentとCost ExplorerのAmazon Q統合は、コスト異常対応のランブックに組み込むことで、インシデント対応の初動を自動化できます。たとえば、Slackに通知されたコスト異常を起点に、Amazon Qに追加質問を投げかけて原因を深掘りし、Jiraチケットを自動生成してエンジニアに割り当てる、といったワークフローが構築できます。プレビュー段階での検証を通じて、既存のコスト監視ツール（CloudWatch Anomaly DetectionやAWS Budgetsなど）との棲み分けを整理しておくことが重要です。

CloudWatch Logs Insightsの機能拡張は、ログベースの監視とアラートを高度化できます。たとえば、IP関連関数を使ってプライベートIPからのアクセスとパブリックIPからのアクセスを分類し、セキュリティインシデントの検知精度を向上させることができます。rate関数やhistogram関数を活用すれば、パフォーマンス劣化の早期検知やSLI（Service Level Indicator）の計測が容易になります。これらの新機能を既存のCloudWatch Alarmと組み合わせることで、より精緻な閾値設定とアラート運用が可能です。

AWS European Sovereign Cloud（ドイツ）での機能拡充（AWS Backup for EKS、S3 Access Grants）は、GDPR等の欧州規制に対応する必要がある組織にとって重要です。特にEKSのバックアップ機能は、コンテナ環境のディザスタリカバリー計画に組み込むことで、RTOとRPOの達成を確実にします。ドイツリージョンで稼働するEKSクラスタがある場合、本番環境への導入前に、バックアップと復旧のテストを実施し、所要時間を測定しておくことをおすすめします。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS Backup support for Amazon EKS (European Sovereign Cloud - Germany)](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-backup-amazon-eks-aws-european-sovereign-cloud/) | AWS Backup が Amazon EKS に対応し、AWS European Sovereign Cloud（ドイツ）リージョンで利用可能に。フル管理型でポリシーベースのデータ保護、クロスリージョン・クロスアカウントコピー、イミュータブルボールト、自動スケジューリング、保持管理などの機能を提供 |
| 2 | [Amazon SageMaker Unified Studio Notebooks now support EMR Serverless](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-unified-studio-emr/) | SageMaker Unified Studio Notebooks が EMR Serverless with Apache Spark Connect に対応。PySpark と Spark SQL を EMR Serverless 上で実行でき、AI アシスタント「SageMaker Data Agent」による自然言語からのコード生成も可能 |
| 3 | [Amazon S3 Access Grants (European Sovereign Cloud - Germany)](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-s3-access-grants-european-sovereign-cloud-germany-region) | AWS European Sovereign Cloud（ドイツ）で S3 Access Grants が利用可能に。Microsoft Entra ID や AWS IAM などのディレクトリ内のアイデンティティを S3 データセットにマッピングし、大規模なデータ権限管理を効率化 |
| 4 | [AWS announces Claude Fable 5](https://aws.amazon.com/about-aws/whats-new/2026/06/claude-fable-5-aws/) | 初の一般提供 Mythos クラスモデル Claude Fable 5 を発表。強固な安全対策（safeguards）を備え、金融・法務・エンジニアリングなどの分野で学習に基づきスキルを自律的に更新。Amazon Bedrock または Claude Platform on AWS からアクセス可能 |
| 5 | [Run Interactive Workloads on Amazon EMR Serverless with Spark Connect](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-emr-serverless-spark-connect) | EMR Serverless が Spark Connect に対応し、インタラクティブセッション機能を提供。クライアント-サーバーアーキテクチャにより、任意のノートブック環境から Spark アプリケーションを開発・実行可能に。セッション単位のコスト可視化にも対応 |
| 6 | [AWS FinOps Agent (Preview)](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/) | FinOps 実践者向けの AI エージェントをプレビュー提供。コスト質問への回答、最適化機会の提示、コスト異常の自動調査、Slack 通知、Jira チケット自動作成などが可能。プレビュー期間は無料で利用可能（米国東部リージョン） |
| 7 | [Amazon CloudWatch Logs Insights adds 23 new query commands and functions](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-logs-insights-new/) | CloudWatch Logs Insights のクエリ言語に 23 個の新機能を追加。ハッシュ関数（md5、sha256）、IP 処理関数（isPrivateIP、isPublicIP等）、分析関数（rate、histogram等）、CSV/XML パース、条件分岐（if）などに対応 |
| 8 | [AWS Cost Explorer launches intelligent cost explanations powered by Amazon Q](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-cost-explorer-intelligent-cost-explanations) | Cost Explorer に Amazon Q を活用した「Analyze with Amazon Q」機能を追加。ワンクリックでコスト傾向、主要コストドライバー、異常値などを包括的に分析。対話形式で追加質問も可能。全商用リージョンで追加料金なしで利用可能 |
| 9 | [PostgreSQL 19 Beta 1 (RDS Database Preview Environment)](https://aws.amazon.com/about-aws/whats-new/2026/06/postgresql-19-beta-1-amazon-rds-database-preview-environment/) | PostgreSQL 19 Beta 1 が Database Preview Environment で利用可能に。ネイティブグラフクエリ機能（SQL/PGQ）、同時テーブル再パック、論理レプリケーション強化（シーケンス自動同期、再起動なしの有効化）などが追加 |

## まとめ

今回のアップデートは、**AIエージェントによる運用自動化**、**データ主権とコンプライアンス対応**、**開発者体験の向上**という3つのテーマが明確です。

特にAI/MLエージェントの実用化が進んでおり、FinOps AgentやCost ExplorerのAmazon Q統合により、コスト管理業務の自動化が現実的になってきました。これらは単なる分析ツールではなく、SlackやJiraと統合された「エージェント」として、人間の意思決定を支援する存在に進化しています。

一方で、EMR ServerlessのSpark Connect対応やCloudWatch Logs Insightsの機能拡張は、データエンジニアリングと運用監視の基盤を強化するものです。これらの機能は地味に見えるかもしれませんが、日々の開発・運用効率に直結する重要なアップデートです。

AWS European Sovereign Cloud（ドイツ）での機能拡充は、欧州市場におけるAWSの戦略的投資を示しています。データ主権要件が厳しい組織にとって、これらの機能は単なる利便性向上ではなく、コンプライアンス遵守の前提条件となります。

PostgreSQL 19 Beta 1のプレビュー提供は、オープンソースコミュニティとの連携を重視するAWSの姿勢を示すものです。特にネイティブグラフクエリ機能（SQL/PGQ）は、グラフデータベースの専用製品なしで関係性データを扱えるようになる重要な進化です。

全体として、運用自動化とコスト最適化を支援するAIエージェント、開発者体験を向上させる新機能、そしてコンプライアンス対応を強化する地域展開という、バランスの取れたアップデートとなっています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)