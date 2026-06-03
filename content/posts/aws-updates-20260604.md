---
title: "【AWS】2026/06/04 のアップデートまとめ"
date: 2026-06-04T08:02:11+09:00
draft: false
tags: ["aws", "iot", "sagemaker", "bedrock", "step-functions", "rds", "config", "eks", "aurora", "neptune", "keyspaces", "application-recovery-controller"]
categories: ["AWS Updates"]
summary: "2026/06/04 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260604/header.png)

# 2026年6月4日 AWS アップデート情報

## はじめに

2026年6月4日、AWSは12件のアップデートを発表しました。本日の注目は、**Amazon SageMaker Unified Studio のノートブックスケジューリング機能**と、**AWS Step Functions の AgentCore 統合による AI エージェント推論ステップ**です。

機械学習とデータ分析の生産性向上を目的とした SageMaker 関連のアップデートが複数登場し、特にノートブックを本番環境のワークフローに組み込むためのスケジューリング機能は、多くのデータチームが待ち望んでいた機能といえるでしょう。また、Step Functions への AgentCore 統合により、AI エージェントをエンタープライズワークフローに組み込む道筋が明確になりました。

その他、Amazon Keyspaces の CDC イテレータ位置情報の追加、Amazon EKS の Kubernetes 1.36 対応、AWS Config の新規リソースタイプ対応など、運用効率化とセキュリティ強化に貢献するアップデートが並んでいます。

---

## 注目アップデート深掘り

### Amazon SageMaker Unified Studio のノートブックスケジューリング機能

Amazon SageMaker Unified Studio に**ノートブックスケジューリング機能**が追加されたことで、データサイエンスチームの生産性が大きく向上します。従来、Jupyter ノートブックで構築した分析ロジックやモデル学習パイプラインを本番環境で定期実行するには、Apache Airflow や AWS Step Functions などの外部オーケストレーション基盤を構築し、ノートブックをスクリプト化して統合する必要がありました。これには以下のような課題がありました：

- オーケストレーション基盤の構築・運用コスト
- ノートブックからスクリプトへの変換作業
- インタラクティブな開発環境と本番環境の乖離

今回のアップデートにより、**ノートブックインターフェース内から直接スケジュール設定が可能**になります。インタラクティブセッションを中断せずに、専用コンピュートでバックグラウンド実行やスケジュール実行をトリガーできるため、開発から本番化までの移行が大幅に簡素化されます。

#### ノートブックパラメータ化による再利用性の向上

特に注目すべきは**ノートブックパラメータ化**機能です。例えば、複数の配送業者向けに出荷パフォーマンスレポートを生成する場合、従来は業者ごとにノートブックを複製するか、スクリプト化して引数を渡す必要がありました。パラメータ化により、単一のノートブックを複数の入力値で再利用できます：

```python
# ノートブックセル内でパラメータを定義
# Parameters
shipper_name = "ACME Corp"  # デフォルト値
start_date = "2026-06-01"
end_date = "2026-06-04"

# 実行時にパラメータをオーバーライドして複数業者向けに実行
```

スケジュール設定時に、これらのパラメータを動的に変更することで、異なる業者や期間に対して同じロジックを適用できます。

#### ワークフローツールによる複数ノートブックの連携

さらに、**Workflow Studio 内の Notebook Operator** を使用することで、複数のノートブックを連携させた複雑なパイプラインを構築できます。例えば、以下のような多段階の分析ワークフローが実現可能です：

1. データ取得ノートブック → 2. データクレンジングノートブック → 3. 特徴量エンジニアリングノートブック → 4. モデル学習ノートブック → 5. レポート生成ノートブック

各ノートブックの実行結果は次のノートブックの入力として渡され、1つの実行結果を複数の下流ノートブックで再利用することも可能です。

#### AI 支援トラブルシューティング（Data Agent）

スケジュール実行やバックグラウンド実行が失敗した場合、**SageMaker Data Agent** が自動的に根本原因を特定し、ノートブック内で修正案を提示します。これにより、エラーログを手動で調査する時間を削減し、迅速な問題解決が可能になります。

Data Agent は自然言語でのスケジュール作成やノートブック実行にも対応しており、「毎週月曜日の午前9時に売上レポートを実行」といった指示でスケジュール設定が完了します。

---

### AWS Step Functions への AgentCore 統合による AI エージェント推論ステップ

AWS Step Functions に **Amazon Bedrock の AgentCore との統合**が追加され、ワークフロー内で AI エージェントの推論タスクを直接実行できるようになりました。これは、エンタープライズワークフローに生成 AI の推論能力を組み込むための重要な一歩です。

#### 従来のワークフローとの違い

従来の Step Functions ワークフローは、Lambda 関数や API 呼び出しなどの決定論的なステップで構成されていました。AI エージェントを統合する場合、以下のような実装が必要でした：

- Lambda 関数内で Bedrock API を呼び出し
- エージェントの入出力を JSON で管理
- トークン使用量やエラーハンドリングを自前で実装
- 監査ログの記録を別途構築

AgentCore 統合により、これらの処理が **Step Functions のネイティブステップ** として実行可能になります。ワークフロー定義内で直接エージェントの推論タスクを記述でき、実行履歴にはエージェントの入出力、トークン使用量、実行時間が自動的に記録されます。

#### 複数エージェントの並列・順序実行

Step Functions の制御フロー機能を活用することで、1つのワークフロー内の異なる判断ポイントで**複数の AI エージェントを並列実行または順序実行**でき、タスクの特性に応じた最適な実行パターンを選択できます。例えば、ドキュメント分類エージェントとデータ抽出エージェントを `Parallel` ステートで同時に走らせ、両方の結果を統合してから次のステップに進む、といったワークフローが構築可能です。

また、セッション ID を用いることで**エージェントのコンテキストを呼び出し間で永続化**でき、同一ワークフロー内はもちろん、複数のワークフロー実行をまたいで会話状態を引き継ぐこともできます。

ステートの正確なリソース指定子やパラメータ構文は、[AWS Step Functions のドキュメント](https://docs.aws.amazon.com/step-functions/)で最新の定義を確認してください。

#### 人間による承認ステップの組み込み

重要なアクション前に**人間による承認ステップ**を組み込むことができる点も、エンタープライズ利用において重要です。例えば、AI エージェントが顧客データの削除や重要な取引の承認を推論した場合、実際の実行前に人間のレビューを必須にすることで、リスクを最小化できます。

#### 実行時パラメータのオーバーライド

公式の説明によると、既存のエージェント設定を再利用しつつ、**呼び出しごとにモデル・システムプロンプト・ツールといったパラメータをオーバーライド**できます。これにより、設定を複製することなく、各ワークフローの文脈に合わせてエージェントの挙動を調整可能です。

例えば、共通のエージェント定義をベースにしつつ、財務分析ワークフローではリスク評価に特化したシステムプロンプトに差し替える、といった使い分けが、設定の重複なしに実現できます。オーバーライド対象の具体的なフィールド名や指定方法は[公式ドキュメント](https://docs.aws.amazon.com/step-functions/)で確認してください。

---

## SRE 視点での活用ポイント

### ノートブックスケジューリングの運用シナリオ

SageMaker Unified Studio のノートブックスケジューリング機能は、データパイプラインの運用自動化に直接寄与します。特に、**定期的なデータ品質チェックやモデルモニタリング**のユースケースでは、外部オーケストレーション基盤を管理するオーバーヘッドを削減しながら、迅速に本番運用を開始できます。

例えば、CloudWatch Alarms と組み合わせることで、データ品質異常を検出した際に自動的にスケジュール実行を停止し、運用チームに通知するといったフローが構築可能です。ノートブック実行履歴は完全に記録されるため、インシデント発生時の振り返りや監査にも対応できます。

導入時の判断基準としては、以下の点を考慮すると良いでしょう：

- **チームのスキルセット**: データサイエンティストが Python ノートブックに慣れている場合、学習コストが最小化されます
- **ワークフローの複雑性**: 単純な定期実行であればノートブックスケジューリングで十分ですが、複雑な分岐や外部サービス連携が必要な場合は Step Functions との併用を検討
- **コスト**: 専用コンピュートでの実行となるため、実行頻度やインスタンスタイプを適切に設定し、コストを監視

### Step Functions と AgentCore 統合の運用観点

Step Functions への AgentCore 統合は、**AI エージェントを既存のエンタープライズワークフローに組み込む標準的な手法**を提供します。特に、承認フローや監査要件が厳格なシステムにおいて、人間によるレビューステップを挟みながら AI の推論能力を活用できる点が重要です。

運用面では、以下のような活用が考えられます：

- **障害対応ランブック**: インシデント発生時に、AI エージェントがログやメトリクスを分析し、推定される根本原因と修復手順を提示。SRE が承認後、自動修復を実行
- **コスト最適化ワークフロー**: 定期的に利用状況を分析し、リソースの最適化提案を生成。承認後、Terraform や CloudFormation で変更を適用
- **セキュリティ監査**: CloudTrail ログを定期的にスキャンし、異常なアクセスパターンを検出。重要度に応じて自動対応または人間によるレビューを実施

注意点としては、AI エージェントのトークン使用量が予期せず増加するリスクがあるため、CloudWatch によるコスト監視とアラート設定を併用することが推奨されます。また、エージェントの推論結果は確率的であるため、冪等性が求められる操作には適用前の検証ステップを挟むべきです。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [AWS IoT Device Management adds MQTT session data to connectivity status API](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-iot-device-management-mqtt/) | 接続状態 API に MQTT セッションデータが追加され、デバイス切断後も無期限にデータを保持。ソケットレベルの詳細情報も取得可能に |
| 2 | [Amazon SageMaker Unified Studio now supports notebook scheduling](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-unified-studio/) | ノートブック内から直接スケジュール設定、パラメータ化、オーケストレーションが可能に。AI 支援トラブルシューティングも提供 |
| 3 | [Amazon SageMaker Data Agent now supports conversation history](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-data-agent/) | Data Agent が会話履歴機能をサポート。過去の分析セッションやコード生成を参照可能に |
| 4 | [ARC Region switch adds Amazon Aurora scaling and Amazon Neptune global database failover](https://aws.amazon.com/about-aws/whats-new/2026/06/region-switch-aurora-scaling-neptune-failover/) | ARC Region switch に Aurora のスケーリングと Neptune のグローバルデータベースフェイルオーバーの実行ブロックを追加 |
| 5 | [OpenAI GPT-5.4 generally available on Amazon Bedrock in AWS GovCloud (US-West)](https://aws.amazon.com/about-aws/whats-new/2026/06/GPT54-available-in-aws-govcloud-us-west/) | Bedrock が GovCloud (US-West) で GPT-5.4 を一般提供開始。政府機関と規制対象産業向けに高性能 AI モデルを提供 |
| 6 | [AWS Step Functions adds AgentCore-powered agentic reasoning step](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-step-functions-agentcore/) | Step Functions に AgentCore 統合による AI エージェント推論ステップを追加。複数エージェントの並列・順序実行、人間承認ステップをサポート |
| 7 | [Amazon RDS for Db2 launches support for IBM Db2 v12.1 and Db2 Community Edition](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-rds-db2-v12-community-edition) | RDS for Db2 が v12.1 と Db2 Community Edition をサポート。開発・テスト用途では商用ライセンス料金が不要に |
| 8 | [AWS Config now supports 9 new resource types](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-config-new-resource-types) | Bedrock、Bedrock AgentCore、SageMaker の9つの新しいリソースタイプを自動追跡可能に |
| 9 | [Amazon SageMaker Unified Studio now supports a localized experience in twelve languages](https://aws.amazon.com/about-aws/whats-new/2026/06/sagemaker-localization) | SageMaker Unified Studio が12言語に対応。日本語を含む多言語 UI を提供 |
| 10 | [Amazon SageMaker AI launches multi-turn reinforcement learning for AI agent model customization](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/) | マルチターン強化学習により、複数ステップのエージェントタスクに特化したモデルを効率的にカスタマイズ可能に |
| 11 | [Amazon Keyspaces (for Apache Cassandra) now provides CDC iterator position](https://aws.amazon.com/about-aws/whats-new/2026/06/keyspaces-cdc-iterator-position/) | Keyspaces CDC ストリームがイテレータ位置情報を返却。ポーリング頻度を動的に調整してコスト削減が可能に |
| 12 | [Amazon EKS and Amazon EKS Distro now supports Kubernetes version 1.36](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-eks-distro-kubernetes-version-1-36) | EKS が Kubernetes 1.36 をサポート。User Namespaces GA、Mutating Admission Policies、Pod レベルのリソース垂直スケーリングなどが追加 |

---

## まとめ

本日のアップデートは、**生成 AI と機械学習の運用化**に焦点を当てた内容が目立ちました。SageMaker Unified Studio のノートブックスケジューリング機能により、データサイエンスチームが実験段階のコードを本番環境に移行する障壁が大幅に低減されます。また、Step Functions への AgentCore 統合により、AI エージェントをエンタープライズワークフローに組み込む標準的な手法が確立されつつあります。

インフラストラクチャ面では、Amazon Keyspaces の CDC イテレータ位置情報追加により、リアルタイムデータパイプラインの効率化とコスト削減が実現可能になりました。Amazon EKS の Kubernetes 1.36 対応では、User Namespaces の GA やリソース垂直スケーリングなど、セキュリティと運用効率の向上に寄与する機能が追加されています。

全体として、**AI/ML ワークロードの本番運用を支援する機能強化**と、**既存サービスの運用効率化・コスト最適化**という2つの軸で進化が続いていることが確認できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)