---
title: "【AWS】2026/07/25 のアップデートまとめ"
date: 2026-07-25T08:02:17+09:00
draft: false
tags: ["aws", "kinesis", "ec2", "lambda", "ses", "bedrock", "cloudwatch", "alb", "s3", "data-firehose", "license-manager"]
categories: ["AWS Updates"]
summary: "2026/07/25 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260725/header.png)

# 直近の AWS アップデート情報（2026年7月）

## はじめに

今回は、直近で発表された9件のAWSアップデートを紹介します。Amazon Kinesis Data Streamsのスケールダウン機能追加、EC2 Dedicated HostsのHost Resource Groups機能強化、Lambda Managed Instancesのログ機能、Amazon SESのSMTP送信簡素化、Claude OpusとSonnetの最新モデル対応、AI エージェントベンチマーク「aws-bench」の公開、Lambda Durable Execution SDK for .NETのGA、そしてCloudWatch LogsによるALBログサポートなど、コンピューティング、ネットワーク、AI/ML、監視・運用の各領域で重要な機能改善が含まれています。

特に注目すべきは、運用コストとパフォーマンスのバランス最適化に関するアップデート群です。Kinesis Data StreamsとALB CloudWatch Logsは、既存のストリーミングおよびロードバランシング環境の可視化とコスト効率を同時に向上させる改善であり、Lambda Durable Functionsは長時間ワークフローの実装を外部オーケストレーションなしで実現する新しいアプローチを提供します。またAI/ML領域では、Claude最新モデルの追加とエージェント性能測定の標準化により、生成AIワークロードの実装・評価基盤が整いつつあることが伺えます。

## 注目アップデート深掘り

### Amazon Kinesis Data Streams のスケールダウン機能

Amazon Kinesis Data Streamsの**On-demand Advantageモード**に、待望のスケールダウン機能が追加されました。従来、warm throughput（ウォームスループット）はスケールアップのみに対応しており、トラフィックが減少しても過剰な容量が維持されるという課題がありました。

#### なぜこのアップデートが重要なのか

Kinesisを使用したストリーミングアプリケーションでは、トラフィックの変動に応じた容量管理が運用コストの大きな要素です。日中と夜間、平日と週末、イベント時とそれ以外でトラフィック量が大きく変動する場合、これまではピーク時の容量を維持し続けるか、手動でスケーリング調整を行う必要がありました。

今回のアップデートにより、warm throughput を低い値に設定するとスケールダウンをトリガーでき、ストリームの容量は**要求した値と過去1時間のピークのデータ取り込み量を支えるのに必要な容量のいずれか高い方**に調整されます。これにより、現在のトラフィックに必要な容量は確保しつつ、一時的なバーストで膨らんだ過剰容量を解放できるようになりました。

#### 検証のポイント

この機能を活用する際の検証ポイントは以下の通りです。

1. **On-demand Advantageモードの有効化**: On-demand Advantage はストリーム単位ではなく**アカウントレベルの設定**で、有効にするとリージョン内のすべてのオンデマンドストリームに適用されます。warm throughput のスケールダウン自体は、On-demand Advantage モードを有効にしたオンデマンドストリームで追加費用なく利用できます。一方で、モードの有効化にはアカウント単位で最低 25MiB/s のデータ取り込みと 25MiB/s のデータ取得のコミットメントが伴い、有効化後は最低24時間経過するまで無効化できないため、切り替えは既存の利用量を確認したうえで判断します。

2. **スケールダウン挙動の観測**: warm throughputの設定値を段階的に変更し、実際のスケールダウンがどのように発生するかを観測します。特に、過去1時間のピークトラフィック判定ロジックがどう働くかを確認することで、予期しない容量不足を防げます。

3. **CloudWatchメトリクスでの影響確認**: スケールダウン前後で、`GetRecords.Latency`、`IteratorAgeMilliseconds`、`IncomingBytes`、`IncomingRecords`などのメトリクスを比較します。スケールダウンによってコンシューマーのレイテンシやバックログに悪影響が出ていないかを確認する必要があります。

4. **コスト削減効果の定量化**: スケールアップのみの運用と比較して、実際のコスト削減効果を測定します。トラフィックの変動パターンが明確なワークロード（ECサイトのアクセス変動、IoTデバイスからの周期的なデータ送信など）ほど、バースト後に戻せる容量が大きく、効果を定量化しやすくなります。

#### 従来モードとの比較

Kinesisには現在、**Provisionedモード**、**On-demand Standardモード**、**On-demand Advantageモード**の3つのモードが存在します。Provisionedモードは自分でシャード数を指定して管理する必要があり、On-demand Standardモードは実使用量に応じた自動スケーリングのみで warm throughput の設定には対応していません。On-demand Advantageモードは以前から warm throughput による事前のウォームアップに対応していましたが、今回のアップデートでスケールダウンのトリガーが加わり、双方向の容量調整ができるようになりました。

> **Note:** スケールダウンは過去1時間のピークトラフィックを考慮するため、急激なトラフィック増加に対しても一定の余裕を持った容量が確保されます。しかし、過去1時間を超える長期的なトラフィック予測が必要な場合は、warm throughput設定を適切に調整する必要があります。

### Amazon CloudWatch Logs による ALB ログのサポート

Amazon CloudWatch Logsが、Application Load Balancer（ALB）のログを**vended logs**としてサポートするようになりました。これにより、ALBのアクセスログ、接続ログ、ヘルスチェックログを直接CloudWatchで分析できるようになり、ネットワークトラフィックパターンの可視化とデバッグが大幅に簡素化されます。

#### なぜこのアップデートが重要なのか

従来、ALBのログはS3バケットに保存され、分析にはAthenaやその他のツールを使用する必要がありました。これは以下の課題を抱えていました：

- **リアルタイム性の欠如**: S3へのログ配信には数分の遅延があり、障害発生時の即座なデバッグが困難
- **クエリの複雑さ**: Athenaでのクエリ実行には、テーブル定義やパーティション管理が必要
- **分散した監視環境**: アプリケーションログとインフラログが別々のシステムで管理される

CloudWatch Logsへの統合により、これらの課題が解決されます。

#### 具体的な活用方法

**1. CloudWatch Logs Insightsでの分析**

ALBログがCloudWatch Logsに統合されることで、CloudWatch Logs Insightsの強力なクエリ機能を使用できます。例えば、特定のステータスコードを持つリクエストのパターン分析、レイテンシの高いリクエストの特定、特定クライアントからのトラフィック追跡などが、構造化されたクエリで簡単に実行できます。

**2. メトリクスフィルターによるカスタムメトリクス生成**

ログから特定のパターンを抽出し、カスタムメトリクスを生成できます。例えば、4xxや5xxエラーの発生率、特定のURLパスへのリクエスト数、ターゲットヘルスチェック失敗率などをメトリクス化し、CloudWatch Alarmsと連携した自動アラート設定が可能になります。

**3. Live Tailによるリアルタイムデバッグ**

CloudWatch Logs Live Tailを使用すると、ログをリアルタイムでストリーミング表示できます。障害発生時に即座にログを確認し、クライアント接続エラーやタイムアウトの原因を迅速に特定できます。

**4. テレメトリ有効化ルールによる一括設定**

組織全体、特定アカウント、または特定リソースに対して、既存および新規に作成されたALBリソースのログ記録を自動的に設定できます。これにより、手動設定なしで一貫した監視を確保でき、コンプライアンス要件への対応も容易になります。

#### コストと配信オプション

ALBログは、CloudWatch Logs および Amazon Data Firehose へ配信する場合に vended logs として課金されます。配信先としては Amazon S3（Apache Parquet 形式に対応）もサポートされ、S3への配信自体は無料ですが、Parquet変換には$0.035/GB（バージニア北部リージョン）のコストがかかります。

配信先の選択は、リアルタイム性・分析の容易さと保存コストのトレードオフになります。リアルタイム分析はCloudWatch Logs、長期保管はS3という使い分けが取りやすい構成です。

> **Note:** すべてのAWS Commercialリージョンおよび GovCloud で利用可能です。AWS Management Console、CLI、SDKのいずれでも設定できます。

## SRE視点での活用ポイント

### Kinesis スケールダウン機能の運用シナリオ

Kinesis Data Streamsのスケールダウン機能は、予測可能なトラフィックパターンを持つストリーミングアプリケーションで特に有効です。例えば、IoTデバイスからのテレメトリデータ収集、Webアプリケーションのクリックストリーム分析、ログ集約パイプラインなど、時間帯や曜日によってトラフィックが変動する環境では、自動スケールダウンによって運用コストを大幅に削減できる可能性があります。

導入時の判断基準としては、まずトラフィックパターンの分析が重要です。CloudWatchメトリクスで過去1〜3ヶ月のトラフィック推移を確認し、ピークと通常時の差が大きいほど、バースト後にスケールダウンで戻せる容量も大きくなります。ただし、過去1時間のピーク取り込み量を下限とする判定ロジックがあるため、1時間以内に急激なトラフィック増加が発生するパターンでは、warm throughput設定を慎重に調整する必要があります。

On-demand Advantage はストリーム単位ではなくアカウント・リージョン単位の設定のため、有効化はアカウント全体の取り込み量とコミットメント（25MiB/s）を踏まえて判断し、有効化後に各ストリームの warm throughput を個別に調整する運用になります。また、CloudWatch Alarmsでコンシューマーのバックログ（`IteratorAgeMilliseconds`）や書き込みスロットリングを監視し、スケールダウンが意図しないパフォーマンス低下を引き起こしていないかを継続的に確認します。

### CloudWatch Logs ALB統合の運用改善シナリオ

CloudWatch LogsによるALBログサポートは、障害対応のランブックに組み込むことで真価を発揮します。例えば、アプリケーションの応答時間が遅延した場合、従来はAthenaでS3ログをクエリする必要がありましたが、CloudWatch Logs Insightsでリアルタイムにターゲット応答時間やエラーレートを確認できるようになります。

メトリクスフィルターとCloudWatch Alarmsを組み合わせると、ALBレベルの異常を自動検知し、オンコール担当者に通知する仕組みを構築できます。例えば、5xxエラー率が閾値を超えた場合、特定のターゲットグループのヘルスチェック失敗が増加した場合などのシナリオで、従来よりも迅速な障害検知が可能になります。

注意点としては、CloudWatch Logsのストレージコストと保持期間の管理が挙げられます。高トラフィックのALBでは大量のログが生成されるため、適切なログ保持ポリシー（例：7日間はCloudWatch Logs、それ以降はS3にアーカイブ）を設定することが推奨されます。また、Logs Insightsクエリの実行コストも考慮し、頻繁に実行するクエリは定期的なメトリクス生成に置き換えることも検討すべきです。

テレメトリ有効化ルールを使用すると、組織内の全ALBに対して一括でログ設定を適用できるため、マルチアカウント環境やControl Tower管理下の環境では、統一的な監視基盤を構築する際の有力な選択肢となります。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon Kinesis Data Streams now supports scaling down ingest capacity with warm throughput](https://aws.amazon.com/about-aws/whats-new/2026/07/kinesis/on-demand-scale-down) | Kinesis Data Streams の On-demand Advantage モードがスケールダウンに対応。warm throughput 設定により、トラフィック減少時に自動的に過剰容量を解放し、コスト効率を向上 |
| 2 | [Amazon EC2 Dedicated Hosts now support host resource groups without self-managed licenses](https://aws.amazon.com/about-aws/whats-new/2026/07/ec2-dedicated-hosts-hrg/) | EC2 Dedicated Hosts で SML なしの Host Resource Groups 作成が可能に。EC2 Mac インスタンスやハードウェア分離が必要なワークロードで柔軟なリソース管理を実現 |
| 3 | [AWS Lambda now publishes logs for Lambda Managed Instances capacity providers](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-lambda-managed-instances-logs/) | Lambda Managed Instances の容量プロバイダーが CloudWatch Logs にログ発行。スケーリング活動とインスタンスライフサイクルイベントを構造化JSONで記録し、プロビジョニング問題のデバッグを高速化 |
| 4 | [Amazon SES simplifies sending emails over SMTP using Mail Manager](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ses-simplified-smtp-mail-manager) | Amazon SES が Mail Manager を使用した SMTP 送信を簡素化。ガイド付きセットアップにより、わずか数クリックで本番環境対応の SMTP エンドポイントと認証情報を取得可能 |
| 5 | [Opus 4.8, Sonnet 5, and User Activity Monitoring now available on Kiro in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/kiro-opus-sonnet-monitoring-launch-aws-govcloud-us/) | AWS GovCloud (US) で Claude Opus 4.8、Sonnet 5、ユーザアクティビティ監視機能が利用可能に。複雑な開発タスクと低コストAIエージェント構築、組織全体の使用状況可視化を実現 |
| 6 | [Claude Opus 5 is now available on AWS](https://aws.amazon.com/about-aws/whats-new/2026/07/claude-opus-5-aws/) | Claude Opus 5 が AWS で利用可能に。ゼロデータリテンション対応で、コーディング能力向上、長時間稼働エージェント、複雑な業務処理での精度向上を実現。Amazon Bedrock と Claude Platform on AWS の2つのアクセス方法を提供 |
| 7 | [AWS announces aws-bench, an open-source benchmark for AI agents on AWS](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-bench/) | AI エージェントが AWS タスクをどの程度正確かつ効率的に完了できるかを測定するオープンソースベンチマーク「aws-bench」を発表。実際の AWS 使用パターンから派生した客観的で再現可能なテストケースを提供 |
| 8 | [AWS Lambda durable execution SDK for .NET is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/07/lambdadf-dotnet/) | Lambda Durable Execution SDK for .NET が GA。C# 開発者が Lambda Durable Functions で長時間実行ワークフローを構築可能に。外部オーケストレーションなしで決済処理、AI エージェント統合、人間承認ワークフローを実装 |
| 9 | [Amazon CloudWatch Logs now supports Application Load Balancer logs](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-cloudwatch-logs/) | CloudWatch Logs が ALB ログを vended logs としてサポート。アクセスログ、接続ログ、ヘルスチェックログを直接分析可能に。テレメトリ有効化ルールで組織全体の自動ログ設定を実現 |

## まとめ

今回紹介した9件のアップデートは、AWSの各レイヤーにわたる継続的な改善を示しています。特に、**運用効率とコスト最適化**、**AI/MLワークロードの実用化**、**可観測性の強化**という3つのテーマが明確です。

Kinesis Data StreamsのスケールダウンとCloudWatch LogsのALB統合は、既存のワークロードをより効率的に運用するための重要な改善であり、特にトラフィック変動が大きい環境やリアルタイムデバッグが求められる環境で大きな価値を提供します。Lambda Durable Execution SDK for .NETとLambda Managed Instancesのログ機能は、サーバーレスアーキテクチャの適用範囲を拡大し、長時間実行ワークフローの実装を容易にします。

AI/ML領域では、Claude Opus 5の追加と aws-bench の公開により、生成AIワークロードの実装と評価の選択肢が広がりました。特に aws-bench は、自然言語のクエリ・定義済みのクラウドリソース状態・正解データを組み合わせたテストケースにより、エージェントやモデルを一貫した検証可能な基準で採点できる点が特徴です。

SRE業務においては、これらのアップデートを段階的に評価し、既存の監視・運用プロセスに統合していくことが有効です。特にCloudWatch Logs統合やKinesis自動スケーリングは、PoC環境での検証を経てから本番環境に適用することで、運用負荷とコストへの影響を見極めながら導入できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)