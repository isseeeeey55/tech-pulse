---
title: "【AWS】2026/07/16 のアップデートまとめ"
date: 2026-07-16T08:02:07+09:00
draft: false
tags: ["aws", "cognito", "cloudwatch", "mq", "msk", "rds", "aurora", "opensearch", "ec2", "lambda"]
categories: ["AWS Updates"]
summary: "2026/07/16 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260716/header.png)

# 直近のAWSアップデートまとめ — 2026年7月

## はじめに

今回は、直近で発表された13件のAWSアップデートを紹介します。データベースの運用柔軟性向上、ログ管理の大幅な改善、Lambda の開発者体験強化など、幅広い領域でのアップデートが発表されました。特に注目すべきは、Amazon CloudWatch Logs のインテリジェントストレージティアリング機能や、Amazon Cognito のパスワードハッシュインポート対応です。これらは長年要望されていた機能であり、運用コストとユーザー体験の両面で大きな改善が期待できます。また、EC2 や RDS の新世代インスタンスが複数リージョンに拡大され、グローバル展開がさらに容易になっています。

本記事では、特に運用改善インパクトの大きい2つのアップデートを深掘りし、SRE視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon CloudWatch Logs のインテリジェントストレージティアリング

Amazon CloudWatch Logs に**インテリジェントストレージティアリング**機能が追加されました。この機能は、ログデータのアクセスパターンを自動的に監視し、Standard、Infrequent Access、Archive Instant Access の3つのストレージ層に自動分類します。

#### なぜこのアップデートが重要なのか

従来、CloudWatch Logs にはアクセス頻度に応じて自動的にストレージ層を移動する仕組みがなく、長期保存コストの最適化には S3 へのエクスポートやサードパーティツールへの転送が使われてきました。しかし、これらの運用には以下の課題がありました。

- S3 エクスポートの定期実行とライフサイクル管理の運用負荷
- エクスポートしたログの検索性低下（CloudWatch Insights が使えない）
- 複数のストレージを跨いだログ分析の複雑化
- アーカイブログへのアクセスが必要になった際の復元待ち時間

新しいインテリジェントティアリングは、これらの課題を解決し、CloudWatch Logs 単体で長期保存とコスト最適化を両立できるようになります。

#### 3つのストレージ層の特徴

アップデート情報によれば、以下の3層が自動的に管理されます。

- **Standard**: 頻繁にアクセスされるログデータ向け
- **Infrequent Access**: アクセス頻度が低下したログデータ向け
- **Archive Instant Access**: 長期保存が必要だがアクセスが稀なログデータ向け

重要なのは、すべての層で CloudWatch Insights によるクエリが可能であり、アクセスパターンに応じて自動的に層が昇格・降格される点です。運用者がストレージ層を意識する必要がなく、必要なときに必要なログへ即座にアクセスできます。

#### 実装と検証のポイント

この機能は AWS Management Console、CLI、SDK から有効化できます。告知によると、30日間アクセスがないデータは Infrequent Access へ、90日間アクセスがないデータは Archive Instant Access へ自動分類され、古いデータへアクセスするとそのデータは30日間 Standard 層へ自動昇格します。中東（バーレーン）と中東（UAE）を除くすべての AWS 商用リージョンで利用可能です。

検証すべきポイントとしては、以下が挙げられます。

1. **下位層への移行タイミング**: 30日（Infrequent Access）・90日（Archive Instant Access）という自動分類の閾値が、自社のログアクセスパターンと合っているか
2. **クエリ体験**: 告知ではどの層にデータがあっても同じクエリ体験が得られるとされているため、実際のクエリ応答を検証で確認
3. **コスト削減効果**: 実際のログボリュームとアクセスパターンに基づいた試算

告知では下位層は低コスト（lower-cost tiers）と説明されていますが、具体的な削減率は明示されていません。30日以上保持し、かつ日常的なアクセスが少ないログを対象に、自社のログ量で効果を試算するのがよいでしょう。

### Amazon Cognito のパスワードハッシュインポート対応

Amazon Cognito が CSV ユーザーインポート時に**パスワードハッシュをインポートできる機能**をサポートしました。これにより、既存システムからの移行時にユーザーが既存の認証情報でそのままサインインできるようになります。

#### 従来の課題とユーザー体験への影響

従来の Cognito では、CSV ファイルからユーザーをインポートする際、パスワードハッシュを含めることができませんでした。そのため、インポートされたユーザーは初回サインイン時に必ずパスワードリセットが必要でした。

これは特にエンタープライズシステムや既存のユーザーベースを持つアプリケーションにとって大きな障壁でした。ユーザーに「パスワードをリセットしてください」という追加手順を強いることで、以下の問題が発生していました。

- 移行直後のカスタマーサポート問い合わせの急増
- パスワードリセットメールが届かないなどの技術的問題
- ユーザーの離脱率増加（特にモバイルアプリでは深刻）
- 移行プロジェクトのリスク増大

#### サポートされるハッシュアルゴリズム

今回のアップデートでは、以下の4つの主要なハッシュアルゴリズムがサポートされます。

- **bcrypt**: Node.js や Ruby on Rails などで広く使われる
- **scrypt**: パスワードハッシュの標準的な選択肢の一つ
- **Argon2id**: 最新の推奨アルゴリズム、サイドチャネル攻撃に強い
- **PBKDF2 with SHA-256**: Java や .NET 環境で一般的

インポート作成時にソースシステムで使用されているアルゴリズムを指定すると、Cognito はユーザーの初回サインイン時にインポートされたハッシュに対してパスワードを検証します。また、すべてのインポート済みハッシュは保存前に追加の暗号化保護層を受け取ると告知に明記されています。

#### 実装シナリオ

実際の移行シナリオでは、以下のステップで実装します。

1. ソースシステムからユーザー情報とパスワードハッシュを抽出
2. CSV ファイルにハッシュアルゴリズムとともに整形
3. Cognito のインポート機能で CSV をアップロード、アルゴリズムを指定
4. ユーザーは既存のパスワードでそのままログイン可能に

この方式では、ユーザー体験を損なうことなく段階的な移行が可能です。特に数万〜数十万ユーザーを抱えるシステムでは、移行時の混乱を最小化できる点が大きなメリットです。

## SRE視点での活用ポイント

### CloudWatch Logs インテリジェントティアリングの運用戦略

CloudWatch Logs のインテリジェントティアリングは、ログ管理戦略を根本から見直す機会となります。特に以下のシナリオで効果を発揮します。

有効化の手段として告知に明記されているのは AWS Management Console、CLI、SDK の3つです（IaC ツールの対応状況は各プロバイダーのリリースを確認してください）。重要なのは、有効化後の効果測定です。コストと使用状況レポートでストレージコストの推移を追跡し、導入前後の変化を定期的にモニタリングします。

また、古いデータにアクセスすると該当データは30日間 Standard 層へ自動昇格するため、障害調査などで一時的に古いログを繰り返し参照するケースでも、その間のアクセスは Standard 層で処理されます。

移行の閾値（30日で Infrequent Access、90日で Archive Instant Access）は自動管理であり、告知時点でカスタマイズ可能とは明記されていません。コンプライアンス要件やログの参照パターンにこの固定的な挙動が合うかを事前に確認しましょう。また、既存の S3 エクスポート運用がある場合、段階的な移行計画を立てることで、運用の複雑化を避けられます。

### Cognito パスワードハッシュインポートの移行計画

Cognito へのユーザー移行プロジェクトでは、このアップデートにより移行リスクが大幅に低減されます。障害対応のランブックに組み込む際は、以下の点を考慮します。

まず、移行前にソースシステムのパスワードハッシュアルゴリズムを正確に特定することが重要です。システムによっては複数のアルゴリズムが混在している場合があり（過去のバージョンアップ時に変更など）、これを見落とすと一部ユーザーがログインできない事態になります。

段階的な移行戦略として、少数のテストユーザーで先行検証し、ログイン成功率やエラーパターンを分析します。本番移行時は、カスタマーサポートチームとの連携体制を整え、問題発生時の escalation フローを明確にしておきます。

また、移行後もしばらくは旧システムを並行稼働させ、ログイン失敗が発生した場合のフォールバック機構を用意しておくことで、ユーザー体験の維持とリスク管理を両立できます。セキュリティ監査の観点では、インポート時のハッシュアルゴリズムと追加暗号化層の詳細をドキュメント化し、定期的なレビュー対象に含めます。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon Cognito | パスワードハッシュを含む CSV ユーザーインポートに対応（bcrypt、scrypt、Argon2id、PBKDF2 対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-cognito-password-hash-import/) |
| Amazon CloudWatch Logs | インテリジェントストレージティアリング機能を追加（Standard、Infrequent Access、Archive Instant Access の3層を自動管理） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-cloudwatch-intelligent-tiering/) |
| Amazon MQ for RabbitMQ | M7g インスタンスで EBS ストレージサイズを独立設定可能に（5GB 単位でカスタマイズ、クラスタ展開のみ対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-mq-rabbitmq-configurable-storage/) |
| Amazon MSK Express | Apache Kafka 4.2 に対応（ELR 機能強化、新リバランスプロトコル、Streams Rebalance Protocol 追加） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-msk-express-version-42/) |
| Amazon RDS for Db2 | 5つの新リージョンで利用可能に（タイ、マレーシア、台北、メキシコ中部、カナダ西部） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-db2-available-additional-aws-commercial-regions) |
| Amazon RDS / Aurora | R8gd と M8gd インスタンスを複数リージョンに拡大（Optimized Reads 対応、R6g 比最大 165% スループット向上） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-aurora-r8gd-m8gd-regions/) |
| Amazon RDS / Aurora | Graviton4 ベースの R8g と M8g インスタンスを複数リージョンに拡大（Graviton3 比最大 40% パフォーマンス向上、オンデマンド料金で最大 29% の価格性能比向上） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/7/amazon-rds-aurora-r8g-m8g-regions/) |
| Amazon OpenSearch Service | Agent Toolkit for AWS に対応（Claude Code、Kiro、Cursor などの AI コーディングエージェントから自然言語で操作可能） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-opensearch-service-agent/) |
| Amazon RDS | 24時間のローリングウィンドウ内で最大4回のストレージ修正が可能に（6時間クールオフ期間が不要に） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-upto-four-storage-modifications-24-hours) |
| Amazon CloudWatch | lookup processor 機能を追加（CSV 参照データを使用したログエンリッチメントを自動化） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-cloudwatch-lookup-processor/) |
| Amazon EC2 | M8in、M8idn、M8ib、M8idb インスタンスが3リージョンに拡大（オハイオ、アイルランド、東京）、第6世代 Intel Xeon 搭載で前世代比最大 43% パフォーマンス向上 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/m8in-m8idn-m8ib-m8idb-new-regions) |
| AWS Lambda | 自己管理型 S3 バケットでのコード保存に対応（75GB の制限を超えた運用が可能、Lambda 管理ストレージのデフォルト上限も 300GB に拡大） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/lambda-self-managed-code-storage/) |
| AWS Lambda Console | コーディングエージェント向けワンクリックセットアップ機能を追加（AWS Serverless スキルと Serverless MCP サーバーを自動構成） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-lambda-prompt-coding-agents/) |

## まとめ

今回紹介したアップデート群は、運用の自動化とコスト最適化、開発者体験の向上という3つの軸で整理できます。

CloudWatch Logs のインテリジェントティアリングは、長年の課題であったログ管理コストの最適化に対する AWS の回答です。S3 エクスポートや外部ツールへの依存を減らし、CloudWatch 単体で完結する運用が可能になったことで、システムアーキテクチャがシンプルになります。

Cognito のパスワードハッシュインポートは、レガシーシステムからのモダナイゼーションを加速させる重要な機能です。ユーザー体験を損なわない移行が実現できることで、より多くの企業が Cognito への移行を検討できるようになるでしょう。

データベース関連では、RDS と Aurora の新世代インスタンスが複数リージョンに拡大され、グローバル展開がさらに容易になっています。また、RDS のストレージ修正制限緩和や、Amazon MQ のストレージ独立設定など、細かな運用改善も着実に進んでいます。

Lambda の自己管理型コード保存対応とコンソールのコーディングエージェント統合は、サーバーレス開発の生産性向上に直結します。特に AI コーディングエージェントとの統合は、今後の開発スタイルの変化を先取りした機能と言えるでしょう。

これらのアップデートは、個別に見ても有用ですが、組み合わせることでさらに大きな効果を発揮します。自社の運用課題や開発スタイルに照らし合わせて、適用可能なアップデートから段階的に導入していくことをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)