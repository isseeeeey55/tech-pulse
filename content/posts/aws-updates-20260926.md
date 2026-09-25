---
title: "【AWS】2026/09/26 のアップデートまとめ"
date: 2026-09-26T08:02:01+09:00
draft: false
tags: ["aws", "End User Messaging", "IAM", "STS", "Transcribe", "KMS", "Elastic Disaster Recovery", "DataSync", "Billing and Cost Management", "EventBridge", "ElastiCache", "PrivateLink", "CloudTrail", "Resource Access Manager"]
categories: ["AWS Updates"]
summary: "2026/09/26 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260926/header.png)

# 今回は、直近で発表された8件のAWSアップデートを紹介します

## はじめに

今回は、直近で発表された8件の AWS アップデートを紹介します。今回のアップデートでは、**エンタープライズ規模のイベント駆動アーキテクチャを実現する Amazon EventBridge の Custom event bus 刷新**や、**WhatsApp 内で音声通話が可能になった AWS End User Messaging の拡張**などが含まれます。

また、セキュリティとガバナンスの面では、**IAM outbound identity federation が VPC エンドポイントに対応**し、厳格なネットワーク分離環境でも OIDC ベースの認証が可能になりました。さらに **Amazon Transcribe のカスタマー管理型 KMS キー対応**、**ElastiCache Global Datastore のタグベースアクセス制御**など、コンプライアンス要件への対応が強化されています。

ディザスタリカバリと運用監視の領域では、**AWS DRS が Graviton ベース（arm64）のソースサーバーに対応**し、**DataSync のコンソールに監視ダッシュボード**が追加されました。

---

## 注目アップデート深掘り

### 1. Amazon EventBridge が企業規模対応の Custom event bus をリリース

Amazon EventBridge が、機能を強化した新しい Custom event bus をリリースしました。カスタムイベントバスを作成してアカウント間で共有し、チームが厳密な順序保証・オープンなイベント形式・組み込みの保持期間・高度なイベント変換を使ってイベントを発行・購読できます。

#### 新しい Custom event bus の機能

- **複数アカウント間での event bus 共有**：AWS Resource Access Manager を通じて、組織内の異なるアカウント間で event bus を共有できます。これにより、集約的なイベント処理ハブを構築しつつ、各チームは独立した AWS アカウントで運用できます
- **厳密な順序保証**：受け取った順序どおりにイベントを処理できます
- **CloudEvents などのオープン形式対応**：新しいイベント発行 API で、CloudEvents などの JSON ベースのイベント形式をスキーマを変えずに発行できます
- **組み込み保持期間（24時間〜最大1年）**：アプリケーションエラーからの復旧や、新しいマイクロサービスのオンボーディング時に履歴イベントを供給できます
- **Subscriber リソース**：イベントをフィルタリングし、250 以上の AWS サービスに配信できます
- **内容ベースの重複排除**：新しいイベント評価により自動で重複を排除します

#### 実際の活用シナリオ

マイクロサービスアーキテクチャを採用している組織では、チーム間の疎結合を維持しながらイベント通信を実現することが重要です。新しい Custom event bus を使用すると、以下のような運用が可能になります：

**マルチアカウントでのイベント集約**：チームごとに別の AWS アカウントを使っている場合でも、共有した中央の event bus に各アカウントのパブリッシャーから直接イベントを送れます。

**履歴イベントを活用した復旧**：アプリケーションにバグが混入し、一部のイベント処理に失敗した場合、保持期間内の履歴イベントを再処理することで、データの整合性を回復できます。保持期間は既定の24時間から最大1年まで延長できます。

**新規サービスのオンボーディング**：新しいコンポーネントを追加する際に、保持されている過去のイベントでデータを投入（hydrate）できます。

#### 既存環境からの移行検討

既存の Custom event bus は「Custom event bus - classic」に名称変更されましたが、既存の API はすべて変更ありません。新しい Custom event bus は、コンソール、AWS CLI、AWS SDK、Serverless Agent skill、AWS CloudFormation で作成・共有できます。移行手順は告知には書かれていないため、公式ドキュメントを確認してください。

---

### 2. IAM outbound identity federation が VPC エンドポイント経由の OIDC discovery をサポート

AWS IAM の outbound identity federation が、OIDC discovery API 用の VPC エンドポイントをサポートしました。

#### 背景：なぜこの機能が必要だったのか

IAM outbound identity federation は、AWS のワークロードが外部サービスにアクセスする際に長期的な認証情報を不要にする仕組みです。ワークロードは AWS STS から短期の JSON Web Token（JWT）を取得し、外部サービスは OIDC discovery エンドポイントで公開されている検証キーとメタデータでトークンを検証します。

これまで OIDC discovery エンドポイントにはパブリックインターネット経由でしか到達できなかったため、インターネットにアクセスできない VPC で動く検証側のワークロードは、検証キーを取得できませんでした。

#### VPC エンドポイント対応による改善

インターフェース VPC エンドポイントを作成すれば、AWS PrivateLink 経由で OIDC discovery のメタデータと JWKS（JSON Web Key Set）の検証キーエンドポイントに VPC 内からアクセスでき、検証キー取得のトラフィックを AWS ネットワーク内に留められます。

**通信フローの変化**：

- **従来**：VPC 内のワークロード → NAT Gateway または Internet Gateway → パブリックインターネット → OIDC discovery エンドポイント
- **新方式**：VPC 内のワークロード → VPC エンドポイント（AWS PrivateLink） → OIDC discovery エンドポイント

インターネットへのアクセスが制限された VPC で動くワークロードでも、ネットワークセキュリティ要件を満たしながら JWT の検証ができます。

#### 設定と運用上のポイント

VPC エンドポイントを作成する際には、以下の点に注意が必要です：

- **セキュリティグループの設定**：VPC エンドポイントに適切なセキュリティグループを割り当て、必要な通信のみを許可します
- **料金**：AWS PrivateLink の標準料金以外に、この機能の追加料金はかかりません

この機能は、すべての商用 AWS リージョン、AWS GovCloud (US) リージョン、中国リージョンで利用できます。

---

## SRE 視点での活用ポイント

**DataSync の監視ダッシュボード**では、アカウント内のタスク実行について、ステータス、データとファイルの転送レート、所要時間、転送量をコンソールで確認できます。ステータス・タスク・タスクモード・実行 ID・開始時刻で絞り込み、失敗した実行を選んでエラーを確認できます。タスクごとの成功・失敗の件数もまとめて表示されるため、定期転送の状況確認に使えます。

**ElastiCache Global Datastore のタグベースアクセス制御**では、IAM ポリシーや SCP の条件にタグを使い、個々のリソースを列挙せずに権限を付与できます。たとえば `Environment:production` タグを持つリソースにのみ本番環境の権限を付与するといった制御ができます。Global Datastore のタグの変更は、対象のすべてのリージョンに自動で伝播します。

**AWS DRS の Graviton 対応**により、Graviton ベース（arm64）のソースサーバーも、x86 と同じ DRS の手順で保護・復旧できるようになりました。arm64 サーバーは自動で識別され、Graviton インスタンスに復旧されます。追加料金はかかりません。Graviton へ移行したワークロードも、復旧テストで RPO/RTO を実測しておきます。

**IAM outbound identity federation の VPC エンドポイント対応**は、インターネットへのアクセスを制限した VPC で JWT を検証するワークロードがある場合に関係します。インターフェース VPC エンドポイントには AWS PrivateLink の標準料金がかかる点は事前に確認します。

---

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| **AWS End User Messaging** | WhatsApp 内で音声通話の発信・受信が可能に。チャットから通話へシームレスに移行でき、会話コンテキストを維持 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-voice-calling-whatsapp) |
| **AWS IAM** | outbound identity federation が OIDC discovery APIs 用の VPC エンドポイントをサポート。PrivateLink 経由でプライベートアクセスが可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-sts-vpc-oidc/) |
| **Amazon Transcribe** | カスタマー管理型 KMS キーによる暗号化をサポート。カスタム語彙、語彙フィルター、カスタム言語モデルに対して独自の暗号化キーを指定可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-transcribe/) |
| **AWS Elastic Disaster Recovery** | Graviton ベース（arm64）のソースサーバーのディザスタリカバリに対応。x86 と同じ DRS の手順で保護・復旧可能（追加料金なし） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/elastic-disaster-recovery-graviton/) |
| **AWS DataSync** | コンソール内に監視ダッシュボードを追加。アカウント全体のデータ転送を一元的に可視化し、ステータス、転送速度、実行時間などを確認可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/datasync-monitoring-dashboard) |
| **AWS Billing and Cost Management** | 新 API「ListBillingViewSegments」を提供。指定期間のアカウント請求コンテキスト（請求階層内の位置付け）を返す | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-billing-and-cost-management-billing-context-api/) |
| **Amazon EventBridge** | 機能を強化した新しい Custom event bus をリリース（既存バスは「Custom event bus - classic」に改称）。厳密な順序保証、CloudEvents 対応、最大1年の保持期間、Subscriber リソースなどをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/eventbridge-relaunches-custom-event-buses/) |
| **Amazon ElastiCache** | Global Datastore がタグ付けとタグベースアクセス制御に対応。タグ変更は対象の全リージョンに自動伝播し、権限とコスト配分のポリシーをリージョンごとの操作なしに揃えられる | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-elasticache-global-datastore-tagging/) |

---

## まとめ

EventBridge は、アカウント間での共有、厳密な順序保証、CloudEvents などのオープン形式、最大1年の保持、250 以上の AWS サービスへ配信できる Subscriber リソースを備えた新しい Custom event bus をリリースしました。既存のバスは「Custom event bus - classic」に改称され、既存の API は変わりません。

セキュリティとガバナンスの面では、IAM outbound identity federation の OIDC discovery 用 VPC エンドポイント、Transcribe のカスタマー管理 KMS キー、ElastiCache Global Datastore のタグベースアクセス制御が加わりました。運用面では、DataSync の監視ダッシュボードと DRS の Graviton 対応があります。

このほか、請求コンテキストを返す Billing and Cost Management の `ListBillingViewSegments` API と、WhatsApp 上での音声通話（End User Messaging）が追加されています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)