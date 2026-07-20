---
title: "【AWS】2026/07/21 のアップデートまとめ"
date: 2026-07-21T08:02:26+09:00
draft: false
tags: ["aws", "data-exports", "bedrock", "ec2", "local-zones", "managed-service-for-apache-flink", "connect", "cloudtrail", "cloudwatch", "synthetics", "s3", "ebs", "ecs", "eks", "vpc", "direct-connect", "kms"]
categories: ["AWS Updates"]
summary: "2026/07/21 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260721/header.png)

# 直近のAWSアップデート情報 2026年7月版

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。今回のアップデートは、AI/ML活用の可視化、グローバル展開の促進、セキュリティ強化という3つの軸で大きな進展が見られます。特に注目すべきは、AWS Data ExportsがAmazon Bedrockのメタデータに対応したことで、生成AIコストの可視化が一気に現実的になった点です。また、Amazon CloudWatchにCoding Agent Insightsが追加され、組織全体でのAIコーディングツールのROI評価が可能になりました。さらに、CloudTrailのユーザーアイデンティティフィルタリング、CloudWatch Syntheticsの顧客管理KMSキー対応など、セキュリティとコンプライアンス強化に関する機能も充実しています。インフラ面では、EC2の新世代インスタンス（I8ge、R8i/R8i-flex）がGovCloudや欧州リージョンに展開され、政府機関や規制業界での選択肢が広がっています。

## 注目アップデート深掘り

### 1. AWS Data ExportsによるAmazon Bedrockコストの可視化

#### なぜこのアップデートが重要なのか

生成AIの利用が拡大する中、FinOpsチームにとって最大の課題の一つが「Bedrockのコストを正確に把握し、最適化する」ことでした。今回のアップデートにより、AWS Data Exports が標準化された Bedrock プロダクトメタデータを提供するようになり、モデル別・推論タイプ別のコスト内訳を標準フィールドとして扱えるようになりました。

#### 標準化されたメタデータの内容

AWS Data Exportsで提供される標準属性には以下が含まれます：

- **モデルプロバイダー**：使用しているモデルの提供元（Anthropic、AI21 Labsなど）
- **モデル名**：具体的なモデル識別子（Claude、Titanなど）
- **価格設定単位**：課金の単位（トークン、画像など）
- **推論タイプ**：入力トークン、出力トークンといった区別
- **機能**：On-Demand、Batch といった推論の提供モード

これらの標準フィールドは、AWS Data Exports を利用する Amazon Bedrock 顧客に対して追加コストなしでデフォルトで提供されます。エクスポート先の Amazon S3 に配信し、Amazon Athena でクエリするか、データウェアハウスにロードして分析できます。

#### 従来のCUR 2.0との違い

告知によると、CUR 2.0 においては、モデルプロバイダー・モデル名・推論タイプ・機能の各属性は `product` マップ列の中に格納され、価格設定単位のみが独立した列として提供されています。つまりマップ列から個々の属性を取り出す操作が必要でした。

今回の標準化により、これらの属性を標準フィールドとして扱えるようになります。

#### 実践的な活用シナリオ

以下は告知そのものではなく、提供される標準フィールドから導ける活用例です。

**モデル別コスト分析**では、モデルプロバイダーとモデル名が標準フィールドになるため、どのモデルにどれだけ支出しているかをモデル単位で集計できます。推論タイプが入力トークンと出力トークンに分かれていることから、入出力どちらがコストを押し上げているかの比率も把握できます。

**提供モード別の比較**では、機能フィールドで On-Demand と Batch が区別されるため、同じモデルを異なる提供モードで使った場合のコスト差を、自前のタグ付けに頼らず集計できます。

いずれも従来は `product` マップ列から属性を取り出す必要があった集計で、標準フィールド化によってクエリが単純になる点が今回の実質的な変化です。

### 2. AWS CloudTrailのユーザーアイデンティティフィルタリング

#### セキュリティ監視における課題

VPCエンドポイント経由のネットワークアクティビティを監視する際、従来のCloudTrailではすべてのイベントが記録されるため、大量のログノイズが発生していました。特に開発環境や大規模なマルチテナント環境では、信頼できるユーザーからの正常なアクセスと、潜在的な脅威となる不審なアクセスが混在し、セキュリティチームがインシデント調査に多大な時間を費やす原因となっていました。

#### UserIdentityフィルタリングの仕組み

今回のアップデートにより、CloudTrailの高度なイベントセレクター機能を使用して、IAMユーザーアイデンティティに基づいたフィルタリングが可能になりました。具体的には以下のような設定が可能です：

**信頼できるユーザーリストの除外**：組織内で承認されたIAMロールやユーザーからのアクセスをログから除外し、それ以外のアイデンティティからのアクセスのみを記録します。これにより、ログ量を大幅に削減しながら、セキュリティ上重要なイベントに集中できます。

**アクセス拒否イベントの選別的記録**：VpceAccessDeniedイベントのうち、特定のユーザーアイデンティティに関連するもののみをフィルタリングできます。例えば、開発者ロールからのアクセス拒否は通常の動作として除外し、未承認ロールからの拒否イベントのみを記録することで、潜在的な侵入試行を効率的に検出できます。

#### ログコストとノイズの削減

告知では、信頼できるアイデンティティからの通常のトラフィックを除外しつつ未承認のアクセス試行を捕捉することで、「ログのコストとノイズの両方を削減する」と説明されています。削減幅を示す具体的な数値は告知に含まれていないため、実際の効果は自身の環境でのイベント構成比を確認して見積もる必要があります。

#### セキュリティモニタリングへの統合

このフィルタリング機能は、既存のセキュリティツールと組み合わせることで真価を発揮します：

**SIEM への転送量削減**：CloudTrail ログを SIEM に取り込んでいる場合、記録段階でルーチンなイベントを除外できるため、転送・取り込み対象そのものが減ります。

**調査対象の絞り込み**：許可リスト外のアイデンティティからのアクセス拒否だけが残るため、調査の起点となるイベントを特定しやすくなります。

なお、告知が示しているのは「どのイベントを記録するかをアイデンティティで選別できる」という記録側の制御までです。検知後の自動ブロックなどの対応フローは、別途自分で設計する領域になります。また、除外したイベントは記録自体が残らないため、許可リストの範囲は監査要件と突き合わせて決める必要があります。

## SRE視点での活用ポイント

### 生成AIコスト管理の自動化

AWS Data ExportsのBedrock対応は、SREチームにとって重要な可視化ツールになります。特にマイクロサービスアーキテクチャで複数のサービスがBedrockを利用している場合、サービス別のコスト配賦が課題になります。Terraformでタグ管理を標準化している環境であれば、リソースタグとData Exportsのメタデータを組み合わせて、サービスオーナー別のコストレポートを自動生成できます。導入効果が出やすいのは、複数部門・複数サービスが同じアカウントで Bedrock を使っていて、これまでモデル単位の内訳を取るのに手間がかかっていた環境です。

### セキュリティログの効率的な運用

CloudTrailのUserIdentityフィルタリングは、SREの「シグナル対ノイズ比」改善に直結します。Terraformで管理しているIAMロールがあれば、信頼できるロールのリストをコード管理し、CloudTrailのイベントセレクターに適用することで、一貫性のあるフィルタリングポリシーを維持できます。特にマルチアカウント環境でAWS Organizationsを使用している場合、組織トレイルにフィルタリングを適用すれば、すべてのアカウントで統一されたログ戦略を実現できます。注意点としては、フィルタリングルールの定期的な見直しが必要です。新しいサービスやロールが追加された際に、許可リストの更新を忘れると重要なイベントが記録されない可能性があります。Infrastructure as Codeでロール作成とフィルタリングルール更新を自動化することで、このリスクを軽減できます。

### AIコーディングツールのROI測定

CloudWatchのCoding Agent Insightsは、組織的なAIツール導入の効果測定に役立ちます。GitHub Copilotを全社展開する前に、パイロットチームでメトリクスを収集し、コミット頻度やPRレビュー速度の改善を定量化できます。OpenTelemetryメトリクスの料金が発生するため、メトリクス収集対象を絞り込むことでコストを抑えられます。例えば、本番環境のコミットメトリクスのみを収集し、開発環境は除外するといった戦略が考えられます。複数のコーディングエージェントを併用・比較検討している段階では、エージェントをまたいだ比較ができる点が特に効いてきます。部門別のトークン使用量を可視化することで、予算配分の根拠を示しやすくなります。

## 全アップデート一覧

| サービス | アップデート内容 | 概要 |
|---------|---------------|------|
| [AWS Data Exports](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-data-exports-amazon-bedrock-product-metadata/) | Amazon Bedrock標準メタデータ対応 | モデル別・推論タイプ別のコスト分析が可能に。FinOpsチーム向けの構造化データを追加コストなしで提供 |
| [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-i8ge-instances-aws-govcloud-us-regions/) | I8ge インスタンスがGovCloud対応 | Graviton4搭載のストレージ最適化インスタンス。前世代のGraviton2ベースのストレージ最適化インスタンス比で最大60%のコンピュート性能向上、Im4gn比でTBあたり最大55%のリアルタイムストレージ性能向上 |
| [AWS Local Zones](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-local-zone-athens-greece/) | アテネLocal Zone一般提供開始 | ギリシャでのデータレジデンシー要件に対応。S3とEBS Local Snapshotsをサポート |
| [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-r8i-r8i-flex-instances-in-stockholm-zurich-regions/) | R8i/R8i-flexインスタンスが欧州展開 | ストックホルムとチューリッヒで利用可能に。R7i比で20%高性能、前世代Intelベースインスタンス比でメモリ帯域幅2.5倍 |
| [Amazon Managed Service for Apache Flink](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-flink-2-3/) | Apache Flink 2.3対応 | 適応的パーティション選択によるバックプレッシャー改善。CDCパイプラインのデータ正確性向上 |
| [AWS](https://aws.amazon.com/about-aws/whats-new/2026/07/knfsd-file-cache/) | KNFSD File Cacheプレビュー公開 | NFSキャッシュをAWS上に構築するオープンソースソリューション。高遅延リンクを吸収し、ローカルVPC速度でデータ提供 |
| [Amazon Connect](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-connect-agentic-voice/) | 50以上の言語と100以上の新音声に対応 | 日本語を含む多言語でのAI音声エージェント。速度・音量・感情を調整できるスピーチコントロールを提供 |
| [AWS CloudTrail](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-cloudtrail-filter-useridentity-advance-selectors/) | UserIdentityフィルタリング機能追加 | VPCエンドポイント経由のイベントをIAMアイデンティティで選別的に記録。ログコスト削減とセキュリティ監視の効率化 |
| [Amazon CloudWatch Synthetics](https://aws.amazon.com/about-aws/whats-new/2026/07/synthetics-customer-managed-keys/) | 顧客管理KMSキー対応 | Canaryの環境変数を顧客管理キーで暗号化可能に。規制業界向けのキー管理ポリシーと監査証跡をサポート |
| [Amazon CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/07/cloudwatch-coding-agent-insights/) | Coding Agent Insights発表 | Claude Code、Codex、GitHub Copilot のコーディングエージェント利用状況を可視化。Claude Code は Claude apps gateway for AWS 経由で追加の計装なしにテレメトリを収集 |

## まとめ

今回のアップデート群は、「可視化」「グローバル展開」「セキュリティ強化」という3つの軸で一貫したメッセージを発信しています。AWS Data ExportsのBedrock対応とCloudWatch Coding Agent Insightsは、生成AIとAIコーディングツールという新しい技術領域のコスト管理を現実的なものにしました。これまで「AIツールは便利だが、ROIが見えにくい」という課題があった組織にとって、定量的な評価基盤が整ったことは大きな意味を持ちます。

インフラ面では、EC2の新世代インスタンス（I8ge、R8i/R8i-flex）が政府機関向けリージョンや欧州に展開され、データレジデンシー要件を持つ組織の選択肢が広がりました。アテネLocal Zoneの追加も同様の文脈にあり、AWSがグローバル展開と地域固有の規制対応を両立させる戦略を着実に進めていることが分かります。

セキュリティ領域では、CloudTrailのUserIdentityフィルタリングとCloudWatch Syntheticsの顧客管理KMSキー対応が、「セキュリティ強化とコスト最適化の両立」という課題に応えています。特にCloudTrailのフィルタリングは、SREチームが長年直面してきた「重要なシグナルがノイズに埋もれる」問題を解決する実用的な機能です。

また、Apache Flink 2.3対応やKNFSD File Cacheのプレビュー公開は、ストリーミングデータ処理とハイブリッドクラウド環境という、現代のシステムアーキテクチャにおける重要なユースケースに対応しています。いずれもプレビューまたは新バージョン対応の段階であり、既存構成への適用可否は個別に検証が必要です。

今後は、これらの新機能を実際の環境で検証し、組織固有のユースケースに適用していくフェーズに入ります。特にコスト可視化機能は、早期に導入することで継続的な最適化サイクルを確立できるため、優先的に検討する価値があります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)