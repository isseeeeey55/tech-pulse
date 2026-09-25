---
title: "【AWS】2026/09/11 のアップデートまとめ"
date: 2026-09-11T08:02:20+09:00
draft: false
tags: ["aws", "api-gateway", "lambda", "opensearch", "redshift", "outposts", "mq", "cloudwatch", "elemental-mediatailor", "elemental-medialive", "elemental-mediapackage", "elemental-inference", "transform", "s3", "sqs", "sns", "data-firehose", "athena", "cloudfront", "ec2"]
categories: ["AWS Updates"]
summary: "2026/09/11 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260911/header.png)

# 今回は、直近で発表された14件のAWSアップデートを紹介します

## はじめに

今回の14件の中心は、Amazon API Gateway の実行ログの拡張、AWS Elemental メディアサービス群への5機能の追加、AWS Lambda durable functions と Pydantic AI の統合です。このほか、AWS Transform for .NET の単体テスト生成、第2世代シングルラック Outposts、Amazon MQ の RabbitMQ 4.3 対応、CloudWatch のネットワーク監視拡張などが含まれます。

> **Note:** 「CloudWatch Network Monitor now provides NHI for Transit Gateway peering」という告知も通知されましたが、リンク先が存在せず（404）、内容は同日の「Amazon CloudWatch now supports network health indicator for TGW inter-Region peering using synthetic monitors」と同じ機能のため、1件にまとめています。

---

## 注目アップデート深掘り

### Amazon API Gateway：実行ログの大幅強化と柔軟な配信先設定

Amazon API Gateway の REST API 実行ログで、配信先を選べるようになり、ログイベントのサイズ上限も拡大されました。これまで実行ログは API Gateway が管理する単一の CloudWatch Logs ロググループに配信され、ログイベントは 1 KB で切り詰められていました。

**ログサイズの拡大と可視性の向上**

実行ログを最大 **1 MB** まで記録できるようになり、これまで 1 KB で切り詰められていたリクエスト・レスポンスのデータを確認しやすくなりました。

**複数配信先への同時送信**

配信先として、自分の CloudWatch Logs ロググループ、Amazon S3 バケット、Amazon Data Firehose ストリームを選べ、**複数の配信先へ同時に**送れます。告知の例は、S3 に Apache Parquet 形式で送って低コストの長期保存と Amazon Athena での分析に使いつつ、CloudWatch Logs には構造化 JSON ログを送ってリアルタイムのアラートに使う構成です。

**設定と料金**

設定は API Gateway コンソール、AWS CLI、AWS CloudFormation から行えます。この機能で配信される実行ログは vended logs の料金で課金されます。AWS GovCloud (US) を含む、API Gateway REST API が提供されているすべてのリージョンで利用できます。

### AWS Lambda durable functions と Pydantic AI の統合

AWS Lambda durable functions が、Python で AI エージェントを構築するオープンソースのフレームワーク Pydantic AI と統合されました。

**AI エージェントにおける課題**

告知の例は、一連のドキュメントをレビューしたり、多くの情報源にまたがってトピックを調べたりするモデル呼び出しの連鎖です。途中で中断して最初からやり直すと、同じ作業のトークン代を再び支払うことになり、顧客への二重請求のような副作用が起きることもあります。

**durable functions による自動チェックポイント**

Lambda durable functions は、Pydantic AI エージェントの進捗を実行中に保存します。エージェントの各モデル呼び出し・ツール呼び出しが durable execution のステップになるため、タイムアウトなどで中断しても最後に完了したステップから再開し、完了済みの呼び出しは繰り返しません。

**実装の透明性**

Python の Lambda durable function であれば利用でき、Lambda durable functions が提供されているすべてのリージョンで使えます。使い始めるには、Pydantic AI をインストールし、Pydantic AI の AWS Lambda durability のページか、durable execution SDK のリファレンスに従います。

---

## SRE 視点での活用ポイント

### API Gateway ログの運用設計

これまで 1 KB で切り詰められていたペイロードを最大 1 MB まで記録できるため、インシデント調査で実際のリクエスト・レスポンスを確認しやすくなります。CloudWatch Logs でアラートを設定しつつ、S3 に Parquet で長期保存する構成が取れます。

ただし、ログイベントが大きくなる分、ログ量と vended logs の料金も増えるため、想定トラフィックで料金を試算してから有効化します。

### Lambda durable functions のユースケース検討

多くのモデル呼び出しやツール呼び出しを連ねる Pydantic AI エージェントを Lambda で動かしている場合、中断後に完了済みのステップを再実行しない構成にできます。決済のように二重実行が問題になる操作をツールとして呼ぶエージェントでは、特に検討する価値があります。

### Lambda 再帰ループ検出（European Sovereign Cloud）

AWS European Sovereign Cloud でも、Lambda の再帰ループ検出が使えるようになりました。S3・SQS・SNS などのイベントソースで意図しない再帰呼び出しが発生した場合に検出して停止します。意図的に再帰させている関数がある場合は、関数ごとの再帰ループ設定を確認します。

---

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Transform for .NET が単体テスト自動生成に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-transform-net-unit-tests) | .NET Framework から最新 .NET への移行時に、ビジネスロジックやコントローラーの単体テストを自動生成。移行完了時点でテストカバレッジが確保され、手動記述の負荷を削減 |
| [Amazon API Gateway の実行ログが 1 MB に拡大、複数配信先に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-api-gateway-1-mb-execution-logs) | ログイベントサイズを 1 KB から 1 MB へ拡大。CloudWatch Logs、S3、Data Firehose への同時配信が可能。S3 では Parquet 形式で保存し Athena 分析に最適化 |
| [Lambda 再帰ループ検出がヨーロッパソブリンクラウドで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/lambda-recursion-europe-sovereign-cloud) | 意図しない再帰呼び出しを自動検出・停止。S3、SQS、SNS などのイベントソースに対応 |
| [Amazon OpenSearch Serverless が Vercel v0 で利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-opensearch-serverless-available-V0-vercel) | アイデアを本番対応の Web アプリケーションにする AI プラットフォーム v0 で、自然言語プロンプトから OpenSearch Serverless を使うアプリを構築可能に。インフラ管理不要で需要に応じて自動スケーリング |
| [AWS Lambda durable functions が Pydantic AI と統合](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-durable-pydantic-ai) | AI エージェントの実行進捗を自動保存し、中断後は最後のステップから再開。トークンコスト削減と副作用の重複実行を防止 |
| [Amazon Redshift RG インスタンスがチューリッヒリージョンで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-redshift-rg-available-zurich) | Graviton プロセッサ搭載。前世代 RA3 比で最大 2.4 倍高速、vCPU あたりの価格は 30% 低い。Iceberg・Parquet データの直接処理に対応 |
| [第2世代シングルラック AWS Outposts が一般提供開始](https://aws.amazon.com/about-aws/whats-new/2026/09/single-rack-aws-outposts) | 42U 単一ラックで最大 2,688 vCPU、100TB EBS を提供。最新 EC2 インスタンス（M8i、C8i、R8i など）に対応し、スペース制約環境に最適化 |
| [Amazon MQ が RabbitMQ 4.3 をサポート](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-mq-rabbitmq-43) | Quorum Queue のディスクコンパクション、32 段階優先度、自動リトライ、細粒度タイムアウト制御を追加。m7g インスタンスで利用可能 |
| [CloudWatch が TGW リージョン間ピアリングのネットワーク健全性インジケータに対応](https://aws.amazon.com/about-aws/whats-new/2026/09/cloudwatch-network-monitoring-tgw-support) | 合成モニターで TGW ピアリング経由パスの健全性をリアルタイム監視。AWS ネットワーク起因の問題を迅速に特定 |
| [AWS Elemental MediaTailor が低遅延 HLS 広告挿入に対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-elemental-mediatailor-low-latency-hls-ad-insertion) | HLS Interstitials で LL-HLS の低遅延を維持しながら広告挿入。同一キャッシュ可能なプレイリストで CDN 効率化 |
| [AWS Elemental に Dynamic Multiview 機能を追加](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-elemental-dynamic-multiview-video) | 複数ライブ映像を視聴者選択のタイルレイアウトで配信。再エンコード不要でコスト削減、標準 HLS/DASH 形式で既存デバイス対応 |
| [AWS Elemental Inference がライブビデオからリアルタイムメタデータ生成](https://aws.amazon.com/about-aws/whats-new/2026/09/elemental-inference-contextual-metadata) | IAB 分類、GARM ブランド適合性、オブジェクト検出、シーン説明を自動抽出。MediaTailor でコンテキスト対応広告配信を実現 |
| [AWS Elemental MediaTailor が Yield Optimization を提供](https://aws.amazon.com/about-aws/whats-new/2026/09/mediatailor-yield-optimization) | 未売却広告枠を Amazon Ads 需要で自動収益化。ゼロコストで有効化、価格フロア・カテゴリフィルタリングで制御可能 |
| [AWS Elemental MediaLive が A/B フォレンジック透かしに対応](https://aws.amazon.com/about-aws/whats-new/2026/09/medialive-ab-forensic-watermarking) | A/B 2 バリアント出力で視覚的に透明な透かしを付与。再エンコード・スクリーンキャプチャ後も保持され、流出コンテンツの出所を特定 |

---

## まとめ

API Gateway の実行ログは最大 1 MB になり、複数の配信先へ同時に送れるようになりました。Lambda durable functions と Pydantic AI の統合では、エージェントの各モデル呼び出し・ツール呼び出しがチェックポイントされ、中断後は最後に完了したステップから再開します。

AWS Elemental では、低遅延 HLS の広告挿入、Dynamic Multiview、ライブ映像からのリアルタイムメタデータ生成、Yield Optimization、A/B フォレンジック透かしの5機能が追加されました。

インフラ関連では、Redshift RG インスタンスのチューリッヒリージョン展開、第2世代 Outposts、RabbitMQ 4.3 対応が加わりました。CloudWatch の合成モニターでは、Transit Gateway のリージョン間ピアリングを通るパスにもネットワーク健全性インジケータ（NHI）が使えるようになりました。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)