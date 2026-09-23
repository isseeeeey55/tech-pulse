---
title: "【AWS】2026/09/24 のアップデートまとめ"
date: 2026-09-24T08:02:07+09:00
draft: true
tags: ["aws", "connect", "bedrock", "cloudwatch", "emr", "athena", "quicksight", "eks", "s3"]
categories: ["AWS Updates"]
summary: "2026/09/24 のAWSアップデートまとめ"
---

# 直近の AWS アップデート 6 件を徹底解説 - Amazon Connect・Bedrock・CloudWatch Omni など

## はじめに

今回は、直近で発表された 6 件の AWS アップデートを紹介します。コンタクトセンター機能を強化する Amazon Connect の新機能、AI エージェント開発を加速する Amazon Bedrock と CloudWatch Omni のアップデート、そして安定運用を支える Amazon EMR の長期サポート導入など、AI 駆動の次世代サービスと大規模データ処理基盤の両面で重要な進化が見られます。

特に注目すべきは、AI エージェント同士が協調して顧客対応を行う Amazon Connect のエージェント間協調機能と、マルチクラウド環境を統合管理できる CloudWatch Omni の一般提供開始です。また、Amazon Bedrock が Salesforce と Zendesk のネイティブ連携に対応したことで、RAG アプリケーション構築の敷居が大きく下がりました。データ処理基盤では EMR が 36 ヶ月の長期サポートを導入し、本番環境での安定運用とアップグレード戦略の柔軟性が向上しています。

## 注目アップデート深掘り

### Amazon Bedrock が Salesforce・Zendesk のネイティブコネクタに対応

Amazon Bedrock Managed Knowledge Base が Salesforce と Zendesk のネイティブデータソースコネクタに対応しました。これは RAG（Retrieval-Augmented Generation）ベースの AI アプリケーション構築において、大きな運用効率化をもたらすアップデートです。

**従来の課題と新機能の価値**

これまで Salesforce や Zendesk のコンテンツを Bedrock Knowledge Base に取り込むには、カスタムの取り込みパイプラインを構築する必要がありました。具体的には、各プラットフォームの API を使ったデータ抽出処理、メタデータの正規化、差分検知ロジック、定期同期スケジューラーなど、運用に必要な複数のコンポーネントを自前で実装・保守する必要があったのです。

今回のアップデートにより、インスタンス認証情報を提供するだけで、以下が自動的に処理されるようになりました。

- **データのクローリング**: Salesforce ナレッジ記事や Zendesk のヘルプセンター記事・コミュニティ投稿を自動検出
- **メタデータ抽出**: 記事のタイトル、カテゴリ、作成日、更新日などの構造化情報を自動抽出
- **差分同期**: 変更のあったコンテンツのみを自動的に検知して更新

**RAG アプリケーション構築の流れ**

この機能により、顧客サポートチャットボットや社内ナレッジ検索システムの構築が大幅に簡素化されます。Zendesk ヘルプセンターの記事をリアルタイムで同期しておけば、最新のトラブルシューティング手順や製品情報に基づいて顧客の質問に回答できます。Salesforce のナレッジベースと組み合わせることで、営業担当者が案件準備中に関連する製品情報や過去の成功事例を自動検索・提示するアシスタントも容易に実現できます。

**他のデータソースとの統合**

Bedrock Managed Knowledge Base は、S3 や Confluence など他のデータソースコネクタとも併用できます。複数のデータソースを組み合わせることで、Salesforce の営業ナレッジ、Zendesk のサポート記事、社内 Confluence のドキュメントを統合したハイブリッド知識アシスタントの構築が可能になります。Knowledge Base が常に最新コンテンツを反映するため、手動介入なしに RAG アプリケーションが常に最新の情報を利用できる点も重要なメリットです。

**検証ポイント**

実際に導入を検討する際は、以下の点を確認することをお勧めします。

- データ同期の遅延時間と更新頻度の実測
- メタデータ抽出の正確性と、検索精度への影響
- 従来のカスタムパイプライン開発時間（数週間〜数ヶ月）と、ネイティブコネクタの設定時間（数時間）の比較
- 既存の Salesforce / Zendesk ユーザー権限モデルとの整合性確認

カスタムパイプラインの開発・保守コストと比較すると、ネイティブコネクタの導入により運用負荷が大幅に削減されることが期待できます。

### Amazon CloudWatch Omni: AI 駆動のマルチクラウド可観測性

Amazon CloudWatch Omni が一般提供を開始しました。これは AI を活用した次世代の可観測性プラットフォームで、従来の CloudWatch を大きく進化させた統合管理体験を提供します。

**マルチクラウド環境の統合可視化**

CloudWatch Omni の最大の特徴は、AWS アカウント・リージョン間だけでなく、**Azure ワークロードを含む他クラウドのテレメトリーも一箇所で可視化できる「Space」機能**です。これにより、ハイブリッドクラウドやマルチクラウド構成を採用している組織でも、分散した監視ツールを統合し、単一のインターフェースで運用できるようになります。

従来は AWS 環境と Azure 環境で別々の監視ツールを使い分け、障害発生時には複数のダッシュボードを行き来しながら原因を特定する必要がありました。Space 機能を使えば、これらのテレメトリーデータを統合し、サービスの依存関係を跨いだトレーシングや、クラウド境界を越えたメトリクス相関分析が可能になります。

**OpenTelemetry との相互運用性**

CloudWatch Omni は OpenTelemetry との相互運用性を備えています。これにより、既存の計装コードを変更することなく、OpenTelemetry で収集したトレース、メトリクス、ログを CloudWatch Omni に送信できます。CloudWatch のスケーラビリティと信頼性を活かしながら、標準的な可観測性フレームワークを継続利用できる点は、ベンダーロックインを避けたいチームにとって重要な選択肢となります。

**自動検出と AI 支援のトラブルシューティング**

Omni は、サービスの自動検出、依存関係のマッピング、ゴールデンメトリクスの自動抽出により、運用ワークフローを効率化します。新しいサービスがデプロイされると、自動的に検出され、既存のサービスマップに組み込まれます。ゴールデンメトリクス（レイテンシー、トラフィック、エラー、サチュレーション）も自動的に抽出されるため、手動でダッシュボードを構築する手間が省けます。

さらに、自然言語での質問、ポイント・クリック操作、Agent Toolkit for AWS の連携など、複数の方法でテレメトリーとやり取りできます。AWS DevOps Agent がルート原因の特定をサポートするため、「過去 1 時間でレイテンシーが上昇したサービスは？」といった質問を自然言語で投げかけるだけで、関連するメトリクスやログが自動的に収集・分析されます。

**エージェント開発者向けの専用機能**

AI エージェント開発者向けには、LangGraph、CrewAI、OpenAI Agents SDK などの AI フレームワークに対応した専用の可観測性体験があり、評価駆動開発ワークフローで品質検証と実験実行が可能です。VS Code・Cursor 用の無料拡張機能も提供されており、開発者は IDE から直接テレメトリーにアクセスして迅速にデバッグできます。

**導入時の考慮事項**

実際の導入にあたっては、以下の検証が推奨されます。

- Space 作成から SSO 連携までの具体的な設定手順の確認
- 既存 CloudWatch との機能比較（テレメトリー統合、検索速度、UI/UX など）
- OpenTelemetry Collector の設定と、既存の計装コードとの互換性検証
- マルチクラウド環境でのネットワークレイテンシーとデータ転送コストの試算

マルチクラウド環境を運用している組織や、AI エージェント開発を本格的に進めているチームにとって、CloudWatch Omni は統合可観測性の新しい選択肢となるでしょう。

## SRE 視点での活用ポイント

**ルーティング分析とキャパシティプランニング**

Amazon Connect のルーティングステップデータがアナリティクスデータレイクで利用可能になったことで、コンタクトセンター運用の改善サイクルが加速します。Athena でルーティングステップごとの待機時間やエージェント利用率を分析し、QuickSight でダッシュボード化すれば、リアルタイムでボトルネックを特定できます。ルーティング設定の変更前後でパフォーマンスを比較し、A/B テスト的にルーティング戦略を最適化する運用が可能になります。従来はダッシュボード単体で概要を把握するに留まっていましたが、データレイクへの統合により、過去数ヶ月分のトレンド分析や、サービスレベル達成状況の詳細分析が容易になります。導入時には Athena と QuickSight の利用料金をシミュレーションし、得られる価値と比較検討することが重要です。

**AI エージェントのコンテキスト継続性**

Amazon Connect のエージェント間協調機能は、複雑な顧客リクエストを段階的に解決する運用フローに適しています。オープンなエージェント間プロトコル（A2A）を通じて、Connect Customer 内外の AI エージェントがテキストまたは双方向音声で協調作業できるため、フロントラインエージェントから専門スコアリングエージェント、紛争解決エージェントへとシームレスに引き継ぐワークフローが実現します。単一の連絡記録にすべてのエージェントの発言内容、呼び出したツール、各ステップの所要時間が記録されるため、事後分析や AI 品質管理が容易です。導入時には、既存の人間エージェントへのエスカレーション基準と、AI エージェント間のハンドオフ基準を明確に定義し、監視とガードレールを適切に設定することが求められます。

**安定運用と計画的アップグレード**

Amazon EMR が 36 ヶ月の長期サポート（LTS）を導入したことで、本番環境のデータ処理基盤を長期安定稼働させる選択肢が生まれました。重大度の高いセキュリティ脆弱性、バグ、データ破損問題の修正が継続的に提供されるため、アップグレードのタイミングを慎重に計画できます。Apache Iceberg v3 の完全サポートにより、地理空間データや高精度タイムスタンプを含むデータレイクの構築が可能になり、列レベル・行レベルのきめ細かいアクセス制御で規制対応やデータ保護要件を満たせます。クロスアカウントカタログ参照に対応したことで、マルチテナント環境でのデータ共有も柔軟になります。導入時には、EMR Serverless のストレージ上限拡大（200 GiB → 1 TiB）により大規模シャッフル操作の制約が緩和される点も確認し、ワークロードの特性に応じたプラットフォーム選択（EC2、EKS、Serverless）を行うことが重要です。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [Amazon Connect Customer now provides routing step data in the analytics data lake](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-routing-step-data/) | ルーティングステップデータがアナリティクスデータレイクで利用可能に。Athena や QuickSight でルーティング決定を分析し、待機時間やエージェント利用率の最適化が可能。 |
| [Amazon Bedrock Managed Knowledge Base now supports Salesforce and Zendesk as native data source connectors](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-managed-knowledge-base-salesforce-zendesk-native-data-source-connectors/) | Salesforce と Zendesk のネイティブコネクタ対応により、カスタムパイプライン不要でナレッジベースの自動同期が可能に。RAG アプリケーション構築を大幅に簡素化。 |
| [Amazon Connect Customer launches agent-to-agent collaboration](https://aws.amazon.com/about-aws/whats-new/2026/09/Amazon-Connect-Customer-A2A) | エージェント間協調機能をサポート。オープンな A2A プロトコルで AI エージェント同士がテキスト・音声で協調作業し、複雑な顧客リクエストを段階的に解決。単一の連絡記録で分析・品質管理が容易に。 |
| [Amazon CloudWatch Omni: AI-first observability for agents and applications](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-cloudwatch-omni-ai/) | AI 駆動の次世代可観測性プラットフォーム。AWS と Azure を含むマルチクラウド環境を統合管理する Space 機能、OpenTelemetry 相互運用性、自然言語での質問対応、AI エージェント開発者向けの専用機能を提供。 |
| [Amazon EMR 7.14 is now available](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-emr-7-14-available/) | Apache Spark 3.5.8、Apache Iceberg 1.10.1 にアップグレード。Iceberg materialized views が CDC を活用して高速リフレッシュ。EMR on EKS で Spark Connect エンドポイントと IPv6 対応。EMR Serverless のストレージ上限を 1 TiB に拡大。 |
| [Amazon EMR introduces Long Term Support with Apache Spark 4.1](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-emr-long-term-support-spark-4-1/) | 36 ヶ月の長期サポート（LTS）を導入。Apache Iceberg v3 の完全サポートで地理空間データ、高精度タイムスタンプに対応。クロスアカウントカタログ参照、きめ細かいアクセス制御、Spark Connect のトークンベース認証をサポート。 |

## まとめ

今回のアップデートでは、AI エージェントを中心とした顧客体験の向上と、マルチクラウド環境における運用効率化が大きなテーマとなっています。Amazon Connect のエージェント間協調機能と、CloudWatch Omni の統合可観測性は、複雑化するシステムアーキテクチャを管理するための新しいアプローチを示しています。

また、Amazon Bedrock のネイティブコネクタ対応により、RAG アプリケーション構築の敷居が大きく下がり、既存の企業ナレッジを AI に活用する道が開けました。データ処理基盤では、EMR の長期サポート導入により、本番環境での安定運用とアップグレード戦略の柔軟性が向上し、Apache Iceberg v3 の対応で地理空間データや高度なアクセス制御が可能になっています。

AI 駆動のサービスが成熟し、実運用に耐える信頼性とガバナンスが整いつつあることが、今回のアップデートから読み取れます。特に可観測性とデータ分析基盤の強化により、AI エージェントの品質管理と継続的改善のサイクルを回しやすくなった点は、今後の AI 活用拡大に向けた重要な布石と言えるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)