---
title: "【AWS】2026/07/17 のアップデートまとめ"
date: 2026-07-17T08:02:39+09:00
draft: true
tags: ["aws", "ec2", "ssm", "managed-grafana", "sustainability", "redshift", "rds", "postgresql", "s3", "eventbridge", "control-tower", "cloudwatch-logs"]
categories: ["AWS Updates"]
summary: "2026/07/17 のAWSアップデートまとめ"
---

# 直近の AWS アップデート 11 件を徹底解説：EC2、CloudWatch Logs、Control Tower の進化に注目

## はじめに

今回は、直近で発表された **11 件の AWS アップデート** を紹介します。EC2 では公開 AMI の SSM パラメータ自動表示機能や、高性能な G7e・U7in インスタンスの新リージョン対応が実現しました。CloudWatch Logs Insights には 25 の新しいクエリコマンドが追加され、ログ分析の幅が大きく広がっています。Control Tower Account Factory for Terraform では OU 間のアカウント移動時に自動でカスタマイズが再適用される機能が登場し、運用の自動化がさらに進化しました。また、Amazon Redshift の新 RG インスタンス、PostgreSQL 19 Beta 2 のプレビュー提供、S3 イベント通知のシステム生成タグ対応、AWS Sustainability サービスへの水使用量データ追加など、データベース、ストレージ、サステナビリティ領域でも重要な機能追加が行われています。

それぞれのアップデートについて、技術的な背景と実務での活用方法を掘り下げて解説していきます。

---

## 注目アップデート深掘り

### 1. Amazon EC2 公開 AMI に関連する SSM パラメータの自動表示

Amazon EC2 が公開 AMI に関連付けられた AWS Systems Manager (SSM) Parameter Store のパラメータを AMI メタデータに直接表示するようになりました。これは Infrastructure as Code (IaC) で AMI を管理する際の自動化を大きく改善する機能です。

**背景と重要性**

従来、公開 AMI（例：Amazon Linux、Ubuntu、Windows Server の公式イメージなど）を最新バージョンで利用したい場合、SSM Parameter Store に公開されているパラメータを手動で検索し、そのパラメータ名をコード内に記述する必要がありました。例えば Amazon Linux 2023 の最新 AMI ID を参照するには、`/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64` のようなパラメータ名を知っている必要がありましたが、このパラメータ名を見つけるためには SSM のネームスペースを探索する作業が必要でした。

今回の改善により、`describe-images` API を呼び出した際のレスポンスに、関連する SSM パラメータ情報が自動的に含まれるようになります。これにより、AMI を検索した時点で「この AMI は SSM パラメータ `/aws/service/...` で参照できる」という情報が即座に得られます。

**実務での活用方法**

AWS CLI で実際に確認する場合、以下のようなコマンドで公開 AMI の詳細とともに SSM パラメータ情報が取得できます：

```bash
$ aws ec2 describe-images \
    --owners amazon \
    --filters "Name=name,Values=al2023-ami-*" \
    --query 'Images[0]'
```

レスポンスには従来の AMI メタデータに加えて、関連する SSM パラメータの情報が含まれるため、このパラメータ名をそのまま Terraform や CloudFormation のデータソースで利用できます。

Terraform での活用例として、従来はハードコードされた AMI ID や手動で調べた SSM パラメータ名を使う必要がありましたが、今後は AMI 検索結果から得られた SSM パラメータ名を使って常に最新版を参照する構成が容易になります。SSM パラメータは自動的に最新の AMI ID に解決されるため、定期的な AMI 更新作業が不要になり、セキュリティパッチ適用の自動化も実現しやすくなります。

**従来との比較**

- **従来の方法**: AMI を選定 → SSM パラメータを手動検索 → パラメータ名を IaC に記述
- **新しい方法**: AMI を検索 → レスポンスに含まれる SSM パラメータ情報を直接利用

この改善により、マルチリージョンでのデプロイメント時にも各リージョンの最新 AMI を効率的に参照できるようになります。CI/CD パイプラインでは AMI ID のハードコーディングを排除し、常に推奨される最新イメージを自動選択する仕組みが構築しやすくなります。

---

### 2. AWS Control Tower Account Factory for Terraform の OU 移動時自動カスタマイズ再適用

AWS Control Tower Account Factory for Terraform (AFT) に、アカウントを異なる Organization Unit (OU) に移動する際、カスタマイズ設定を自動的に再適用する機能が追加されました。これは大規模な AWS Organizations 環境で運用の一貫性を保ちながら組織変更に対応するための重要な改善です。

**背景と課題**

AWS Control Tower では、OU 単位でガードレール（統制ルール）や Service Control Policy (SCP) を適用し、アカウントのガバナンスを実現します。AFT を使うと、Terraform でアカウントのプロビジョニングとカスタマイズ（セキュリティ設定、ネットワーク構成、タグ付けルールなど）を自動化できますが、従来は登録済みアカウントを別の OU に移動した際、その OU に適したカスタマイズを再適用するには手動でワークフローをトリガーする必要がありました。

例えば、開発環境用 OU から本番環境用 OU にアカウントを昇格させる場合、本番環境固有のセキュリティベースライン（厳格な CloudTrail 設定、AWS Config ルール、VPC 設定など）を手動で適用し直す必要があり、設定漏れや不整合（設定ドリフト）のリスクがありました。

**新機能の仕組み**

AFT デプロイメントの設定に以下のパラメータを追加することで、自動再適用を有効化できます：

```hcl
aft_customization_triggers = ["account_move"]
```

この設定により、アカウントが OU 間で移動されると、AFT が自動的にカスタマイズワークフローを起動します。ワークフローはブートストラップ（初期セットアップ）やプロビジョニングフェーズをスキップし、グローバルカスタマイズとアカウントレベルのカスタマイズのみを実行するため、高速に完了します。

個別のアカウントで自動再適用を無効にしたい場合は、そのアカウントの設定に以下を追加します：

```hcl
account_skip_customization_triggers = "true"
```

これにより、特定のアカウント（例：テスト中のアカウントや特殊な構成のアカウント）を自動再適用の対象から除外し、チームが柔軟に制御できます。

**実務での効果**

- **組織再編時の安全性向上**: 部門統廃合で OU 構成を変更する際、数百のアカウントが移動しても設定の一貫性が自動的に維持される
- **コンプライアンス要件の動的適用**: セキュリティレベル別の OU（例：PCI-DSS 準拠 OU）にアカウントを移動すると、即座に該当する統制ルールが適用される
- **開発→ステージング→本番の段階的昇格**: アカウントライフサイクル管理において、環境レベルに応じた自動的なポリシー切り替えが実現

さらに今回のアップデートでは、Terraform Cloud/Enterprise のカスタムワークスペース命名変数対応、AFT ロギングバケットへのアクセス制御強化、大規模な AWS Enterprise Support 登録時のスケーリング改善も含まれており、エンタープライズ環境での AFT 運用がより安定します。

---

### 3. Amazon CloudWatch Logs Insights に 25 の新しいクエリコマンドと関数を追加

Amazon CloudWatch Logs Insights のクエリ言語が大幅に強化され、25 個の新しいコマンドと関数が追加されました。これによりログ分析の表現力が飛躍的に向上し、複雑な分析を CloudWatch 上で直接実行できるようになります。

**追加された機能カテゴリ**

新機能は以下のカテゴリに分類されます：

1. **型変換・エンコーディング関数**: `hexToAscii`, `hexToDec`, `decToHex` など、16 進数エンコードされたログデータを復号化・変換
2. **日時関数**: `parseDate`, `formatDate`, `queryStartTime`, `queryEndTime`, `queryTimeRange` で、柔軟な時刻処理とクエリ範囲の参照
3. **文字列・JSON 検査関数**: `messageSize`, `jsonArraySize`, `jsonArrayContains` で、ログメッセージや JSON 構造の詳細分析
4. **統計コマンド**: `variance`, `topk`, `countFrequent` で分散計算や頻出要素の抽出
5. **行処理・Null 値処理**: `autoregress`, `accum`, `filldown`, `fillmissing` で時系列データの欠損値補完
6. **セッション化・時間比較**: `sessionize`, `logcompare` でユーザーセッション追跡や時間ウィンドウ間のログ比較
7. **異常検知**: `outlier` で統計的な外れ値を自動検出
8. **データ結合・ルックアップ**: `cidrlookup` で CIDR ベースの IP アドレス検証とルックアップテーブル結合

**実務での活用例**

従来の CloudWatch Logs Insights では、基本的な `fields`, `filter`, `stats` コマンドで集計やフィルタリングを行うことはできましたが、以下のような高度な分析には外部ツール（Athena、EMR、Lambda による後処理など）が必要でした：

- **セッション分析**: ユーザーの一連の操作ログをセッション単位でグループ化し、セッション時間やイベント順序を分析
- **異常検知**: API レスポンスタイムの統計的外れ値を自動検出し、パフォーマンス劣化の兆候を早期発見
- **時系列データの欠損補完**: 定期的な監視ログで欠損した時刻のデータを前後の値で補完
- **CIDR ベースのアクセス制御監査**: アクセスログの送信元 IP が許可リスト内の CIDR 範囲に含まれるか検証

新しいコマンドにより、これらの分析が CloudWatch Logs Insights 上で直接実行できるようになり、ログデータを外部にエクスポートする手間やコストが削減されます。

**具体的な使用イメージ**

例えば、API ゲートウェイのアクセスログから異常に遅いリクエストを検出する場合、従来は手動で閾値を設定していましたが、`outlier` コマンドを使うと統計的に外れ値を自動抽出できます。また、`sessionize` を使えば、ユーザー ID やセッション ID でログをグループ化し、セッション継続時間やセッション内のイベント数を分析できます。

`cidrlookup` は、セキュリティ監査で「このアクセスは許可された IP 範囲からのものか」を判定する際に有用です。CIDR リストをルックアップテーブルとして定義し、ログ内の IP アドレスと照合することで、不正アクセスの可能性があるログエントリを即座に抽出できます。

時間関連の関数（`queryStartTime`, `queryEndTime` など）を使うと、「現在のクエリ対象期間の開始時刻から 1 時間前」といった相対的な時刻計算が可能になり、定型レポートやダッシュボードのクエリをより柔軟に記述できます。

---

## SRE 視点での活用ポイント

### 運用自動化とインシデント対応の効率化

今回のアップデートは、SRE が日常的に直面する「運用の自動化」「設定の一貫性維持」「障害の早期検知と迅速な分析」といった課題に対する実践的な解決策を提供します。

**AMI 管理の自動化と一貫性の確保**

公開 AMI の SSM パラメータ自動表示機能は、Terraform や CloudFormation で管理しているインフラがある場合、AMI バージョン管理の自動化を大きく前進させます。SSM パラメータを data source として参照することで、定期的なセキュリティパッチ適用を手動介入なしで実現できます。ただし、AMI の自動更新は本番環境では慎重に扱うべきで、ステージング環境での検証プロセスを組み込むことが重要です。Golden AMI パイプラインと組み合わせると、組織独自のカスタマイズを施した AMI についても同様の自動更新の仕組みを構築できます。

**Control Tower 環境でのガバナンス強化**

AFT の OU 移動時自動カスタマイズ再適用機能は、大規模な AWS Organizations 環境で「アカウントが増えても統制が効く」運用を実現するための鍵です。開発環境から本番環境への昇格プロセスをランブックに組み込む際、アカウント移動のステップに自動的にセキュリティベースラインやネットワーク設定が適用されるため、手動チェックリストの項目を減らせます。ただし、自動再適用の対象から除外すべきアカウント（テスト中、特殊構成、段階的移行中など）を明確に定義し、`account_skip_customization_triggers` で適切に管理することが重要です。監査ログと CloudWatch アラームを組み合わせて、意図しないカスタマイズ再適用が発生していないか監視する仕組みも検討すべきです。

**ログ分析の高度化と障害対応の迅速化**

CloudWatch Logs Insights の新コマンド群は、インシデント発生時の根本原因分析（RCA）を大幅に加速します。`outlier` コマンドで異常なレスポンスタイムやエラー率の急上昇を即座に可視化でき、障害対応のランブックに「CloudWatch Logs Insights でこのクエリを実行」というステップを追加することで、オンコールエンジニアが状況を素早く把握できます。`sessionize` を使えば、特定ユーザーが報告した問題を再現するための操作履歴をセッション単位で追跡できます。`logcompare` は、正常時と異常時のログパターンを比較する際に有用で、「昨日の同時刻と今日のログの差分」を定量的に評価できます。

ただし、これらの新機能を活用するには、クエリのベストプラクティスやパフォーマンス特性を理解する必要があります。大量のログに対して複雑なクエリを実行すると処理時間が長くなる可能性があるため、ログの保存期間やクエリ対象範囲を適切に設計することが重要です。

### リソース選択とコスト最適化の判断基準

Redshift の新 RG インスタンスや EC2 の G7e、U7in インスタンスの追加は、ワークロードの性能要件とコスト制約のバランスを取る際の選択肢を増やします。RG インスタンスは RA3 比で vCPU あたり 30% 低価格かつ最大 2.4 倍高速ですが、既存クラスタからの移行にはスナップショット・リストアやエラスティックリサイズが必要です。移行時のダウンタイムや検証工数を考慮し、まずはステージング環境で性能・互換性を確認することが推奨されます。G7e インスタンスは LLM 推論ワークロードで G6e 比 2.3 倍の性能向上を実現しますが、GPU メモリや EFA の構成によってはアプリケーション側の最適化も必要です。新リージョン（フランクフルト、ストックホルム、ムンバイ）での提供開始は、ユーザー近接性やデータレジデンシー要件を満たす選択肢を提供します。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon EC2 now surfaces the public SSM parameters associated with public AMIs](https://aws.amazon.com/about-aws/whats-new/2026/07/ec2-public-images-ssm-parameters) | 公開 AMI の詳細情報取得時に関連 SSM パラメータが自動表示され、IaC での AMI 管理が簡素化 |
| 2 | [Amazon Managed Grafana achieves FedRAMP High authorization in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-grafana-fedramp-high/) | AWS GovCloud で FedRAMP High 認可を取得し、連邦機関・公共部門での利用が可能に |
| 3 | [AWS Sustainability service now includes water withdrawals data](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-sustainability-water-withdrawals/) | カーボン排出量に加えて水使用量データが追加され、環境影響の統合的な可視化が実現 |
| 4 | [Amazon Redshift adds rg.large and rg.12xlarge instance sizes](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-redshift-adds-rg-large-12xlarge-instance-sizes) | Graviton 搭載の新 RG インスタンスが追加され、RA3 比で最大 2.4 倍高速・30% 低価格を実現 |
| 5 | [PostgreSQL 19 Beta 2 is now available in Amazon RDS Database Preview Environment](https://aws.amazon.com/about-aws/whats-new/2026/07/postgresql-19-beta-2-amazon-rds-database-preview-environment/) | PostgreSQL 19 Beta 2 がプレビュー環境で利用可能に。並列自動バキュームやオンラインテーブル再構築など新機能を検証可能 |
| 6 | [Amazon EC2 High Memory U7in-24TB instances now available in AWS Europe (Paris) region](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-high-memory-europe/) | 24 TiB メモリを搭載した U7in インスタンスがパリリージョンで提供開始。SAP HANA など大規模インメモリ DB 向け |
| 7 | [Amazon S3 Event Notifications now include system-generated tags](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-s3-event-notifications-system-generated-tags/) | S3 イベント通知にシステム生成タグが含まれ、タグベースのフィルタリングで大規模バケット管理が効率化 |
| 8 | [AWS Control Tower Account Factory for Terraform now re-applies customizations when accounts move between OUs](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-control-tower-account/) | AFT がアカウントの OU 間移動時に自動的にカスタマイズを再適用し、運用の一貫性を維持 |
| 9 | [Amazon CloudWatch Logs Insights adds 25 new query commands and functions](https://aws.amazon.com/about-aws/whats-new/2026/7/amazon-cloudwatch-logs-insights-ql/) | 型変換、日時処理、統計、異常検知、セッション化など 25 の新コマンドでログ分析が大幅強化 |
| 10 | [Amazon EC2 G7e instances now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-g7e-additional-regions/) | NVIDIA RTX PRO 6000 Blackwell 搭載の G7e インスタンスが欧州・アジア太平洋リージョンで提供開始。G6e 比 2.3 倍の推論性能 |

---

## まとめ

今回紹介した 11 件のアップデートは、AWS の運用自動化、ガバナンス、分析、性能最適化の各領域で重要な進化をもたらします。特に EC2 の AMI 管理、Control Tower の OU 移動時自動適用、CloudWatch Logs Insights の高度なクエリ機能は、SRE チームが日常的に直面する運用課題に対する実践的な解決策となります。

Redshift の RG インスタンスや EC2 の G7e・U7in インスタンスは、性能とコストのバランスを取る際の選択肢を増やし、ワークロードの特性に応じた最適なリソース選択を可能にします。PostgreSQL 19 Beta 2 のプレビュー提供は、次期メジャーバージョンへの移行準備を早期に開始できる機会を提供します。

S3 イベント通知のシステム生成タグ対応は、大規模なバケット管理において EventBridge ルールの簡素化とメンテナンス性向上に貢献します。AWS Sustainability サービスへの水使用量データ追加は、ESG 目標達成に向けた環境影響の可視化を強化します。Managed Grafana の FedRAMP High 認可は、公共部門や規制の厳しい業界での採用を促進します。

これらの新機能を活用する際は、まずステージング環境や Preview Environment で動作を確認し、本番環境への適用前に性能・互換性・運用影響を評価することが重要です。特に自動化機能（AMI 自動更新、OU 移動時の自動カスタマイズ再適用など）は、意図しない影響を避けるため段階的な導入と監視体制の整備が推奨されます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)