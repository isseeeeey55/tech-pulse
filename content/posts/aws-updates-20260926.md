---
title: "【AWS】2026/09/26 のアップデートまとめ"
date: 2026-09-26T08:02:01+09:00
draft: true
tags: ["aws", "End User Messaging", "IAM", "STS", "Transcribe", "KMS", "Elastic Disaster Recovery", "DataSync", "Billing and Cost Management", "EventBridge", "ElastiCache", "PrivateLink", "CloudTrail", "Resource Access Manager"]
categories: ["AWS Updates"]
summary: "2026/09/26 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報まとめ（8件）

## はじめに

今回は、直近で発表された8件の AWS アップデートを紹介します。今回のアップデートでは、**エンタープライズ規模のイベント駆動アーキテクチャを実現する Amazon EventBridge の Custom event bus 刷新**や、**WhatsApp 内で音声通話が可能になった AWS End User Messaging の拡張**など、エンタープライズ向けの機能強化が目立ちます。

また、セキュリティとガバナンスの面では、**IAM outbound identity federation が VPC エンドポイントに対応**し、厳格なネットワーク分離環境でも OIDC ベースの認証が可能になりました。さらに **Amazon Transcribe のカスタマー管理型 KMS キー対応**、**ElastiCache Global Datastore のタグベースアクセス制御**など、コンプライアンス要件への対応が強化されています。

ディザスタリカバリと運用監視の領域では、**AWS DRS が Graviton ベースサーバーに対応**し、**DataSync の監視ダッシュボード**が追加されるなど、マルチアーキテクチャ環境の運用効率化が進んでいます。

それでは注目のアップデートから詳しく見ていきましょう。

---

## 注目アップデート深掘り

### 1. Amazon EventBridge が企業規模対応の Custom event bus をリリース

Amazon EventBridge が企業規模対応の新しい Custom event bus をリリースしました。このアップデートは、マイクロサービスアーキテクチャやイベント駆動アプリケーションを本格的に展開する組織にとって重要な機能強化です。

#### なぜこのアップデートが重要なのか

従来の Custom event bus - classic では、大規模なマルチチーム・マルチアカウント環境での運用において、いくつかの制約がありました。特にイベントの順序保証、長期保持、標準形式対応などの面で、エンタープライズグレードのイベント駆動アーキテクチャを構築するには課題がありました。

今回のリリースにより、以下の機能が新たにサポートされます：

- **複数アカウント間での event bus 共有**：AWS Resource Access Manager を通じて、組織内の異なるアカウント間で event bus を共有できます。これにより、集約的なイベント処理ハブを構築しつつ、各チームは独立した AWS アカウントで運用できます
- **厳密な順序保証**：金融取引やオーダー処理など、イベントの処理順序が重要なユースケースに対応できます
- **CloudEvents などのオープン形式対応**：ベンダーロックインを避け、標準化されたイベント形式でシステム間連携が可能になります
- **組み込み保持期間（24時間〜最大1年）**：アプリケーションエラーからの復旧や、新しいマイクロサービスのオンボーディング時に履歴イベントを供給できます
- **250以上の AWS サービスへの配信をサポートする Subscriber リソース**：内容ベースの重複排除も自動対応します

#### 実際の活用シナリオ

マイクロサービスアーキテクチャを採用している組織では、チーム間の疎結合を維持しながらイベント通信を実現することが重要です。新しい Custom event bus を使用すると、以下のような運用が可能になります：

**マルチアカウント環境でのイベント集約**：本番環境、ステージング環境、開発環境をそれぞれ別の AWS アカウントで運用している場合でも、共有された event bus を通じてイベントを集約・配信できます。これにより、環境間の分離を維持しつつ、統一されたイベント処理基盤を構築できます。

**履歴イベントを活用した復旧**：アプリケーションにバグが混入し、一部のイベント処理に失敗した場合、保持期間内の履歴イベントを再処理することで、データの整合性を回復できます。24時間のデフォルト保持期間は最大1年まで延長可能なため、長期的な監査やコンプライアンス要件にも対応できます。

**新規サービスのオンボーディング**：新しいマイクロサービスをシステムに追加する際、過去のイベントを供給することで、現在の状態を構築できます。これにより、既存システムを停止することなく、新しいコンポーネントをシームレスに統合できます。

#### 既存環境からの移行検討

既存の Custom event bus - classic を利用している場合、新しい event bus への移行パスを検討する必要があります。リリースノートでは、新機能と従来機能の共存が可能であることが示唆されていますが、具体的なマイグレーション手順については、AWS の公式ドキュメントを確認することをお勧めします。

---

### 2. IAM outbound identity federation が VPC エンドポイント経由の OIDC discovery をサポート

AWS IAM の outbound identity federation が、OIDC discovery APIs に対応した VPC エンドポイント機能をサポートしました。これは、厳格なネットワーク分離要件を持つ組織にとって重要な機能追加です。

#### 背景：なぜこの機能が必要だったのか

従来、外部サービスとの連携時には長期的な認証情報（IAM ユーザーのアクセスキーなど）を使用することが一般的でした。しかし、長期認証情報は漏洩リスクが高く、ローテーション管理も煩雑です。

IAM outbound identity federation では、AWS STS から短期的な JWT トークンを取得し、外部サービスがそれを検証する仕組みを提供しています。外部サービスは OIDC discovery エンドポイントで公開されている検証キー（JWKS）を使用してトークンを検証します。

しかし、これまで OIDC discovery エンドポイントはパブリックインターネット経由でのみアクセス可能でした。そのため、以下のような課題がありました：

- **ゼロトラストセキュリティポリシーへの非対応**：インターネットへの出口を完全に塞いでいる VPC 環境では、JWKS を取得できない
- **コンプライアンス要件との不整合**：金融機関やヘルスケア業界など、データの出口管理が厳格な組織では利用が困難
- **ネットワーク監査の複雑化**：パブリックインターネット経由の通信が混在すると、監査証跡の管理が複雑になる

#### VPC エンドポイント対応による改善

今回の機能追加により、AWS PrivateLink を使用して OIDC discovery メタデータと JWKS 検証キーエンドポイントにプライベートアクセスできるようになりました。これにより、トラフィックがパブリックインターネットを経由する必要がなくなります。

**通信フローの変化**：

- **従来**：VPC 内のワークロード → NAT Gateway または Internet Gateway → パブリックインターネット → OIDC discovery エンドポイント
- **新方式**：VPC 内のワークロード → VPC エンドポイント（AWS PrivateLink） → OIDC discovery エンドポイント

すべての通信が AWS のプライベートネットワーク内で完結するため、セキュリティ要件が厳格な環境でも JWT ベースの認証が実現できます。

#### 設定と運用上のポイント

VPC エンドポイントを作成する際には、以下の点に注意が必要です：

- **セキュリティグループの設定**：VPC エンドポイントに適切なセキュリティグループを割り当て、必要な通信のみを許可します
- **CloudTrail によるログ記録**：OIDC discovery エンドポイントへのアクセスを CloudTrail で追跡し、監査証跡として記録できます
- **料金**：AWS PrivateLink の標準料金のみが適用され、この機能自体に追加料金はかかりません

この機能は、すべての商用 AWS リージョン、AWS GovCloud (US)、China リージョンで利用可能です。

---

## SRE 視点での活用ポイント

今回のアップデートを SRE の観点から見ると、**運用の可観測性とセキュリティガバナンスの強化**が際立っています。

**DataSync の監視ダッシュボード**は、複数の拠点から AWS へのデータ移行を行う際に、転送速度や成功率を一元的に監視できるようになりました。これまで CloudWatch でカスタムダッシュボードを構築していた手間が不要になり、失敗したタスクをフィルタリングして即座にエラー詳細を確認できます。定期的なバックアップタスクの SLI（転送成功率、転送速度）を追跡し、SLO に基づいたアラート設計に活用できるでしょう。

**ElastiCache Global Datastore のタグベースアクセス制御**は、マルチリージョン環境での権限管理を大幅に簡素化します。従来は各リージョンごとにリソース ARN を列挙した IAM ポリシーを管理する必要がありましたが、タグベースのポリシーに移行すれば、`Environment:production` タグを持つリソースにのみ本番環境の権限を付与するといった柔軟な制御が可能です。特に、タグの変更が自動的に全リージョンに伝播するため、ポリシーの一貫性を保ちやすくなります。

**AWS DRS の Graviton 対応**は、コスト最適化のために Graviton インスタンスへの移行を進めている組織にとって、ディザスタリカバリの空白を埋める重要な機能です。x86 と Graviton のワークロードを統一的な DRS プロセスで保護できるため、アーキテクチャの異なるインスタンス群を混在させても運用負荷は増えません。復旧テストを定期的に実行し、RPO/RTO の実測値をモニタリングすることで、災害対策の実効性を担保できます。

**IAM outbound identity federation の VPC エンドポイント対応**は、ゼロトラストアーキテクチャを採用している組織で、Lambda や ECS などのサーバーレス・コンテナワークロードから外部 API を呼び出す際のセキュリティ要件を満たします。Terraform で VPC エンドポイントを管理している場合、必要なエンドポイントをコード化してデプロイすることで、ネットワーク設定の再現性が向上します。ただし、VPC エンドポイントの追加により AWS PrivateLink の料金が発生する点は、コスト最適化の観点で事前に評価すべきです。

---

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| **AWS End User Messaging** | WhatsApp 内で音声通話の発信・受信が可能に。チャットから通話へシームレスに移行でき、会話コンテキストを維持 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-voice-calling-whatsapp) |
| **AWS IAM** | outbound identity federation が OIDC discovery APIs 用の VPC エンドポイントをサポート。PrivateLink 経由でプライベートアクセスが可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-sts-vpc-oidc/) |
| **Amazon Transcribe** | カスタマー管理型 KMS キーによる暗号化をサポート。カスタム語彙、語彙フィルター、カスタム言語モデルに対して独自の暗号化キーを指定可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-transcribe/) |
| **AWS Elastic Disaster Recovery** | Graviton ベース（arm64）サーバーのディザスタリカバリに対応。x86 と同じプロセスで Graviton ワークロードを保護・復旧可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/elastic-disaster-recovery-graviton/) |
| **AWS DataSync** | コンソール内に監視ダッシュボードを追加。アカウント全体のデータ転送を一元的に可視化し、ステータス、転送速度、実行時間などを確認可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/datasync-monitoring-dashboard) |
| **AWS Billing and Cost Management** | 新 API「ListBillingViewSegments」を提供。指定期間のアカウント請求コンテキスト（請求階層内の位置付け）を返す | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-billing-and-cost-management-billing-context-api/) |
| **Amazon EventBridge** | 企業規模対応の新しい Custom event bus をリリース。厳密な順序保証、CloudEvents 対応、最大1年の保持期間、Subscriber リソースなどをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/eventbridge-relaunches-custom-event-buses/) |
| **Amazon ElastiCache** | Global Datastore がタグ機能とタグベースアクセス制御に対応。タグ変更が自動的に全リージョンに伝播し、統一的な権限管理とコスト配分が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-elasticache-global-datastore-tagging/) |

---

## まとめ

今回紹介した8件のアップデートは、**エンタープライズグレードの運用基盤強化**という共通のテーマが見えてきます。

EventBridge の Custom event bus 刷新は、マイクロサービスアーキテクチャの本格導入を後押しする機能強化です。順序保証や長期保持といったエンタープライズ要件に対応し、マルチアカウント環境での疎結合なイベント駆動システムの構築が現実的になりました。

セキュリティとコンプライアンスの面では、IAM の VPC エンドポイント対応、Transcribe の KMS 対応、ElastiCache のタグベースアクセス制御が揃い、厳格なネットワーク分離とデータ保護要件を満たす選択肢が増えています。特にゼロトラストアーキテクチャやデータ主権要件への対応が求められる組織にとって、これらの機能は導入検討の価値があります。

運用効率の面では、DataSync の監視ダッシュボードと DRS の Graviton 対応により、大規模なデータ移行やマルチアーキテクチャ環境のディザスタリカバリが管理しやすくなりました。これらは運用の可観測性を高め、SRE チームの負荷軽減に貢献するでしょう。

また、AWS Billing and Cost Management の新 API や End User Messaging の音声通話対応など、エンタープライズ顧客の多様なニーズに応える機能拡張も続いています。これらのアップデートを活用することで、より堅牢で効率的な AWS 環境の構築が可能になります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)