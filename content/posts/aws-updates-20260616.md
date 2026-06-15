---
title: "【AWS】2026/06/16 のアップデートまとめ"
date: 2026-06-16T08:02:15+09:00
draft: true
tags: ["aws", "cloudwatch", "bedrock", "route53", "cost-explorer", "lambda", "ecs", "devops-agent", "organizations", "billing-conductor", "ec2", "ebs", "eni", "s3", "security-hub", "config", "marketplace", "opentelemetry", "grafana", "promql"]
categories: ["AWS Updates"]
summary: "2026/06/16 のAWSアップデートまとめ"
---

# 直近の AWS アップデート 9 件まとめ — CloudWatch 統合分析、マルチアカウント監視、DevOps Agent 拡張など

## はじめに

今回は、直近で発表された 9 件の AWS アップデートを紹介します。Amazon CloudWatch の統合分析・監視機能の大幅強化、Route 53 DNS Firewall への Palo Alto Networks 統合、Amazon Bedrock AgentCore Memory の厳密一貫性メタデータ対応、AWS Lambda Managed Instances のタグ伝播、ECS Express Mode の GovCloud 対応、AWS DevOps Agent のカスタム SRE エージェント対応など、運用効率とセキュリティ向上に焦点を当てた内容が中心です。特に CloudWatch 関連の 3 つのアップデートは、ログ分析・メトリクス可視化・クロスアカウント監視の各領域で統合体験を強化しており、マルチアカウント・マルチリージョン環境での運用負荷軽減に大きく貢献します。

---

## 注目アップデート深掘り

### Amazon CloudWatch Log Analytics — 統合コンソールでログ分析を効率化

Amazon CloudWatch に **Log Analytics** という新しい統合コンソール機能が追加されました。これまで **CloudWatch Logs Insights**（ログ検索・分析）、**Live Tail**（リアルタイムログストリーミング）、**Contributor Insights**（トップコントリビューター分析）は個別のツールとして提供されていましたが、今後はこれらが 1 つの場所に統合され、**複数クエリのタブ並行実行**、**パターン認識**、**保存済みクエリ**、**ファセット検索**、**自然言語クエリ生成**、**ビジュアライゼーション**などの既存機能もすべて利用できます。

#### なぜこのアップデートが重要なのか

マイクロサービスアーキテクチャや複数の AWS アカウント・リージョンを運用する環境では、インシデント発生時に複数のログソースを同時に調査する必要があります。従来は個別のツールを行き来しながら、それぞれの UI で操作を繰り返す必要がありました。Log Analytics により、**単一のワークスペースで複数のログストリームを並行調査**できるため、インシデント対応時間の短縮と運用効率の向上が期待できます。

#### 従来の方法との比較

- **従来**：Logs Insights でクエリを実行 → 別ウィンドウで Live Tail を起動 → さらに別の画面で Contributor Insights を確認、という複数ステップが必要
- **Log Analytics 導入後**：1 つのコンソールで複数のタブを開き、Logs Insights クエリ、Live Tail、Contributor Insights を同時に実行・比較可能

自然言語クエリ生成機能により、SQL や CloudWatch Logs Insights のクエリ構文に不慣れなメンバーでも、自然言語で「過去 1 時間のエラーログを集計」といった指示を入力すれば、適切なクエリが自動生成されます。これにより、SRE チーム以外のメンバー（開発者、プロダクトマネージャーなど）もログ分析に参加しやすくなります。

#### 料金体系

既存の CloudWatch Logs Insights、Live Tail、Contributor Insights と同じ料金体系が適用されます。新しい統合 UI の利用自体に追加料金は発生しません。

> **Note:** すべての商用 AWS リージョンで利用可能です。

---

### Amazon CloudWatch のクロスアカウント・メトリクス集約機能 — 中央監視の実現

Amazon CloudWatch の **メトリクス集約機能** が一般提供されました。この機能により、複数の AWS アカウント・リージョンに散在する CloudWatch メトリクスを、単一の宛先アカウントに自動レプリケーションできます。

#### なぜこのアップデートが重要なのか

エンタープライズ企業では、開発・ステージング・本番環境がそれぞれ別の AWS アカウントで管理され、さらに複数リージョンにまたがることが一般的です。従来、こうした環境の監視では、アカウントごと・リージョンごとに CloudWatch コンソールを切り替えて確認する必要があり、全体像の把握に時間がかかっていました。今回の機能により、AWS Organizations 経由で集約ルールを定義するだけで、ソースアカウント・リージョンのメトリクスが中央アカウントに自動集約されます。これにより、**中央チームがメトリクスデータの完全な所有権を獲得**し、クエリ・アラーム・コンプライアンス・ガバナンスを一元管理できるようになります。

#### 対応機能

CloudWatch メトリクスと OpenTelemetry メトリクスの両方に対応しており、以下の機能と完全互換です：

- Metrics Insights
- ダッシュボード
- アラーム
- Metric Math
- 異常検出
- Metric Streams
- PromQL

#### 実装の流れ

1. AWS Organizations で集約ルールを定義
2. ソースアカウント・リージョンを指定
3. 宛先アカウントを指定
4. メトリクスが自動的に中央アカウントにレプリケーションされる
5. 中央アカウントで Metrics Insights やダッシュボードを使用して統合分析

この機能により、複数リージョンのメトリクスを組み合わせた高度なオートスケーリングルールの作成や、グローバルなインシデント検知が可能になります。

> **Note:** 米国東部・西部、アジア太平洋（ムンバイ・大阪・ソウル・シンガポール・シドニー・東京）、カナダ中部、ヨーロッパ（フランクフルト・アイルランド・ロンドン・パリ・ストックホルム）、南米（サンパウロ）で利用可能です。

---

### AWS Lambda Managed Instances のタグ伝播機能 — ガバナンスとコスト管理の自動化

AWS Lambda Managed Instances（LMI）が **タグ伝播機能** に対応しました。この機能により、容量プロバイダーの設定で指定したタグが、LMI が管理する EC2 インスタンス、EBS ボリューム、ENI（Elastic Network Interface）などのリソースに自動的に適用されます。

#### なぜこのアップデートが重要なのか

Lambda Managed Instances は、Lambda 関数の実行環境を管理する EC2 インスタンスやネットワークリソースを自動で作成しますが、これまではこれらのリソースにタグを伝播させる方法がありませんでした。その結果、以下のような課題がありました：

- **コスト追跡の困難さ**：部門別・プロジェクト別のコスト配分ができない
- **ガバナンスの実装困難**：セキュリティポリシーで「必須タグがないリソースは削除」といったルールを適用できない
- **コンプライアンス要件への対応不足**：監査で必要なメタデータ（オーナー、CostCenter など）を自動記録できない

今回のアップデートにより、容量プロバイダーレベルでタグを設定するだけで、配下のすべてのマネージドリソースに一貫性を持たせることができます。

#### 実装方法

容量プロバイダーの設定でタグを指定します。公式ドキュメントでは、CreateCapacityProvider API に PropagateTags パラメータが追加されています。CloudFormation や AWS CDK を使用する場合も、容量プロバイダーリソースのプロパティとしてタグを定義できます。

#### ユースケース例

- **チャージバック・内部請求**：部門別にタグを自動適用して正確な集計
- **セキュリティコンプライアンス**：全リソースに必須のセキュリティタグを自動付与
- **ガバナンス強化**：SCP（サービスコントロールポリシー）で「承認されたタグなしリソースの削除」を自動執行
- **マルチテナント環境**：テナントごとのタグを自動適用してリソース分離
- **監査対応**：すべてのリソースにメタデータを自動記録

従来は手動でタグを付与するスクリプトを実装したり、定期的な棚卸し作業が必要でしたが、今後はこれらの工数を削減できます。

---

## SRE 視点での活用ポイント

### Log Analytics と Query Studio の統合体験

CloudWatch Log Analytics と Query Studio（こちらも GA になりました）により、ログとメトリクスの統合分析が 1 つのワークスペースで完結するようになりました。SRE チームがインシデント対応時に複数の画面を行き来する手間が減り、**MTTD（Mean Time To Detect）と MTTR（Mean Time To Resolve）の短縮**に直結します。特に、自然言語クエリ生成機能は、オンコールローテーションに参加する開発者が初めて CloudWatch を触る場合でも、迅速にログ調査を開始できる点で有用です。

既に Terraform で CloudWatch ダッシュボードを管理しているチームであれば、Log Analytics と Query Studio で作成したクエリやビジュアライゼーションを、Terraform リソース定義にエクスポートして IaC 化する流れを検討すると良いでしょう。

### クロスアカウント・メトリクス集約と Cost Explorer 履歴保持の組み合わせ

メトリクス集約機能により、複数アカウントの監視を中央で一元化できますが、同時に **Cost Explorer の履歴データ保持機能**（請求グループ内のアカウントで元の AWS 請求レートの履歴データにアクセス可能になったアップデート）と組み合わせることで、**コスト監視と運用監視を統合した分析**が可能になります。例えば、特定リージョンのメトリクススパイク時にコスト増加も同時に確認し、スケーリングポリシーの見直しを判断する、といったシナリオが考えられます。

AWS Billing Conductor と Billing Transfer を導入している環境では、請求グループ設定前後の Cost Explorer データの連続性が保たれるようになったため、長期的なコスト推移分析が容易になります。これにより、マルチアカウント環境での FinOps 活動を支援するダッシュボードを CloudWatch と Cost Explorer の両方から構築できます。

### Lambda Managed Instances のタグ伝播とガバナンス

Lambda Managed Instances のタグ伝播機能は、**SCP（サービスコントロールポリシー）と組み合わせたガバナンス自動化**に有効です。例えば、「CostCenter タグが付与されていないリソースは起動を拒否する」といったポリシーを SCP で定義し、容量プロバイダーレベルでタグを設定することで、手動タグ付け漏れを防げます。

また、AWS Config ルールと組み合わせて「タグが付与されていないリソースを検出したら通知」という自動監査フローを構築すると、コンプライアンス要件を満たしつつ運用負荷を削減できます。導入時の注意点としては、既存の容量プロバイダーにタグを追加する場合、リソースの再作成が必要になる可能性があるため、事前にテスト環境で動作確認を行うことを推奨します。

### DevOps Agent のカスタム SRE エージェント

AWS DevOps Agent の **カスタム SRE エージェント** と **MCP/A2A プロトコル対応** により、定期的な SRE ワークフローの自動化が可能になります。例えば、日次でデータベースの遅いクエリを検出し、パラメータチューニングを提案するレポートを自動生成したり、過去 24 時間のアプリケーションログを自動解析して異常を検知・通知するエージェントを実装できます。

IDE から直接 DevOps Agent を呼び出せるようになったことで、開発者が本番環境の健全性をワンクリックで確認し、インシデント調査を迅速化できます。Kiro や Claude といったコーディングアシスタントと統合することで、コードレビュー中に運用メトリクスを参照する、といった新しいワークフローも考えられます。

運用改善の障害対応ランブックに組み込む際は、Agent Spaces 内でカスタムエージェントをスケジュール実行する設定を Terraform で管理し、チーム全体で再現可能な形にすることを推奨します。

---

## 全アップデート一覧

| タイトル | 概要 | リンク |
|---------|------|--------|
| Amazon CloudWatch introduces Log Analytics for unified log analysis | Logs Insights、Live Tail、Contributor Insights を統合した新しいコンソール機能。複数クエリのタブ並行実行、自然言語クエリ生成に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-log-analytics/) |
| Amazon Bedrock AgentCore Memory now supports strictly consistent metadata for long-term memory | AgentCore Memory に厳密一貫性メタデータ機能を追加。アプリケーションから直接メタデータ値を指定でき、マルチテナント環境やコンプライアンス境界の実装が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/agentcore-memory-scmetadata/) |
| Amazon Route 53 Resolver DNS Firewall now supports Palo Alto Networks Advanced DNS Security (Preview) | Route 53 DNS Firewall に Palo Alto Networks の DNS 脅威対策を統合（プレビュー）。別途ファイアウォールをデプロイせずに DNS レイヤーでの脅威対策が可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-route-53-resolver-dns/) |
| AWS launches Cost Explorer historical data retention for accounts in billing groups | Billing Conductor と Billing Transfer で請求グループにマップされたアカウントが、元の AWS 請求レートの履歴データに Cost Explorer でアクセス可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-cost-explorer/) |
| Amazon CloudWatch Query Studio is now generally available | PromQL と Metrics Insights（SQL）で OpenTelemetry と AWS ネイティブメトリクスを統合クエリできるツールが GA。クロスアカウント・クロスリージョン対応、8 種類以上の可視化タイプをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-query-studio-generally-available/) |
| Amazon CloudWatch now supports cross-account metrics centralization | 複数の AWS アカウント・リージョンに散在する CloudWatch メトリクスを単一の宛先アカウントに自動レプリケーション。Metrics Insights、ダッシュボード、アラーム、Metric Math、異常検出、Metric Streams、PromQL と完全互換 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cross-account-metrics-centralization/) |
| Amazon ECS Express Mode is now available in AWS GovCloud (US) Regions | ECS Express Mode が GovCloud（US）で利用可能に。コンテナイメージを提供するだけで自動的にアプリケーションを展開、AWS 生成ドメイン名により即座にアクセス可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ecs-express-mode-govcloud/) |
| AWS Lambda Managed Instances now supports Tag Propagation for Managed Resources | Lambda Managed Instances がタグ伝播機能に対応。容量プロバイダーで指定したタグが、LMI が管理する EC2 インスタンス、EBS ボリューム、ENI に自動適用 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-lambda-managed-instances-tag-propagation/) |
| AWS DevOps Agent expands with custom SRE agents and MCP/A2A protocols | DevOps Agent がカスタム SRE エージェント、MCP/A2A プロトコルに対応。定期実行ワークフロー自動化、IDE や Claude からの直接アクセスが可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-devops-agent-custom-agents/) |

---

## まとめ

今回のアップデート群は、**統合監視・分析体験の強化** と **ガバナンス・コスト管理の自動化** という 2 つの大きなテーマで整理できます。

CloudWatch 関連の 3 つのアップデート（Log Analytics、Query Studio、クロスアカウント・メトリクス集約）は、マルチアカウント・マルチリージョン環境での運用負荷を大幅に削減します。特に、複数のツールを行き来する手間が減り、SRE チームのインシデント対応時間短縮に直結する点が重要です。自然言語クエリ生成機能により、非エンジニアメンバーもログ分析に参加しやすくなり、チーム全体の可観測性向上が期待できます。

一方、Lambda Managed Instances のタグ伝播、Cost Explorer の履歴データ保持、Route 53 DNS Firewall の Palo Alto Networks 統合といったアップデートは、ガバナンス・セキュリティ・コスト管理の自動化を支援します。タグ伝播機能は SCP や AWS Config ルールと組み合わせることで、手動運用のミスを防ぎ、コンプライアンス要件を自動的に満たすインフラ構築が可能になります。

また、ECS Express Mode の GovCloud 対応や、DevOps Agent のカスタム SRE エージェント対応は、それぞれ政府機関向けクラウドサービスの迅速構築、定期的な SRE ワークフローの自動化という新しいユースケースを切り開きます。特に DevOps Agent の MCP/A2A プロトコル対応は、既存の開発ツール（IDE、Claude、Kiro など）との統合を可能にし、開発者の日常ワークフローに運用監視を自然に組み込める点で注目です。

これらのアップデートを組み合わせることで、監視・分析・ガバナンス・コスト管理を統合した、より高度な運用自動化を実現できます。Terraform で管理しているインフラがあれば、これらの新機能を IaC 化し、チーム全体で再現可能な運用プラクティスとして定着させることを推奨します。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)