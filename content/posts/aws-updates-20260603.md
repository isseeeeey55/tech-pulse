---
title: "【AWS】2026/06/03 のアップデートまとめ"
date: 2026-06-03T08:02:24+09:00
draft: false
tags: ["aws", "location-service", "config", "security-hub", "deadline-cloud", "sagemaker", "cur", "athena", "redshift", "elasticache", "valkey", "rds", "sql-server", "license-manager", "healthomics"]
categories: ["AWS Updates"]
summary: "2026/06/03 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260603/header.png)

# 2026年6月3日 AWS アップデート解説

## はじめに

2026年6月3日のまとめとして、直近で発表されたAWSの9件のアップデートを解説します。本日の注目ポイントは、**Amazon Location ServiceがTransit/Intermodalルーティングに対応**し、公共交通機関を含む複雑な移動計画が可能になったこと、**AWS Configが内部サービスリンク規則をサポート**してセキュリティハブなどのサービスが独立してコンプライアンス評価を実施できるようになったこと、そして**ElastiCache for Valkeyに耐久性機能が追加**され、キャッシュ以外の用途にも本格利用できるようになったことです。また、**AWS Cost and Usage Report 2.0がAthena/Redshift統合**に対応し、コスト分析のハードルが大きく下がりました。HealthOmicsではNextflow v26.04対応とランタイムバージョン指定機能が追加され、ゲノム解析パイプラインの柔軟性が向上しています。

## 注目アップデート深掘り

### AWS Config 内部サービスリンク規則のサポート

#### なぜ重要なのか

AWS Configはこれまで、お客様が自身で管理する規則（カスタマーマネージド規則）とレコーダーを通じて、リソースのコンプライアンス評価を行ってきました。しかし、AWS Security Hub CSPMなどのセキュリティサービスが独自にコンプライアンス評価を実施したい場合、お客様のAWS Config環境に影響を与えずに独立した評価基盤を持つ必要がありました。

今回追加された**内部サービスリンク規則**は、この課題を解決します。AWSサービス側が独自にAWS Configのマネージド規則をデプロイ・管理し、評価結果を直接サービスに配信できるようになります。重要なのは、この仕組みが**既存のお客様管理のAWS Config環境と完全に独立して動作**する点です。

#### 従来のサービスリンクレコーダーとの違い

従来のサービスリンクレコーダー機能は、AWSサービスがお客様のアカウント内のリソース設定情報を記録するための仕組みでした。一方、今回の内部サービスリンク規則は、記録だけでなく**評価（規則による判定）**まで独立して実施できる点が拡張されています。

| 項目 | サービスリンクレコーダー | 内部サービスリンク規則 |
|------|------------------------|----------------------|
| 主な用途 | リソース設定情報の記録 | コンプライアンス評価の実施 |
| 評価結果の配信先 | お客様のAWS Config | AWSサービスに直接配信 |
| お客様への課金 | なし | なし |
| 既存Config環境への影響 | なし | なし |

#### 実装の検証ポイント

AWS Security Hub CSPMで内部サービスリンク規則を有効にする場合、以下のような動作を確認することになります：

```bash
# Security Hub CSPMの有効化（内部サービスリンク規則が自動デプロイされる）
$ aws securityhub enable-organization-admin-account \
    --admin-account-id 123456789012

# 内部サービスリンク規則の動作確認
$ aws config describe-configuration-recorders
# この出力に、お客様管理のレコーダーとは別に、内部サービスリンク規則専用のレコーダーは表示されない
# （独立して動作するため、通常のAWS Config APIからは見えない）

# Security Hub側で評価結果を確認
$ aws securityhub get-findings \
    --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' \
    --max-results 10
```

この仕組みにより、Security Hub CSPMは組織全体の数千のアカウントに対して、お客様のAWS Config環境に負荷をかけることなく、独自のコンプライアンス評価を実施できます。

#### コスト面でのメリット

内部サービスリンク規則による評価結果は、お客様のAWS Config料金には影響しません。これは、評価がAWSサービス側で完結し、お客様のConfig環境を経由しないためです。大規模なマルチアカウント環境でSecurity Hub CSPMを導入する際、この料金分離は重要な判断材料となります。

---

### AWS Cost and Usage Report 2.0のAthena/Redshift統合

#### なぜこのアップデートが重要なのか

AWS Cost and Usage Report（CUR）は、AWSの詳細な利用料金データを提供するサービスです。従来のCUR 1.0では、データをS3にエクスポートした後、独自のETL処理を構築してデータウェアハウスに取り込む必要がありました。CUR 2.0では、この統合作業が大幅に簡素化され、**Athena または Redshift との統合が自動化**されました。

#### 統合の仕組み

CUR 2.0でAthenaまたはRedshift統合を選択すると、以下が自動的に提供されます：

- **最適化されたデータフォーマット**：Parquet形式（列指向ストレージで高速クエリ可能）、GZIP圧縮
- **インフラストラクチャテンプレート**：Athenaテーブル定義やRedshiftスキーマが自動生成
- **自動更新メカニズム**：CURデータが定期的に更新される際、追加のETL処理なしにテーブルへ自動反映

#### Athena統合の実装例

CUR 2.0をAthenaと統合した場合、以下のようなSQLクエリで即座にコスト分析が可能になります：

```sql
-- 過去30日間のサービス別コスト集計
SELECT 
  line_item_product_code AS service,
  SUM(line_item_unblended_cost) AS total_cost
FROM 
  cur_database.cur_table
WHERE 
  line_item_usage_start_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY 
  line_item_product_code
ORDER BY 
  total_cost DESC
LIMIT 20;

-- 特定タグによるコスト配分
SELECT 
  resource_tags_user_cost_center AS cost_center,
  DATE_TRUNC('day', line_item_usage_start_date) AS usage_date,
  SUM(line_item_unblended_cost) AS daily_cost
FROM 
  cur_database.cur_table
WHERE 
  line_item_usage_start_date >= DATE '2026-06-01'
  AND resource_tags_user_cost_center IS NOT NULL
GROUP BY 
  cost_center, usage_date
ORDER BY 
  usage_date, daily_cost DESC;
```

#### Redshift統合の選択基準

Athena統合とRedshift統合のどちらを選ぶべきかは、以下の基準で判断できます：

| 基準 | Athena統合 | Redshift統合 |
|------|-----------|-------------|
| クエリ頻度 | ad-hocな分析向き | 定期的な大量クエリ向き |
| 初期コスト | なし（従量課金） | Redshiftクラスタの起動が必要 |
| クエリ単価 | スキャンデータ量に応じた従量課金 | クラスタの時間課金 |
| 他データとの結合 | S3上の他データとフェデレーション可能 | データウェアハウス内で高速結合 |
| BI ツール連携 | JDBC/ODBC経由で可能 | ネイティブ統合が豊富 |

#### 自動更新フローの確認

CUR 2.0データは通常1日1回更新されます。CUR 2.0はBCM Data Exports機能の一部として管理されるため、エクスポート設定の確認には `bcm-data-exports` のAPIを使用します：

```bash
# CUR 2.0（Data Exports）のエクスポート一覧を確認
$ aws bcm-data-exports list-exports

# 個別エクスポートの詳細（テーブル設定やS3出力先）を確認
$ aws bcm-data-exports get-export --export-arn <export-arn>

# Athenaテーブルの最新パーティション確認
$ aws athena start-query-execution \
    --query-string "SHOW PARTITIONS cur_database.cur_table" \
    --result-configuration OutputLocation=s3://my-athena-results/
```

統合を有効にすると、Parquet形式での配信に加え、Athenaテーブル定義やRedshiftスキーマ、データ読み込み手順といったインフラストラクチャテンプレートが自動的に提供されます。CUR 2.0データの更新も追加のETLなしにテーブルへ自動反映されるため、データアナリストはインフラ管理を意識せずSQLクエリの作成に集中できます。

## SRE視点での活用ポイント

### 内部サービスリンク規則による運用改善

SREチームがマルチアカウント環境でコンプライアンス監視を行う場合、これまではAWS Configの規則を全アカウントに一律適用し、その評価結果を集約する必要がありました。内部サービスリンク規則を活用することで、**セキュリティ評価基盤とインフラ監査基盤を分離**できます。

例えば、Security Hub CSPMに組織全体のセキュリティ評価を任せつつ、AWS Config自体は特定の内部規制（例：特定のタグ付けルールや、DR要件を満たすバックアップ設定）の監視に特化させることができます。これにより、AWS Config の規則数とコストを最適化しながら、セキュリティハブ側では包括的なCSPM評価を並行して実施できます。

注意点として、内部サービスリンク規則の評価結果はAWS Configコンソールには表示されないため、**アラート設定やダッシュボードはSecurity Hub側で構築**する必要があります。既存のAWS Config EventBridgeルールとは独立して、Security Hub Findingsに対するイベント処理を実装することになります。

### CUR 2.0統合によるコスト可視化の民主化

従来、詳細なコスト分析を行うには専任のデータエンジニアリングチームがETLパイプラインを構築・運用する必要がありました。CUR 2.0のAthena/Redshift統合により、**SREチームが独自にコスト分析SQLを書いて即座に実行**できるようになります。

例えば、突発的なコスト増加アラートを受け取った際、以下のようなad-hocクエリで原因を特定できます：

- 過去1時間のリソース種別ごとの利用量増加率の算出
- 特定のEC2インスタンスタイプへの支出集中の検出
- タグ付けされていないリソースの洗い出し

Terraformで管理しているインフラであれば、CUR 2.0のデータとTerraform stateを突き合わせることで、**コード管理されていないリソース**や**想定外の課金源**を特定する運用も可能です。

ただし、Athena統合の場合、大量のクエリを実行するとスキャンコストが累積します。定期実行するダッシュボードクエリは、Redshift統合や、集計済みビューの事前作成を検討すると良いでしょう。

### ElastiCache for Valkey耐久性機能の運用判断

ElastiCache for Valkeyの耐久性機能は、従来「キャッシュ = 揮発性」という前提を覆すものです。SRE視点では、**どのワークロードを耐久性付きValkeyに載せるべきか**の判断が重要です。

適用を検討すべきケース：
- **分散システムの状態管理**：マイクロサービス間のトランザクション状態を一時的に保持し、ノード障害時にも状態を復元したい場合
- **レートリミット用カウンタ**：API Gateway や自前のレートリミッターでカウンタを管理しており、再起動後もカウンタを維持したい場合
- **セッションストア（高トラフィック）**：大量のセッション書き込みがあり、かつセッション損失が許容できない場合（非同期書き込みモードを選択）

一方、従来のキャッシュ用途（読み取り頻度が極めて高く、元データがRDBにある場合）では、耐久性機能は不要です。また、同期書き込みモードは書き込みレイテンシーがシングル桁ミリ秒になるため、**マイクロ秒レイテンシーが必須のワークロードでは非同期モードを選択**し、稀な障害時の最大10秒のデータ損失を許容できるかを検討する必要があります。

障害対応のランブックに組み込む際は、同期/非同期の選択に応じてリカバリ手順が異なる点に注意が必要です。非同期モードの場合、最大10秒分のデータ損失が発生する可能性があるため、その影響範囲を事前に評価し、ログやメトリクスで損失の有無を検証する手順を含めると良いでしょう。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|---------|---------|------|
| 1 | Amazon Location Service | [公共交通機関・インターモーダルルーティング対応](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-location-service/amazon-location-new-public-transit-intermodal-routing) | Routes APIにTransitとIntermodalトラベルモードを追加。バス・電車・徒歩・タクシーなどを組み合わせた複雑なルート計算が可能に |
| 2 | AWS Config | [内部サービスリンク規則のサポート](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-config-supports-internal-service-linked-rules) | Security Hub CSPMなどのAWSサービスがAWS Config規則を独立して管理・評価できるように。顧客管理のConfig環境とは独立動作 |
| 3 | AWS Deadline Cloud | [Service Managed Fleetsで永続ストレージ対応](https://aws.amazon.com/about-aws/whats-new/2026/06/deadline-cloud/persistent-storage) | ワーカーにEBSボリュームを永続接続し、Conda環境やシェーダーキャッシュを保持。ワーカー起動時間を短縮 |
| 4 | Amazon SageMaker Studio | [セットアップ時間を20秒以下に短縮・モデルカスタマイズ権限を自動設定](https://aws.amazon.com/about-aws/whats-new/2026/01/quick-setup-model-customization-sagemaker-studio/) | 従来2分以上かかっていたセットアップが20秒以下に。新規環境では「AmazonSageMakerModelCustomizationCoreAccess」ポリシーが自動付与され、即座にファインチューニング可能 |
| 5 | AWS Cost and Usage Report 2.0 | [AthenaとRedshift統合をサポート](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-cur2.0-athena-redshift/) | CUR 2.0データをAthena/RedshiftでSQLクエリ可能に。Parquetフォーマットとテーブル定義が自動生成され、ETL不要で分析開始 |
| 6 | Amazon ElastiCache for Valkey | [耐久性（Durability）機能を追加](https://aws.amazon.com/about-aws/whats-new/2026/06/durability-amazon-elasticache) | Multi-AZトランザクションログによるデータ永続化。同期書き込み（ゼロデータ損失）と非同期書き込み（マイクロ秒レイテンシー、無料）を選択可能 |
| 7 | Amazon RDS for SQL Server | [Bring Your Own Media（BYOM）対応](https://aws.amazon.com/about-aws/whats-new/2026/06/rds-sqlserver-supports-bring-your-own-media/) | 既存のSQL Serverライセンス（Software Assurance含む）をMicrosoftライセンスモビリティプログラム経由で再利用可能に。License Managerと統合しコンプライアンス管理を簡素化 |
| 8 | AWS HealthOmics | [Nextflow v26.04をサポート](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-healthomics-nextflow-version-26-04/) | レコード型、厳密な構文パーサー、JSON出力サマリー、エージェントログモードなどの新機能を追加。ワークフロー開発の可読性とAI連携を強化 |
| 9 | AWS HealthOmics | [Nextflowバージョンをランタイムで指定可能に](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-healthomics-nextflow-version-pinning-at-runtime/) | StartRun APIの新しいengine-settingsパラメータでNextflowバージョン（22.04～26.04）を実行時に選択可能。ワークフロー定義を変更せずに複数バージョン検証が可能 |

## まとめ

本日のアップデートは、**運用効率とコスト最適化**に焦点を当てたものが目立ちました。AWS Configの内部サービスリンク規則は、セキュリティ評価とインフラ監査の責任分離を促進し、大規模組織での運用を洗練させます。CUR 2.0のAthena/Redshift統合は、コスト可視化の民主化により、全エンジニアが自律的にコスト分析を行える環境を整えます。

また、ElastiCache for Valkeyの耐久性機能は、インメモリデータストアの適用範囲を大きく広げ、AI エージェントのメモリ管理やRAG知識ベースなど、新しいユースケースを切り開いています。SageMaker Studioのセットアップ高速化は、ML開発者のオンボーディング体験を劇的に改善し、組織全体でのML活用を加速させるでしょう。

HealthOmicsのNextflow関連アップデートは、ゲノム解析パイプラインの柔軟性と信頼性を向上させ、規制対応が求められる医療・ライフサイエンス分野での採用を後押しします。Location Serviceの公共交通ルーティングは、モビリティサービスや都市計画アプリケーションの実装ハードルを大きく下げるものです。

全体として、既存サービスの成熟度を高め、エンタープライズ環境での採用を促進するアップデートが揃った一日でした。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)