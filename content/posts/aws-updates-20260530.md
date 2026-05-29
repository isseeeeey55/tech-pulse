---
title: "【AWS】2026/05/30 のアップデートまとめ"
date: 2026-05-30T08:02:06+09:00
draft: false
tags: ["aws", "shield", "rds", "oracle", "redshift", "connect", "s3", "cloudwatch", "firehose", "pinpoint", "direct-connect"]
categories: ["AWS Updates"]
summary: "2026/05/30 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260530/header.png)

# 2026年5月30日 AWS アップデート解説

## はじめに

2026年5月30日、AWSは8件のアップデートを発表しました。本日の注目ポイントは、**AWS Shield AdvancedにDDoS攻撃フローログ機能が追加**されたこと、および**AWS End User MessagingのRCS for Businessが20ヶ国に拡大**したことです。セキュリティ強化とグローバルコミュニケーション基盤の拡充が同時に進められており、エンタープライズ企業のクラウド活用をさらに後押しする内容となっています。また、Oracle Database@AWSが20リージョンに拡大するなど、データベース関連の地域展開も加速しています。

---

## 注目アップデート深掘り

### AWS Shield Advanced の DDoS 攻撃フローログ機能

#### なぜこのアップデートが重要なのか

DDoS攻撃は現代のクラウドインフラにおける最も深刻な脅威の一つです。従来、AWS Shield Advancedは攻撃の検知と自動的な緩和を提供していましたが、攻撃の詳細な分析には限界がありました。今回追加された**DDoS攻撃フローログ機能**により、パケットレベルでの攻撃トラフィックの可視化が実現し、事後分析、コンプライアンス対応、そして将来の防御戦略策定に不可欠なデータが得られるようになりました。

ログには送信元IP、宛先IP、ポート番号、プロトコル、パケット数、バイト数、送信元国情報といった豊富なメタデータが含まれており、攻撃の全体像を把握できます。これらのデータは**Amazon S3**、**Amazon CloudWatch Logs**、または**Amazon Data Firehose**に5分間隔で自動送信されるため、リアルタイムに近い形で攻撃状況を追跡できます。

#### 有効化の流れとログの内容

公式アナウンスによれば、フローログを利用するには、対象リソースを Shield Advanced で保護したうえで、配信先に応じたログ配信を構成します。アクティブな攻撃が発生している間、ログは選択した宛先へ **5分間隔** で自動的に配信されます。

ログには、パケットレベルの詳細情報として以下が含まれるとされています。

- 送信元・宛先の IP アドレス
- 送信元・宛先のポート
- プロトコル
- パケット数・バイト数
- 送信元の国情報 など

> **Note:** 本記事執筆時点で、公式アナウンスにはログフィールドの完全なスキーマや有効化用の CLI/API の詳細までは記載されていません。正確なログフォーマットと設定手順は[AWS公式ドキュメント](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html)を参照してください。

#### ログの分析基盤

配信先によって分析方法を選べる点がこの機能の利点です。**Amazon CloudWatch Logs** に配信すれば Logs Insights でインタラクティブにクエリでき、**Amazon S3** に蓄積すれば Amazon Athena による SQL 分析やコスト効率の良い長期保管が可能です。**Amazon Data Firehose** を経由すれば、OpenSearch や任意のデータレイクへストリーミングし、既存の分析パイプラインに統合できます。

たとえば「送信元の国別トラフィック量」「プロトコル別のパケット数の推移」といった切り口で集計すれば、攻撃元の地理的分布や攻撃手法の傾向を把握できます。具体的なクエリやテーブル定義は、確定したログスキーマに合わせて組み立ててください。

#### 従来の方法との比較

従来のShield Advancedでは、攻撃イベントの概要（攻撃開始時刻、影響を受けたリソース、緩和状況）は確認できましたが、具体的な攻撃元や攻撃手法の詳細は限定的でした。フローログ機能により、以下が可能になります。

- **攻撃元の地理的分布の把握**：どの国・地域からの攻撃が多いかを定量化
- **攻撃パターンの分類**：SYN Flood、UDP Amplification、HTTP Floodなどの判別
- **ボットネット分析**：送信元IPの多様性から分散攻撃の規模を推定
- **コンプライアンス対応**：金融・医療業界で求められる詳細な監査証跡の保持

---

### AWS End User Messaging RCS for Business の対応国拡大

#### なぜこのアップデートが重要なのか

従来のSMSは文字数制限があり、画像やボタンといったリッチコンテンツを送信できませんでした。**RCS（Rich Communication Services）**はSMSの進化版として、画像、動画、位置情報、カルーセル、アクションボタンなどを含むリッチメッセージを送信でき、かつ企業側のブランド認証により、なりすましや詐欺メッセージのリスクを大幅に低減します。

今回、**オーストリア、ブラジル、コロンビア、チェコ、デンマーク、ドミニカ共和国、フランス、ドイツ、グアテマラ、イタリア、メキシコ、オランダ、ノルウェー、ペルー、ポーランド、シンガポール、スロバキア、スペイン、スウェーデン、イギリス**の20ヶ国が追加され、既存のアメリカ・カナダと合わせて合計22ヶ国での展開となりました。これにより、グローバルに展開するEC、金融、ヘルスケア、物流企業が、統一的なカスタマーコミュニケーション基盤を構築できるようになります。

#### 実装の具体例

既存の`SendTextMessage` APIをそのまま使用でき、アプリケーションの変更は不要です。RCS対応端末には自動的にRCSメッセージが送信され、非対応端末にはSMSにフォールバックされます。

以下はAWS SDK for Python (Boto3) を使った送信例です。

```python
import boto3

client = boto3.client('pinpoint-sms-voice-v2', region_name='us-east-1')

response = client.send_text_message(
    DestinationPhoneNumber='+4412345678901',  # イギリス
    OriginationIdentity='arn:aws:sms-voice:us-east-1:123456789012:phone-number/+12025551234',
    MessageBody='Your order #12345 has been shipped! Track here: https://example.com/track',
    MessageType='TRANSACTIONAL',
)

print(response['MessageId'])
```

公式アナウンスでも「既存の SendTextMessage API でアプリケーションの変更なしに送信できる」と明言されており、RCS非対応端末の場合は上記コードのままSMS送信にフォールバックします。追加の条件分岐やエラーハンドリングは不要です。

#### RCS vs SMS vs Push Notification 比較

| 機能 | RCS | SMS | Push Notification |
|------|-----|-----|-------------------|
| リッチメディア対応 | ○（画像、動画、カルーセル等） | × | ○ |
| ブランド認証 | ○ | × | ○（アプリ内） |
| アプリインストール不要 | ○ | ○ | × |
| 配信確実性 | ○（SMSフォールバック） | ○ | △（通知OFF可能） |
| 双方向コミュニケーション | ○ | △ | ○ |
| クロスプラットフォーム | ○ | ○ | △（OS依存） |

#### 対応国拡大による料金インパクト

RCSの料金はSMSよりも高めですが、エンゲージメント率の向上により総コストが下がるケースもあります。送信先国によって料金が異なるため、主要地域での比較が重要です。

> **Note:** 料金詳細は[AWS Pricing Calculator](https://calculator.aws/)および公式ドキュメントで確認してください。送信先国ごとに異なる価格体系が適用されます。

---

## SRE視点での活用ポイント

### DDoS攻撃フローログのSRE活用シナリオ

SRE業務において、DDoS攻撃は「予測できないが備えるべき」障害の典型例です。フローログ機能は、単なる事後分析だけでなく、**継続的な改善活動の基盤**として活用できます。

たとえば、週次のポストモーテム会議で攻撃パターンのトレンド分析を行い、特定地域からの攻撃が増加している場合はWAFルールを強化する判断材料にできます。また、CloudWatch Logs に配信したログにメトリクスフィルターを設定すれば、一定の閾値を超えるトラフィックを検知してアラート化でき、攻撃の初期段階でオンコール担当者に通知して迅速なエスカレーションにつなげられます。Infrastructure as Code で運用している場合は、ログ配信先（S3バケットや CloudWatch ロググループ）の構成もコード化して一元管理するとよいでしょう。配信設定に対応するリソースは、利用する IaC ツールの対応状況に合わせて確認してください。

コスト面では、ログストレージとクエリコストが追加で発生します。アクティブな攻撃時には5分間隔でログが配信されるため、大規模な攻撃ではデータ量が増大する可能性があります。S3ライフサイクルポリシーで古いログを低頻度アクセス階層やアーカイブ階層へ移行するなど、保管コストを抑える設計が推奨されます。

### RCS for Business の運用改善ポイント

グローバル展開しているSaaSやECサイトでは、複数の通知チャネル（メール、SMS、Push通知）を併用していますが、それぞれのエンゲージメント率や到達率のモニタリングが煩雑になりがちです。RCSの導入により、統一的なメッセージング基盤を構築しつつ、CloudWatchメトリクスで送信成功率やフォールバック率を可視化できます。

特に、ワンタイムパスワード（OTP）や決済通知のような重要な通知では、RCSのブランド認証機能が信頼性向上に寄与します。フィッシング対策として、エンドユーザーが「この通知は正規の企業から送られている」と視覚的に判断できるため、カスタマーサポートへの問い合わせ削減も期待できます。

導入時の判断基準としては、以下を検討すべきです。

- **対象顧客の地理的分布**：今回対応した22ヶ国にユーザーが集中しているか
- **RCS対応端末の普及率**：主要市場でのAndroid/iOS比率とRCS対応状況
- **既存SMS基盤との互換性**：既存のSendTextMessage APIをそのまま活用できるため、移行コストは最小限
- **コンプライアンス要件**：金融業界など、送信者認証が規制要件になっている場合は導入効果が大きい

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Redshift Serverless now offers 4-RPU Minimum Capacity in 7 additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-redshift-serverless-4-rpu-seven-regions/) | Redshift Serverless の最小容量4 RPUが7つの追加リージョンで利用可能に |
| 2 | [AWS End User Messaging RCS for Business now available in 20 additional countries](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-rcs-countries/) | RCS for Businessが20ヶ国追加、合計22ヶ国に拡大。既存APIで利用可能、SMS自動フォールバック対応 |
| 3 | [AWS Interconnect - multicloud now offers a free 500 Mbps tier](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-interconnect-multicloud-offers-free-500-mbps-tier) | AWS Interconnect - multicloud に無料500 Mbpsティアが追加。月間約160TBのデータ転送に対応し、CloudWatch Network Synthetic Monitor も無料で利用可能 |
| 4 | [Oracle Database@AWS is now available in twenty AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/oracle-database-aws-available-twenty-regions/) | Oracle Database@AWS が8つの新リージョンで利用可能になり、合計20リージョンに拡大。チューリッヒ、ミラノ、パリ、大阪、シンガポール、メルボルン、サンパウロなどが追加 |
| 5 | [Amazon RDS for Oracle now supports April 2026 Release Update and Supplemental Patch Bundle](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-rds-oracle-supports-april-2026-release-update-supplemental-patch-bundle) | RDS for Oracle が2026年4月リリースアップデートに対応。Oracle Database 19c/21c でセキュリティパッチを提供。Supplemental Patch Bundle（旧Oracle Spatial Patch Bundle）に名称変更 |
| 6 | [Amazon Connect Customer now supports scheduling tasks up to 90 days in advance](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-connect-customer-tasks-90day-schedule) | Amazon Connect でタスク予約期間が最大90日に延長。StartTaskContact API、フロー、エージェントワークスペースから予約可能 |
| 7 | [AWS Shield Advanced introduces DDoS attack flow logs](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-shield-ddos/) | Shield Advanced にDDoS攻撃フローログ機能が追加。パケットレベルの詳細情報をS3、CloudWatch Logs、Data Firehose に5分間隔で送信 |
| 8 | [Amazon S3 Tables are now available in two additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-s3-tables-aws-regions/) | S3 Tables が台北およびニュージーランドリージョンで利用可能に。Apache Iceberg ネイティブサポートで自動テーブルメンテナンスを提供 |

---

## まとめ

本日のアップデートは、**セキュリティ強化**（Shield Advanced フローログ）、**グローバルコミュニケーション基盤の拡充**（RCS for Business 20ヶ国追加）、**マルチクラウド接続の民主化**（Interconnect - multicloud 無料ティア）、**データベース地域展開の加速**（Oracle Database@AWS 20リージョン）と、幅広い分野をカバーしています。

特にSRE・DevOpsエンジニアにとって、Shield Advancedのフローログは事後分析だけでなく予防的な改善活動の基盤として価値が高く、RCS for Businessはグローバル展開における顧客コミュニケーションの品質向上に直結します。また、Interconnect - multicloud の無料ティアは、マルチクラウド戦略の検証コストを大幅に削減し、より柔軟なクラウド選択を可能にします。

引き続き、各アップデートの詳細はAWS公式ドキュメントで確認し、自社の運用要件に合わせて導入を検討していくことをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)