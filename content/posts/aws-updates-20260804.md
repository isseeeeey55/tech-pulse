---
title: "【AWS】2026/08/04 のアップデートまとめ"
date: 2026-08-04T08:02:01+09:00
draft: false
tags: ["aws", "ec2", "gamelift", "sagemaker", "resilience-hub", "healthomics", "config", "waf", "ecr", "aurora", "fis"]
categories: ["AWS Updates"]
summary: "2026/08/04 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260804/header.png)

# 直近の AWS アップデート 9 件まとめ — ストレージ最適化インスタンスの新リージョン展開、レジリエンステスト自動化、ECR レイヤー拡大など

## はじめに

今回は、直近で発表された 9 件の AWS アップデートを紹介します。EC2 の高性能ストレージインスタンス I7i が新リージョンに展開され、AWS Resilience Hub がレジリエンステストの推奨機能を追加しました。また Amazon ECR のイメージレイヤー上限が 200GB に拡大され、大規模な機械学習モデルやゲノミクスデータを含むコンテナのデプロイが容易になります。SageMaker AI のサーバーレスモデルカスタマイズがフルファインチューニングに対応し、AWS Config が 15 の新リソースタイプをサポートするなど、運用性・セキュリティ・AI/ML の各領域で重要な機能強化が行われています。

## 注目アップデート深掘り

### AWS Resilience Hub の推奨レジリエンステスト機能

AWS Resilience Hub に新たに追加された**推奨レジリエンステスト**機能は、プラットフォームエンジニアリングチームや SRE チームが既知の障害シナリオに対するサービスの応答と復旧を体系的に検証できるようにします。

#### なぜこのアップデートが重要なのか

告知は本機能を、プラットフォームエンジニアリングチームと SRE チームが「既知の障害シナリオに対してサービスがどう応答し復旧するか」を検証するためのものと位置づけています。障害注入には **AWS Fault Injection Service (FIS)** を使用し、定義した復旧目標の範囲内でサービスが復旧するかを評価します。

#### 機能の仕組みと特徴

告知が説明しているテストの流れは以下のとおりです。

1. **自動ターゲット選定**: 各テストがサービス内のリソースを自動的にターゲットにします
2. **障害注入実行**: 必要な障害を注入します。対象シナリオとして挙げられているのは、**アベイラビリティゾーンの障害（Availability Zone impairment）、リージョンの障害（Regional impairment）、依存関係の障害（dependency failure）** です
3. **合否判定**: **アラーム評価と復旧目標**に基づいて、合格・不合格の結果を出力します
4. **詳細レポート生成**: テストの詳細レポートを生成します

サービスの構成変更が頻繁に行われる環境では、変更のたびにレジリエンステストを CI/CD パイプラインに組み込むことで、リグレッションを早期に発見できます。

> **Note:** 本機能は以下の 15 リージョンで利用可能です — 米国東部（バージニア北部・オハイオ）、米国西部（オレゴン）、カナダ（中部）、欧州（アイルランド・ロンドン・フランクフルト・パリ・ストックホルム）、アジアパシフィック（ムンバイ・シンガポール・シドニー・東京・ソウル）、南米（サンパウロ）。詳細な設定方法は [AWS Resilience Hub の公式ドキュメント](https://docs.aws.amazon.com/resilience-hub/)を参照してください。

### Amazon ECR のイメージレイヤー上限 200GB への拡大

Amazon ECR（Elastic Container Registry）が Docker push 経由で送信するコンテナイメージのレイヤーサイズ上限を **200GB** に拡大しました。これは、大規模なアセットをコンテナイメージに含める必要がある現代的なワークロードに対応する重要な改善です。

#### 背景と課題

告知がユースケースとして挙げているのは、**大規模言語モデルの埋め込み、ゲノミクスデータセットのバンドル、大容量バイナリ依存関係のパッケージ化**の3つです。いずれも単一のファイルが大きくなりやすく、レイヤーサイズの上限が制約になりやすい領域です。

なお、拡大前の上限値は告知に記載されていません。

#### 改善効果

200GB への上限拡大により、大規模モデルやデータセットを単一レイヤーとして直接コンテナイメージに含めることが可能になります。これにより以下のメリットが得られます。

1. **ビルドプロセスの簡素化**: 複雑な分割ロジックが不要になり、Dockerfile がシンプルになります
2. **デプロイの高速化**: コンテナレジストリからのプル時にすべてが揃っているため、外部ダウンロード待ちが不要
3. **CI/CD の効率化**: 単一のアーティファクトとして管理でき、バージョン管理が容易

#### 実装における注意点

告知は「AWS SDK または CLI（`UploadLayerPart` API）を使ってプッシュされたイメージは 50GB の制限のまま」と明記しています。200GB の上限は Docker push 経由のイメージにのみ適用されます。このため、既存の自動化スクリプトで SDK/CLI を直接使用している場合は、Docker push を使う方式に切り替える必要があります。

また、200GB のレイヤーを含むイメージは、ネットワーク帯域幅とプル時間に影響を与えます。高速なネットワーク環境（VPC エンドポイント経由など）を使用するか、頻繁にデプロイされるサービスではイメージのキャッシュ戦略を慎重に設計することが推奨されます。

ストレージコストについても考慮が必要です。ECR の料金は保存データ量に基づくため、200GB のレイヤーを含む複数バージョンのイメージを保持する場合、ライフサイクルポリシーを適切に設定してコストを管理する必要があります。

> **Note:** この機能はバーレーンおよび UAE リージョンを除くすべての AWS リージョンで利用可能です。

## SRE 視点での活用ポイント

### レジリエンステストの継続的な実行

AWS Resilience Hub の推奨レジリエンステスト機能は、SRE チームがレジリエンスを「測定可能な指標」として扱えるようにします。Terraform で管理されているインフラであれば、コードの変更後に自動的にレジリエンステストを実行する CI/CD ステージを追加することで、アーキテクチャ変更が復旧目標に与える影響を事前に検証できます。

特に、マイクロサービスアーキテクチャでは依存関係が複雑化しがちです。依存サービスの障害シナリオを自動テストすることで、サービスメッシュやサーキットブレーカーの設定が適切に機能しているかを定期的に確認できます。導入時には、まずステージング環境で実行し、アラームの閾値や復旧目標の妥当性を検証してから本番環境に展開するアプローチが有効です。

### 大規模コンテナイメージの管理戦略

ECR のレイヤー上限拡大は、機械学習推論基盤を運用する SRE チームにとって大きな改善です。LLM を含むコンテナイメージをそのままデプロイできるため、外部ストレージとの同期処理やダウンロード失敗時のリトライロジックが不要になります。

一方で、200GB のイメージをプルする時間は無視できません。Amazon EKS や ECS で大規模イメージを運用する場合、ノードの事前ウォームアップ（イメージキャッシュ）戦略が重要です。たとえば、スケールアウト前に新しいノードでバックグラウンドプルを実行しておくことで、実際のトラフィック増加時の起動時間を短縮できます。

また、イメージのバージョン管理とライフサイクルポリシーを慎重に設計する必要があります。モデルの更新頻度が高い場合、古いバージョンを自動削除するポリシーを設定しないとストレージコストが急速に増加します。CloudWatch のコスト異常検出と組み合わせることで、予期しないコスト増加を早期に発見できます。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| **Amazon EC2** | [I7i インスタンスがアジアパシフィック（タイ）・イスラエル（テルアビブ）リージョンで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-i7i-instances-in-additional-regions/) | 全コアターボ 3.2GHz の第 5 世代 Intel Xeon プロセッサ搭載。前世代 I4i 比で計算性能が**最大 23%** 向上、価格性能比は **10% 以上**改善。リアルタイムストレージ性能が最大 50% 向上、ストレージ I/O レイテンシが最大 50% 低下、同レイテンシの変動が最大 60% 低減。最大 45TB の NVMe ストレージ。 |
| **Amazon GameLift** | [Streams でストリーム URL 共有をサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-gamelift-streams/) | AWS アカウント不要でブラウザからゲームストリーム再生が可能に。CreateStreamUrl、GetStreamUrl、ListStreamUrls、RevokeStreamUrl API を提供。 |
| **Amazon SageMaker** | [AI サーバーレスモデルカスタマイズがフルファインチューニングをサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-sagemaker-fft) | 25 を超えるオープンソースモデル（gpt-oss、Gemma、Llama、Nemotron、Qwen の各ファミリー）に対応。重みの一部のみ更新する LoRA 等のパラメータ効率手法に対し、全パラメータを更新してより深く適応させられる。米国東部（バージニア北部）、米国西部（オレゴン）、アジアパシフィック（東京）、欧州（アイルランド）で利用可能。 |
| **AWS Resilience Hub** | [推奨レジリエンステスト機能を提供](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-resilience-hub/) | サービスアーキテクチャに基づく事前設定済みテスト。AWS FIS を使用した制御された障害注入、自動合否判定、詳細レポート生成。 |
| **AWS HealthOmics** | [WDL ワークフローでタスクレベルタイムアウトをサポート](https://docs.aws.amazon.com/omics/latest/dev/workflow-languages-wdl.html)（※） | WDL タスクの `runtime` セクションに `omicsTimeout` 属性を指定してタスクの最大実行時間を設定できる。値は整数（秒）または `s` / `m` / `h` / `d` を組み合わせた文字列（`"40m"`、`"1h30m"` など）。粒度は1分で、60秒未満の値は60秒に切り上げられる。 |
| **AWS Config** | [15 の新しいリソースタイプをサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-config-new-resource-types) | AppSync、Bedrock、Connect、Glue、OpenSearch Serverless、SageMaker など主要サービスのリソースを追跡可能に。Config rules および aggregators でも利用可能。 |
| **AWS WAF** | [Miggo Security 管理ルールグループをサポート](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-waf-miggo-managed-rule-groups) | 「Miggo Rules for AWS WAF – High Emerging Application Threats」と「Miggo Rules for AWS WAF – AI/ML Application Protection」の 2 つを提供。前者は CISA Known Exploited Vulnerabilities (KEV) カタログ掲載の脆弱性、後者は AI エージェントフレームワーク・LLM ゲートウェイ・モデルサービング基盤といった生成 AI スタックを対象。料金は Miggo が AWS Marketplace で設定。 |
| **AWS Transform** | [Windows モダナイゼーションでオフラインスキーマ変換をサポート](https://aws.amazon.com/about-aws/whats-new/2026/7/aws-transform-windows-sql-schema-aurora) | SQL Server の DDL ファイルをアップロードし、データベースとストアドプロシージャの複雑度を評価して変換プランを生成。テーブル・スキーマとストアドプロシージャ等のコードオブジェクトを変換し、機能的等価性を検証したうえで Aurora PostgreSQL へデプロイ。.NET アプリケーションの接続文字列、ADO.NET、Entity Framework のデータアクセス呼び出しも更新。米国東部（バージニア北部）で利用可能。 |
| **Amazon ECR** | [イメージレイヤー上限を 200GB に拡大](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecr-image-layers/) | Docker push 経由のイメージで最大 200GB の単一レイヤーをサポート。LLM の埋め込み、ゲノミクスデータセットのバンドル、大容量バイナリ依存関係のパッケージ化が対象。SDK/CLI（`UploadLayerPart` API）経由は 50GB のまま。中東（バーレーン・UAE）を除く全リージョンで利用可能。 |

※ AWS HealthOmics の告知については、RSS フィードが返す What's New の URL が現時点で 404 を返すため、`omicsTimeout` 属性の仕様を記載した公式ドキュメントへリンクしています。

## まとめ

今回紹介したアップデートは、運用性の向上、セキュリティの強化、AI/ML ワークロードへの対応という 3 つの軸で AWS エコシステムを拡張しています。

AWS Resilience Hub の推奨レジリエンステスト機能は、カオスエンジニアリングの実践を大幅に簡素化し、SRE チームがレジリエンスを継続的に測定・改善するための基盤を提供します。一方、Amazon ECR のレイヤー上限拡大は、機械学習やゲノミクスなど大規模データを扱うワークロードのデプロイメントプロセスを簡素化します。

AWS Config の新リソースタイプ対応や AWS WAF の Miggo Security 管理ルールグループは、セキュリティ運用の自動化とカバレッジ拡大を促進します。特に Bedrock や SageMaker など AI/ML サービスのリソース追跡が可能になったことは、ガバナンスの観点で重要です。

SageMaker のフルファインチューニング対応は、ドメイン特化型 AI モデルの構築を容易にし、AWS Transform のオフラインスキーマ変換はレガシーシステムのモダナイゼーションを加速します。これらのアップデートを組み合わせることで、現代的なクラウドネイティブアーキテクチャへの移行と運用効率化を同時に実現できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)