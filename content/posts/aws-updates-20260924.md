---
title: "【AWS】2026/09/24 のアップデートまとめ"
date: 2026-09-24T08:02:07+09:00
draft: false
tags: ["aws", "connect", "bedrock", "cloudwatch", "emr", "athena", "amazon-quick", "eks", "s3"]
categories: ["AWS Updates"]
summary: "2026/09/24 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260924/header.png)

# 今回は、直近で発表された6件のAWSアップデートを紹介します

## はじめに

今回の6件は、Amazon Connect Customer の2件（エージェント間協調、ルーティングステップデータのデータレイク提供）、Amazon Bedrock Managed Knowledge Base の Salesforce / Zendesk コネクタ、Amazon CloudWatch Omni の一般提供、Amazon EMR の2件（EMR 7.14、長期サポート（LTS）リリースの導入）です。本記事では Bedrock のコネクタと CloudWatch Omni を深掘りし、SRE 視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon Bedrock Managed Knowledge Base：Salesforce・Zendesk コネクタに対応

フルマネージドの RAG（Retrieval-Augmented Generation）サービスである Amazon Bedrock Managed Knowledge Base に、Salesforce と Zendesk のデータソースコネクタが追加されました。Salesforce のナレッジ記事と、Zendesk の記事およびコミュニティ投稿を、ナレッジベースに直接同期できます。

これまでは、これらのプラットフォームのコンテンツを Bedrock Knowledge Bases に取り込むには独自の取り込みパイプラインが必要でした。今回のコネクタでは、インスタンスの認証情報を渡すだけで、次の処理をコネクタが自動で行います。

- データのクローリング
- メタデータの抽出
- 差分同期（インクリメンタル同期）

告知が挙げる例は、最新の Zendesk ヘルプセンター記事とコミュニティの回答を使う顧客向けサポートボットや、商談準備中に関連する Salesforce ナレッジ記事を取り出す社内向けの営業支援アシスタントです。ナレッジベースがこれらのプラットフォームと同期し続けるため、RAG アプリケーションは手作業なしで最新のコンテンツを反映します。

### Amazon CloudWatch Omni：一般提供開始

Amazon CloudWatch Omni が一般提供されました。告知では「Amazon CloudWatch の進化版」と位置づけられ、OpenTelemetry の相互運用性と CloudWatch のスケール・信頼性を組み合わせたものとしています。

告知に記載された主な機能は次の通りです。

- **スペース**: 中央アカウントにスペースを作成し、AWS のアカウントとリージョンをまたいだテレメトリーに加え、Azure ワークロードを含む他クラウドのテレメトリーも確認できる
- **自動検出**: サービスを自動で検出し、依存関係をマッピングし、ゴールデンメトリクスを提示する
- **自然言語での問い合わせ**: 自然言語で質問すると、関連するテレメトリーを見つけて動的なビューを構成する
- **根本原因の特定**: AWS DevOps Agent による根本原因の特定を支援する
- **Agent Toolkit for AWS**: テレメトリーへの直接アクセスに利用できる
- **AI エージェント開発者向け**: LangGraph、CrewAI、OpenAI Agents SDK、Vercel AI SDK、Strands に対応
- **IDE 拡張**: VS Code、Cursor、Kiro 向けの CloudWatch Omni 拡張

提供リージョンは米国東部（バージニア北部）、米国西部（オレゴン）、欧州（アイルランド）です。料金は専用の料金ページで案内されています。

## SRE 視点での活用ポイント

### CloudWatch Omni の評価

- AWS と Azure の両方でワークロードを運用している場合、スペースで他クラウドのテレメトリーをまとめて見られるかが評価の中心になります
- 提供リージョンは現時点で3リージョンのため、中央アカウントをどのリージョンに置くかを含めて検討します
- 料金は告知本文には書かれていないため、既存の CloudWatch 利用分と合わせて料金ページで確認します

### Amazon Connect のルーティング分析

Amazon Connect Customer のルーティングステップデータが分析用データレイクで提供されるようになり、Amazon Athena や Amazon Quick で、各ルーティングステップでキューに入った件数やエージェントにつながった件数の傾向を、複雑なデータパイプラインなしで分析できます。告知の例では、コンタクトが各ルーティングステップをどう進んだか、エージェントのマッチング条件がどこで緩和されたか、ルーティングステップの設定が待機時間とエージェント稼働率にどう影響したかを分析できるとしています。

### Amazon Connect のエージェント間協調

Connect Customer の AI エージェントは、オープンな A2A（agent-to-agent）プロトコルで、テキストまたは双方向音声を使って、互いに、また Connect Customer 外の AI エージェントとも協調できるようになりました。告知の例は、顧客の電話に対応する最前線の AI エージェントが不正評価を専門エージェントに委ね、複雑な異議申し立てを別のエージェントにエスカレーションする銀行のシナリオです。各エージェントの発言、呼び出したツール、各ステップの所要時間が1つのコンタクトレコードにまとまり、分析や AI の品質管理に使えます。複数エージェントでの構成を運用する場合は、このコンタクトレコードを品質確認の起点にできます。

### Amazon EMR の LTS と 7.14

- LTS リリースは emr-spark-8.1.0（Apache Spark 4.1）から始まり、36 か月サポートされます。提供されるのは、重大度が critical / high のセキュリティ・バグ・データ破損の修正です（告知では「利用可能な場合」の条件付き）。アップグレード頻度を抑えたい本番ワークロードでは候補になります
- EMR 7.14 では、EMR Serverless の Spark ジョブのストレージ上限が 200 GiB から 1 TiB に拡大され、シャッフルデータに使える容量が増えました

## まとめ

Bedrock Managed Knowledge Base の Salesforce / Zendesk コネクタにより、独自の取り込みパイプラインなしでこれらのコンテンツを RAG に使えるようになりました。CloudWatch Omni は、他クラウドを含むテレメトリーの横断表示、自動検出、自然言語での問い合わせ、AI エージェント向けの可観測性を備えて一般提供されました。Amazon Connect ではエージェント間協調とルーティングステップデータの分析、EMR では LTS リリースの導入と EMR 7.14 が加わっています。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [Amazon Connect Customer now provides routing step data in the analytics data lake](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-routing-step-data/) | ルーティングステップデータがアナリティクスデータレイクで利用可能に。Amazon Athena や Amazon Quick で、ルーティングステップ設定が待機時間やエージェント稼働率に与える影響を、複雑なデータパイプラインなしで分析可能。 |
| [Amazon Bedrock Managed Knowledge Base now supports Salesforce and Zendesk as native data source connectors](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-managed-knowledge-base-salesforce-zendesk-native-data-source-connectors/) | Salesforce のナレッジ記事、Zendesk の記事とコミュニティ投稿を同期可能に。インスタンス認証情報を渡すだけで、クローリング・メタデータ抽出・差分同期をコネクタが自動で処理。 |
| [Amazon Connect Customer launches agent-to-agent collaboration](https://aws.amazon.com/about-aws/whats-new/2026/09/Amazon-Connect-Customer-A2A) | エージェント間協調機能をサポート。オープンな A2A プロトコルで AI エージェント同士がテキスト・音声で協調作業し、複雑な顧客リクエストを段階的に解決。単一の連絡記録で分析・品質管理が容易に。 |
| [Amazon CloudWatch Omni: AI-first observability for agents and applications](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-cloudwatch-omni-ai/) | CloudWatch の進化版として一般提供開始。AWS アカウント・リージョンと Azure などの他クラウドのテレメトリーを横断して見られるスペース、OpenTelemetry との相互運用性、自然言語での問い合わせ、AI エージェント開発者向けの可観測性を提供。バージニア北部・オレゴン・アイルランドで利用可能。 |
| [Amazon EMR 7.14 is now available](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-emr-7-14-available/) | Apache Spark 3.5.8、Apache Iceberg 1.10.1 にアップグレード。更新・削除のあるテーブルで Iceberg マテリアライズドビューが変更データキャプチャ（CDC）により高速にリフレッシュ。EMR on EKS でトークン認証付き Spark Connect エンドポイントと IPv6 EKS クラスターに対応。EMR Serverless の Spark ジョブのストレージ上限を 200 GiB から 1 TiB に拡大。 |
| [Amazon EMR introduces Long Term Support with Apache Spark 4.1](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-emr-long-term-support-spark-4-1/) | emr-spark-8.1.0（Apache Spark 4.1）から、36 か月サポートされる長期サポート（LTS）リリースを導入。Apache Iceberg v3 の完全サポートで地理空間データ、高精度タイムスタンプに対応。クロスアカウント・S3 Tables カタログの名前参照、きめ細かいアクセス制御の対象拡大、EMR on EKS での Spark Connect のトークンベース認証をサポート。 |

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)