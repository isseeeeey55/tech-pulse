---
title: "【AWS】2026/09/09 のアップデートまとめ"
date: 2026-09-09T08:02:22+09:00
draft: false
tags: ["aws", "aws-transform", "healthomics", "bedrock", "builder-id", "cloudfront", "mwaa", "rds", "mariadb", "guardduty", "govcloud", "airflow", "apache-airflow", "rekognition", "kinesis", "eventbridge", "cloudwatch", "ecs", "lambda", "organizations"]
categories: ["AWS Updates"]
summary: "2026/09/09 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260909/header.png)

# 今回は、直近で発表された8件のAWSアップデートを紹介します

## はじめに

今回は、直近で発表された8件のAWSアップデートを紹介します。AWS GovCloudリージョンでのサービス拡充、生命科学分野でのワークフロー最適化、セキュリティ機能の強化など、多岐にわたるアップデートが含まれています。なかでも、AWS TransformとAmazon MWAA ServerlessがAWS GovCloud (US)リージョンで利用可能になったことで、政府機関や規制対象の組織がより広範なAWSサービスを活用できるようになった点です。また、Amazon GuardDutyのCustom Detection Rules、Amazon Bedrock AgentCore MemoryのIngestData API、CloudFrontのDynamic Image Transformationの新機能なども含まれます。

本記事では、これらのアップデートの中から特に運用面でのインパクトが大きいものを深掘りし、SREの視点での活用ポイントを解説していきます。

## 注目アップデート深掘り

### Amazon GuardDuty のカスタム検出ルール

Amazon GuardDutyに追加された**Custom Detection Rules**は、CloudTrailの管理イベントに対する脅威検出をより柔軟に制御できる機能です。35個の事前構築されたオプトイン型ルールライブラリが提供され、26種類のユニークな検出タイプをカバーしています。

この機能が重要な理由は、**環境によって脅威の意味が異なる活動に対応できる**点にあります。例えば、AMIの外部共有、VPCフローログの無効化、MFAなしでのサインインといった活動は、本番環境では明確なセキュリティリスクですが、開発環境やサンドボックス環境では正常な運用手順の一部である場合があります。Custom Detection Rules では、こうした活動が想定外となる環境でだけ検出を有効化できます。

すべてのルールは**10のMITRE ATT&CK®戦術にマッピング**されており、組織のセキュリティフレームワークと整合性を取りやすい設計になっています。

特筆すべきは**ドライランモード**の存在です。ルールをドライランモードで有効化し、本番運用前に検出の有効性を評価できます。

また、GuardDutyが**ログの取得、正規化、保存といった重い処理を不要にしている**点も運用上のメリットです。ルールは GuardDuty のコンソールまたは API から参照できます。すべての AWS 商用リージョンと AWS GovCloud (US) リージョンで利用できます。

### Amazon Bedrock AgentCore Memory の直接取り込み機能

Amazon Bedrock AgentCore Memoryに追加された**IngestData API**は、エージェントの記憶管理アーキテクチャに大きな変化をもたらす機能です。従来、すべてのコンテンツは短期メモリイベントとして保存される必要がありましたが、新APIにより**長期メモリへの直接取り込み**が可能になりました。

これにより、短期メモリとは独立して長期メモリを使えるようになりました。

IngestData APIは**2種類のペイロード形式**に対応しています。1つ目は会話ペイロードで、USER/ASSISTANTロールを持つメッセージを含みます。2つ目はJSONペイロードで、行動イベント、アクティビティログ、システムイベントなどの構造化データを扱います。これにより、会話ログとシステムイベントを混在させた複雑なエージェント記憶管理が実現できます。

取り込んだ内容は、CreateEvent と同じ抽出パイプラインを通り、設定済みの長期メモリ戦略に送られます。失敗した抽出は `ListMemoryExtractionJobs` で再実行（redrive）できます。

抽出結果は `ListMemoryRecords` や `RetrieveMemoryRecords` で確認でき、Kinesis ストリーミングによるリアルタイム通知も利用できます。オプションのメタデータも抽出パイプラインに渡せます。

### Amazon RDS for MariaDB の量子耐性暗号化対応

Amazon RDS for MariaDBが最新のコミュニティマイナーバージョン（10.6.28、10.11.19、11.4.13、11.8.9、12.3.3）をサポートし、**量子耐性TLS（PQ-TLS）鍵交換**が利用可能になりました。これは量子コンピュータによる将来的な暗号解読リスクに備える重要なセキュリティ強化です。

量子耐性暗号化の重要性は、「Store Now, Decrypt Later（今保存して、後で解読する）」攻撃に対する防御にあります。この攻撃手法では、攻撃者が現在の暗号化通信を記録しておき、将来の量子コンピュータで解読するというシナリオが想定されています。金融機関や医療機関など、長期間のデータ保護が求められる業界では、今から対策を講じる必要があります。

RDS for MariaDBでは、**3つのアップグレード方式**が提供されています。1つ目は**RDS Blue/Greenデプロイメント**で、本番環境と同一構成のGreen環境を作成し、検証後にトラフィックを切り替えることで、ダウンタイムを最小化できます。2つ目は**インプレースアップグレード**、3つ目は**スナップショットからの復元**です。

大規模運用では、**自動マイナーバージョンアップグレード**を有効にし、**AWS Organizations Upgrade Rollout Policy**でクラスターのアップグレードを段階的に進められます。

告知は、旧バージョンの CVE の修正や、MariaDB コミュニティによるバグ修正・性能改善を取り込むため、新しいマイナーバージョンへのアップグレードを推奨しています。

## SRE視点での活用ポイント

### セキュリティとコンプライアンスの自動化

GuardDuty の Custom Detection Rules では、アカウントごとに有効にするルールを選べます。たとえば AMI の外部共有が日常的な開発アカウントでは無効のまま、本番アカウントでのみ有効化する、といった使い分けができます。

ドライランモードで一定期間の検出状況を確認してから本番で有効化すれば、誤検知によるアラート負荷を事前に確かめられます。

検出結果は MITRE ATT&CK の10戦術にマッピングされているため、既存のランブックの分類と対応付けやすくなっています。

### エージェントシステムの知識管理最適化

Bedrock AgentCore Memory の IngestData API により、会話以外の構造化データ（行動イベント、アクティビティログ、システムイベント）も、短期メモリを経由せずに長期メモリへ送れます。

短期メモリと長期メモリを独立して運用できるため、**リアルタイムの対話セッション（短期）と組織の知識ベース（長期）を分離**して管理できます。これにより、セッション終了後も重要な知見だけを長期メモリに保存し、エージェントの知識を段階的に蓄積する運用が可能になります。

失敗した抽出は `ListMemoryExtractionJobs` で再実行できるため、取り込みの失敗時の運用手順に組み込めます。

### データベースアップグレードのリスク管理

RDS for MariaDBのアップグレード運用では、**Blue/Greenデプロイメントを活用したリスク最小化**が鍵となります。本番環境でBlue環境を稼働させながら、新バージョンのGreen環境で性能テストと結合テストを実施し、問題がなければ切り替える、というフローを標準化できます。

自動マイナーバージョンアップグレードを有効化する場合は、メンテナンスウィンドウをトラフィックの少ない時間帯に設定します。

AWS Organizations Upgrade Rollout Policyを使用すれば、**複数アカウントでの段階的ロールアウト**が可能です。開発 → ステージング → 本番の順に展開し、各段階で問題がないことを確認してから次に進められます。

PQ-TLS 鍵交換は、長期間の機密性が必要なデータを扱う環境ほど検討する意義があります。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Transform が AWS GovCloud (US-West) で利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-transform-govcloud-us-west/) | 政府機関や規制対象組織が、VMware、ベアメタル、Hyper-V、データベースワークロードの大規模マイグレーションを GovCloud 環境で実行可能に。サーバーのレプリケーションとカットオーバーを自動化。 |
| [AWS HealthOmics が WDL ワークフローにリソースフォールバック機能を追加](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-healthomics-resourcefallback-wdl/) | WDL ワークフローのタスクで、優先するアクセラレータの種類を順序付きで指定可能に（CPU インスタンスへのフォールバックも可）。利用不可の場合は自動的に代替リソースにフォールバックし、診断とリサブミットの時間を削減。各アクセラレータプロファイルにタイムアウトを設定可能。 |
| [Amazon Bedrock AgentCore Memory が長期メモリへの直接取り込みをサポート](https://aws.amazon.com/about-aws/whats-new/2026/09/agentcore-memory-direct-ingest) | 新しい IngestData API により、短期メモリを経由せずにコンテンツを直接長期メモリに送信可能に。会話ペイロードと JSON ペイロード（行動イベント、アクティビティログ、システムイベント）の両方に対応。 |
| [AWS Builder ID に復旧オプションと MFA サポートを追加](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-builder-id-recovery-mfa-third-party/) | 回復用メールアドレスの登録とセルフサービス復旧オプションを追加。Google、Apple、GitHub、Amazon のサードパーティログインでも MFA デバイスを登録可能に。アカウント復旧とセキュリティを強化。 |
| [CloudFront Dynamic Image Transformation に4つの新機能](https://aws.amazon.com/about-aws/whats-new/2026/08/dynamic-image-transfromation-adds-new-features/) | カスタムラベル検出を組み込んだスマートクロッピング、デバイス最適化された自動画像最適化、変換テスト用プレイグラウンド、ECS と Lambda の完全機能パリティを追加。未最適化トラフィック約30%を含むすべてのデバイスへの配信を改善。 |
| [Amazon MWAA Serverless が AWS GovCloud (US) で利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-mwaa-serverless-aws-govcloud/) | Apache Airflow のサーバーレスオプションが GovCloud（US-East、US-West）で利用可能に。ワークフローの実行時間に対してのみ課金する従量課金モデル。 |
| [Amazon RDS for MariaDB が最新マイナーバージョンをサポート](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-mariadb-community-versions/) | コミュニティ版 MariaDB の 10.6.28、10.11.19、11.4.13、11.8.9、12.3.3 をサポート。量子耐性 TLS（PQ-TLS）鍵交換に対応し、セキュリティパッチとパフォーマンス改善を含む。Blue/Green デプロイメントや Organizations Upgrade Rollout Policy で段階的アップグレードが可能。 |
| [Amazon GuardDuty が Custom Detection Rules を提供](https://aws.amazon.com/about-aws/whats-new/2026/09/guardduty-optional-detection-rules/) | 35個の事前構築オプトイン型ルールライブラリを提供。CloudTrail 管理イベントに対する脅威検出を拡張し、26種類の検出タイプと10の MITRE ATT&CK 戦術をカバー。環境ごとに必要なルールだけを有効化可能で、ドライランモードで検出効果を評価できる。 |

## まとめ

今回の8件には、**AWS GovCloud でのサービス拡充**、**生命科学・AI 分野の機能追加**、**セキュリティ機能の強化**が含まれます。

AWS TransformとMWAA ServerlessがGovCloudリージョンで利用可能になったことで、政府機関や規制対象組織が最新のクラウド技術を活用できる範囲が広がりました。MWAA Serverless は、ワークフローの実行時間に対してのみ課金される従量課金モデルです。

HealthOmics のリソースフォールバックは、優先するアクセラレータが使えないときに自動で代替リソース（CPU を含む）に切り替え、ワークフローの再投入を減らします。Bedrock AgentCore Memory の IngestData API は、短期メモリを経由せずに長期メモリへ直接取り込めるようにします。

GuardDutyのカスタム検出ルールとRDS for MariaDBの量子耐性暗号化は、**将来のセキュリティリスクへの備え**という点で重要です。

CloudFrontの画像最適化機能は、グローバル配信の品質とコストの両面で改善をもたらします。デバイス分類とClient Hintsの組み合わせにより、これまでブラウザの対応状況の差で最適化されずに配信されていた約30%のトラフィックにも、最適化が及ぶようになりました。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)