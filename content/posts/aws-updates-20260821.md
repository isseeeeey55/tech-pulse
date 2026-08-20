---
title: "【AWS】2026/08/21 のアップデートまとめ"
date: 2026-08-21T08:02:33+09:00
draft: true
tags: ["aws", "partner-central", "cloudfront", "s3", "eks", "direct-connect", "sagemaker", "marketplace", "cloudwatch", "bedrock"]
categories: ["AWS Updates"]
summary: "2026/08/21 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報まとめ — 2026年8月

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。注目すべきは、CloudFrontのS3 Multi-Region Access Points対応、EKSのCA自動ローテーション機能、そしてAmazon Bedrockの外部Web検索機能拡張など、エンタープライズ運用とセキュリティを強化する実用的な機能が多数含まれている点です。特にマルチリージョン・マルチアカウント環境での運用効率化、コンプライアンス要件への対応、そしてAIエージェントのセキュアな情報取得といった、現場のエンジニアが直面する課題を解決する内容が揃っています。

## 注目アップデート深掘り

### Amazon CloudFront の S3 Multi-Region Access Points 対応による運用改善

Amazon CloudFrontがS3 Multi-Region Access Points（MRAP）に対応したOrigin Access Control（OAC）のサポートを開始しました。このアップデートは、グローバルなコンテンツ配信を行う組織にとって大きな運用改善をもたらします。

**なぜこのアップデートが重要なのか**

従来、CloudFrontからS3 MRAPへアクセスする際は、Lambda@Edgeでカスタム関数を実装し、Asymmetric Signature Version 4（SigV4a）認証ヘッダーを動的に生成する必要がありました。この方式では以下の課題がありました：

- Lambda@Edge関数の開発・保守コストが発生
- 署名ロジックの実装ミスによるセキュリティリスク
- エッジロケーションでの関数実行による追加レイテンシー
- Lambda@Edge実行に対する従量課金コスト

今回のネイティブOAC対応により、CloudFrontが自動的にS3 MRAPへのリクエストに署名するようになりました。これにより、複雑なカスタムコード不要で、キャッシュミス時に最寄りのリージョンから高速にコンテンツを配信でき、OACによるアクセス制限も実現します。

**従来方式との比較**

従来のLambda@Edge方式では、カスタム署名ロジックの実装と維持管理が必要でした。具体的には、リクエストヘッダーの操作、署名計算、エラーハンドリングなどを自前で実装する必要がありました。一方、新しいネイティブOAC方式では、CloudFrontのコンソール、CLI、SDK、CloudFormationから標準的な設定として有効化できます。

設定の観点からも、Lambda@Edge削除によるアーキテクチャのシンプル化が実現します。Lambda関数のバージョン管理、デプロイ、モニタリングといった運用タスクが不要になり、CloudFrontの標準機能として一元管理できるようになります。

**グローバル分散ユーザーへのメリット**

S3 MRAPは複数リージョンのS3バケットを単一のグローバルエンドポイントとして扱い、リクエストを最適なリージョンに自動ルーティングします。CloudFrontのOAC対応により、エンドユーザーに最も近いエッジロケーションからキャッシュ提供され、キャッシュミス時は最寄りのS3リージョンから取得されるため、グローバルでのパフォーマンスと耐障害性が大幅に向上します。

マルチリージョン構成での運用では、リージョン障害時の自動フェイルオーバーも実現されます。あるリージョンのS3バケットが利用不可能になっても、MRAPが自動的に別リージョンへルーティングするため、手動でのオリジン切り替え作業が不要です。

> **Note:** 中国リージョンではOAC機能が制限されているため、代替としてOrigin Access Identity（OAI）の使用を検討する必要があります。

### Amazon EKS の証明書認証局ローテーション機能による長期運用の安定化

Amazon EKSがクラスタの証明書認証局（CA）ローテーション機能を発表しました。これは2018年のEKSローンチ以来、多くのクラスタが10年の有効期限を持つCAの更新時期を迎えることへの対応として、非常にタイムリーなアップデートです。

**背景と課題**

各EKSクラスタはKubernetes APIへの暗号化接続を可能にする独自のCAを持っています。このCAには10年の有効期限が設定されており、2018年から2020年代初期に構築されたクラスタでは、今後数年のうちにCA有効期限切れによるクラスタ全体の停止リスクが迫っています。CA有効期限が切れると、すべてのノードとクライアントがAPIサーバーに接続できなくなり、クラスタ全体が機能停止します。

これまでCA更新の方法が提供されていなかったため、多くの組織では「有効期限前にクラスタを再構築する」といった大規模な移行作業を計画せざるを得ませんでした。本番環境でのクラスタ再構築は、ワークロードの移行、ダウンタイムの調整、多数の関連システムの更新など、膨大な工数とリスクを伴います。

**自動ライフサイクル管理の仕組み**

新機能では、AWSが管理コンポーネント（コントロールプレーン、kube-proxy、CoreDNS、AWS VPC CNIなど）の自動更新を担当します。ユーザー側では、ワーカーノードと外部クライアント（CI/CDツール、モニタリングシステム、kubectl設定など）の更新が必要です。

自動セーフガード機能により、以下のライフサイクルが提供されます：

- **有効期限前通知**: CA有効期限が近づくと、EventBridge経由で自動通知
- **後継CAの自動追加**: 新しいCAが既存クラスタに自動追加され、新旧両方のCAが一時的に共存
- **自動アクティベーション**: 指定したスケジュールで新CAへの切り替えが実行
- **ロールバック機能**: 問題発生時に旧CAへ戻すことが可能

**ワーカーノード更新の責任分界**

EKS Auto ModeおよびAWS Fargateで実行されているノードは、AWSが自動的に更新します。一方、自己管理型ノードグループやマネージド型ノードグループでEC2インスタンスを使用している場合、ユーザーが新しいCA証明書を含むノードイメージへの更新作業を実施する必要があります。

具体的には、新しいCA証明書を信頼するようにkubelet設定を更新し、ノードを段階的にローリングアップデートします。この際、Podの再スケジューリングが発生しますが、適切なPodDisruptionBudget設定により、サービスへの影響を最小限に抑えることができます。

**外部クライアント更新の重要性**

見落とされがちですが、クラスタ外部からAPIサーバーにアクセスするすべてのクライアントも更新が必要です。これには以下が含まれます：

- CI/CDパイプライン（Jenkins、GitLab CI、GitHub Actionsなど）のkubeconfig
- 監視・ログ収集エージェント（Prometheus、Datadog、Fluentdなど）
- 管理ツール（Terraform、Helm、ArgoCD、Fluxなど）
- 開発者のローカル環境のkubectl設定

各クライアントのkubeconfigファイルに含まれる証明書データを更新する必要があるため、事前に全クライアントをインベントリ化し、更新手順を文書化しておくことが重要です。

**段階的なローテーション戦略**

推奨される実施手順は以下の通りです：

1. 既存クラスタのCA有効期限を確認（AWS CLI、EKS API、Consoleで確認可能）
2. 非本番環境（開発・ステージング）で先行してローテーションをテスト実施
3. ワーカーノード更新手順を検証し、Podの再スケジューリング挙動を確認
4. 外部クライアントリストを作成し、各クライアントでの接続テストを実施
5. 本番環境で段階的にローテーション実行（まず管理コンポーネント、次にノード、最後に外部クライアント）
6. CloudTrailでCA関連イベントを監視し、問題発生時の早期検知体制を構築

ロールバック手順も事前に確認しておくべきです。新CA適用後に予期しない問題が発生した場合、旧CAへ戻す操作が可能ですが、ロールバックウィンドウには制限があるため、迅速な意思決定が求められます。

> **Note:** この機能は追加コスト無しで、全商用AWSリージョンで利用可能です。AWS CLI、EKS APIs、CloudFormation、AWS Consoleから設定できます。

## SRE視点での活用ポイント

### インフラセキュリティと運用自動化の進化

今回のアップデート群は、SREが日常的に直面する「セキュリティと運用効率のバランス」という課題に対する実践的な解を提供しています。

CloudFrontのS3 MRAP対応は、グローバルCDN運用でのセキュリティポリシー実装を大幅に簡素化します。Lambda@Edgeのカスタムコードを削除できることで、コードレビュー、脆弱性スキャン、定期的な依存関係更新といったセキュリティ維持コストが削減されます。Terraform管理しているインフラであれば、`aws_cloudfront_distribution`リソースの`origin_access_control`設定を追加するだけで移行でき、既存のIaCパイプラインに容易に統合できます。

EKSのCA自動ローテーション機能は、証明書管理という見落とされがちだが致命的な運用リスクへの対応です。有効期限切れによるクラスタ全停止は、障害対応のランブックに「事前予防」として組み込むべき項目です。CloudWatchアラームやEventBridgeルールと組み合わせることで、CA有効期限の6ヶ月前・3ヶ月前・1ヶ月前といった段階的な通知を設定し、計画的なローテーション実施を促す仕組みを構築できます。

Direct Connectのプリフィックス制限緩和は、大規模なハイブリッドクラウド環境での運用ボトルネック解消に直結します。100プリフィックス制限により、複数VIFの管理や複雑なルート集約に苦労していたネットワークチームにとって、1,000プリフィックスへの拡大は運用を大きく簡素化します。既存のネットワーク監視（NetFlow、VPCフローログ）と組み合わせて、プリフィックス使用状況をダッシュボード化することで、キャパシティプランニングの精度も向上します。

### 可観測性とコスト最適化の統合

CloudWatch pipelinesの新プロセッサ（GeoIP、RDS、XML）は、ログ分析の前処理工程を削減し、インシデント対応の初動を高速化します。従来はログを別システムに転送してパース処理を行い、その後可視化ツールに投入するといった多段構成が必要でしたが、取り込み時点で構造化されることで、CloudWatch Logs InsightsやOpenSearchでの即座のクエリが可能になります。

特にGeoIPエンリッチメントは、セキュリティインシデント対応で頻繁に必要となる「異常な地理的アクセス」の検知を自動化できます。例えば、通常は日本とシンガポールからのみアクセスがあるシステムに対して、東欧やアフリカからの突然のアクセスが発生した場合、CloudWatch Logs Insightsクエリで即座に抽出し、SNS/PagerDuty経由でアラート送信する仕組みを構築できます。

CloudWatch Centralizationのタグ伝播機能は、マルチアカウント環境でのコスト可視化を改善します。Cost Explorerでタグベースのコスト分析を行う際、ログ集約後もタグが維持されることで、「どの部門・プロジェクトがログストレージコストをどれだけ消費しているか」を正確に把握できます。IAM条件でのアクセス制御と組み合わせれば、各チームが自チームのログのみにアクセスできる権限設定を、集約後も維持できます。

### AI/ML機能の安全な運用統制

Amazon BedrockのWeb Search機能拡張（external_web_accessパラメータ、ドメインフィルタリング）は、生成AIアプリケーションの運用リスク管理を大きく前進させます。金融や医療などの規制業界では、AIが参照する情報源の統制が必須要件です。ドメインホワイトリストとexternal_web_access制御により、「社内承認済みのドメインのみから情報取得する」といったガバナンス要件を技術的に実装できます。

SageMaker AI StudioのGenerative AI Inference Recommendationsは、MLインフラの運用コスト最適化を自動化します。従来は数週間かけて手動でベンチマークを実施し、インスタンスタイプとコンテナ設定の最適な組み合わせを探っていましたが、これが数時間に短縮されます。コスト削減目標が明確なプロジェクトでは、この機能で推奨された構成を採用することで、予算承認プロセスも加速します。

導入判断では、ワークロードの特性を見極めることが重要です。リアルタイム推論とバッチ推論では最適な構成が異なるため、ユースケースプロファイル（Interact、Generate、Summarize）を正しく選択する必要があります。また、推奨結果は現時点のインスタンス価格と可用性に基づいているため、定期的な再評価も検討すべきです。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|-----------------|--------|
| AWS Partner Central | MCP ServerがOAuthとAWS Sign-Inに対応。既存ツールから追加認証ソフト不要でPartner Centralエージェントにアクセス可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/8/aws-partner-central-mcp/) |
| Amazon CloudFront | S3 Multi-Region Access Points（MRAP）に対応したOrigin Access Control（OAC）をサポート。Lambda@Edgeのカスタム署名不要に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cloudfront-oac-s3-mrap) |
| Amazon EKS | クラスタの証明書認証局（CA）ローテーション機能を追加。自動ライフサイクル管理とセーフガード機能を提供 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-eks-certificate-authority-ca-rotation-automated-lifecycle-management) |
| AWS Direct Connect | インバウンドプリフィックスコントロール機能を追加。VIFあたり最大1,000プリフィックス（IPv4/IPv6各）に拡大 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-direct-connect-new-prefix-controls) |
| Amazon SageMaker | AI StudioにGenerative AI Inference Recommendationsを追加。ノーコードで最適なインスタンス/コンテナ/最適化戦略を推奨 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/generative-ai-inference-recommendation-for-amazon-sagemaker-now-available-in-the-sagemaker-ai-studio) |
| AWS Marketplace | カテゴリベース通知とマルチチャネル配信をサポート。パートナーが通知を部門別に振り分け可能に（メール、Slack、Teams対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-marketplace/) |
| Amazon CloudWatch | pipelines に3つの新プロセッサ追加：RDS（Auroraログ構造化）、XML（JSON変換）、GeoIP（地理情報付加） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/cloudwatch-geoip-rds-xml/) |
| Amazon Bedrock | AgentCoreのWeb Searchにドメイン/公開日フィルタリング追加。アイルランドと東京リージョンに拡大 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/web-search-amazon-bedrock/) |
| Amazon CloudWatch | Centralizationがタグ伝播機能をサポート。集約先ログループにソースアカウントのタグを自動コピー | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cloudwatch-centralization-tag-propogation/) |
| Amazon Bedrock | Web SearchにExternal Web Accessパラメータ追加。公開Web検索とAWS内部インデックス検索を切り替え可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-web-access-web-search/) |

## まとめ

直近のAWSアップデートは、エンタープライズ運用の成熟度向上を支援する機能が中心となっています。特に、長期運用における証明書管理（EKS CA）、グローバル分散環境でのセキュリティ実装簡素化（CloudFront OAC）、大規模ネットワークのスケーラビリティ向上（Direct Connect）といった、実運用で必ず直面する課題への対応が充実しています。

可観測性の分野では、CloudWatch pipelinesの新プロセッサにより、ログの前処理工程が削減され、インシデント対応の初動が高速化されます。マルチアカウント環境でのタグ伝播機能は、コスト管理とアクセス制御の両面で運用を改善します。

AI/ML機能では、セキュリティとガバナンスを重視した機能拡張が目立ちます。Bedrockのドメインフィルタリングや外部Web検索制御は、規制業界での生成AI活用を現実的にする重要な進化です。SageMakerのInference Recommendationsは、コスト最適化の自動化により、ML運用の敷居を下げています。

これらのアップデートは、いずれも追加コストなしまたは従量課金の範囲内で利用でき、既存環境への段階的な導入が可能です。SREチームとしては、まず非本番環境での検証を行い、運用への影響を評価したうえで、計画的に本番環境へ適用していくアプローチが推奨されます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)