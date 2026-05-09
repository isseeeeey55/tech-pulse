---
title: "【AWS】2026/05/09 のアップデートまとめ"
date: 2026-05-09T08:02:12+09:00
draft: false
tags: ["aws", "iam", "terraform", "marketplace", "service-catalog", "cloudformation", "route53", "ec2", "cloudwatch", "cloudtrail"]
categories: ["AWS Updates"]
summary: "2026/05/09 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260509/header.png)

# 2026年5月9日 AWS アップデート解説

## はじめに

2026年5月9日、AWSは6件のアップデートを発表しました。本日の注目は、IAMポリシー管理の自動化を実現する「IAM Policy Autopilot」のJavaおよびTerraform対応、IPv6トラフィックに完全対応したRoute 53 Resolverエンドポイントの機能強化、そして欧州主権クラウド向けのGPUインスタンス拡充です。セキュリティ、ネットワーク、コンピューティングの各領域で、運用の自動化とグローバル展開の柔軟性が大きく向上しています。

## 注目アップデート深掘り

### IAM Policy Autopilot：Terraform対応で実現する真の最小権限ポリシー

#### なぜこのアップデートが重要なのか

IAMポリシーの作成は、AWSにおけるセキュリティ設計の中核ですが、最小権限の原則を実現することは容易ではありません。開発速度を優先すると、つい `"Resource": "*"` のようなワイルドカードに頼りがちです。しかし、これはセキュリティリスクを拡大させ、万が一の認証情報漏洩時の影響範囲を広げてしまいます。

IAM Policy Autopilotは、re:Invent 2025で発表された無料のオープンソースツールで、アプリケーションのソースコードを静的解析し、実際に使用されるAWS API呼び出しに基づいてポリシーを自動生成します。今回のアップデートでは、Javaサポートの追加により、対応言語がPython、TypeScript、Go、Javaの4言語に拡大しました。

さらに重要なのが、**Terraform対応のポリシー生成機能**です。この機能により、Terraformリソース定義とコード内のSDK呼び出しを相互参照し、実際のリソースARNを解決できるようになりました。これまではワイルドカードで指定せざるを得なかったリソースも、具体的なARN（例：`arn:aws:s3:::my-app-bucket-prod`）を指定した厳密なポリシーが生成されます。

#### 検証手順：Javaアプリケーションでの動作確認

まず、IAM Policy AutopilotのGitHubリポジトリをクローンし、環境をセットアップします。

```bash
$ git clone https://github.com/awslabs/iam-policy-autopilot.git
$ cd iam-policy-autopilot
```

次に、サンプルのJavaアプリケーションとTerraformファイルを用意します。以下は、S3とDynamoDBを使用するJavaアプリケーションの例です。

```java
// src/main/java/com/example/App.java
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;

public class App {
    public static void main(String[] args) {
        S3Client s3 = S3Client.create();
        s3.listBuckets(); // S3バケット一覧取得
        
        DynamoDbClient dynamodb = DynamoDbClient.create();
        dynamodb.putItem(PutItemRequest.builder()
            .tableName("orders")
            .build());
    }
}
```

対応するTerraformファイルは以下の通りです。

```hcl
# terraform/main.tf
resource "aws_s3_bucket" "app_bucket" {
  bucket = "my-app-bucket-prod"
}

resource "aws_dynamodb_table" "orders" {
  name           = "orders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "orderId"
  
  attribute {
    name = "orderId"
    type = "S"
  }
}
```

IAM Policy Autopilotを実行します。

```bash
$ iam-policy-autopilot generate \
  --source-dir ./src \
  --terraform-dir ./terraform \
  --language java \
  --output policy.json
```

生成されたポリシーは、以下のように具体的なリソースARNを含みます。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/orders"
    }
  ]
}
```

#### 従来の方法との比較

従来、手動でポリシーを作成する場合、以下のように広範な権限を付与しがちでした。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "dynamodb:*"
      ],
      "Resource": "*"
    }
  ]
}
```

IAM Policy Autopilotを使用すると、実際に使用されるアクション（`s3:ListAllMyBuckets`、`dynamodb:PutItem`）のみが許可され、DynamoDBについては特定のテーブル（`orders`）のみにスコープが限定されます。これにより、不要な権限を排除し、セキュリティインシデント発生時の影響範囲を最小化できます。

#### Terraform連携の技術的なメリット

Terraform連携の最大の利点は、**インフラ定義とアプリケーションコードを一元的に分析できる**点です。例えば、コード内で `s3.putObject("my-app-bucket-prod", ...)` のような呼び出しがあっても、バケット名が環境変数や設定ファイルから読み込まれる場合、従来のツールではリソースARNを特定できませんでした。Terraform対応により、`aws_s3_bucket.app_bucket` リソース定義を参照し、正確なARNを解決できます。

さらに、複数の環境（開発、ステージング、本番）でTerraform workspaceを使い分けている場合でも、それぞれの環境に応じたポリシーを自動生成できます。

### Route 53 Resolver エンドポイント：IPv6完全対応で実現するハイブリッドDNS

#### IPv6移行の課題とDNS64の役割

企業のネットワークインフラは、IPv4からIPv6への移行期にあります。しかし、すべてのサービスを一度にIPv6対応させることは現実的ではなく、IPv4とIPv6が混在する「デュアルスタック期間」が長期化します。この期間における大きな課題が、**IPv6専用クライアントからIPv4専用サービスへのアクセス**です。

今回のアップデートで、Route 53 Resolverのインバウンドエンドポイントに**DNS64機能**が追加されました。DNS64は、Aレコード（IPv4アドレス）しか持たないドメインに対して、AAAAレコード（IPv6アドレス）を合成する技術です。これにより、オンプレミスのIPv6専用クライアントが、AWS上のIPv4サービスにシームレスにアクセスできるようになります。

#### DNS64の技術的な仕組み

DNS64は以下のように動作します。

1. IPv6クライアントがドメイン（例：`api.example.com`）のAAAAレコードを問い合わせ
2. 実際のDNSレコードはAレコード（`198.51.100.10`）のみ
3. DNS64がこのIPv4アドレスを特定のIPv6プレフィックス（例：`64:ff9b::/96`）と組み合わせて合成
4. 合成されたIPv6アドレス（`64:ff9b::198.51.100.10`）をクライアントに返却
5. クライアントはこのIPv6アドレスに接続し、NAT64ゲートウェイでIPv4に変換

#### 設定手順：インバウンドエンドポイントでのDNS64有効化

Route 53 ResolverインバウンドエンドポイントでDNS64を有効化するには、以下のAWS CLIコマンドを使用します。

```bash
$ aws route53resolver create-resolver-endpoint \
  --creator-request-id unique-id-123 \
  --security-group-ids sg-0123456789abcdef0 \
  --direction INBOUND \
  --ip-addresses SubnetId=subnet-0abc123,Ip=2001:db8::1 \
  --protocols DoH DoT \
  --resolver-endpoint-type IPV6 \
  --dns64-enabled
```

重要なパラメータは `--dns64-enabled` です。これにより、IPv4のAレコードをIPv6に合成する機能が有効化されます。

#### アウトバウンドエンドポイントのIPv6対応

もう一つの重要な機能強化が、アウトバウンドエンドポイントでの**インターネットゲートウェイ（IGW）経由のIPv6ネームサーバー転送**です。これにより、VPC内のワークロードから公開IPv6 DNSサーバー（例：Google Public DNS `2001:4860:4860::8888`）へのクエリ転送が可能になります。

設定例は以下の通りです。

```bash
$ aws route53resolver create-resolver-rule \
  --creator-request-id unique-id-456 \
  --rule-type FORWARD \
  --domain-name example.com \
  --resolver-endpoint-id rslvr-out-0123456789abcdef \
  --target-ips Ip=2001:4860:4860::8888,Port=53
```

#### ハイブリッドクラウド環境での活用パターン

オンプレミスのデータセンターがIPv6移行を進めている一方で、AWS上のレガシーアプリケーションがIPv4のままである場合、DNS64を活用することでサービス側の変更なしに相互通信が実現します。

例えば、オンプレミスの新規マイクロサービス（IPv6専用）からAWS上のデータベースAPI（IPv4）を呼び出すシナリオを考えます。

1. オンプレミスのDNSサーバーは、Route 53 Resolverインバウンドエンドポイントにクエリをフォワード
2. Route 53 ResolverはDNS64でAレコードをAAAAレコードに合成して返却
3. オンプレミスのIPv6クライアントは合成されたIPv6アドレスに接続
4. NAT64ゲートウェイでIPv4に変換され、AWS上のサービスに到達

この構成により、既存のIPv4サービスを変更することなく、新規のIPv6インフラを段階的に導入できます。

> **Note:** DNS64を使用する場合、NAT64ゲートウェイも併せて構成する必要があります。AWS Transit GatewayやサードパーティのNAT64ソリューションを検討してください。

## SRE視点での活用ポイント

### IAM Policy Autopilotの運用組み込み

IAM Policy Autopilotは、CI/CDパイプラインに組み込むことで真価を発揮します。例えば、GitHub ActionsやGitLab CIで、プルリクエスト作成時に自動的にポリシーを生成し、レビュワーがセキュリティ要件を満たしているかを確認するフローを構築できます。Terraformとの連携により、インフラ変更とアプリケーション変更が同時に行われる場合でも、整合性のあるポリシーが自動生成されるため、手動での調整ミスを防げます。

導入時の判断基準として、まずは開発環境から始め、生成されたポリシーの精度を検証することをお勧めします。特に、動的なリソース参照（環境変数経由のARN取得など）が多用されるアプリケーションでは、Terraform定義との突合により期待通りのARN解決が行われるかを確認する必要があります。

リスクとしては、ツールが検出できないAPI呼び出し（リフレクションや動的コード生成による呼び出し）が存在する可能性があります。そのため、生成されたポリシーをそのまま本番適用するのではなく、統合テスト環境で実際のワークロードを実行し、権限不足エラーが発生しないかを検証するステップを挟むべきです。CloudTrailログと組み合わせ、実際に使用されたAPIコールと生成ポリシーを突合することで、カバレッジを確認できます。

### Route 53 Resolver IPv6対応の運用戦略

ハイブリッドクラウド環境でのDNS設計は、障害時の影響範囲を最小化する観点で重要です。Route 53 ResolverのDNS64対応により、オンプレミスとクラウド間でIPv4/IPv6混在環境のDNS解決が統一的に管理できるようになりました。

SRE的な視点では、DNS64を有効化する際に、CloudWatch Logsを使った集中ログ記録を必ず設定すべきです。特に、合成されたAAAAレコードのクエリ頻度や、変換失敗のパターンを監視することで、IPv6移行の進捗状況を定量的に把握できます。

```bash
$ aws route53resolver put-resolver-query-log-config \
  --name dns64-logs \
  --destination-arn arn:aws:logs:us-east-1:123456789012:log-group:/aws/route53/dns64 \
  --creator-request-id unique-log-id
```

また、DNS64は正引き（名前→IPアドレス）の解決のみを行うため、逆引き（IPアドレス→名前）には対応していません。ログ分析やセキュリティ監視で逆引きを使用している場合、IPv6環境では別の識別方法（タグやメタデータ）を併用する設計を検討する必要があります。

障害対応のランブックには、「IPv6クライアントからIPv4サービスへの接続不可」シナリオを追加し、DNS64の合成状況確認手順とNAT64ゲートウェイのヘルスチェック方法を記載しておくと良いでしょう。Route 53 Resolverのエンドポイント自体は高可用性ですが、NAT64ゲートウェイが単一障害点にならないよう、冗長化とモニタリングが不可欠です。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [IAM Policy Autopilot adds Java support and Terraform-aware policy generation](https://aws.amazon.com/about-aws/whats-new/2026/05/iam-policy-autopilot/) | IAMポリシー自動生成ツールがJavaサポートとTerraform連携機能を追加。ワイルドカードではなく具体的なリソースARNを指定した最小権限ポリシーを自動生成可能に |
| [AWS Marketplace introduces Tax management portal for sellers](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-marketplace-tax/) | AWS Marketplace売り手向けの税務管理ポータルをリリース。請求書の一元管理、検索・フィルタリング、API経由のプログラマティックアクセスに対応 |
| [AWS Service Catalog is now available in the AWS Asia Pacific (New Zealand) and Canada West (Calgary) regions](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-service-catalog-calgary-new-zealand-regions/) | AWS Service Catalogがニュージーランドとカルガリーの2つの新リージョンで利用可能に。CloudFormationとTerraformベースの承認済みIaCカタログを管理・配布 |
| [Amazon Route 53 Global Resolver now lets you add and remove AWS Regions for anycast DNS resolution](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-route-global-resolver-aws/) | Route 53 Global ResolverでanycastDNS解決に参加するリージョンを動的に追加・削除可能に。設定再作成なしでグローバルDNSインフラを柔軟に調整 |
| [Amazon Route 53 Resolver endpoints now support additional capabilities for IPv6 query traffic](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-route-53-resolver-ipv6/) | Route 53 ResolverエンドポイントがDNS64機能とIPv6ネームサーバー転送に対応。IPv4/IPv6混在環境でのハイブリッドDNS運用を簡素化 |
| [Amazon EC2 G6 instances now available in AWS European Sovereign Cloud (Germany)](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-ec2-g6-aws-european-sovereign-cloud/) | NVIDIA L4 GPU搭載のG6インスタンスが欧州主権クラウド（ドイツ）で提供開始。ML推論、動画処理、ゲームストリーミングなど高性能ワークロードに対応 |

## まとめ

2026年5月9日のアップデートは、**セキュリティ自動化**、**グローバルネットワークの柔軟性**、**主権クラウド対応**という3つのテーマで構成されています。

IAM Policy AutopilotのTerraform連携は、Infrastructure as Codeの進化系として、セキュリティとインフラ定義を統合的に管理する新しいアプローチを提示しています。これにより、開発速度とセキュリティの両立がより現実的になりました。

Route 53 ResolverのIPv6機能強化は、企業のネットワーク移行戦略に大きな選択肢を追加します。DNS64によるシームレスな相互運用性は、レガシーインフラのモダナイゼーションを段階的に進める上で重要な技術基盤となるでしょう。

欧州主権クラウドでのG6インスタンス提供は、データレジデンシ要件が厳しい地域でのAI/MLワークロード展開を加速させます。規制遵守とハイパフォーマンスコンピューティングの両立が、より多くの企業にとって現実的な選択肢になりました。

これらのアップデートを組み合わせることで、グローバルに展開しながらも各国の規制に対応し、セキュリティと運用効率を高次元でバランスさせたシステム設計が可能になります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)