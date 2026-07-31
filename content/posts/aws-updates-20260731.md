---
title: "【AWS】2026/07/31 のアップデートまとめ"
date: 2026-07-31T08:02:03+09:00
draft: false
tags: ["aws", "iam", "redshift", "direct-connect", "msk", "bedrock", "transit-gateway", "opensearch", "glue", "s3"]
categories: ["AWS Updates"]
summary: "2026/07/31 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260731/header.png)

# 直近のAWSアップデートまとめ（2026年7月版）

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。注目すべきは、ネットワークとデータパイプラインの高度化、生成AIモデルの拡充、そしてセキュリティ・コンプライアンス対応の強化です。特にAWS Transit GatewayのPolicy-Based Routing、Amazon MSK ExpressのS3/Iceberg直接配信機能、AWS Glue REST APIコネクタの大幅拡張は、運用効率とコスト削減の両面で大きなインパクトをもたらします。また、Amazon BedrockではGemma 4やGrok 4.3がGovCloudで利用可能となり、規制環境下での生成AI活用の選択肢が広がりました。

本記事では、これらのアップデートの中から特に技術的に深掘りする価値のあるものをピックアップし、SRE視点での活用ポイントとともに解説します。

---

## 注目アップデート深掘り

### AWS Transit Gateway Policy-Based Routing（PBR）の実現と運用改善

AWS Transit Gatewayに**Policy-Based Routing（PBR）**機能が一般提供されました。従来のTransit Gatewayは宛先IPアドレスのみに基づいてトラフィックを転送していましたが、今回のアップデートにより、送信元・宛先IPアドレス、ポート、プロトコルなど複数のパケット属性を組み合わせた条件に基づいた、きめ細かなトラフィック制御が可能になります。

#### なぜこのアップデートが重要なのか

従来、機密性の高いワークロードを分離したり、特定のトラフィックをセキュリティアプライアンスに誘導する必要がある場合、複数のVPCと追加のルーティング階層を構築する必要がありました。これは運用の複雑さを増し、ネットワークのオーバーヘッドも発生させていました。PBRによって、Transit Gatewayネイティブの機能でインラインでのトラフィック分類・誘導が実現し、追加インフラなしに高度なトラフィック制御が可能になります。

#### 設定の仕組みと動作原理

PBRの設定は、Transit Gatewayアタッチメントに**ポリシーテーブル**を関連付けて、順序付きルールセットを定義する形で行います。各ルールはトラフィックを分類し、マッチしたパケットを指定されたルートテーブルに送信する「最初にマッチしたルールが優先」のロジックで動作します。

具体的なユースケースとしては、以下のようなシナリオが考えられます：

- **セキュリティ検査の自動化**: 機密ワークロードからのトラフィックを送信元IPやポートで分類し、AWS Network Firewallや第三者製検査アプライアンスに自動的に誘導
- **パス最適化**: 送信元やプロトコルに基づいて、特定のアプリケーショントラフィックをAWS Direct ConnectまたはAWS VPNパスで適切にルーティング
- **マイクロセグメンテーション**: 本番環境と開発環境を異なるルーティングドメインに分離し、横展開（ラテラルムーブメント）を制限

#### 従来構成との比較

従来の構成では、トラフィック分類のために複数のVPCを経由させる必要があり、ホップ数の増加によるレイテンシーの増大や、管理対象の増加による運用負荷の増大が課題でした。PBRを使用することで、Transit Gateway上で直接トラフィックを分類・誘導できるため、ネットワークトポロジーがシンプルになり、レイテンシーも削減されます。

マルチテナント環境では、テナント間のトラフィック分離をルールベースで柔軟に定義できるため、コンプライアンス要件に基づいたトラフィック制御の自動化が容易になります。

---

### Amazon MSK ExpressのS3/Iceberg直接配信による運用コスト削減

Amazon MSK Expressブローカーが、Apache KafkaデータをAmazon S3に直接配信する機能と、Apache Icebergのストリーミングテーブルへのデータ配信機能に対応しました。これらは完全マネージド型の機能で、自己管理型コネクタと比べて導入・運用コストを最大60%削減し、ダウンストリームのクエリコストを最大30%削減できます。

#### 背景：従来のKafka-S3統合の課題

従来、KafkaからS3やIcebergにデータを配信するには、Kafka Connectを使ったカスタムパイプラインの構築が必要でした。これには以下の課題がありました：

- **複雑な運用**: コネクタのスケーリング、リトライ、バックプレッシャー処理を手動で管理
- **小ファイル問題**: Icebergへの大量取り込みで多数の小さいParquetファイルが生成され、クエリ性能が低下
- **並行書き込み競合**: 高スループット環境での並行書き込みの調整が困難
- **コスト**: ブローカーエグレススループットの追加プロビジョニングが必要

#### MSK Expressが提供する改善

今回のアップデートでは、これらの課題が一気に解決されます：

**S3直接配信**では、最大10GB/sのスループットをサポートし、スケーリング、リトライ、バックプレッシャー処理を自動管理します。ブローカーエグレススループットの追加プロビジョニングが不要で、容量スケーリングやバージョンアップグレードなどの運用も自動化されます。

**Iceberg配信**では、インラインコンパクション機能が小ファイルの性能影響を排除し、クエリ性能を予測可能に保ちながらデータ鮮度を維持します。また、組み込み調整機能が高スループット環境での並行書き込み競合を解決します。

#### ユースケースと実装シナリオ

実際の活用シナリオとしては、以下のような構成が考えられます：

- **不正検知システム**: Kafkaでリアルタイム入力した取引データをIcebergに継続化して、近リアルタイム分析を実行
- **ログアーカイブ**: Kafkaから大量のログをS3に自動配信し、長期保存・分析基盤を構築
- **AI/MLモデル学習**: KafkaストリームのデータをS3に配信し、機械学習パイプラインの学習データとして活用
- **データレイク構築**: 複数のKafkaクラスタからデータを集約し、一元的なデータレイク化

従来のKafka Connect構成と比較すると、MSK Expressではコネクタのデプロイ・管理が不要になり、運用負荷が大幅に削減されます。また、ネイティブ機能のため追加のブローカー出力スループットコストが発生せず、インフラコストも削減できます。

---

### AWS Glue REST APIコネクタの機能拡張と実践活用

AWS GlueのREST APIコネクタが大幅に機能拡張され、VPCサポート、フィルタプッシュダウン、パーティション機能が追加されました。従来、REST APIを通じたデータ取得はカスタムコード作成が必要でしたが、今回のアップデートでノーコード/ローコードでの実装が可能になります。

#### 3つの新機能の技術的詳細

**VPCサポート**により、プライベートサブネット内のデータソースやVPN、AWS PrivateLink経由で接続されたシステムに安全にアクセス可能になり、トラフィックをインターネットに露出させません。これにより、レガシーシステムや社内APIとの連携がセキュアに実現できます。

**フィルタプッシュダウン**は、クエリの条件をAPIネイティブなパラメータに変換し、ソース側で条件に合致するレコードだけを送信させることで、データ転送量を削減し、ジョブパフォーマンスを向上させます。例えば、特定の日付範囲や特定の顧客IDのみを取得する場合、APIパラメータとして条件を渡すことで、不要なデータの転送を回避できます。

**パーティション機能**は大規模データセットを複数のSparkワーカーに分割し、高容量でページング型のAPIから並列読み込みを実現し、取得時間を短縮します。パーティション戦略は、フィールドベース（特定のフィールド値で分割）とレコード数ベース（レコード数で均等分割）の2種類が提供されます。

#### 実装上の考慮事項

SaaSプロバイダーのAPIから定期的にデータを抽出し、Data Lakeに集約するETLパイプラインを構築する場合、以下の点を考慮する必要があります：

- **認証トークン管理**: AWS Secrets Managerと連携して、APIトークンを安全に管理
- **レート制限対策**: APIのレート制限に応じて、適切なリトライポリシーを設定
- **データスキーマの変化**: API仕様変更に対応するため、AWS Glue Data Catalogのスキーマ進化機能を活用

従来のカスタムコード方式では、これらを自前で実装・保守する必要がありました。標準化されたコネクタを使うことで、その実装分の開発・保守対象を減らせます。

---

## SRE視点での活用ポイント

これらのアップデートは、SREの日常業務に多くの改善をもたらします。

**Transit Gateway PBR**は、障害対応のランブックに組み込むことで、障害発生時に特定のトラフィックを自動的に迂回ルートに切り替える仕組みを構築できます。Terraformで管理しているインフラがあれば、ポリシーテーブルとルールをコード化し、環境間で再現可能な構成管理が実現できます。導入時は、既存のルーティング設定との整合性を慎重に検証し、段階的にルールを追加していくアプローチが推奨されます。ルール評価順序が重要なため、設計段階で優先順位を明確にし、テスト環境で十分な検証を行うことが重要です。

**MSK ExpressのS3/Iceberg配信**は、ストリーミングデータの永続化戦略を大幅にシンプル化します。CloudWatchアラームと組み合わせると、配信失敗時の自動通知や、スループット監視によるキャパシティプランニングが可能になります。既存のKafka Connect構成からの移行を検討する場合、データフォーマットの互換性、配信レイテンシーの変化、コスト削減効果を事前に評価することが重要です。特に、Iceberg配信ではインラインコンパクションが小ファイルによる性能影響を排除するため、ダウンストリームのクエリコストを最大30%削減できます。

**Glue REST APIコネクタの拡張**は、SaaSとの連携において運用負荷を大幅に削減します。VPCサポートにより、プライベートネットワーク内のAPIエンドポイントへの安全なアクセスが可能になり、セキュリティポリシーとの整合性が保たれます。フィルタプッシュダウンとパーティション機能を組み合わせることで、大規模APIからのデータ取得時間とコストを最適化できますが、APIのレート制限やページングロジックに応じた適切な設定が必要です。Glueジョブのメトリクスを定期的に監視し、パフォーマンスチューニングを継続的に行うことで、安定したデータパイプラインを維持できます。

---

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| IAM | IAM Policy SimulatorがIAMコンソールに移行し、追加機能を提供 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/iam-policy-simulator-iam-console/) |
| Amazon Redshift | Gravitonベースの RG large/12xlarge インスタンスがトレーリングトラックで利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-redshift-rg-large-12xlarge-trailing-track) |
| AWS Direct Connect | BGPルート可視化機能が仮想インターフェースで利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-direct-connect-bgp-visibility/) |
| Amazon MSK | MSK ExpressがApache Icebergのストリーミングテーブルへのデータ配信に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-msk-streaming-tables-for-apache-iceberg) |
| Amazon MSK | MSK ExpressがAmazon S3へのKafkaデータ直接配信に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-msk-express-brokers-delivers-to-amazon-s3) |
| Amazon Bedrock | OpenAI GPT-5.6 モデルが最大80%の値下げ（Luna は80%、Terra は20%のオンデマンド推論価格引き下げ） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/openai-gpt-terra-luna-pricing-bedrock/) |
| Amazon Bedrock | Gemma 4モデルがGovCloud (US-West)で利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/gemma-4-bedrock-govcloud/) |
| Amazon Bedrock | xAI Grok 4.3がGovCloud (US-West)で利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/grok-4-3-bedrock-govcloud/) |
| AWS Transit Gateway | Policy-Based Routing（PBR）機能が一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-transit-gateway-policy-based-routing/) |
| Amazon OpenSearch Service | OpenSearch バージョン 3.7 に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-opensearch-service/) |
| AWS Glue | REST APIコネクタがVPCサポート、フィルタプッシュダウン、パーティション機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-glue-rest-connector-filtering-partitioning-vpc) |

---

## まとめ

今回紹介したアップデートは、AWS の成熟度の高まりを示しています。特にネットワーク制御の高度化（Transit Gateway PBR、Direct Connect BGP可視化）、データパイプラインの運用簡素化（MSK Express、Glue REST APIコネクタ）、生成AIの選択肢拡大（Bedrock GovCloud対応）は、エンタープライズ環境での実用性を大きく向上させるものです。

また、Amazon RedshiftのGravitonベースインスタンスがトレーリングトラックで利用可能になったことや、OpenSearch 3.7のベクトル検索最適化など、コスト削減とパフォーマンス向上を両立させる機能強化も目立ちます。

これらのアップデートは、個別に導入するだけでなく、組み合わせることでさらに大きな効果を発揮します。例えば、Transit Gateway PBRでトラフィックを制御しながら、MSK ExpressでストリーミングデータをIcebergに配信し、OpenSearchで近リアルタイム分析を行う、といった統合的なアーキテクチャが構築できます。各アップデートの詳細な技術仕様や制限事項については、公式ドキュメントを参照し、自組織の要件に合わせた検証を行うことをおすすめします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)