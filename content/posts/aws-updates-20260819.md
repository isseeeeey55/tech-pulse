---
title: "【AWS】2026/08/19 のアップデートまとめ"
date: 2026-08-19T08:01:55+09:00
draft: false
tags: ["aws", "ec2", "rds", "postgresql", "sagemaker", "bedrock", "iam", "mwaa", "msk", "ecr", "corretto", "workspaces"]
categories: ["AWS Updates"]
summary: "2026/08/19 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260819/header.png)

# 直近の AWS アップデート情報まとめ（2026年8月）

## はじめに

今回は、直近で発表された10件の AWS アップデートを紹介します。EC2 の新インスタンスタイプの地域拡大、PostgreSQL 19 Beta のプレビュー提供、IAM Policy Autopilot の Terraform 対応、Amazon Bedrock AgentCore の決済機能 GA など、コンピューティング、データベース、セキュリティ、AI/ML の各領域で注目すべき機能強化が行われています。特に、運用効率とセキュリティを高める Infrastructure as Code 関連の改善や、サーバーレス環境の機能拡充が目立ちます。本記事では、これらのアップデートの中から特に実務に影響の大きいものを深掘りし、SRE の視点での活用ポイントを交えて解説します。

## 注目アップデート深掘り

### IAM Policy Autopilot の Terraform plan ファイル対応

IAM Policy Autopilot が Terraform plan ファイルの入力に対応しました。これは、Infrastructure as Code（IaC）で AWS インフラを管理する組織にとって、セキュリティと運用効率の両面で大きな価値を持つアップデートです。

**なぜ重要なのか**

従来、Terraform でインフラを構築する際、IAM ポリシーの設計は手動で行うか、広範な権限を持つ管理者ポリシーに頼る必要がありました。最小権限の原則に従ったポリシーを作成するには、各リソースの CRUD 操作を詳細に理解し、ARN パターンを正確に記述する必要があり、時間とセキュリティの専門知識が求められました。

今回の機能により、Terraform plan ファイルを入力するだけで、そのプランに含まれるリソース操作に必要な IAM ポリシーが自動生成されます。生成されるポリシーは、ワイルドカード（`*`）ではなく、可能な限り具体的なリソース ARN を参照するため、AWS のセキュリティベストプラクティスに準拠した形になります。

**従来の方法との比較**

従来、多くのチームは以下のような課題を抱えていました：

- **過剰な権限付与**: `AdministratorAccess` や `PowerUserAccess` など広範な権限を持つポリシーを使用し、セキュリティリスクが高まる
- **手動作成の負担**: リソースごとに必要なアクションを調査し、JSON でポリシーを記述する作業に時間がかかる
- **保守の困難さ**: インフラ変更時に IAM ポリシーの更新を忘れ、権限不足や過剰権限が発生する

IAM Policy Autopilot を使うことで、Terraform plan の内容を決定論的に分析し、必要最小限の権限のみを含むポリシーが自動生成されます。例えば、S3 バケットと Lambda 関数を作成する plan であれば、`s3:CreateBucket`、`lambda:CreateFunction` などの具体的なアクションと、それぞれのリソース ARN が明示されたポリシーが出力されます。

**実際の使用方法**

IAM Policy Autopilot はオープンソースツールとして提供されており、追加コストなしで利用できます。基本的な流れは以下の通りです：

1. Terraform で `terraform plan -out=plan.tfplan` を実行し、plan ファイルを生成
2. `terraform show -json plan.tfplan` で JSON 形式に変換
3. IAM Policy Autopilot に JSON plan ファイルを入力
4. 生成された IAM ポリシーを確認し、CI/CD パイプラインや Terraform モジュールに組み込む

生成されたポリシーは、従来のアプリケーションソースコード分析と組み合わせることで、エンドツーエンドの IaC セキュリティ対応を実現できます。

### PostgreSQL 19 Beta 3 のプレビュー環境提供

Amazon RDS で PostgreSQL 19 Beta 3 がプレビュー環境で利用可能になりました。このベータ版では、クエリパフォーマンスと autovacuum 管理に関する重要な新機能が追加されています。

**主な新機能とその意義**

PostgreSQL 19 Beta 3 では、データベース運用の課題として長年指摘されてきた autovacuum のチューニングとクエリプランの安定性に関する改善が行われています。

**autovacuum の可視化とパフォーマンス向上**

`pg_stat_autovacuum_scores` ビューが新たに追加され、autovacuum がどのテーブルを優先的に処理しているかを監視・チューニングできるようになりました。従来は autovacuum の挙動がブラックボックス化しやすく、大規模テーブルのメンテナンスが遅延してテーブル肥大化やトランザクション ID 枯渇のリスクが発生することがありました。

さらに、並列 autovacuum により、複数ワーカーを使用して大規模テーブルのメンテナンスを高速化できます。これにより、数百 GB 以上のテーブルを持つシステムでも、メンテナンスウィンドウ内に処理を完了させやすくなります。

**クエリプランの安定化**

`pg_plan_advice` モジュールでは、効率的なクエリプランを「ロック」して予期しないスローダウンを防止できます。本番環境では、統計情報の変化やデータ分布の変動により、突然クエリプランが変わってパフォーマンスが劣化することがあります。この機能により、特定のクエリについて最適なプランを固定し、安定したパフォーマンスを維持できます。

**集計クエリの最適化**

Eager Aggregation により、集計クエリの性能が向上します。これは、BI ツールや分析クエリを多用するアプリケーションにとって重要な改善です。

**プレビュー環境の活用**

RDS のプレビュー環境では、最大 60 日間インスタンスを保持できます。本番環境への導入前に、以下の検証を行うことが推奨されます：

- 既存アプリケーションとの互換性確認
- PostgreSQL 18 とのパフォーマンスベンチマーク比較
- 新機能による運用改善効果の測定
- メジャーバージョンアップグレードのリハーサル

プレビュー環境から本番環境への移行は、ダンプ・ロードによるデータ移行が必要です。

## SRE 視点での活用ポイント

**IAM ポリシー自動生成による運用改善**

Terraform で AWS インフラを管理している組織であれば、IAM Policy Autopilot を CI/CD パイプラインに組み込むことで、セキュリティと開発速度の両立が可能になります。例えば、プルリクエスト時に自動的にポリシーを生成し、レビューの一部として確認するワークフローが考えられます。

導入時の判断基準としては、以下の点を考慮すると良いでしょう：

- **Terraform の利用状況**: すでに Terraform でインフラを管理しているプロジェクトでは導入効果が高い
- **IAM ポリシー管理の複雑さ**: マルチアカウント環境や多数のリソースを扱う場合、手動管理のリスクが大きい
- **セキュリティ要件**: 最小権限の原則を厳密に適用する必要がある組織で特に有効

注意点として、生成されたポリシーは必ずレビューし、組織のセキュリティポリシーに適合しているか確認する必要があります。また、オープンソースツールであるため、バージョンアップや既知の問題を定期的にチェックする運用体制も必要です。

**PostgreSQL 19 のプレビュー環境活用**

PostgreSQL のメジャーバージョンアップグレードは、互換性確認とパフォーマンステストに時間がかかります。RDS のプレビュー環境を活用することで、本番環境への影響を最小限に抑えながら新バージョンの評価が可能です。

特に、`pg_stat_autovacuum_scores` による autovacuum の可視化は、大規模データベースを運用するチームにとって価値があります。CloudWatch と組み合わせてメトリクスを収集し、アラートを設定することで、テーブル肥大化の兆候を早期に検知できます。

並列 autovacuum については、本番導入前に以下の点を検証すると良いでしょう：

- ワーカー数増加による CPU・I/O への影響
- 他のトランザクションへの影響（ロック競合など）
- メンテナンスウィンドウ内での処理完了の確実性

**その他のアップデートの運用への適用**

Amazon MWAA Serverless の PythonOperator / BashOperator 対応は、データパイプラインの運用を簡素化します。公式告知では、データ変換・フォーマット変換・データ品質チェックといった日常的なコードパターンを、追加のインフラをプロビジョニングせずに実行できる点が挙げられています。Python モジュールやシェルスクリプトを S3 にアップロードし、ワークフロー作成時に参照する形で利用します。ただし、実行時間が長い処理や大量のリソースを消費する処理については、従来のワーカーベースの実行との性能比較が必要です。

Amazon Corretto の8月度クリティカルセキュリティパッチ（CSPU）は、Java ランタイムを運用しているチームにとって計画的な適用が必要な更新です。対象は Corretto 26・25・21・17・11・8 の各系統で、Linux では Apt / Yum / Apk リポジトリを構成しておくと自動更新の対象にできます。告知では個別の CVE 番号までは示されていないため、詳細が必要な場合は Corretto のリリースページを確認してください。

Amazon WorkSpaces の Nested Virtualization 対応は、仮想デスクトップ上で Docker Desktop や WSL2、KVM ベースのワークロードを直接動かせるようになる点で、開発者向け VDI の適用範囲を広げます。導入時は前提条件に注意が必要で、DCV プロトコルが必須、Power（4 vCPU）以上が推奨、GPU バンドル・PCoIP・Windows Server 2016・Windows 10 は非対応です。また、中国（寧夏）とイスラエル（テルアビブ）の両リージョンは対象外とされています。

Amazon MSK のカスタムドメイン名対応は、公式告知でもクラスター移行・災害復旧フェイルオーバー・スケーリング操作のシナリオが挙げられています。クライアントアプリケーションが同じ接続エンドポイントを維持できるため、これらの操作時に再構成が不要になります。運用上は、DNS キャッシュの TTL 設定に注意し、切り替え時間を適切に見積もる必要があります。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon EC2 | [R8i instances available in Israel (Tel Aviv)](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-r8i-israel-tel-aviv/) | メモリ最適化インスタンス R8i がテルアビブリージョンで利用可能に。Intel Xeon 6 搭載で R7i 比 20% 高性能。PostgreSQL で最大 30%、NGINX で最大 60%、AI ディープラーニング推薦モデルで最大 40% 高速 |
| Amazon RDS | [PostgreSQL 19 Beta 3 in Preview Environment](https://aws.amazon.com/about-aws/whats-new/2026/08/postgresql-19-beta-3-amazon-rds-database-preview-environment/) | PostgreSQL 19 Beta 3 がプレビュー環境で利用可能。autovacuum の可視化・並列化、クエリプランの安定化、集計クエリの最適化などを提供 |
| Amazon SageMaker | [Unified Studio supports data profiling and anomaly detection](https://aws.amazon.com/about-aws/whats-new/2026/05/smus-data-profiling) | データプロファイリングと異常検知機能を追加。AWS Glue Data Quality により、統計プロファイル生成と時系列変化追跡が可能 |
| Amazon Bedrock | [AgentCore payments generally available](https://aws.amazon.com/about-aws/whats-new/2026/08/bedrock-agentcore-payments-ga/) | AI エージェントが有料 API やコンテンツに自動アクセスし、決済を実行。Coinbase・Stripe Privy 統合、支払い制限、エンドツーエンド可観測性を提供 |
| IAM | [IAM Policy Autopilot supports Terraform plan files](https://aws.amazon.com/about-aws/whats-new/2026/08/iam-policy-autopilot-now-supports-terraform-plan-files) | Terraform plan ファイルから IAM ポリシーを自動生成。具体的な ARN 指定によりセキュリティベストプラクティスに準拠 |
| Amazon MWAA | [MWAA Serverless supports PythonOperator and BashOperator](https://aws.amazon.com/about-aws/whats-new/2026/08/mwaa-serverless-pythonoperator-bashoperator/) | サーバーレスランタイム内で Python 関数やシェルスクリプトを直接実行可能に。追加インフラ不要でデータ変換・品質チェックを実行 |
| Amazon MSK | [MSK supports custom domain names](https://aws.amazon.com/about-aws/whats-new/2026/17/amazon-msk-custom-domain-names/) | MSK Provisioned クラスターでカスタムドメイン名を設定可能に。ZooKeeper と KRaft 両対応で、クラスター移行時の再構成が不要 |
| Amazon ECR | [ECR supports 25 replication rules per registry](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecr-increased-replication-rules-limit) | レプリケーションルール上限が 10 から 25 に増加。マルチリージョン・マルチアカウント環境でより柔軟な配信戦略が可能 |
| Amazon Corretto | [August 2026 Critical Security Patch Updates](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-corretto-august-2026-security-updates) | Corretto 26.0.2.11.1・25.0.4.8.1・21.0.12.9.1・17.0.20.10.1・11.0.32.10.1・8u504 に CSPU を提供。Linux は Apt / Yum / Apk リポジトリ経由で更新可能 |
| Amazon WorkSpaces | [WorkSpaces supports Nested Virtualization](https://aws.amazon.com/about-aws/whats-new/2026/08/nested-virtualization-workspaces/) | Windows で Docker Desktop・WSL2 など、Linux で KVM ワークロード・Android エミュレータを実行可能に。DCV プロトコルが必須で、GPU バンドル・PCoIP は非対応 |

## まとめ

今回紹介したアップデートは、Infrastructure as Code によるセキュリティ強化、データベース運用の最適化、サーバーレス環境の機能拡充など、運用効率とセキュリティの両面で実務に直結する改善が中心でした。

特に IAM Policy Autopilot の Terraform 対応は、IaC を採用している組織にとって、セキュリティポリシーの自動化という大きな前進です。PostgreSQL 19 Beta のプレビュー提供は、本番導入前の十分な検証期間を確保できる点で評価できます。

その他、Amazon MWAA Serverless や MSK のカスタムドメイン対応、ECR のレプリケーションルール拡張など、既存サービスの使い勝手を向上させるアップデートが多く見られました。これらの機能は、段階的に導入を検討し、実際の運用シナリオでの効果を測定しながら活用していくことが推奨されます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)