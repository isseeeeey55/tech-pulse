---
title: "【AWS】2026/09/25 のアップデートまとめ"
date: 2026-09-25T08:02:40+09:00
draft: false
tags: ["aws", "rds", "gamelift", "sagemaker", "emr", "eks", "lambda", "dynamodb", "kinesis", "waf", "shield"]
categories: ["AWS Updates"]
summary: "2026/09/25 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260925/header.png)

# 今回は、直近で発表された12件のAWSアップデートを紹介します

今回取り上げる12件では、データベースサービスの機能強化、リージョン拡大、セキュリティ機能の拡充が目立ちます。なかでも RDS for PostgreSQL の耐量子暗号 TLS キー交換対応、DynamoDB グローバルテーブルのマルチリージョン強い一貫性（MRSC）の対応リージョン拡大、Kinesis Data Streams のサービスマネージド パーティションキーは、運用面への直接的な影響が大きい変更です。

本記事では、これら3件を深掘りし、SRE 視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon RDS for PostgreSQL の耐量子暗号（Post-Quantum）TLS キー交換対応

Amazon RDS for PostgreSQL で、TLS キー交換に使う暗号グループを指定する `ssl_groups` パラメータを変更できるようになりました。対象は PostgreSQL 18 以上です。RDS for PostgreSQL の許可リストから暗号グループを選択し、組織のセキュリティ基準に合わせた構成にできます。設定は RDS Management Console または AWS CLI から行えます。

#### なぜ耐量子暗号なのか

RSA や楕円曲線暗号（ECDHE など）による鍵交換は、将来の量子コンピュータで解読されるおそれがあります。特に「Store Now, Decrypt Later（今記録して後で解読）」と呼ばれる脅威モデルでは、攻撃者が現在の暗号化通信を記録しておき、将来解読することが懸念されます。長期にわたって機密性を保つ必要があるデータを扱うシステムほど、鍵交換を早めに耐量子化する意義があります。

#### 設定のポイント

- 対象は **PostgreSQL 18 以上**。それ未満のバージョンでは、まずメジャーバージョンアップグレードが必要です
- `ssl_groups` に指定できる値は **RDS for PostgreSQL の許可リスト** に含まれる暗号グループに限られます。告知本文には具体的なアルゴリズム名は記載されていないため、選択可能なグループは公式ドキュメントの許可リストを確認してください
- 再起動の要否や適用手順も告知には記載がありません。パラメータ変更の反映方法は公式ドキュメントで確認してから本番に適用します

### Amazon Kinesis Data Streams のサービスマネージド パーティションキー

Amazon Kinesis Data Streams の On-Demand Standard / On-Demand Advantage ストリームで、パーティションキーを指定せずにレコードを送信できるようになりました。サービスが利用可能なウォームキャパシティに基づいてレコードを自動的に分散します。すべての AWS 商用リージョンで、追加コストなしで利用できます。

#### これまでの課題

Kinesis はパーティションキーのハッシュ値でレコードの送信先シャードを決めます。順序保証が不要なワークロードでは、ランダムなパーティションキー（UUID など）を生成して分散させるのが一般的でした。しかし告知では、ランダムなパーティショニングでもシャード間のスループットに偏りが生じ、ストリーム全体の容量が十分でも一部のパーティションキーでスロットリングが起きることがあると説明しています。

#### 新機能の仕組みと適用範囲

- パーティションキーを省略して送信すると、サービスがウォームキャパシティに基づいてレコードを分散します
- 対象は **On-Demand Standard / On-Demand Advantage** のストリームです（告知にプロビジョンドモードの記載はありません）
- 利用には **最新の AWS SDK または Kinesis Producer Library（KPL）** へのアップグレードが必要です
- 告知が挙げる代表的なユースケースは、ログ集約、メトリクス収集、IoT テレメトリなど、**レコードの順序保証が不要なワークロード** です

同じパーティションキーを持つレコードは同じシャードに入り、シャード内で順序が保たれます。この性質に依存している処理（エンティティ単位で順序が必要な処理）では、引き続き明示的なパーティションキーを指定します。

### DynamoDB グローバルテーブルのマルチリージョン強い一貫性（MRSC）の対応リージョン拡大

Amazon DynamoDB グローバルテーブルのマルチリージョン強い一貫性（MRSC）が、新たに5リージョンに対応しました。対応リージョンは合計15です。

- 追加リージョン: Canada (Central)、Europe (Stockholm)、Europe (Spain)、Asia Pacific (Mumbai)、Asia Pacific (Singapore)

これにより、北米・ヨーロッパ・アジアパシフィックにまたがる構成が可能になりました。

#### MRSC の特徴

MRSC グローバルテーブルは、任意の3リージョン構成で作成でき、**3レプリカ** または **2レプリカ + 1ウィットネスリージョン** のいずれかを選べます。告知ではリカバリポイント目標（RPO）ゼロを実現するとしています。

告知が挙げる適用先は、ユーザープロファイル管理、在庫管理、注文状態、権利（エンタイトルメント）管理など、厳密な一貫性が求められるアプリケーションです。

## SRE視点での活用ポイント

### 耐量子暗号対応の導入判断

長期にわたって保護が必要なデータ（金融情報、医療データ、個人識別情報など）を扱うシステムでは、検証計画を立てる価値があります。導入時の注意点は次の通りです。

- 非本番環境で PostgreSQL 18 へのアップグレードと `ssl_groups` の変更を検証する
- サーバー側で許可する暗号グループを絞り込む場合、アプリケーション側の PostgreSQL クライアント（および TLS ライブラリ）がそのグループをサポートしているか確認する。共通のグループが無ければ TLS ハンドシェイクは成立しない
- 接続プール（PgBouncer、RDS Proxy など）を使っている構成では、どの区間の TLS が対象になるかを整理しておく

### Kinesis のサービスマネージド パーティションキーでの運用簡素化

ログ集約やメトリクス収集のパイプラインで UUID 生成などの分散ロジックを持っている場合、SDK / KPL を更新してパーティションキーを省略する形に置き換えられます。

- まず一部のプロデューサーだけを切り替えて挙動を確認し、段階的に展開する
- シャードレベルの拡張モニタリングを有効にしている場合は、`IncomingRecords` や `IncomingBytes` をシャード別に見て分散の状況を確認できる
- `WriteProvisionedThroughputExceeded` を引き続き監視し、スロットリングの減少を確認する。プロデューサー側のリトライ処理は従来通り維持する

### DynamoDB MRSC でのリージョン選定

MRSC は書き込み時に複数リージョン間で一貫性を確保するため、結果整合性（MREC）のグローバルテーブルと比べて書き込みレイテンシーが大きくなります。大陸をまたぐ構成ではリージョン間の距離がそのまま書き込みレイテンシーに効くため、主要なユーザーの所在地と可用性要件を踏まえてリージョンを選びます。3レプリカ構成か、2レプリカ + ウィットネス構成かは、3つ目のリージョンで読み書きを受ける必要があるかどうかで判断します。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon RDS | [Multi-AZ for SQL Server Developer Edition](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-sql-server-multi-az-developer-edition/) | RDS for SQL Server の Developer Edition で Always On 可用性グループによる Multi-AZ 配置をサポート。非本番環境で高可用性構成を検証可能に |
| Amazon GameLift | [5新リージョン・8 Local Zones で利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-gamelift-servers-region-expansion-2026) | イスラエル、メキシコ、スペイン、インド、インドネシアの5リージョンと、米国・南米の8 Local Zones に展開され、ゲームサーバーのレイテンシー削減が可能に |
| Amazon SageMaker | [HyperPod Inference Gateway](https://aws.amazon.com/about-aws/whats-new/2026/09/sagemaker-hyperpod-inference-gateway/) | EKS マネージドアドオンとして提供される GPU 対応ルーティングシステム。ラウンドロビンに代わるリアルタイム推論シグナル駆動のルーティングにより、混在ハードウェア・バーストトラフィックのシナリオで最初のトークンまでのレイテンシを最大82%削減 |
| Amazon EMR on EKS | [Spark Connect による対話的ワークロード](https://aws.amazon.com/about-aws/whats-new/2026/09/emr-eks-spark-connect-interactive/) | SageMaker Unified Studio や Jupyter、VS Code から対話的に Spark アプリケーションを開発・デバッグ可能に |
| AWS Network Security Manager | [US East (N. Virginia) で GA](https://aws.amazon.com/about-aws/whats-new/2026/09/network-security-manager-us-east-va/) | AWS 組織全体にファイアウォール・DDoS 保護設定を一元適用し、ドリフトの検出と修復を自動化。WAF と Shield Advanced に対応（Network Firewall は近日対応予定） |
| Amazon RDS for PostgreSQL | [PostgreSQL 19 Beta 4 対応](https://aws.amazon.com/about-aws/whats-new/2026/09/postgresql-19-beta-4-amazon-rds-database-preview-environment/) | Database Preview Environment で PostgreSQL 19 Beta 4 が利用可能に。autovacuum 管理とクエリパフォーマンスが改善 |
| AWS Lambda | [Durable Functions が European Sovereign Cloud で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/09/durablefunctions-european-sovereign-cloud/) | 複数ステップのアプリケーションや AI ワークフローを構築できる Durable Functions が AWS European Sovereign Cloud で提供開始 |
| Amazon RDS for PostgreSQL | [耐量子暗号 TLS キー交換対応](https://aws.amazon.com/about-aws/whats-new/2026/09/postgresql-post-quantum-tls-key-exchange/) | PostgreSQL 18 以上で `ssl_groups` パラメータによる post-quantum TLS 対応 |
| Amazon RDS for MySQL | [Extended Support マイナーバージョン](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-mysql-extended-support-minor-5744-8046-rds/) | MySQL 5.7.44 と 8.0.46 の拡張サポート版がリリース。標準サポート終了後も最大3年間の CVE・バグ修正を提供 |
| Amazon DynamoDB | [MRSC が追加リージョン・クロスコンティネント構成に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/dynamodb-mrsc-additional-regions/) | グローバルテーブルのマルチリージョン強い一貫性が5新リージョンに対応し、合計15リージョンで利用可能。3大陸にまたがる構成も可能に |
| Amazon EMR on EKS | [IPv6 EKS クラスターをサポート](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-emr-eks-ipv6-support) | IPv6 対応 EKS クラスターで Apache Spark や Flink を実行可能に。セカンダリ CIDR などの IPv4 節約策が不要になり、500 エグゼキューター規模の Spark ジョブもアドレス上限を気にせず並行実行可能に |
| Amazon Kinesis Data Streams | [サービスマネージド パーティションキー](https://aws.amazon.com/about-aws/whats-new/2026/09/kinesis/service-managed-partition-keys) | パーティションキーを指定せずにデータを送信可能。順序保証が不要なワークロードでホットパーティションキーを解消（On-Demand ストリーム対象、追加コストなし） |

## まとめ

今回のアップデートで目立つのは、**運用の簡素化** です。Kinesis のサービスマネージド パーティションキーでは、パーティションキーの分散ロジックを自前で持つ必要がなくなります。Network Security Manager は、WAF と Shield Advanced の保護設定を AWS 組織全体に一元的に適用する仕組みを提供します。

**セキュリティ面** では、RDS for PostgreSQL の耐量子暗号 TLS キー交換対応により、PostgreSQL 18 以上で鍵交換の暗号グループを組織の基準に合わせて選べるようになりました。

**リージョン展開** では、GameLift Servers の5リージョン・8 Local Zones への拡大、DynamoDB MRSC の対応リージョン拡大（合計15リージョン、大陸をまたぐ構成に対応）がありました。EMR on EKS の IPv6 クラスター対応は、IPv4 アドレス数を気にせず大規模ジョブを並行実行するための変更です。

データベースとアナリティクスでは、PostgreSQL 19 Beta 4 のプレビュー提供、MySQL の Extended Support マイナーバージョン、EMR on EKS の Spark Connect 対応が加わりました。


---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)