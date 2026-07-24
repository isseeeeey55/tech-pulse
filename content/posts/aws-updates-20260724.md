---
title: "【AWS】2026/07/24 のアップデートまとめ"
date: 2026-07-24T08:01:57+09:00
draft: false
tags: ["aws", "billing", "cost-management", "evs", "vmware", "ec2", "rds", "mysql", "sagemaker", "bedrock", "claude", "govcloud", "cloudwatch"]
categories: ["AWS Updates"]
summary: "2026/07/24 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260724/header.png)

# 直近のAWSアップデート情報（2026年7月）

## はじめに

今回は、直近で発表された9件のAWSアップデートを紹介します。クレジットメモの自動適用機能による請求管理の効率化、Amazon EVSやEC2インスタンスの新リージョン対応によるグローバル展開の加速、そしてMySQL 9.7のプレビュー提供やClaude Sonnet 5のGovCloud対応など、データベース・AI分野の重要なアップデートが含まれています。特に注目すべきは、Amazon Bedrock AgentCoreの統一ロギング機能で、これまで分散していたエージェントのトレース情報とログが単一のロググループに集約され、デバッグ効率が大幅に向上しました。また、EC2 M8idやC7aなどの新世代インスタンスの拡充により、コンピュート集約的なワークロードの選択肢がさらに広がっています。

---

## 注目アップデート深掘り

### Amazon Bedrock AgentCore：統一可観測性による運用効率の向上

Amazon Bedrock AgentCoreが提供を開始した統一可観測性機能は、マルチエージェントシステムの運用において大きなブレイクスルーとなります。

**背景と課題**  
従来、Bedrockエージェントのトレース情報と実行ログは異なるCloudWatch ロググループに分散していました。これにより、エージェントの動作をデバッグする際には複数のロググループを横断的に検索する必要があり、特にマルチエージェント構成では各エージェントの実行コンテキストを追跡するのが困難でした。

**統一ロググループによる改善**  
このアップデートにより、エージェントのトレース、プロンプト、構造化ログ、標準出力がすべて単一のエージェント専用ロググループに統合されます。これは単なる利便性向上にとどまらず、以下の運用面での利点をもたらします。

まず、IAMポリシーをエージェント単位で細粒度に設定できるようになります。複数のチームが異なるエージェントを運用している環境では、エージェントごとにアクセス権限を分離できることで、セキュリティポリシーの実装が簡素化されます。

次に、カスタマー管理キー（CMK）による暗号化もエージェント単位で適用可能です。機密性の異なる複数のエージェントを運用する場合、エージェントごとに異なる暗号化キーを割り当てることで、コンプライアンス要件への対応が容易になります。

**適用方法と注意点**  
この機能は2026年7月20日以降に作成された新規エージェントでは自動的に有効化されます。既存のエージェントに対しては、`UNIFIED_TRACES_DESTINATION_ENABLED=true` の設定を明示的に行うことで統一ロググループ機能を有効化できます。

デバッグ効率の観点では、プロンプトと応答、エラートレース、中間ステップのログが同じロググループ内で時系列順に並ぶため、エージェントの意思決定プロセスを一箇所で追跡できます。これにより、ツール呼び出しの失敗やエラーからの復旧プロセスの可視化が飛躍的に向上します。

---

### MySQL 9.7プレビュー：LTSリリースの事前検証環境

Amazon RDS for MySQLがMySQL 9.7をDatabase Preview Environmentでサポート開始しました。これにより、本番環境への導入前に最新のLong-Term Support（LTS）リリースを安全に評価できます。

**MySQL 9.7 LTSの位置づけ**  
MySQL 9.7はコミュニティ版MySQLの最新LTSリリースであり、バグ修正、セキュリティパッチ、新機能が含まれています。LTS指定により、長期的なサポートが保証され、エンタープライズ環境での採用判断がしやすくなっています。

**プレビュー環境の特性と制約**  
RDS Database Preview Environmentは、本番環境のUS East（オハイオ）リージョンのインスタンスと同じ価格設定で利用できます。ただし、プレビューインスタンスは最大60日間保持され、その後自動削除される点に注意が必要です。また、プレビュー環境で作成したスナップショットはプレビュー環境内でのみ復元可能であり、本番環境への直接的な移行パスは提供されていません。

**検証プロセスの設計**  
60日間の評価期間を最大限活用するには、計画的な検証アプローチが重要です。まず既存アプリケーションとの互換性テストを優先し、SQLクエリの構文変更や非推奨機能の影響を確認します。次に、パフォーマンステストとして、クエリ実行速度やメモリ使用量を既存バージョンと比較測定します。

セキュリティパッチの内容を確認し、既知の脆弱性への対応状況を評価することも重要です。特にエンタープライズ環境では、セキュリティ監査チームとの連携が必要になる場合があります。

**移行計画への組み込み**  
プレビュー環境での検証結果をもとに、本番環境への移行ロードマップを策定します。MySQL 9.7の新機能を活用する場合は、アプリケーション側の対応も必要になるため、開発チームとの調整期間も考慮に入れる必要があります。

> **Note:** プレビュー環境は検証専用であり、本番データの投入や長期運用は想定されていません。60日の期限を踏まえた検証スケジュールを事前に策定してください。

---

## SRE視点での活用ポイント

**クレジットメモ自動適用の運用効率化**  
請求管理の自動化は、SREが担当する財務オペレーションの負荷軽減に直結します。複数のAWSアカウントを運用している組織では、クレジット適用のタイミングと対象請求書の選択が煩雑になりがちです。この機能により、組織の会計ポリシーに合わせた適用ルールを一度設定すれば、以降は手動介入なしで処理されるため、月次クローズ作業の効率が向上します。ただし、元の請求書への適用を優先するか、最も古い未払い請求書に充当するかは、キャッシュフロー戦略やチャージバック運用に影響するため、財務部門と事前に調整しておくことが推奨されます。

**統一可観測性によるインシデント対応の高速化**  
Bedrock AgentCoreの統合ロギングは、AIエージェントを活用したシステムの障害対応において重要な改善です。複数のエージェントが連携する構成では、障害時にどのエージェントのどのステップで問題が発生したかを特定することが難しく、ロググループを横断して検索する必要がありました。統一ロググループにより、CloudWatch Logs Insightsで単一クエリですべてのテレメトリデータを取得できるため、MTTRの短縮につながります。エージェント単位でのIAM制御は、チーム間の責任分界を明確にしつつ、障害時のログアクセスをスムーズにする点でも有用です。ただし、ログボリュームが増大する可能性があるため、CloudWatch Logsのログ保持期間とコストを定期的に見直す必要があります。

**リージョン拡大による災害復旧戦略の多様化**  
Amazon EVSやEC2 M8id、C7aインスタンスの新リージョン対応は、地理的に分散した冗長構成の選択肢を増やします。特にヨーロッパやアジア太平洋リージョンでの可用性向上は、グローバル展開するサービスのRTOとRPOの目標達成に寄与します。ただし、リージョン間のレイテンシ、データ転送コスト、コンプライアンス要件（GDPRなど）を総合的に評価し、実際のワークロードでテストしてから本番導入を決定することが重要です。Terraformなどのインフラコードを活用している環境では、新リージョンへの展開が比較的容易ですが、リージョン固有の制約（サービスクォータなど）を事前に確認する必要があります。

---

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **請求管理** | [AWS now supports automatic credit memo application preferences](https://aws.amazon.com/about-aws/whats-new/2026/07/credit-memo-applications/) | EFT支払い顧客向けに、クレジットメモの自動適用ルールを設定可能に。元の請求書、次の対象、最も古い未払いなど複数の適用方法を選択できる |
| **VMware/ハイブリッド** | [Amazon EVS is now available in additional Regions](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-evs-available-in-additional-regions/) | Amazon EVSがソウル、チューリッヒ、ストックホルムで利用可能に。VCF 9.0/9.1対応でメモリティアリングなど最新VMware機能を活用可能 |
| **データベース** | [Amazon RDS for MySQL supports MySQL 9.7 in Amazon RDS Database Preview Environment](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-mysql-long-term-9-7-rds-database-preview/) | MySQL 9.7 LTSリリースをプレビュー環境で検証可能。最大60日間保持、バグ修正とセキュリティパッチを本番導入前に評価 |
| **AI/機械学習** | [Announcing region expansion of G6 instances on SageMaker AI Inference](https://aws.amazon.com/about-aws/whats-new/2026/07/g6-sagemaker-ai-inference/) | AWS GovCloud (US-East)でG6インスタンスが利用可能に。NVIDIA L4 GPU搭載でG4dn比最大2倍の推論パフォーマンスを実現 |
| **AI/機械学習** | [Announcing region expansion of G7e instances on SageMaker AI inference](https://aws.amazon.com/about-aws/whats-new/2026/07/g7e-sagemaker-ai/) | G7eインスタンスがソウル、ロンドン、東京で利用可能に。NVIDIA RTX PRO 6000 Blackwell GPU搭載、単一インスタンスで最大768GB GPUメモリ |
| **コンピュート** | [Amazon EC2 M8id instances are now available in Europe (Ireland) region](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-m8id-europe-ireland/) | M8idインスタンスが欧州（アイルランド）で利用可能に。Intel Xeon 6搭載でM6id比43%性能向上、3.3倍のメモリバンド幅、最大22.8TB NVMe SSD |
| **AI/機械学習** | [Claude Sonnet 5 is now available on Amazon Bedrock in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/claude-sonnet-5-govcloud/) | Claude Sonnet 5がGovCloud (US)で利用可能に。コーディング、エージェント、知識業務で高性能。bedrock-runtimeとbedrock-mantleエンドポイントで提供 |
| **AI/機械学習** | [Amazon Bedrock AgentCore now delivers unified observability with traces and logs in a single log group](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-bedrock-agentcore-unified-observability-single-log-group/) | エージェントのトレース、プロンプト、ログを単一のロググループに統合。エージェント単位でのIAM制御とCMK暗号化が可能に |
| **コンピュート** | [Amazon EC2 C7a instances are now available in the US West (N. California) Region](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-c7a-instances-us-west-ncalifornia-region/) | C7aインスタンスが米国西部（北カリフォルニア）で利用可能に。AMD EPYC Genoa搭載、C6a比50%性能向上、メモリ帯域幅2.25倍、EBSボリューム接続数128個に増加 |

---

## まとめ

今回のアップデート群は、運用効率化、グローバル展開の加速、そして次世代コンピュート基盤の充実という3つのテーマで整理できます。

請求管理の自動化やBedrock AgentCoreの統一ロギングは、日常的な運用タスクの効率を大幅に改善します。特に統一可観測性は、AIエージェントを活用したシステムが増える中で、デバッグとトラブルシューティングの標準的なベストプラクティスとなります。

リージョン拡大のアップデートは、グローバル展開における選択肢の多様化を意味します。Amazon EVSの新リージョン対応は、VMwareワークロードのクラウド移行を検討している組織にとって重要なマイルストーンであり、G6/G7eインスタンスのリージョン拡大は、AIワークロードを低レイテンシで提供するための地理的カバレッジを強化しています。

EC2インスタンスの新世代化（M8id、C7a）は、従来世代から大幅なパフォーマンス向上を実現しており、既存ワークロードの最適化機会を提供しています。特にメモリバンド幅の向上とEBSボリューム接続数の増加は、I/O集約的なワークロードやデータベースシステムにとって重要な改善です。

MySQL 9.7プレビューやClaude Sonnet 5のGovCloud対応は、エンタープライズ環境での最新技術の評価と導入を加速する基盤となります。60日間のプレビュー期間を活用した計画的な検証により、安全かつスムーズなバージョンアップやAI機能の統合が可能になります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)