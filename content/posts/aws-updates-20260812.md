---
title: "【AWS】2026/08/12 のアップデートまとめ"
date: 2026-08-12T08:02:14+09:00
draft: true
tags: ["aws", "bedrock", "secrets-manager", "glue", "sagemaker", "rds", "mariadb", "connect", "ec2"]
categories: ["AWS Updates"]
summary: "2026/08/12 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報（2026年8月版）

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。Amazon Bedrock のコスト管理機能拡張、AWS Secrets Manager の外部サービス統合、SageMaker JumpStart への大量の新しい基盤モデル追加など、多様なアップデートがリリースされました。特に注目すべきは、生成AI関連のコスト可視化とセキュリティ管理の強化、そして SageMaker JumpStart が新しいモデルのデプロイメントプラットフォームとしての地位を確立しつつある点です。また、データ分析基盤の統合や、Amazon Connect のケース管理機能強化など、エンタープライズ運用を支える実務的な改善も目立ちます。

本記事では、これらのアップデートの中から特に運用インパクトの大きいものを深掘りし、SRE の視点での活用ポイントを解説します。

---

## 注目アップデート深掘り

### Amazon Bedrock の IAM プリンシパル コスト配分が bedrock-mantle エンドポイントに対応

Amazon Bedrock において、IAM プリンシパル（IAM ユーザーやロール）単位でのコスト配分機能が、従来の `bedrock-runtime` エンドポイントに加えて **`bedrock-mantle` エンドポイント**にも拡張されました。この機能により、組織内の複数チーム、プロジェクト、コストセンターが共有している Bedrock 環境において、生成 AI 利用コストを正確に按分できるようになります。

#### なぜこのアップデートが重要なのか

生成 AI の利用が拡大する中で、「誰が・どのプロジェクトで・どれだけのコストを消費しているのか」を可視化することは、予算管理とチャージバック制度の運用において不可欠です。従来は `bedrock-runtime` エンドポイント経由のリクエストのみがコスト配分の対象でしたが、`bedrock-mantle` を利用する特定のワークロードではコスト追跡ができませんでした。今回の拡張により、両エンドポイントを統一的に管理できるようになり、組織全体での生成 AI コストガバナンスが実現します。

#### 設定と活用方法

コスト配分を有効化するには、以下のステップを実施します。

1. **IAM プリンシパルにタグを付与**  
   IAM ユーザーやロールに対して、`team`、`project`、`cost-center` などのタグを設定します。タグの命名規則は組織の会計ポリシーに合わせて統一しましょう。

2. **AWS Billing and Cost Management コンソールでタグを有効化**  
   コスト配分タグの管理画面で、使用するタグキーを「アクティブ化」します。この操作により、以降のコストデータにタグ情報が付与されます。

3. **AWS Cost Explorer または CUR 2.0 でコスト分析**  
   Cost Explorer のフィルタ機能を使って、タグごとにコストをグループ化し、レポートを生成します。CUR 2.0（Cost and Usage Report 2.0）では、より詳細な行単位のコストデータを取得し、Athena や Redshift で分析できます。

#### bedrock-runtime と bedrock-mantle の違い

公式の告知には `bedrock-mantle` の詳細な技術仕様は記載されていませんが、`bedrock-runtime` が一般的なモデル推論リクエストを処理するエンドポイントであるのに対し、`bedrock-mantle` は特定の利用シナリオ（たとえばエージェント機能や特殊なワークフロー）で使用されるエンドポイントであると推測されます。両者を統一的に管理できることで、組織全体の Bedrock 利用コストを漏れなく把握できるようになります。

#### チャージバック運用のベストプラクティス

複数部門が Bedrock を利用している組織では、以下のようなタグ設計が推奨されます。

- `cost-center`: 部門別の予算管理
- `project`: プロジェクト単位の ROI 分析
- `environment`: 本番・開発環境の分離
- `team`: チーム単位の利用状況モニタリング

これらのタグを IAM ロールに事前設定しておくことで、Cost Explorer で柔軟なコスト分析が可能になります。また、予算アラートを設定し、特定のタグ値に基づいた使用量超過を自動検知することで、予算オーバーランを未然に防げます。

---

### AWS Secrets Manager が Jenkins と SonarQube の認証情報ローテーションに対応

AWS Secrets Manager が **Jenkins** と **SonarQube** の API トークン自動ローテーションに対応しました。これにより、これまで手作業やカスタムコードで管理していた CI/CD および静的解析ツールの認証情報を、AWS が提供するマネージドサービスで安全に管理できるようになります。

#### なぜこのアップデートが重要なのか

Jenkins や SonarQube は多くの開発組織で標準的に使われている CI/CD および品質管理ツールですが、これらの API トークンは長期間有効なままになりがちで、漏洩リスクが高い状態が続いていました。定期的な手動ローテーションは運用負荷が高く、ヒューマンエラーによる CI/CD パイプライン停止のリスクもあります。今回の対応により、Secrets Manager が自動的にトークンをローテーションし、セキュリティと運用効率の両立が実現します。

#### Jenkins でのローテーションの仕組み

Jenkins のトークンローテーションでは、**新しいトークンを生成してから古いトークンを無効化する**という安全なフローが採用されています。これにより、ローテーション実行中も CI/CD パイプラインが中断することなく動作し続けます。

Secrets Manager は以下の 2 つのローテーション方式をサポートしています。

- **セルフローテーション方式**: トークン自身が持つ権限で新しいトークンを生成します。シンプルな設定で済みますが、トークンに自己更新権限が必要です。
- **管理者アシスト型**: 管理者用の別トークンを使用してローテーションを実行します。より厳格な権限管理が必要な組織に適しています。

#### SonarQube でのトークン管理

SonarQube では、以下の 3 種類のトークンをローテーション可能です。

- **ユーザートークン**: 個人アカウントに紐づくトークン。セルフローテーション方式で管理します。
- **グローバル分析トークン**: 組織全体の静的解析で使用。管理者トークンで管理します。
- **プロジェクト分析トークン**: 特定プロジェクト専用のトークン。管理者トークンで管理します。

これにより、組織の権限モデルに応じた柔軟なトークン管理が可能になります。

#### 他の外部サービス対応状況

Secrets Manager は今回の Jenkins、SonarQube に加えて、以下の外部サービスにも対応しています。

- BigID
- Confluent Cloud
- Datadog
- GitLab
- MongoDB Atlas
- Okta
- Paddle
- Salesforce
- Snowflake

これらのサービスを利用している組織では、Secrets Manager を中心とした統一的な認証情報管理基盤を構築できます。

---

## SRE 視点での活用ポイント

### コスト可視化とチャージバック制度の実装

Bedrock の IAM プリンシパル コスト配分機能は、生成 AI の利用が拡大する組織において、予算管理の透明性を大幅に向上させます。Terraform で IAM ロールを管理しているインフラがあれば、タグ付けを IaC（Infrastructure as Code）に組み込むことで、新しいロールが作成されるたびに自動的にコスト追跡対象となります。

Cost Explorer の API を CloudWatch アラームと組み合わせると、特定のプロジェクトやチームのコストが閾値を超えた際に自動通知できます。たとえば、「開発チームの Bedrock 利用コストが月予算の 80% を超えたら Slack に通知」といった運用が実現できます。

導入時の判断基準としては、複数チームが共有環境を使っている場合や、内部チャージバック制度を運用している組織では即座に導入すべき機能です。一方、単一チームでの利用や PoC フェーズの小規模環境では、設定コストに見合う効果が得られない可能性があります。

### CI/CD パイプラインのセキュリティ強化

Jenkins や SonarQube のトークンを Secrets Manager で管理することで、障害対応のランブックに「トークン漏洩時の自動無効化手順」を組み込むことができます。たとえば、セキュリティインシデント発生時に Lambda 関数から Secrets Manager API を呼び出し、即座にローテーションを実行するといった自動化が可能です。

Terraform で Secrets Manager のシークレットとローテーション設定を管理している場合、ローテーション間隔やアラート設定を IaC で一元管理できます。これにより、複数環境（開発・ステージング・本番）で一貫したセキュリティポリシーを適用できます。

導入時の注意点としては、Jenkins や SonarQube 側でトークンの自動更新に対応したクライアント実装が必要になる点です。既存の CI/CD パイプラインがハードコードされたトークンに依存している場合、Secrets Manager からの動的取得に切り替えるためのコード修正が発生します。また、ローテーション実行時に一時的な認証エラーが発生しないよう、リトライロジックの実装も検討しましょう。

### データ分析基盤の統合とアクセス管理

AWS Glue から SageMaker Unified Studio へのワンクリックアクセスは、データエンジニアの作業効率を大幅に向上させます。従来は Glue でカタログを確認した後、IAM ロールを切り替えて SageMaker に移動する必要がありましたが、今回のアップデートでシームレスな移動が可能になります。

Lake Formation でデータカタログのアクセス制御を管理している環境では、Glue と SageMaker Unified Studio が同じ IAM ロールを使用するため、一貫したセキュリティポリシーを適用できます。CloudWatch Logs と組み合わせて、誰がどのカタログにアクセスし、どの分析ツールを使用したかを監査ログとして記録することも可能です。

導入時のリスクとしては、初回セットアップ時の IAM ポリシー設定が不適切だと、不要な権限が付与される可能性があります。最小権限の原則に基づいて、必要なリソースへのアクセスのみを許可するポリシー設計を心がけましょう。

---

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **コスト管理** | [Amazon Bedrock が bedrock-mantle エンドポイントで IAM プリンシパル コスト配分に対応](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-bedrock-expands-iam-principal-cost-allocation-bedrock-mantle/) | bedrock-mantle エンドポイント経由のモデル推論コストを IAM プリンシパル単位で追跡可能に。Cost Explorer と CUR 2.0 で詳細分析が可能 |
| **セキュリティ** | [AWS Secrets Manager が Jenkins と SonarQube の認証情報管理に対応](https://aws.amazon.com/about-aws/whats-new/2026/08/secrets-manager-integration-jenkins-sonarqube/) | Jenkins と SonarQube の API トークン自動ローテーション機能を追加。セルフローテーションと管理者アシスト型の両方に対応 |
| **データ統合** | [AWS Glue が SageMaker Unified Studio へのワンクリックアクセスに対応](https://aws.amazon.com/about-aws/whats-new/2026/08/smus-glue-access) | Glue コンソールから SageMaker Unified Studio へシームレスに移動可能。IAM 設定も Glue コンソール内で完結 |
| **データベース** | [Amazon RDS for MariaDB が MariaDB 12.3 に対応](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-rds-mariadb-1232-available/) | Oracle 互換性強化、IS JSON 述語追加、クエリオプティマイザー改善を含む MariaDB 12.3.2 をサポート |
| **機械学習** | [NVIDIA Nemotron 3.5 Lightning が SageMaker JumpStart で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/01/nvidia-nemotron-3.5-lightning-on-sagemaker-jumpstart/) | エージェント型ワークロード最適化モデル。毎秒約 410 トークン処理、最大 100 万トークンコンテキスト対応 |
| **機械学習** | [LocateAnything-3B、Qwen-AgentWorld-35B-A3B、Qwen3.5-122B-A10B が SageMaker JumpStart で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/01/locateAnything-3B-qwen-agentworld-35B-A3B-qwen3.5-122B-A10B-on-sagemaker-jumpstart/) | 画像内物体検出、エージェント環境シミュレーション、大規模マルチモーダル推論に特化した 3 つの基盤モデルを追加 |
| **カスタマーサービス** | [Amazon Connect Cases がパフォーマンスダッシュボードを提供開始](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-connect-cases-dashboard/) | ケース件数、解決時間、SLA 達成率をリアルタイム監視。テンプレート、担当者、キュー別の詳細分析が可能 |
| **機械学習** | [GLM-5.2 FP8、NVIDIA-Nemotron-Nano-12B-v2、GLM-OCR が SageMaker JumpStart で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/01/glm-5.2-fp8-nemotron-nano-12b-v2-glm-ocr-on-sagemaker-jumpstart/) | 長期エージェントタスク（1M トークン）、ハイブリッド推論（6 倍スループット）、高度文書理解に特化した 3 モデルを追加 |
| **機械学習** | [langcache-embed-v3-small、Mellum2-12B-A2.5B-Thinking、LightOnOCR-2-1B が SageMaker JumpStart で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/01/langcache-embed-v3-small-mellum2-12B-A2.5B-thinking-lightOnOCR-2-1B-on-sagemaker-jumpstart/) | セマンティックキャッシング、コード生成・推論、文書 OCR に特化した 3 つの基盤モデルを追加 |
| **機械学習** | [FLUX.2-small-decoder と gemma-4-12B-it が SageMaker JumpStart で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/01/flux.2-small-decoder-gemma-4-12B-it-on-sagemaker-jumpstart/) | 高速画像デコーディング（1.4 倍高速、VRAM 1.4 倍削減）とマルチモーダル統合理解に特化した 2 モデルを追加 |
| **コンピューティング** | [Amazon EC2 U7in-24TB インスタンスが南米（サンパウロ）リージョンで利用可能](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-high-memory-u7i-south-america) | 24TiB DDR5 メモリ、896vCPU、最大 100Gbps EBS 帯域幅を備えた高メモリインスタンスが南米で利用可能に |

---

## まとめ

今回紹介したアップデートは、生成 AI のコスト管理、セキュリティ強化、データ分析基盤の統合という、エンタープライズ運用の 3 つの重要な柱に焦点を当てています。

特に Bedrock のコスト配分機能拡張と Secrets Manager の外部サービス対応は、組織的な AI 活用とセキュリティガバナンスを両立させるための基盤となります。また、SageMaker JumpStart への大量のモデル追加は、AWS が基盤モデルのデプロイメントプラットフォームとしての地位を強化していることを示しています。

データ分析領域では、Glue と SageMaker Unified Studio の統合により、データエンジニアとデータサイエンティストの協業がよりスムーズになります。Amazon Connect Cases のダッシュボード機能は、カスタマーサポート運用の可視化を促進します。

これらのアップデートを活用することで、運用効率とセキュリティを同時に向上させることができるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)