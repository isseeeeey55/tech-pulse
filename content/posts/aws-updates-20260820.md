---
title: "【AWS】2026/08/20 のアップデートまとめ"
date: 2026-08-20T08:02:35+09:00
draft: false
tags: ["aws", "ec2", "sagemaker", "athena", "redshift", "emr", "lake-formation", "iam-identity-center", "cloudtrail", "bedrock", "cost-anomaly-detection", "cost-explorer", "workspaces", "opensearch", "quick", "corretto", "cloudwatch", "european-sovereign-cloud"]
categories: ["AWS Updates"]
summary: "2026/08/20 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260820/header.png)

# 直近の AWS アップデート情報まとめ（2026年8月）

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。ロンドンリージョンへの新しいアベイラビリティゾーン追加、Amazon SageMaker NotebooksのTrusted Identity Propagation対応、Amazon BedrockでのGrok 4.6やOpenAIモデルのサポート拡大など、幅広い領域でのアップデートが発表されました。特にセキュリティとガバナンス強化、生成AIワークロードの拡充、インフラ容量の拡大が際立っています。

本記事では、特に運用面でのインパクトが大きいアップデートを深掘りし、SRE視点での活用ポイントを整理していきます。

## 注目アップデート深掘り

### Amazon SageMaker notebooks の Trusted Identity Propagation 対応

Amazon SageMaker Notebooks が **Trusted Identity Propagation (TIP)** に対応しました。これにより、Amazon Athena、Amazon Redshift、Amazon EMR Serverless との連携時に、ユーザーごとのアクセス制御が実現します。

#### なぜこのアップデートが重要なのか

従来、SageMaker Notebooks では共通の実行ロール（Execution Role）を使用してデータアクセスを行っていたため、ノートブックを利用するすべてのユーザーが同じ権限を持つ状態でした。これは以下のような課題を抱えていました：

- **過剰なアクセス権限**: データアナリストが本来不要なデータまでアクセス可能
- **監査の困難性**: CloudTrail ログでは実行ロールの操作は記録されるが、実際の利用者が特定しにくい
- **コンプライアンスリスク**: 金融や医療などの規制業界では、ユーザー単位の厳密なアクセス制御が求められる

TIP はこれらの課題を根本的に解決します。IAM Identity Center で認証されたユーザーの認証情報が AWS Lake Formation に自動的に伝播され、そのユーザーに付与された権限に基づいてのみテーブル、カラム、行にアクセスできるようになります。

#### 仕組みと従来方式との違い

**従来の方式**では、以下のようなフローでした：

1. ユーザーが SageMaker Notebook にログイン
2. Notebook は単一の IAM 実行ロールを使用
3. すべてのユーザーが実行ロールの権限でデータにアクセス
4. CloudTrail には実行ロールの操作のみ記録

**TIP 対応後**のフローは次のように変わります：

1. ユーザーが IAM Identity Center で認証
2. ユーザーの Identity が SageMaker Unified Studio の Project に紐づく
3. データアクセス時に Lake Formation がユーザーの Identity を評価
4. ユーザーに付与された細粒度権限（テーブル、カラム、行レベル）で制御
5. CloudTrail にはユーザー単位の操作が記録

#### セキュリティと監査の強化

TIP による最大のメリットは、**ユーザーごとのデータ境界が自動で強制**される点です。管理者は Lake Formation で以下のような細粒度権限を設定できます：

- 特定のテーブルへのアクセス許可
- 特定のカラムのみを表示（例：個人情報カラムを特定ユーザーからは隠す）
- 行レベルフィルタ（例：所属部門のデータのみ表示）

さらに、CloudTrail では **誰がどのデータにいつアクセスしたか**を完全に監査できます。これにより、規制業界で求められるアクセスログの追跡要件を満たすことができます。

#### 実装のポイント

TIP を利用するには、SageMaker Unified Studio の TIP 対応 Project にノートブックを接続する必要があります。セットアップ後は、追加のログイン管理やトークン管理は不要です。Lake Formation で事前に権限を設定しておけば、ユーザーがノートブックで Athena、Redshift、EMR Serverless にアクセスする際、自動的にユーザー Identity に基づいた権限が適用されます。

対応するエンジンは Athena、Redshift、EMR Serverless の3つです。本機能は、Amazon SageMaker Unified Studio が利用可能な全 AWS リージョンで提供されます。

### AWS Cost Anomaly Detection の Amazon Bedrock 対応

AWS Cost Anomaly Detection が Amazon Bedrock 上の第三者製基盤モデル（Anthropic Claude など）に対応しました。これにより、生成 AI ワークロードの予期しない支出変動を自動検出できるようになります。

#### 生成 AI ワークロードにおけるコスト管理の課題

生成 AI ワークロードは、従来の AWS ワークロードと比較してコスト特性が大きく異なります：

- **トークン従量課金**: モデル呼び出しごとに入力・出力トークン数に応じて課金
- **予測困難性**: ユーザーの質問内容や応答の長さによってコストが変動
- **バグの影響が大**: 無限ループや不適切なリトライ処理で想定外のコストが発生
- **複数モデル利用**: 用途に応じて Claude、GPT など複数モデルを使い分けるため、コスト追跡が複雑

このような特性から、生成 AI ワークロードでは予期しないコスト急増が発生しやすく、早期検知の仕組みが不可欠です。

#### Cost Anomaly Detection の仕組み

Cost Anomaly Detection は、機械学習を使用して過去のコスト傾向を学習し、通常の変動と異常な変動を区別します。今回の対応により、Bedrock 上の第三者製モデルの利用コストも監視対象に加わりました。異常を検出した際の根本原因は、以下の軸で分解されます：

- AWS サービス
- アカウント（複数アカウントを運用している場合）
- リージョン
- 使用タイプ

**セットアップ不要**で、AWS マネージドサービスモニターを通じて自動的に Bedrock モデルの利用コストが監視対象に含まれます。

#### 異常検出時の詳細情報

モデルの支出が予期せず変動すると、アラートとあわせて、ドル影響額の大きい順にランク付けされた根本原因の内訳が提供されます。

これにより、例えば「特定の開発アカウントで Claude モデルの呼び出しが急増している」といった具体的な状況を、他の AWS 支出と同じ速度で把握し、対処できます。

なお本機能は、AWS GovCloud と中国リージョンを除く、全ての AWS 商用リージョンで利用可能です。

#### 他のコスト管理ツールとの使い分け

AWS には複数のコスト管理ツールがありますが、Cost Anomaly Detection は以下の点で特徴的です：

- **AWS Budgets**: 事前に設定した閾値を超えた際にアラート（予測的ではなく閾値ベース）
- **Cost Explorer**: コストの可視化と分析（異常検出機能なし）
- **Cost Anomaly Detection**: 機械学習による自動異常検出（閾値設定不要）

Bedrock ワークロードでは、まず Cost Anomaly Detection で異常を早期検知し、Cost Explorer で詳細分析を行い、必要に応じて Budgets でハードリミットを設定する、という組み合わせが効果的です。

### Amazon Bedrock の Grok 4.6 サポート

Amazon Bedrock が SpaceXAI の Grok 4.6 をサポートし、US Geo と Global の2つのクロスリージョン推論プロファイルが利用できるようになりました。Grok 4.6 は、コーディング、エージェント的なタスク、ナレッジワーク向けに構築されたフロンティアモデルです。

#### クロスリージョン推論という提供形態

今回のサポートで特徴的なのは、モデル単体ではなくクロスリージョン推論とセットで提供される点です。クロスリージョン推論は、推論リクエストを複数の AWS リージョンにまたがって自動的にルーティングする仕組みで、リージョンごとのキャパシティ管理を利用者が行うことなくスループットを高められます。

用意されたプロファイルは2種類です。

- **US Geo（`us.xai.grok-4.6`）**: リクエストを米国の地理的範囲内のみでルーティングします。データが米国内で処理される状態を保ちながらスケールできるため、データレジデンシー要件がある場合に選択します
- **Global（`global.xai.grok-4.6`）**: モデルが利用可能な任意の商用 AWS リージョンからリクエストを処理します。Bedrock のキャパシティに最も広くアクセスでき、需要のスパイク時に最も高いスループットが得られるうえ、トークンあたりの単価も低くなります

どちらを選ぶかは、データレジデンシー要件の有無と、スループット・単価のどちらを優先するかで決まります。規制上の制約がなければ Global、米国内での処理が要件なら US Geo という整理になります。

#### 既存の運用統制がそのまま効く

Grok 4.6 は `bedrock-runtime` エンドポイント上で動作し、Responses、Chat Completions、Converse の各 API に対応します。アカウントレベルの統制についても、他の Bedrock モデルで使っているものがそのまま適用されます。

- モデル呼び出しのロギング（Amazon S3 または Amazon CloudWatch Logs へ配信可能）
- Amazon CloudWatch メトリクス
- AWS Cost Explorer および AWS Cost and Usage Report でのコスト内訳

監査ログの集約先やコスト配分の仕組みを新たに作り直す必要はなく、既存の Bedrock ワークロードに対して行っている監視・コスト管理の運用にそのまま組み込めます。

Grok 4.6 のクロスリージョン推論は、Amazon Bedrock が提供されている全 AWS リージョンで利用可能です。

## SRE視点での活用ポイント

### マルチAZ構成とディザスタリカバリの見直し

ロンドンリージョンへの4番目のAZ追加は、SREにとって高可用性アーキテクチャを再設計する好機です。特に以下の点を検討する価値があります：

**フェイルオーバー戦略の見直し**: アプリケーションを4つの AZ に分散配置できるようになり、フォールトトレランスと高可用性構成の選択肢が広がります。ステートレス層を4AZに分散すれば、1AZ 障害時に残り3AZで負荷を吸収することになるため、AZ あたりに確保しておく余剰キャパシティを3AZ構成より小さく抑えられます。なお、Amazon RDS や Aurora のマルチAZ構成が使用する AZ 数はサービス側の仕様で決まります。リージョンの AZ が4つに増えたからといって、DB 層の冗長度が自動的に上がるわけではない点には注意が必要です。

**AI/MLワークロードの可用性向上**: Trn3、P6 といった最新アクセラレーテッドインスタンスが新AZで利用可能になることで、学習ジョブをAZ障害から保護できます。例えば、Kubernetes（EKS）のノードグループを4AZ間に分散配置し、特定AZでハードウェア障害が発生しても学習を継続できる構成が現実的になりました。

**コスト面の注意点**: AZ をまたぐ通信が増えれば、AZ 間データ転送コストも増えます。VPC フローログを CloudWatch Logs Insights や Athena で分析し、不要な AZ 間通信を最小化する設計が重要です。なお、新 AZ には Europe (London) リージョンの標準料金が適用されます。

### データガバナンスの強化と監査自動化

SageMaker Notebooks の TIP 対応は、データガバナンス強化を検討する組織にとって導入を検討すべき機能です。

**監査ログの自動化**: CloudTrail でユーザー単位のデータアクセスが記録されるため、Athena や OpenSearch を使った監査ログダッシュボードを構築すれば、「誰がいつどのテーブルにアクセスしたか」をリアルタイムで可視化できます。これにより、月次の手動監査作業を大幅に削減できます。

**インシデント対応の迅速化**: データ漏洩インシデント発生時、従来は「共有実行ロールを使っていた全ユーザーが容疑者」という状態でしたが、TIP によりアクセスログから真の操作者を即座に特定できます。ランブックに「CloudTrail ログから該当ユーザーを特定する手順」を追加しておくと、初動対応が迅速化します。

**段階的な導入戦略**: 既存の SageMaker Notebooks 環境から TIP 対応環境への移行は、一度に全チームで行うのではなく、まずコンプライアンス要件が最も厳しいプロジェクトから段階的に導入することをおすすめします。移行時には Lake Formation での権限設計が必要になるため、データ管理者とセキュリティチームの巻き込みが不可欠です。

### 生成AIワークロードのコスト監視体制

Cost Anomaly Detection の Bedrock 対応により、生成 AI ワークロードの「コストサプライズ」を未然に防ぐ体制が整います。

**アラート通知の設計**: SNS トピック経由で Slack や PagerDuty に異常検出アラートを送信する仕組みを構築すれば、営業時間外のコスト急増にも迅速に対応できます。特に開発環境では、開発者が誤って大量のモデル呼び出しを行うケースが多いため、開発アカウント専用のアラートチャンネルを用意すると効果的です。

**ポストモーテムへの活用**: コスト異常が発生した際は、Cost Explorer でドリルダウンして原因を特定し、ポストモーテムドキュメントに記録します。「特定の API エンドポイントでリトライロジックが不適切だった」「特定のユースケースでプロンプトが長すぎた」といった知見を蓄積することで、将来の再発を防止できます。

**予算管理との組み合わせ**: Cost Anomaly Detection は「異常検出」、AWS Budgets は「上限管理」という役割分担です。開発環境では Budgets でハードリミット（例：月額 $1,000）を設定し、本番環境では Cost Anomaly Detection で日次の変動を監視する、という使い分けが推奨されます。

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| インフラ | [AWS announces a new Availability Zone in the Europe (London) Region](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-new-availability-zone-europe/) | ロンドンリージョン（eu-west-2）に4番目のAZ（eu-west-2d）を追加。AI/ML向けの最新アクセラレーテッドインスタンス（Trn3、P6）をサポート |
| セキュリティ | [Amazon SageMaker notebooks now support trusted identity propagation](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-sagemaker/) | SageMaker Notebooks が TIP に対応。IAM Identity Center 経由でユーザーごとのアクセス制御を実現 |
| コスト管理 | [AWS Cost Anomaly Detection supports third-party models on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-cost-anomaly-detection-bedrock-3P/) | Bedrock 上の第三者製基盤モデル（Anthropic Claude など）のコスト異常を自動検出 |
| モニタリング | [Amazon WorkSpaces Applications now offers in-console monitoring capabilities](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-workspaces-applications-console-monitoring) | WorkSpaces Applications にネイティブモニタリング機能を搭載。セッション・インスタンスレベルのメトリクスをリアルタイム表示 |
| データ統合 | [Amazon OpenSearch Ingestion is now available in GovCloud Regions](https://aws.amazon.com/about-aws/whats-new/2026/08/opensearch-ingestion-available-govcloud-regions) | OpenSearch Ingestion が GovCloud (US-East/West) で利用可能に。ノーコードでデータ変換・削除・ルーティング |
| セキュリティ | [Amazon Quick adds deny by default for custom permissions](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-quick-deny-by-default/) | Amazon Quick のカスタム権限に「デフォルト拒否」機能を追加。新 AI 機能を事前制限可能に |
| AI/ML | [Amazon Bedrock now supports SpaceXAI Grok 4.6](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-grok-4-6/) | Bedrock が Grok 4.6 をサポート。US Geo（`us.xai.grok-4.6`）と Global（`global.xai.grok-4.6`）のクロスリージョン推論プロファイルを提供 |
| セキュリティ | [AWS IAM identity federation to external services is now available in AWS European Sovereign Cloud Region](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-iam-european-sovereign-cloud/) | AWS European Sovereign Cloud で IAM outbound identity federation が利用可能に。短寿命 JWT で外部サービスに認証 |
| AI/ML | [Amazon Bedrock now supports OpenAI models in India](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-openai-india-v1/) | Bedrock がインドで OpenAI GPT-5.6 モデル（Terra/Luna）をサポート。クロスリージョン推論でデータレジデンシー要件に対応 |
| セキュリティ | [Amazon Corretto August 2026 Critical Security Patch Updates](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-corretto-august-2026-security-updates) | Corretto の複数バージョン（8/11/17/21/25/26）に重大なセキュリティパッチを公開 |

## まとめ

今回紹介したアップデートは、以下の3つの大きなトレンドを反映しています：

**1. セキュリティとガバナンスの強化**: SageMaker Notebooks の TIP 対応、Amazon Quick のデフォルト拒否機能、IAM identity federation の拡大など、細粒度なアクセス制御と監査機能の充実が目立ちます。規制対応やコンプライアンス要件が厳しい業界では、これらの機能を活用することで運用負荷を削減しながらセキュリティレベルを向上できます。

**2. 生成AIワークロードの本番化支援**: Bedrock での Grok 4.6、OpenAI モデルのインド対応、Cost Anomaly Detection の Bedrock 対応など、生成 AI ワークロードを安全かつ経済的に本番運用するためのツールが充実してきました。PoC フェーズから本番環境への移行を検討している組織にとって、追い風となるアップデートです。

**3. グローバルインフラの拡充**: ロンドンリージョンの新 AZ、GovCloud での OpenSearch Ingestion、European Sovereign Cloud での IAM 機能拡張など、地理的・規制的な要件に応じた選択肢が増えています。データレジデンシー要件が厳しい組織でも、AWS 上で完結したアーキテクチャを構築しやすくなりました。

SRE の観点では、これらのアップデートを「導入するかしないか」ではなく、「どのように既存の運用フローに組み込むか」を考えることが重要です。特にセキュリティとコスト管理の機能は、導入初期に設定コストがかかる一方で、その後の運用負荷を継続的に下げる方向に効きます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)