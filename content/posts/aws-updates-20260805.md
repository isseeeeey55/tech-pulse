---
title: "【AWS】2026/08/05 のアップデートまとめ"
date: 2026-08-05T08:01:49+09:00
draft: false
tags: ["aws", "connect", "emr", "ec2", "bedrock", "elasticloadbalancing", "securityhub", "rds", "organizations", "transform"]
categories: ["AWS Updates"]
summary: "2026/08/05 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260805/header.png)

# 直近の AWS アップデート 11 件まとめ — Bedrock Web Search、継続的モダナイゼーション GA、RFC 9151 対応など

## はじめに

今回は、直近で発表された 11 件の AWS アップデートを紹介します。コンタクトセンター運用の効率化、データ分析基盤の対話的開発環境、生成AIの検索機能強化、ロードバランサーのセキュリティ強化、高性能インスタンスの地域拡大、そしてアカウント管理の可視化まで、幅広い領域をカバーしています。特に、Amazon Bedrock の Web Search 機能や AWS Transform の継続的モダナイゼーション機能は、セキュアな環境を保ちながら最新情報を活用する新しいアプローチを提示しており、SRE や DevOps チームにとって注目すべき内容です。

## 注目アップデート深掘り

### Amazon Bedrock が OpenAI GPT モデル向け Web Search 機能を提供開始

Amazon Bedrock が OpenAI の GPT モデル（GPT-5.4、GPT-5.5、GPT-5.6 Sol/Terra/Luna）向けに **Web Search** 機能の一般提供を開始しました。この機能の最大の特徴は、データが一切 AWS 外に流出せず、セキュアな環境を維持しながら、現在のウェブ情報に基づいた回答を生成できることです。

#### 従来の課題と解決策

これまで生成 AI アプリケーションに最新のウェブ情報を組み込むには、第三者の検索プロバイダーを統合する必要があり、以下のような煩雑さがありました。

- 個別の API キーと請求の管理
- カスタムオーケストレーションの構築
- 外部ベンダーごとの追加コンプライアンスレビュー

Web Search 機能はこれらの課題を解消し、既存の API 呼び出しに1つのパラメータを追加するだけで、標準化されたツール利用インターフェース経由で組み込めます。Amazon 独自のウェブインデックス（**継続的に更新される数百億ドキュメント**）と、検証済みの事実を提供する組み込みの知識グラフを活用し、セマンティックなスニペット抽出により結果を返します。

本機能は米国東部（バージニア北部・オハイオ）および米国西部（オレゴン）で提供されています。

#### なぜこのアップデートが重要なのか

金融・法務関連企業や医療機関、政府機関など、規制要件が厳しい業界では、データレジデンシとセキュリティが最優先課題です。従来のアプローチでは、最新情報を参照する際にデータが外部に流出するリスクがあり、コンプライアンス上の懸念から導入を見送るケースが少なくありませんでした。

この機能により、患者データや機密のサプライチェーン情報を保有しながら、最新の市場動向や医療知見を踏まえた AI 回答を生成することが可能になります。ユーザーサポート業務においても、製品の最新情報や既知の問題を常に参照し、正確でタイムリーなサポート回答を提供できるようになります。

### AWS Transform 継続的モダナイゼーション機能が正式リリース

AWS Transform の継続的モダナイゼーション機能が全対応リージョンで正式利用可能になりました。この機能は、エンジニアチームがソースコードリポジトリ全体の技術的債務を大規模に分析・改善するのを支援します。

#### 機能の詳細と活用方法

GitHub、GitLab、Bitbucket に接続でき、オンデマンドまたはスケジュール実行で分析を実施できます。分析結果は以下の基準で優先順位付けが可能です。

- 技術的債務
- セキュリティ
- AI エージェント対応可能性
- モダナイゼーション対応可能性
- カスタム分析基準

AWS Transform Web アプリケーションから、プロバイダーの接続、分析の実行・スケジューリング、検出結果のレビュー、修復の作成が可能です。修復対象の検出結果に対しては、検証済みコード変更を含むブランチとプルリクエスト/マージリクエストが自動作成されます。

#### セキュリティと柔軟性

分析と修復は AWS アカウント内で実行され、ソースコードは常にあなたの管理下に置かれます。これにより、機密性の高いコードベースでも安心して利用できます。

さらに、IDE やターミナルから Kiro Power やエージェントプラグイン、CLI を使用することも可能で、ローカルリポジトリの分析や EC2・AWS Batch での実行もサポートしています。この柔軟性により、開発者の既存ワークフローに自然に統合できます。

#### 活用シナリオ

大規模組織では、複数チーム・複数リポジトリにわたる技術的債務の全社的なスキャンと優先順位付けが課題となります。AWS Transform を使用することで、セキュリティ脆弱性の自動検出と修復提案によるセキュリティ向上、レガシーコードの AI エージェント対応可能性の事前評価、マイクロサービスやクラウドネイティブへのモダナイゼーション準備状況の把握が可能になります。

CI/CD パイプラインに AWS Transform 分析を組み込むことで、継続的な品質改善のサイクルを構築できます。

## SRE視点での活用ポイント

### セキュアな環境での最新情報活用

Amazon Bedrock の Web Search 機能は、SRE チームが運用する監視・アラート基盤において、インシデント対応時の情報収集を効率化します。Terraform で管理しているインフラで障害が発生した際、最新の既知の問題や回避策をリアルタイムで参照しながら、データが外部に流出することなく対応策を提示できます。

CloudWatch アラームと組み合わせることで、アラート発火時に自動的に関連する最新情報を収集し、ランブックに組み込むことも検討できます。ただし、導入時にはコスト（特に高頻度のクエリ）と応答時間を事前に検証し、クリティカルパスでの使用可否を判断する必要があります。

### 技術的債務の継続的な可視化

AWS Transform は、SRE チームが管理するインフラコードやオートメーションスクリプトの品質を継続的に監視する用途に適しています。Infrastructure as Code のリポジトリに対して定期的にスキャンを実施し、セキュリティリスクや保守性の低下を早期に検出できます。

既存のコード品質ツール（SonarQube、Snyk など）と比較して、AWS 環境内で完結する点、複数のリポジトリを横断的に分析できる点が利点です。ただし、修復の自動プルリクエスト機能については、本番環境への影響を考慮し、レビュープロセスを確立した上で段階的に導入することが推奨されます。

### アカウント管理の事前計画

AWS Organizations のアカウントクォータが Service Quotas で可視化されたことにより、マルチアカウント戦略を推進する SRE チームは、アカウント数が上限に近づいていないか定期的に監視できるようになりました。CloudWatch と連携してアラートを設定することで、クォータに達する前に増加リクエストを自動化するワークフローを構築できます。

Infrastructure as Code でアカウント自動化を行う際の事前チェックとして、GetServiceQuota API をパイプラインに組み込むことも検討に値します。

## 全アップデート一覧

| タイトル | 概要 | リンク |
|---------|------|--------|
| Amazon Connect Customer のケース CSV エクスポート機能 | エージェント ワークスペースからケースを CSV でエクスポート可能に。セキュリティプロファイル権限でアクセス制御可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-connect-export-cases/) |
| Amazon EMR on EC2 で Spark Connect 対応 | インタラクティブな Spark セッションの実行が可能に。SageMaker Unified Studio や Jupyter からの対話的開発をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-emr-ec2-spark-connect/) |
| Amazon Bedrock が OpenAI GPT モデル向け Web Search 提供 | データが AWS 外に流出せず、最新のウェブ情報に基づいた回答を生成。Amazon 独自のウェブインデックスを活用 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-web/) |
| ALB・NLB が RFC 9151 準拠セキュリティポリシーをサポート | Commercial National Security Algorithm (CNSA) 1.0 スイート要件に対する RFC 9151 の TLS サーバー要件に準拠した新ポリシー。米国 NSA が定める暗号要件を TLS 1.2 / 1.3 で実装。全コマーシャルリージョン、GovCloud (US)、中国リージョンで追加費用なしに利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-application-network/) |
| EC2 C8g インスタンスが追加リージョンで利用可能 | 欧州（パリ）、アフリカ（ケープタウン）、イスラエル（テルアビブ）、カナダ西部（カルガリー）で提供開始。AWS Graviton4 搭載で、Graviton3 ベースのインスタンス比**最大 30%** の性能向上。データベースで 40%、Web アプリで 30%、大規模 Java アプリで 45% 高速 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-c8g-instances-additional-regions/) |
| Security Hub Extended にサプライチェーン セキュリティ追加 | 10番目のセキュリティカテゴリとして追加。Chainguard と Socket がパートナー。悪意ある依存関係を検出・ブロック | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-security-hub-extended-adds-supply-chain-security) |
| RDS for SQL Server が追加リージョンで BYOM 対応 | アジア太平洋 7 地域、ヨーロッパ 2 地域、メキシコ 1 地域で BYOM 利用可能。AWS License Manager と統合 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/rds-sql-server-supports-byom-in-additional-aws-regions/) |
| EC2 I8g インスタンスがパリ・ジャカルタで利用可能 | AWS Graviton4 と第3世代 AWS Nitro SSD を搭載。I4g 比で TB あたりのリアルタイムストレージ性能が**最大 65%** 向上、ストレージ I/O レイテンシが**最大 50%** 低下、同レイテンシの変動が最大 60% 低減 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-i8g-instances-aws-paris-jakarta-regions/) |
| OpenAI GPT-5.6 が 100万トークン コンテキストウィンドウに対応 | Sol、Terra、Luna の3モデルが対応。明示的なキャッシュブレークポイントを使ったプロンプトキャッシングが長コンテキストのリクエストにも適用され、繰り返しコンテキストはキャッシュ割引価格で課金される（割引率は告知に記載なし）。Sol は米国東部（バージニア北部・オハイオ）、Terra と Luna はこれに米国西部（オレゴン）を加えたリージョンで利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/gpt-sol-terra-luna-long-context-bedrock) |
| AWS Organizations のアカウントクォータが Service Quotas で可視化 | マネジメントアカウントから現在のアカウント数と上限を確認可能。GetServiceQuota API でプログラマティックアクセス可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-organizations/) |
| AWS Transform 継続的モダナイゼーション機能が正式リリース | GitHub/GitLab/Bitbucket 接続。技術的債務、セキュリティ、AI 対応可能性を分析し、自動修復プルリクエストを生成 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/7/aws-transform-continuous-general-available) |

## まとめ

今回紹介したアップデートは、セキュリティとコンプライアンスを維持しながら、最新技術を活用する方向性が顕著です。Amazon Bedrock の Web Search 機能や AWS Transform の継続的モダナイゼーション機能は、データを外部に流出させることなく、最新情報の活用やコード品質の向上を実現します。

また、EC2 インスタンスの地域拡大（C8g、I8g）や RDS for SQL Server の BYOM 対応拡大は、グローバル展開する企業にとって、各地域の規制要件を満たしながら高性能なインフラを構築できる選択肢を広げています。

セキュリティ面では、ALB・NLB の RFC 9151 準拠ポリシーや Security Hub Extended のサプライチェーン セキュリティカテゴリ追加により、政府機関や規制産業での要件に対応する体制が整いつつあります。

SRE チームとしては、これらの新機能を段階的に検証し、既存の運用ワークフローに統合することで、セキュアで効率的な運用基盤を構築できます。特に可視化・自動化・継続的改善の観点では、Service Quotas の拡張や AWS Transform が長期的な運用品質の底上げにつながります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)