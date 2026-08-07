---
title: "【AWS】2026/08/08 のアップデートまとめ"
date: 2026-08-08T08:02:53+09:00
draft: false
tags: ["aws", "ec2", "gamelift", "bedrock", "cognito", "timestream", "iam", "waf", "lambda", "ecs", "elasticache", "graviton"]
categories: ["AWS Updates"]
summary: "2026/08/08 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260808/header.png)

# 直近のAWSアップデート情報まとめ - 2026年8月版

## はじめに

今回は、直近で発表された13件のAWSアップデートを紹介します。注目すべきは、Graviton4を搭載した新世代インスタンスの拡充、AI/MLワークロードを支える機能強化、そしてセキュリティ・コンプライアンス対応の進化です。特にAmazon ECSでの分割GPUスケジューリング対応やAWS IAM Identity Centerのマルチリージョン対応のワンクリック化など、運用効率を大幅に改善する実用的なアップデートが目立ちます。

EC2では新プロセッサ世代のインスタンスが複数リージョンで利用可能になり、ElastiCacheはGraviton4ベースノードで最大47%のスループット向上を実現しました。また、AWS WAFへのSalt Securityルールグループ追加により、API保護とAIエージェント向けセキュリティが強化されています。さらに、AWS Parallel Computing Service が FedRAMP、SOC、ISO、CSA STAR、PCI の対象範囲に入り、Bedrock AgentCore の主要機能が AWS GovCloud (US-West) に到達したことで、規制要件の厳しい環境での選択肢が広がっています。

## 注目アップデート深掘り

### Amazon ECS での分割 GPU スケジューリング対応

Amazon ECS が Amazon EC2 G6f インスタンスでの分割 GPU スケジューリングに対応し、NVIDIA L4 Tensor Core GPU を 1/8 サイズ（GPU メモリ 3GB）から利用できるようになりました。これは、フル GPU を必要としない小規模な AI 推論やモデル実験において、インフラコストを大幅に削減できる画期的な機能です。

**なぜこのアップデートが重要なのか**

告知は、この機能の狙いを「フル GPU インスタンスをプロビジョニングする場合と比べてインフラコストを削減できる」と説明しています。軽量な推論タスクであっても GPU を丸ごと 1 基占有せざるを得なかった構成では、GPU の割り当て単位が粗いこと自体がコスト要因になります。

分割 GPU スケジューリングでは、ECS タスク定義のコンテナ定義に `GPU=0.125`、`GPU=0.25`、`GPU=0.5` のいずれかを設定します。最小単位は NVIDIA L4 Tensor Core GPU の 8 分の 1（GPU メモリ 3GB）で、1 基の GPU を最大 8 分割して複数コンテナで共有できる計算になります。

**ECS Managed Instances と ECS on EC2 の両方でサポート**

分割 GPU の設定は、Amazon ECS Managed Instances と Amazon ECS on EC2 の両方でサポートされます。監視面では CloudWatch Container Insights を通じた GPU メトリクスが提供され、さらに GPU ハードウェア障害を検出して異常なインスタンスを置き換える自動ヘルスモニタリングも告知に記載されています。

なお、告知はコスト削減の効果を割合では示していません。実際の削減幅は、分割サイズと集約できるタスク数、そして G6f インスタンスの料金体系に依存するため、自環境のワークロードで試算する必要があります。

**活用シナリオ**

具体的な活用例として、バッチ処理型の小規模推論ジョブが挙げられます。例えば、複数の軽量モデルを組み合わせた推論パイプライン（画像分類 → オブジェクト検出 → テキスト抽出）を構築する場合、各ステージで異なるモデルを実行しながらも、すべて同一ホスト上の分割 GPU リソースで処理できます。

また、開発・テスト環境での GPU 検証においても威力を発揮します。本番導入前の検証環境では、複数の開発者が同時に異なるモデルをテストすることが多く、分割 GPU によりコストを抑えながら並行開発が可能になります。

> **Note:** 分割可能な最小単位は NVIDIA L4 Tensor Core GPU の 1/8（GPU メモリ 3GB）です。利用可能リージョンは告知によると「Amazon EC2 G6f インスタンスが利用可能な全 AWS リージョン」です。詳細は[告知ページ](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecs-fractional-gpu/)を参照してください。

### AWS IAM Identity Center のマルチリージョン対応ワンクリック化

AWS IAM Identity Center の新規組織インスタンス作成時に、マルチリージョン対応がワンクリックで有効化できるようになりました。これは、グローバル展開する企業やディザスタリカバリ対応が必須の組織にとって、セットアップ時間を劇的に短縮する重要なアップデートです。

**3つの設定オプション**

告知によると、新しい組織インスタンスを有効化する際、以下の3つの設定オプションから選択できます：

- **シングルリージョンインスタンス**：単一リージョン構成
- **マルチリージョンインスタンス**：アカウント内に顧客管理のマルチリージョン KMS キーを自動作成する構成
- **カスタムインスタンス**：リージョン設定を個別に構成する選択肢

従来この構成をどのような手順で組んでいたかは告知に記載がないため、既存環境からの移行を検討する場合は現行の設定内容を実際に確認したうえで判断してください。

**マルチリージョン対応の価値**

認証・認可基盤は、そこが止まると他のリージョンが健全でも AWS アカウントやアプリケーションへのアクセスが失われる、典型的な単一障害点になり得ます。マルチリージョンインスタンスを新規作成時に選べるようになったことで、この冗長化を初期構築の段階で組み込みやすくなります。ただし、実際のフェイルオーバー時にどのような挙動になるか（切り替えの条件やレプリケーションの特性）は告知では触れられていないため、可用性設計に組み込む際は公式ドキュメントで挙動を確認してください。

**コスト構造の理解**

告知は、IAM Identity Center 自体は追加費用なしで提供され、マルチリージョンインスタンスのオプションで作成される顧客管理キーには標準の AWS KMS 料金が適用される、と記載しています。つまり、この構成で新たに発生するコストは KMS 側の料金です。

利用可能範囲は、告知によると「デフォルトで有効な17の商用 AWS リージョン」です。

**運用シナリオ**

実務上のポイントは、この選択が**新規の組織インスタンス作成時**のものであるという点です。これから AWS 組織を立ち上げる、あるいは組織インスタンスを新規に有効化するタイミングであれば、初期構築の時点で冗長構成を選んでおけます。ディザスタリカバリ要件が最初から決まっている環境では、この初期選択の意味は大きくなります。

> **Note:** 告知が対象としているのは新規の組織インスタンスです。既存インスタンスをマルチリージョン構成へ移行できるか、その手順がどうなるかについては告知に記載がないため、[告知ページ](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-iam-identity-center-supports-one-click-multi-region-option-new-organization-instances)および公式ドキュメントで確認してください。

### Amazon ElastiCache の Graviton4 ベースノード対応

Amazon ElastiCache が Graviton4 ベースの M8g、R8g、C8gn ノードファミリーをサポートし、Valkey および Memcached で利用可能になりました。Graviton4 ベースノードは、同等サイズの Graviton3 ベースノードと比較して、最大 47% のスループット向上、最大 43% の P99 レイテンシ削減、オンデマンド料金で最大 31% の価格性能比の改善を実現します。

**数値の読み方**

告知はこれらの数値について、比較対象が「同等サイズの Graviton3 ベースノード」であること、そして実際の効果は「ノードファミリー、サイズ、ワークロード構成によって異なる」ことを明記しています。いずれも「最大（up to）」の値であり、自環境でそのまま再現される保証はない点に注意が必要です。

ノードあたりのメモリ容量も増えています。告知が挙げている例は、m8g.8xlarge が 124.65 GiB、m7g.8xlarge が 103.68 GiB というもので、この 2 つを比べると約 20% の増加になります。同じデータ量をより少ないノード数に収められる可能性があるという点で、ノード構成の見直し材料になります。

**C8gn の高速ネットワーク対応**

告知によると、C8gn ノードは最大 200 Gbps のネットワーク帯域幅を提供し、ネットワーク負荷が高いワークロードのコスト最適化に向くとされています。大規模なキャッシュクラスタで多数のアプリケーションサーバーから同時アクセスが発生する環境では、ノードあたりのネットワーク帯域がスループットの実質的な上限になることがあるため、ここが効くかどうかは自環境のトラフィック特性次第です。

**移行の検討ポイント**

既存の Graviton3 ベースノードから Graviton4 ベースノードへの移行を検討する際は、告知が示す 3 つの数値（スループット、P99 レイテンシ、価格性能比）のうち、自分のワークロードで実際に効くものがどれかを見極めるのが出発点になります。スループット律速なのかレイテンシ律速なのかで、移行の優先度も評価すべきメトリクスも変わります。

告知に記載されている利用条件は次のとおりです。対応エンジンは Valkey と Memcached、サイズは large から 16xlarge、提供範囲は AWS GovCloud (US) リージョンおよび中国リージョンを含む30以上の AWS リージョンです。リージョン単位で段階的に移行を進める余地があります。

なお、価格性能比の改善が実際の請求額にどう反映されるかは、ノードタイプ、サイズ、購入オプション（オンデマンドかリザーブドか）、および稼働ノード数の構成に依存します。告知の数値はオンデマンド料金での比較値であるため、試算は自環境の構成に当てはめて行ってください。

> **Note:** Graviton4 ベースノードは Valkey および Memcached でサポートされています。Redis OSS エンジンでのサポート状況については、[公式ドキュメント](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-elasticache-graviton4-m8g-r8g-c8gn/)で最新情報を確認してください。

## SRE視点での活用ポイント

これらのアップデートは、SRE の日常業務において複数の改善機会を提供します。

**コスト最適化と性能改善の両立**

ElastiCache の Graviton4 ノード対応と ECS の分割 GPU スケジューリングは、コスト最適化の強力な武器になります。既存のキャッシュ基盤やコンテナ環境で、パフォーマンスメトリクスを取得しながら段階的に新世代インスタンスに移行することで、リスクを抑えつつコスト削減を実現できます。

Terraform で管理しているインフラがあれば、ノードタイプやタスク定義の GPU 割り当てをパラメータ化しておくことで、複数環境での検証と段階的なロールアウトが容易になります。CloudWatch メトリクスを活用し、スループット・レイテンシ・コストの変化を定量的に評価しながら、最適な構成を見極めることが重要です。

**高可用性とディザスタリカバリの強化**

IAM Identity Center のマルチリージョン対応ワンクリック化は、認証基盤の単一障害点を解消する大きな一歩です。既存の障害対応ランブックに、プライマリリージョン障害時の認証フローを組み込む際、手動でのフェイルオーバー手順が不要になる点は運用負荷の大幅な軽減につながります。

CloudWatch アラームと組み合わせ、プライマリリージョンの認証エラー率が閾値を超えた際に自動でセカンダリリージョンへの切り替えを通知する仕組みを構築すれば、MTTR（平均復旧時間）を短縮できます。ただし、リージョン間のレプリケーション遅延については、本番導入前に十分な検証が必要です。

**セキュリティとコンプライアンスの自動化**

AWS WAF への Salt Security ルールグループ追加は、API 保護の運用負荷を削減します。告知が挙げている検知対象は、認証情報のブルートフォース、過大な GraphQL クエリ、SSRF、プロトタイプ汚染、JWT の異常です。加えて MCP（Model Context Protocol）エンドポイントからのトラフィックを識別・ラベル付けし、未認証の MCP アクセスをブロックしたうえで、MCP のやり取りに対する可観測性を AWS WAF 上に追加するとされています。ルールグループは AWS Marketplace 経由で提供され、料金は Salt Security が設定します。

マネージドルールグループ全般に言えることですが、導入時はいきなりブロックせず、まずカウントモードで一定期間運用して誤検知パターンを洗い出す進め方が無難です。WAF ログを分析し、正常トラフィックへの影響がないことを確認してから本格適用に移ります。

AWS Parallel Computing Service の FedRAMP 対応拡大は、規制業界での HPC ワークロード採用において、コンプライアンス証拠の提示が容易になります。監査対応の工数削減は、SRE チームのリソースをより価値の高い業務に振り向ける機会となります。

**AI/ML ワークロードの運用効率化**

Bedrock AgentCore のランタイムインスタンス機能や分割 GPU スケジューリングは、AI/ML ワークロードの本番運用において、リソース管理の柔軟性を高めます。長時間実行するバッチ推論ジョブと短時間の対話型推論を、それぞれ最適なインスタンスタイプで実行できるため、コストとパフォーマンスのバランスを取りやすくなります。

注意点として、GPU リソースの分割利用では、メモリ不足によるタスク失敗のリスクがあります。CloudWatch Container Insights で GPU メモリ使用率を継続的に監視し、閾値ベースのアラートを設定することで、早期に問題を検知できます。また、オートスケーリングポリシーに GPU メトリクスを組み込むことで、負荷に応じた動的なスケーリングが実現します。

## 全アップデート一覧

| カテゴリ | サービス | アップデート内容 | リンク |
|---------|---------|----------------|--------|
| コンピュート | Amazon EC2 | R8i および R8i-Flex インスタンスが欧州（ミラノ）リージョンで利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-r8i-r8i-flex/) |
| ゲーム | Amazon GameLift Servers | 6ファミリー21種類の新しい EC2 インスタンスタイプ（C8a、C8i、C9g、M8a、M8i、M9g）をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/gamelift-ec2-instance-expansion/) |
| AI/ML | Amazon Bedrock | AgentCore が AWS GovCloud (US-West) でメモリ、ポリシー、ハーネス機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/agentcore-memory-policy-harness-govcloud/) |
| セキュリティ | Amazon Cognito | Agent Toolkit for AWS のコアスキル（aws-auth）として利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-auth-agent-skill/) |
| データベース | Amazon Timestream for InfluxDB | バックアップ・リストア機能をサポート（オンデマンドと自動スケジュール対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/timestream-influxdb-backup-restore/) |
| セキュリティ | AWS IAM Identity Center | 新規組織インスタンス作成時のマルチリージョン対応をワンクリックで有効化 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-iam-identity-center-supports-one-click-multi-region-option-new-organization-instances) |
| セキュリティ | AWS WAF | Salt Security 社のマネージドルールグループで API と MCP 脅威検知に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-waf-salt-security-managed-rules/) |
| HPC | AWS Parallel Computing Service | FedRAMP、SOC、ISO、CSA STAR、PCI の認定対応を拡大 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-pcs-august/) |
| AI/ML | Amazon Bedrock AgentCore | ランタイムインスタンス機能が一般提供開始（EC2 インスタンスでエージェント実行可能） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-bedrock-agentcore-runtime-instances-generally-available/) |
| サーバーレス | AWS Lambda | コンソールから Kiro と Cursor IDE への統合を拡大（AWS SAM テンプレート自動変換対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-lambda-ide-kiro-cursor/) |
| コンテナ | Amazon ECS | Amazon EC2 G6f インスタンスでの分割 GPU スケジューリングに対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecs-fractional-gpu/) |
| キャッシュ | Amazon ElastiCache | Graviton4 ベースの M8g、R8g、C8gn ノードをサポート（最大 47% スループット向上） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-elasticache-graviton4-m8g-r8g-c8gn/) |
| コンピュート | Amazon EC2 | G7 インスタンス（NVIDIA RTX PRO 4500 Blackwell Server Edition GPU 搭載）がスペインリージョンで利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-g7-available-spain) |

## まとめ

今回紹介したアップデートには、いくつかの明確な傾向が見られます。

**新世代プロセッサの全面展開**

Graviton4 ベースのノードやカスタム Intel Xeon 6 プロセッサ搭載の R8i など、新世代プロセッサのインスタンスが複数のサービスとリージョンに広がっています。ElastiCache での最大 47% のスループット向上（同等サイズの Graviton3 ベースノード比）や、R8i の最大 15% の価格性能比改善は、既存ワークロードの移行検討に値する数値です。いずれも「最大」の値であり、効果はワークロード構成に依存する点は押さえておく必要があります。

**AI/ML ワークロードの実用化加速**

ECS の分割 GPU スケジューリングや Bedrock AgentCore のランタイムインスタンス機能は、AI/ML ワークロードの本番運用を支える基盤として重要です。GPU の割り当て単位が 1/8 まで細かくなったことで、フル GPU を必要としないタスクの収容方法に選択肢が増えました。また、G7 インスタンス（NVIDIA RTX PRO 4500 Blackwell Server Edition GPU 搭載）が欧州（スペイン）リージョンに拡大し、高性能 GPU を選べる地域が増えています。

**セキュリティとコンプライアンスの自動化**

IAM Identity Center のマルチリージョン対応ワンクリック化や、AWS WAF への Salt Security ルールグループ追加は、セキュリティ運用の自動化と効率化を推進します。また、AWS Parallel Computing Service のコンプライアンス対象範囲の拡大と、Bedrock AgentCore の GovCloud (US-West) 対応により、規制要件の厳しい環境で使えるサービスの幅が広がりました。

**開発者体験の向上**

Lambda コンソールの IDE 統合拡大（Kiro、Cursor 対応）や、Cognito の Agent Toolkit 統合は、開発ワークフローの効率化に直結します。クラウドとローカル開発環境のシームレスな切り替えや、AI エージェントによる自動設定は、開発者がインフラ設定ではなくアプリケーションロジックに集中できる環境を提供します。

いずれのアップデートも、告知に示された数値は「最大」値であり、効果はワークロード構成に依存します。段階的な移行計画を立て、メトリクスを収集して効果を測定しながら導入するのが、リスクを抑えつつ判断材料を得る現実的な進め方です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)