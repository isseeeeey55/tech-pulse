---
title: "【AWS】2026/05/07 のアップデートまとめ"
date: 2026-05-07T08:02:29+09:00
draft: false
tags: ["aws", "site-to-site-vpn", "bedrock", "ec2", "elastic-beanstalk", "marketplace", "neptune", "cloudshell", "cloudwatch", "cloudtrail", "iam", "s3", "lambda", "dynamodb", "cloudformation", "mcp-server", "mediatailor"]
categories: ["AWS Updates"]
summary: "2026/05/07 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260507/header.png)

# 2026年5月7日 AWS アップデート情報

## はじめに

2026年5月7日は、9件のAWSアップデートが発表されました。今回のアップデートでは、既存サービスの運用性向上と、AI/MLエージェント領域への戦略的投資が目立ちます。特に注目すべきは、**AWS Site-to-Site VPNの帯域幅変更機能**により、ハイブリッドクラウド運用の柔軟性が大幅に向上した点、そして**Agent Toolkit for AWS**の正式発表により、AIコーディングエージェントのエンタープライズ活用が現実的になった点です。また、Amazon Bedrockのメモリ機能強化、EC2の最新GPU インスタンス拡大、Elastic BeanstalkのNLB TLS対応など、インフラ運用とAI基盤の両面で実用性の高い改善が実施されています。

## 注目アップデート深掘り

### AWS Site-to-Site VPN - 既存接続での帯域幅変更対応

ハイブリッドクラウド環境を運用するエンジニアにとって、今回のアップデートは運用負荷を大きく軽減する重要な変更です。AWS Site-to-Site VPNで、**既存のVPN接続を維持したまま帯域幅を変更できる**ようになりました。

#### なぜこのアップデートが重要なのか

従来、Standardタイプ（最大1.25 Gbps）からLargeタイプ（最大5 Gbps）へ帯域幅を変更する場合、VPN接続を一度削除して再作成する必要がありました。この操作には以下のような課題がありました：

- **トンネルIPアドレスの変更**：再作成により新しいIPアドレスが割り当てられる
- **オンプレミス側の設定変更**：VPNデバイス、ファイアウォールルール、ルーティング設定などを更新する必要がある
- **変更作業のリスク**：本番環境での設定変更に伴うダウンタイムや設定ミスのリスク
- **事前共有鍵の再配布**：セキュリティ上、新しい鍵を安全に配布する手順が必要

今回のアップデートにより、**IPアドレス、CIDRブロック、事前共有鍵を含むすべての設定を保持したまま**帯域幅のみを変更できるようになり、オンプレミス側の設定変更が完全に不要になりました。

#### 実際の変更手順

AWS CLIを使用した帯域幅変更の例を見てみましょう：

```bash
# 既存のVPN接続情報を確認
$ aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-1234567890abcdef0

# 帯域幅をLargeに変更
$ aws ec2 modify-vpn-connection \
  --vpn-connection-id vpn-1234567890abcdef0 \
  --vpn-tunnel-options TunnelInsideIpVersion=ipv4,TunnelBandwidth=5000

# 変更後の状態を確認
$ aws ec2 describe-vpn-connections \
  --vpn-connection-ids vpn-1234567890abcdef0 \
  --query 'VpnConnections[0].Options.TunnelOptions[*].TunnelBandwidth'
```

Terraformで管理している環境では、以下のように設定を変更するだけで済みます：

```hcl
resource "aws_vpn_connection" "main" {
  vpn_gateway_id      = aws_vpn_gateway.main.id
  customer_gateway_id = aws_customer_gateway.main.id
  type                = "ipsec.1"
  static_routes_only  = false

  # 帯域幅の変更（1250から5000へ）
  tunnel1_bandwidth = 5000
  tunnel2_bandwidth = 5000

  tags = {
    Name = "main-vpn-connection"
  }
}
```

#### 従来方式との比較

| 項目 | 従来（削除・再作成） | 新方式（帯域幅変更） |
|------|---------------------|---------------------|
| オンプレミス側設定変更 | 必須（IPアドレス、鍵など） | 不要 |
| ダウンタイム | 発生（再作成中） | 最小限（詳細は要検証） |
| 作業時間 | 30分〜1時間程度 | 数分程度 |
| 設定ミスのリスク | 高い（複数箇所変更） | 低い（AWS側のみ） |
| 事前共有鍵の管理 | 再配布が必要 | 保持される |

#### CloudWatchでの監視と変更タイミングの検討

帯域幅変更のタイミングを適切に判断するため、CloudWatchメトリクスを活用した監視が重要です：

```bash
# VPN接続のバイト転送量を確認
$ aws cloudwatch get-metric-statistics \
  --namespace AWS/VPN \
  --metric-name TunnelDataIn \
  --dimensions Name=VpnId,Value=vpn-1234567890abcdef0 \
  --start-time 2026-05-01T00:00:00Z \
  --end-time 2026-05-07T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

帯域使用率が継続的に70%を超える場合や、ビジネス要件で大規模なデータ移行が予定されている場合は、事前に帯域幅をアップグレードすることで、パフォーマンス問題を予防できます。

> **Note:** 変更時のダウンタイムの有無や所要時間については、実際の環境でテストすることを推奨します。リリースノートには明示されていないため、本番適用前に検証環境での確認が必須です。

### Agent Toolkit for AWS - AIエージェントの本番環境対応

AWSがAIコーディングエージェント向けに**Agent Toolkit for AWS**を正式リリースしました。これは、AIエージェントがAWS上でアプリケーションを構築する際の課題を解決する本番環境対応のツールスイートです。

#### AIエージェント活用における従来の課題

AIコーディングエージェントをAWS環境で活用する際、以下のような課題がありました：

- **複雑なマルチサービスワークフロー**：複数のAWSサービスを連携させる処理の自動化が困難
- **古い知識への依存**：LLMの学習データが古く、最新のAWSサービスやベストプラクティスに対応できない
- **ガバナンスとセキュリティ**：エージェントに適切な権限制御を行いつつ、監査可能性を確保することが難しい

#### Agent Toolkitの3つのコンポーネント

Agent Toolkit for AWSは、以下の3つの要素で構成されています：

**1. エージェントスキル**

検証済みで最新の手順を提供する再利用可能なタスク定義です。現在、インフラストラクチャコード、ストレージ、分析、サーバーレス、コンテナ、AIサービスにわたって**40以上のスキル**がリリースされており、今後数週間でデータベース、ネットワーキング、IAMなどのスキルが追加予定です。

**2. AWS MCP Server（Model Context Protocol Server）**

フルマネージドのMCPサーバーで、AIエージェントがあらゆるAWSサービスと対話できるようにします。以下の機能を提供します：

- IAMベースのガードレール
- Amazon CloudWatchメトリクスによる可観測性
- AWS CloudTrailによる監査ログ
- サンドボックス化されたPythonスクリプト実行環境

**3. エージェントプラグイン**

MCPサーバーとキュレーションされたスキルセットを単一インストールにバンドルします。現在、アプリケーション開発者向けの**AWS Core**など3つのプラグインがリリースされています。

#### セキュリティとガバナンスの実装

エンタープライズ環境で最も重要なのは、適切な権限制御と監査可能性です。以下はIAMポリシーの最小権限設定例です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::agent-workspace-bucket",
        "arn:aws:s3:::agent-workspace-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction",
        "lambda:GetFunction"
      ],
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:agent-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/agent/*"
    }
  ]
}
```

CloudTrailによる監査ログでは、エージェントが実行したすべてのAWS API呼び出しを追跡できます：

```bash
# エージェントのアクティビティを確認
$ aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=agent-role \
  --start-time 2026-05-07T00:00:00Z \
  --max-results 50
```

#### Python Sandboxed Executionの仕組み

エージェントは、ローカルファイルシステムやシェルツールに直接アクセスせずに、サンドボックス環境内でPythonスクリプトを実行できます。これにより、マルチステップ操作を安全に自動化できます：

```python
# エージェントが実行可能なサンドボックス内のPythonコード例
import boto3

# S3からデータを取得
s3 = boto3.client('s3')
response = s3.get_object(Bucket='data-bucket', Key='input.json')
data = response['Body'].read()

# データを加工
processed_data = transform_data(data)

# DynamoDBに保存
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ProcessedData')
table.put_item(Item=processed_data)
```

サンドボックスの制限事項として、ローカルファイルシステムへの直接アクセスやシェルコマンドの実行は許可されていません。これにより、エージェントが意図しない操作を実行するリスクを最小化しています。

#### 従来のSOP形式との違い

エージェントスキルは、従来の手続き型のSOP（Standard Operating Procedure）形式に代わる、より柔軟でコンテキストウィンドウ効率的な手段を提供します。SOPは固定的な手順書であるのに対し、エージェントスキルはLLMのコンテキストに応じて動的に適用され、トークン消費を最適化できます。

> **Note:** Agent Toolkit for AWSは、AWS Labsで提供されていたMCPサーバー、プラグイン、スキルの後継製品です。既存のLabsプロジェクトを利用している場合は、正式版への移行を検討してください。

## SRE視点での活用ポイント

### Site-to-Site VPN帯域幅変更の運用シナリオ

VPN帯域幅の動的変更機能は、キャパシティプランニングと障害対応の両面でSRE業務を改善します。Terraformでインフラをコード管理している環境であれば、帯域幅変更はコードの数値を変えて`terraform apply`を実行するだけで完結するため、手順書の簡素化と変更履歴の追跡が容易になります。

CloudWatchアラームと組み合わせることで、帯域使用率が閾値を超えた際に自動通知し、事前に帯域幅変更を計画できます。例えば、週次でのバッチ処理や大規模なデータ移行が予定されている場合、事前にLargeへアップグレードし、完了後にStandardへダウングレードすることで、コストと性能のバランスを最適化できます。

導入時の判断基準としては、トラフィックパターンの可視化が前提となります。少なくとも1週間〜1ヶ月分のVPNトラフィックメトリクスを収集し、ピーク時の使用率を把握してから変更を検討すべきです。また、変更時のダウンタイムについては、リリースノートに明示されていないため、必ず非本番環境でテストし、影響範囲を確認してから本番適用することが重要です。

### Agent Toolkit for AWSのインシデント対応活用

AIエージェントをインシデント対応のランブックに組み込むことで、障害復旧の自動化が進みます。例えば、「EC2インスタンスの再起動」「CloudFormationスタックのロールバック」「S3バケットのバージョニング復元」といった標準的な復旧操作を、エージェントスキルとして定義しておくことで、オンコール担当者の負担を軽減できます。

CloudTrailによる監査ログが自動的に記録されるため、「エージェントが何をしたか」が完全に追跡可能です。これは事後分析（ポストモーテム）での説明責任を果たす上でも重要です。IAMポリシーで最小権限を付与することで、エージェントが実行できる操作を制限し、誤操作のリスクを最小化できます。

導入時のリスクとしては、エージェントの判断精度が100%ではない点を認識する必要があります。初期段階では、エージェントの実行結果を人間が確認する「承認フロー」を組み込み、徐々に自動化範囲を拡大するアプローチが推奨されます。また、サンドボックス実行環境の制限により、特定の操作（ローカルファイルシステムへのアクセスなど）は実行できないため、事前に要件を確認することが必要です。

### Elastic Beanstalk NLB TLS対応の運用改善

Elastic Beanstalkで管理するアプリケーションにおいて、NLBでのTLS終端がマネージド機能として提供されることで、証明書管理の負担が軽減されます。AWS Certificate Manager（ACM）と連携することで、証明書の自動更新が可能になり、証明書期限切れによる障害リスクを削減できます。

従来は手動でNLBを構成し、Elastic Beanstalk環境と紐付ける必要がありましたが、今回のアップデートによりコンソールまたはCLIから直接設定できるため、Infrastructure as Codeでの管理が容易になります。Terraformで環境を管理している場合、既存のリソース定義にTLSリスナー設定を追加するだけで済み、再デプロイのリスクが低減されます。

導入判断のポイントとしては、ALBとNLBの使い分けを明確にすることが重要です。低レイテンシーが要求されるゲーミングアプリケーションやリアルタイム通信システムでは、NLBの方が適している場合があります。一方、HTTP/HTTPSのみでアプリケーション層のルーティングが必要な場合は、ALBの方が機能豊富です。パフォーマンステストを実施し、TLS終端による遅延やスループットへの影響を定量的に測定してから、本番適用を判断することを推奨します。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|---------|---------|------|
| 1 | Site-to-Site VPN | [既存VPN接続での帯域幅変更対応](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-site-to-site-vpn-modify-bandwidth/) | Standard（1.25 Gbps）とLarge（5 Gbps）間の帯域幅変更が、IPアドレス・事前共有鍵を保持したまま可能に。オンプレミス側の設定変更が不要 |
| 2 | Bedrock | [AgentCore Memory - 長期記憶のメタデータ対応](https://aws.amazon.com/about-aws/whats-new/2026/05/agentcore-longterm-memory-metadata/) | 長期記憶レコードにメタデータ（最大10キー、STRING/NUMBER/STRING_LIST型）を付与し、構造化検索が可能に。手動付与とLLM自動推論の両方に対応 |
| 3 | EC2 | [P6-B300インスタンスが米国東部で利用可能](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-p6-b300-us-east/) | NVIDIA Blackwell Ultra GPU×8、2.1TB GPUメモリ、6.4Tbps EFAネットワークを搭載。P6-B200比でネットワーク2倍、GPUメモリ1.5倍、TFLOPS 1.5倍 |
| 4 | Elastic Beanstalk | [NLB環境でのTLSリスナー対応](https://aws.amazon.com/about-aws/whats-new/2026/04/elastic-beanstalk-tls-support/) | Network Load Balancer環境でTLSリスナーをコンソール・CLIから直接設定可能に。SSL証明書とセキュリティポリシーをマネージド管理 |
| 5 | Marketplace | [Agreements APIによるプログラマティック調達](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-marketplace-agreements-api/) | 見積生成、オファー承認、料金追跡、エンタイトルメント管理などを自動化するAgreements APIを提供。Discovery APIと組み合わせてエンドツーエンド調達プロセスを実現 |
| 6 | Neptune | [CloudShellとの1クリック接続](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-neptune-cloudshell/) | 手動ネットワーク設定不要でCloudShellからNeptuneへ即座に接続可能に。VPCのみのリソースにも対応し、セットアップ時間を大幅削減 |
| 7 | MCP Server | [AWS MCP Serverの正式リリース](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-mcp-server/) | AIコーディングエージェント向けのModel Context Protocol Serverが一般提供開始。IAMガードレール、CloudWatch/CloudTrail連携、サンドボックスPython実行を提供 |
| 8 | Agent Toolkit | [Agent Toolkit for AWSの発表](https://aws.amazon.com/about-aws/whats-new/2026/05/agent-toolkit/) | AIエージェント向けの本番環境対応ツールスイート。40以上のエージェントスキル、フルマネージドMCPサーバー、プラグインを提供 |
| 9 | MediaTailor | [広告トリックプレイとDASHマニフェスト最適化](https://aws.amazon.com/about-aws/whats-new/2026/05/mediatail-ad-trickplay-and-compact-dash-manifest-optimization/) | HLS/DASHで広告のトリックプレイ対応とマニフェストコンパクト化をダイナミックトランスコーディングで実現。カスタムプロファイル不要 |

## まとめ

2026年5月7日のアップデートは、**運用効率化**と**AI/MLエージェント基盤強化**という2つの軸で展開されました。

Site-to-Site VPNの帯域幅変更機能やElastic BeanstalkのNLB TLS対応は、既存の運用手順を大幅に簡素化し、変更に伴うリスクを削減します。特にVPNの帯域幅変更は、オンプレミス側の設定変更が不要という点で、ハイブリッドクラウド運用の柔軟性を大きく向上させる重要なアップデートです。

一方、Agent Toolkit for AWSとAWS MCP Serverの正式リリースは、AWSがAIエージェントのエンタープライズ活用に本格的に取り組んでいることを示しています。40以上のエージェントスキル、IAMベースのガードレール、CloudTrail監査ログといった本番環境での要件を満たす機能が揃っており、AIによるインフラ運用自動化が現実的な選択肢となりつつあります。

また、Amazon BedrockのAgentCore Memoryがメタデータ対応したことで、より精度の高いコンテキスト検索が可能になり、エンタープライズAIアプリケーションの実用性が向上しました。EC2 P6-B300インスタンスの拡大やNeptuneのCloudShell対応など、開発者体験の向上にも注力されています。

今後数週間でAgent Toolkitにデータベース、ネットワーキング、IAMのスキルが追加される予定であり、AIエージェント活用の幅がさらに広がることが期待されます。SREやインフラエンジニアにとって、これらのアップデートを活用することで、運用の自動化・効率化・安全性向上を実現できる可能性が高まっています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)