---
title: "【AWS】2026/05/16 のアップデートまとめ"
date: 2026-05-16T08:02:08+09:00
draft: false
tags: ["aws", "emr", "organizations", "connect", "cloudfront", "grafana", "rds", "postgresql", "ec2"]
categories: ["AWS Updates"]
summary: "2026/05/16 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260516/header.png)

# 2026年5月16日 AWS アップデート解説

## はじめに

2026年5月16日は、AWS全体で8件のアップデートが発表されました。特に注目すべきは、新しいマルチクラウド接続サービス「AWS Interconnect」のプレビュー公開と、Amazon EC2 M3 Ultra Macインスタンスの一般提供開始です。また、AWS Organizationsの管理機能強化やAmazon CloudFrontのセキュリティ機能追加など、エンタープライズ運用に関わる重要な改善も含まれています。本記事では、これらのアップデートの中から特に技術的に深掘りする価値のある項目を取り上げ、SRE視点での活用方法を解説します。

---

## 注目アップデート深掘り

### AWS Interconnect：マルチクラウド接続の新標準

AWSが業界初となるマルチクラウド専用接続サービス「AWS Interconnect」をプレビュー公開しました。これはOracle Cloud Infrastructure（OCI）との間にプライベートで堅牢な接続を簡単にプロビジョニングできるサービスです。

#### なぜこのアップデートが重要なのか

従来、複数のクラウドプロバイダー間でワークロードを接続する場合、企業は自前で複雑なマルチレイヤーネットワークを構築・管理する必要がありました。VPN接続やハイブリッド接続を組み合わせることで実現できましたが、運用負荷が高く、セキュリティやパフォーマンスの面でも課題がありました。

AWS Interconnectは、クラウド同士が「話す」ための標準化された方法を提供することで、この課題を解決します。現在はOCI（プレビュー）とGoogle Cloud（既に利用可能）に対応しており、Microsoft Azureも2026年後半に対応予定です。

#### 利用方法と検証ポイント

現在、us-east-1（バージニア北部）リージョンでプレビュー提供が開始されており、AWS Management Console、CLI、APIから利用できます。

接続を確立する際の主な検証ポイントは以下の通りです：

1. **接続のプロビジョニング手順の確認**：AWS Management Consoleからどのような手順でOCI接続を設定するか、必要なパラメータや認証情報を整理する
2. **ネットワークパフォーマンス測定**：AWS ↔ OCI間でのレイテンシーとスループットを実測し、従来のVPN接続と比較する
3. **セキュリティ設定の検証**：プライベート接続であることの確認と、セキュリティグループやネットワークACLとの統合方法を確認する

従来の「VPN + ハイブリッド接続」と比較した場合、AWS Interconnectではセットアップ時間の短縮、運用複雑度の低減、セキュリティの向上が期待できます。特にマルチクラウド戦略を採用している企業にとっては、ベンダーロックインを回避しながら技術選定の自由度を確保できる点が大きなメリットです。

---

### AWS Organizations SCP クォータの大幅引き上げ

AWS OrganizationsのService Control Policies（SCP）のクォータが大幅に引き上げられました。1つのノード（ルート、OU、またはアカウント）に設定できるSCPの最大数が5個から10個へ、SCPの最大サイズが5,120文字から10,240文字へと倍増しています。

#### なぜこのアップデートが重要なのか

大規模なAWS組織では、複数の部門ごとに異なるセキュリティポリシーを適用する必要があります。従来の5個という制限では、規制要件ごと（PCI-DSS、HIPAAなど）や環境ステージ別（開発、ステージング、本番）のきめ細かなアクセス制御を実装する際に制約となっていました。

今回のクォータ引き上げにより、より細かい粒度の権限制御と条件分岐を含むポリシーを記述でき、組織全体にわたってより包括的なセキュリティ管理を実現できます。

#### 従来の方法との比較

**ビフォー（旧クォータ）：**
- 最大5個のSCPを組み合わせて複雑なポリシーを表現
- 5,120文字の制限により、複雑な条件分岐を含むポリシーが記述困難
- リソースタイプごと、リージョンごとの制御を1つのSCPに統合する必要があり、可読性が低下

**アフター（新クォータ）：**
- 最大10個のSCPで役割ごとに分割管理可能
- 10,240文字により、詳細な条件分岐やタグベースのアクセス制御を実装可能
- セキュリティポリシーを段階的に適用でき、管理性と監査性が向上

#### 実装例の考え方

新しいクォータを活用することで、以下のようなSCP分割戦略が可能になります：

- **SCP 1**: リージョン制限ポリシー
- **SCP 2**: PCI-DSS準拠ポリシー
- **SCP 3**: HIPAA準拠ポリシー
- **SCP 4**: 開発環境向け制限ポリシー
- **SCP 5**: 本番環境向け厳格ポリシー
- **SCP 6**: タグベースのアクセス制御ポリシー
- **SCP 7**: コスト最適化のためのリソース制限ポリシー
- **SCP 8**: データ保護関連ポリシー
- **SCP 9**: ネットワークセキュリティポリシー
- **SCP 10**: 監査ログ保護ポリシー

このアップデートはすべての商用AWSリージョン、AWS GovCloud（US）リージョン、中国リージョンで自動的に利用可能になり、ユーザー側での手動設定は不要です。

---

### Amazon CloudFront mTLS の OCSP 失効確認対応

Amazon CloudFrontが、Viewer向けのMutual TLS（mTLS）に対してOCSP（Online Certificate Status Protocol）による証明書失効確認機能をサポートしました。これにより、クライアント証明書の失効状態をリアルタイムで検証してから接続を確立できるようになります。

#### 従来の方法との違い

**従来の方法：**
従来は、CloudFront FunctionsとKeyValueStoreを使用して静的な失効リストを管理していました。この方式では、失効リストの更新に手動オペレーションが必要で、リアルタイム性に欠けるという課題がありました。

**新しい方法：**
OCSP対応により、接続時に証明書に埋め込まれたレスポンダURLを自動的にクエリし、認証局から直接失効状態を確認できます。CloudFrontはOCSPレスポンスを最大30分間キャッシュするため、レイテンシへの影響を最小限に抑えます。

#### 実装上のポイント

OCSP結果はConnection Function内で利用でき、以下のようなカスタムロジックの実装が可能です：

- **証明書ローテーションのグレースピリオド設定**：新旧証明書の両方を一定期間有効として扱うことで、無停止での証明書切り替えを実現
- **IP基準の例外処理**：特定のIPアドレス帯からのアクセスに対して異なる検証ルールを適用
- **ログと監査証跡の取得**：失効確認の結果をログに記録し、コンプライアンス監査に対応

追加料金は不要で、金融機関や医療機関など規制業界での厳格な証明書管理要件への対応、ゼロトラスト・アーキテクチャの実装時のクライアント証明書検証、IoTデバイスの認証・認可フローに証明書失効確認を組み込む、といったユースケースで活用できます。

---

## SRE視点での活用ポイント

### AWS Interconnectの運用改善シナリオ

AWS Interconnectは、マルチクラウド戦略を採用する組織において、運用負荷を大幅に軽減できる可能性があります。従来のVPN接続では、各クラウド間の接続ごとに個別の設定と監視が必要でしたが、AWS Interconnectを使うことで、AWS Management Consoleから一元的に管理できるようになります。

Terraformでインフラを管理している場合、AWS Interconnectのリソース定義を追加することで、マルチクラウド接続の構成管理をコード化できます。CloudWatchアラームと組み合わせることで、接続状態の監視やレイテンシーの異常検知を自動化し、障害対応のランブックに組み込むことで、オンコール対応の効率化が期待できます。

導入時の判断基準としては、現在のマルチクラウド接続の運用コスト、セキュリティ要件、パフォーマンス要件を総合的に評価する必要があります。プレビュー期間中は利用可能リージョンが限定されているため、本番環境への適用は一般提供後に検討するのが安全です。

### AWS Organizations SCP クォータ引き上げの活用

大規模な組織でTerraformやAWS CloudFormationを使ってSCPを管理している場合、新しいクォータを活用することで、より細かい粒度でのポリシー分割が可能になります。これにより、変更管理の粒度が細かくなり、特定のポリシーだけを更新する際の影響範囲を最小化できます。

セキュリティ監査の観点では、SCPをカテゴリごとに分割することで、監査ログの追跡が容易になります。たとえば、データ保護関連のポリシー変更と、コスト最適化のためのリソース制限ポリシー変更を別々のSCPとして管理することで、変更履歴の追跡とレビューが効率化されます。

注意点としては、SCPの数が増えることで、全体のポリシー評価が複雑になる可能性があります。SCPは継承されるため、階層構造全体でどのポリシーが適用されているかを可視化するツールやダッシュボードの整備が重要です。

### CloudFront mTLS OCSP対応の実運用

金融機関やヘルスケア業界など、厳格なセキュリティ要件が求められる環境では、クライアント証明書の失効確認が必須要件となることがあります。OCSP対応により、KeyValueStoreを手動更新する運用負荷から解放され、リアルタイムでの失効確認が実現できます。

CloudWatch Logsと連携することで、失効確認の成功・失敗をメトリクスとして収集し、異常な失効確認失敗率をアラート通知することで、セキュリティインシデントの早期検知につなげることができます。

導入時には、認証局のOCSPレスポンダの可用性と応答時間を事前に評価することが重要です。CloudFrontが最大30分間OCSPレスポンスをキャッシュすることを考慮し、失効証明書が実際にブロックされるまでのタイムラグを許容できるかを確認する必要があります。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon EMR Serverless is now available in additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-emr-serverless-aws-regions/) | アジア太平洋地域（ハイデラバード、マレーシア、ニュージーランド、台北、タイ）およびメキシコ（中央）の6つの新しいリージョンでEMR Serverlessが利用可能に。クラスタ管理不要でApache SparkやHiveアプリケーションを実行できるサーバーレス型データ分析ソリューション |
| 2 | [AWS announces AWS Interconnect - multicloud connectivity with Oracle Cloud Infrastructure in preview](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-announces-AWS-interconnect-multicloud-oci-preview/) | 業界初のマルチクラウド専用接続サービスをプレビュー公開。OCIとの間にプライベートで堅牢な接続を簡単にプロビジョニング可能。Google Cloudは既に対応、Microsoft Azureは2026年後半に対応予定 |
| 3 | [AWS Organizations now supports higher quotas for service control policies (SCPs)](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-organizations-increased-scp-quotas/) | SCPの最大添付数が5個から10個へ、最大サイズが5,120文字から10,240文字へ倍増。より細かい粒度の権限制御と複雑な条件分岐を実装可能に |
| 4 | [Amazon Connect Cases now lets you edit related items and delete cases from the agent workspace](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-connect-cases-related-item/) | エージェントがワークスペースから直接、関連アイテムの編集・削除、ケース自体の削除が可能に。コメント更新、誤ってリンクされた連絡先の解除、注文・返品といったカスタム関連アイテムの管理に対応 |
| 5 | [Amazon Managed Grafana now supports in-place upgrade to Grafana version 12.4](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-managed-grafana-v12-update/) | Grafanaバージョン10.4から12.4へのインプレースアップグレードに対応。Grafana Scenesによる高速レンダリング、クエリレスDrilldownアプリ、CloudWatchプラグイン強化（PPL/SQLクエリ、クロスアカウントMetrics Insights、ログ異常検知）を搭載 |
| 6 | [Amazon RDS for PostgreSQL announces Extended Support minor versions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-rds-postgresql-extended-support/) | PostgreSQL 11、12、13のExtended Support新マイナーバージョンをリリース。既知のセキュリティ脆弱性とバグ修正を含み、標準サポート終了後も最大3年間のサポートを提供 |
| 7 | [Amazon CloudFront announces support for OCSP Revocation for Mutual TLS (Viewer)](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-cloudfront-mtls-ocsp/) | Viewer向けmTLSにOCSPによる証明書失効確認機能を追加。接続時に認証局から直接失効状態を確認可能に。OCSPレスポンスを最大30分間キャッシュし、レイテンシへの影響を最小化 |
| 8 | [Announcing general availability of Amazon EC2 M3 Ultra Mac instances](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-m3-ultra-mac-instances-generally-available/) | Apple M3 Ultra Mac Studio搭載の次世代Macインスタンスが一般提供開始。28コアCPU、60コアGPU、32コアNeural Engine、256GBメモリで、前世代M4 Maxと比較してメモリ2倍、CPU 1.75倍、GPU 1.5倍、Neural Engine 2倍の性能向上 |

---

## まとめ

2026年5月16日のアップデートは、マルチクラウド戦略の推進、大規模組織のガバナンス強化、開発者体験の向上という3つの方向性が明確に示されました。

特にAWS Interconnectは、マルチクラウド環境の運用を標準化・簡素化する試みとして注目すべきアップデートです。現在はプレビュー段階ですが、今後AzureやGoogle Cloudとの連携が強化されることで、クラウドベンダーに依存しない柔軟なアーキテクチャ設計が可能になります。

AWS OrganizationsのSCPクォータ引き上げは、エンタープライズ向けのガバナンス機能の成熟を示しており、大規模組織でのAWS採用がさらに加速する可能性があります。CloudFrontのmTLS OCSP対応も、ゼロトラスト・アーキテクチャの実装において重要な一歩です。

Amazon Managed GrafanaやAmazon EC2 M3 Ultra Macインスタンスは、開発者とSREの体験向上を目的としたアップデートであり、観測性の向上とAppleプラットフォーム開発の効率化に貢献します。

これらのアップデートを活用することで、セキュリティ、運用効率、開発生産性のすべてにおいて、より高度なクラウド活用が可能になります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)