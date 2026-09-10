---
title: "【AWS】2026/09/11 のアップデートまとめ"
date: 2026-09-11T08:02:20+09:00
draft: true
tags: ["aws", "api-gateway", "lambda", "opensearch", "redshift", "outposts", "mq", "cloudwatch", "elemental-mediatailor", "elemental-medialive", "elemental-mediapackage", "elemental-inference", "transform", "s3", "sqs", "sns", "data-firehose", "athena", "cloudfront", "ec2"]
categories: ["AWS Updates"]
summary: "2026/09/11 のAWSアップデートまとめ"
---

# 直近の AWS アップデートまとめ（2026年9月版）

## はじめに

今回は、直近で発表された 15 件の AWS アップデートを紹介します。特に注目すべきは、Amazon API Gateway の実行ログ強化、AWS Elemental メディアサービス群の大幅な機能拡張、そして AWS Lambda の AI エージェント統合です。これらのアップデートは、運用可視性の向上、コンテンツ配信の効率化、AI ワークロードの耐障害性強化といった、実運用で直面する課題に対する実践的なソリューションを提供しています。また、.NET モダナイゼーションやインフラ関連の拡充も含まれており、幅広い技術スタックをカバーする内容となっています。

---

## 注目アップデート深掘り

### Amazon API Gateway：実行ログの大幅強化と柔軟な配信先設定

Amazon API Gateway の REST API 実行ログが根本的に強化されました。従来は API Gateway 管理の CloudWatch Logs へ自動配信され、ログイベントは 1 KB に制限されていましたが、今回のアップデートで以下の改善が実現しています。

**ログサイズの拡大と可視性の向上**

ログイベントのサイズ上限が 1 KB から **1 MB** へと 1000 倍に拡大されました。これにより、リクエスト・レスポンスボディの詳細や、複雑な JSON ペイロード、エラースタックトレースなど、従来は切り詰められていた重要な情報を完全に記録できるようになります。マイクロサービスアーキテクチャにおいて、API 間の連携デバッグや問題の根本原因分析が大幅に効率化されます。

**複数配信先への同時送信**

最も重要な変更点は、CloudWatch Logs、Amazon S3、Amazon Data Firehose といった複数の配信先を **同時に指定できる** ことです。これにより、以下のような運用パターンが実現可能になります：

- **リアルタイム監視とコスト最適化の両立**：CloudWatch Logs でアラームやメトリクスフィルタを活用したリアルタイム検知を行いつつ、S3 へ長期保存してストレージコストを削減
- **コンプライアンス対応**：CloudWatch で直近 30 日のログを保持し、S3 で監査要件に応じた長期保管を実施
- **分析基盤への統合**：Firehose 経由で Redshift や Elasticsearch へストリーミング配信し、ログ分析基盤を構築

**Apache Parquet 形式と Athena 連携**

S3 への配信では Apache Parquet 形式がサポートされています。Parquet はカラムナーストレージ形式で、分析クエリに最適化されており、Amazon Athena での検索・集計が高速かつ低コストになります。例えば、API のエンドポイント別レスポンスタイム集計や、エラー率の時系列分析、特定ユーザーのアクセスパターン抽出など、大量のログを対象とした分析が実用的なコストで実施可能です。

**設定と料金**

設定はコンソール、AWS CLI、CloudFormation から実行できます。料金は CloudWatch Vended Logs レートで課金され、従来の API Gateway 管理ログと同じ課金体系です。S3 への保存コストは通常の S3 ストレージ料金、Athena クエリは標準のスキャンデータ量ベースの料金が適用されます。

この機能は AWS GovCloud を含む全リージョンで利用可能で、既存の REST API に対してすぐに有効化できます。

### AWS Lambda durable functions と Pydantic AI の統合

AWS Lambda durable functions が Python の AI エージェントフレームワーク Pydantic AI と統合されました。この統合は、長時間実行される AI エージェントワークフローの耐障害性とコスト効率を大幅に改善します。

**AI エージェントにおける課題**

AI エージェントは通常、複数の LLM API 呼び出し、外部ツール実行、データ取得など、多数のステップを順次実行します。各ステップは時間がかかり、ネットワーク障害や API レート制限、タイムアウトなどで中断されるリスクがあります。従来、こうした中断が発生すると、最初からすべてのステップを再実行する必要があり、以下の問題が生じていました：

- **トークンコストの重複**：同じ LLM API 呼び出しを何度も繰り返し、課金が累積
- **処理時間の増大**：既に完了した処理を再度実行することで、ユーザー体験が悪化
- **副作用の重複**：決済処理や外部 API への書き込みなど、冪等性のない操作が複数回実行されるリスク

**durable functions による自動チェックポイント**

Lambda durable functions は、エージェントの実行進捗を自動的に保存します。Pydantic AI のエージェントが実行する各モデルコール・ツールコールが耐久実行ステップとして記録されるため、タイムアウトやエラーで中断しても、最後に完了したステップから再開できます。

例えば、10 個のドキュメントを順次解析する AI エージェントが 7 個目の処理中にタイムアウトした場合、再開時には 8 個目から処理が続行され、既に完了した 1〜7 個目の LLM API 呼び出しは実行されません。これにより、トークンコストが大幅に削減され、処理時間も最小限に抑えられます。

**実装の透明性**

開発者はチェックポイント管理やリトライロジックを自分で実装する必要がありません。Pydantic AI のコードをそのまま Lambda durable functions 上で実行するだけで、自動的にフォールトトレランスが実現されます。Lambda のサーバーレス特性により、サーバー管理も不要で、使用した計算リソース分のみが課金されます。

この統合は、すべての Lambda durable functions 対応リージョンで利用可能で、複雑なエンタープライズワークフローや、コスト効率が重要なスタートアップの AI アプリケーションに最適です。

---

## SRE 視点での活用ポイント

### API Gateway ログの運用設計

API Gateway のログ強化は、SRE にとって可観測性の大幅な改善をもたらします。従来は切り詰められていたペイロード情報が完全に記録されるため、インシデント発生時のデバッグ効率が向上します。特に、CloudWatch Logs でリアルタイムアラームを設定しつつ、S3 Parquet 形式で長期保存する構成は、即応性とコスト効率を両立できます。

ただし、1 MB のログイベントが大量に発生する環境では CloudWatch Logs のコストが急増する可能性があるため、事前に想定トラフィックでの料金試算が必須です。また、S3 ライフサイクルポリシーを併用し、古いログを Glacier に移行するなど、ストレージコスト最適化も検討すべきです。Athena でのクエリ実行時は、パーティション設計（日付や API ステージ別など）を適切に行うことで、スキャンデータ量を削減し、クエリコストを抑制できます。

### Lambda durable functions のユースケース検討

AI エージェントの耐障害性強化は、特にミッションクリティカルなワークフローで有効です。例えば、顧客対応の自動化や、複雑なデータ処理パイプラインで、処理途中の中断が許容できない場合に適しています。Terraform で管理しているインフラがあれば、Lambda 関数の設定に durable functions オプションを追加するだけで導入でき、既存の監視・アラート体系もそのまま活用できます。

一方、意図的に再帰処理を行う Lambda 関数（例：分割統治アルゴリズムの実装）では、PutFunctionRecursionConfig API で無効化する必要があります。また、SDK バージョンの要件を満たしているか事前確認し、非対応バージョンでのフォールバック動作も把握しておくことが重要です。CloudWatch でのコスト監視と、AWS Health Dashboard での通知設定を組み合わせることで、予期しないループやコスト急増を早期検知できます。

---

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Transform for .NET が単体テスト自動生成に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-transform-net-unit-tests) | .NET Framework から最新 .NET への移行時に、ビジネスロジックやコントローラーの単体テストを自動生成。移行完了時点でテストカバレッジが確保され、手動記述の負荷を削減 |
| [Amazon API Gateway の実行ログが 1 MB に拡大、複数配信先に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-api-gateway-1-mb-execution-logs) | ログイベントサイズを 1 KB から 1 MB へ拡大。CloudWatch Logs、S3、Data Firehose への同時配信が可能。S3 では Parquet 形式で保存し Athena 分析に最適化 |
| [Lambda 再帰ループ検出がヨーロッパソブリンクラウドで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/lambda-recursion-europe-sovereign-cloud) | 意図しない再帰呼び出しを自動検出・停止し、予期しない課金を防止。S3、SQS、SNS などのイベントソースに対応 |
| [Amazon OpenSearch Serverless が Vercel v0 で利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-opensearch-serverless-available-V0-vercel) | ノーコード/ローコードプラットフォーム v0 で、自然言語プロンプトから検索・AI アプリケーションを構築。インフラ管理不要で自動スケーリング |
| [AWS Lambda durable functions が Pydantic AI と統合](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-durable-pydantic-ai) | AI エージェントの実行進捗を自動保存し、中断後は最後のステップから再開。トークンコスト削減と副作用の重複実行を防止 |
| [Amazon Redshift RG インスタンスがチューリッヒリージョンで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-redshift-rg-available-zurich) | Graviton プロセッサ搭載で RA3 比 2.4 倍高速、vCPU あたりコスト 30% 削減。Iceberg・Parquet データの直接処理に対応 |
| [第2世代シングルラック AWS Outposts が一般提供開始](https://aws.amazon.com/about-aws/whats-new/2026/09/single-rack-aws-outposts) | 42U 単一ラックで最大 2,688 vCPU、100TB EBS を提供。最新 EC2 インスタンス（M8i、C8i、R8i など）に対応し、スペース制約環境に最適化 |
| [Amazon MQ が RabbitMQ 4.3 をサポート](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-mq-rabbitmq-43) | Quorum Queue のディスクコンパクション、32 段階優先度、自動リトライ、細粒度タイムアウト制御を追加。m7g インスタンスで利用可能 |
| [CloudWatch が TGW リージョン間ピアリングのネットワーク健全性インジケータに対応](https://aws.amazon.com/about-aws/whats-new/2026/09/cloudwatch-network-monitoring-tgw-support) | 合成モニターで TGW ピアリング経由パスの健全性をリアルタイム監視。AWS ネットワーク起因の問題を迅速に特定 |
| [CloudWatch Network Monitor が TGW ピアリングの NHI を提供](https://aws.amazon.com/amazon-cloudwatch-network-monitor-nhi-transit-gateway-peering) | ハイブリッドネットワークパスのパケットロス・レイテンシーを測定。TGW リージョン間ピアリングのネットワークヘルスを CloudWatch メトリクスで取得 |
| [AWS Elemental MediaTailor が低遅延 HLS 広告挿入に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-elemental-mediatailor-low-latency-hls-ad-insertion) | HLS Interstials 技術で LL-HLS の低遅延を維持しながら広告挿入。同一キャッシュ可能なプレイリストで CDN 効率化 |
| [AWS Elemental に Dynamic Multiview 機能を追加](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-elemental-dynamic-multiview-video) | 複数ライブ映像を視聴者選択のタイルレイアウトで配信。再エンコード不要でコスト削減、標準 HLS/DASH 形式で既存デバイス対応 |
| [AWS Elemental Inference がライブビデオからリアルタイムメタデータ生成](https://aws.amazon.com/about-aws/whats-new/2026/09/elemental-inference-contextual-metadata) | IAB 分類、GARM ブランド適合性、オブジェクト検出、シーン説明を自動抽出。MediaTailor でコンテキスト対応広告配信を実現 |
| [AWS Elemental MediaTailor が Yield Optimization を提供](https://aws.amazon.com/about-aws/whats-new/2026/09/mediatailor-yield-optimization) | 未売却広告枠を Amazon Ads 需要で自動収益化。ゼロコストで有効化、価格フロア・カテゴリフィルタリングで制御可能 |
| [AWS Elemental MediaLive が A/B フォレンジック透かしに対応](https://aws.amazon.com/about-aws/whats-new/2026/09/medialive-ab-forensic-watermarking) | A/B 2 バリアント出力で視覚的に透明な透かしを付与。再エンコード・スクリーンキャプチャ後も保持され、流出コンテンツの出所を特定 |

---

## まとめ

今回のアップデートは、運用可視性、コスト最適化、AI ワークロード、メディア配信の 4 つの軸で大きな改善が見られます。API Gateway のログ強化は、インシデント対応の効率化と長期コスト削減を両立する実用的なアップデートです。Lambda durable functions と Pydantic AI の統合は、AI エージェントの本番運用における信頼性向上に寄与します。

AWS Elemental メディアサービス群の拡充は特に注目に値します。低遅延広告挿入、Dynamic Multiview、リアルタイムメタデータ生成、Yield Optimization、フォレンジック透かしという 5 つの機能追加は、ライブ配信プラットフォームの収益化・効率化・セキュリティ強化を総合的に支援します。

インフラ関連では、Redshift RG インスタンスのチューリッヒリージョン展開、第2世代 Outposts、RabbitMQ 4.3 対応など、既存システムの性能向上とコスト削減を狙える選択肢が増えました。CloudWatch のネットワーク監視拡充は、マルチリージョン構成の可観測性向上に直結します。

これらのアップデートを活用することで、運用負荷の軽減、コスト最適化、ユーザー体験の向上といった複数の課題に対処できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)