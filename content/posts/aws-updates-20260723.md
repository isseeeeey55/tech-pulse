---
title: "【AWS】2026/07/23 のアップデートまとめ"
date: 2026-07-23T08:02:36+09:00
draft: true
tags: ["aws", "ec2", "entity-resolution", "lambda", "kms", "network-load-balancer", "corretto", "secrets-manager", "eventbridge", "direct-connect", "eks", "elastic-disaster-recovery", "ecs"]
categories: ["AWS Updates"]
summary: "2026/07/23 のAWSアップデートまとめ"
---

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。新しいEC2インスタンスタイプのリージョン拡大、AWS Entity Resolutionのリアルタイム処理強化、Lambda Durable Functionsのセキュリティ機能拡充、Network Load Balancerのルーティング機能追加など、コンピューティング、ネットワーク、セキュリティ、コンテナ管理に渡る幅広いアップデートが含まれています。

特に注目すべきは、AWS Entity Resolutionのリアルタイム高度マッチング機能とNetwork Load Balancerのリスナールール対応です。前者はこれまでバッチ処理に限定されていた複雑なマッチングロジックをミリ秒単位で実行可能にし、後者はIPv4/IPv6混在環境での運用を大幅に簡素化します。また、AWS Secrets ManagerがEventBridgeと統合され、シークレット変更を起点としたイベント駆動アーキテクチャの構築が容易になった点も実務上のインパクトが大きいでしょう。

## 注目アップデート深掘り

### AWS Entity Resolution - リアルタイム高度マッチング機能の実現

AWS Entity Resolutionが高度なリアルタイムマッチング機能に対応しました。これまでリアルタイムマッチングは単純なルールベースのワークフローのみに限定されていましたが、今回のアップデートにより、複雑な条件演算子（Exact、ExactManyToManyなど）とAND/ORロジックを組み合わせた高度なルールセットをミリ秒単位で実行できるようになります。

**なぜこのアップデートが重要なのか**

従来、高度なマッチング処理は数分から数時間かかるバッチ処理でのみ利用可能でした。このため、不正検知やリアルタイム顧客認証など即座の判断が必要なユースケースでは、リアルタイム処理用のシンプルなルールと、バッチ処理用の複雑なルールという二重のインフラ管理が必要でした。このアップデートにより、この制約が解消され、アプリケーションの再構築なしに複雑なマッチングロジックをリアルタイムで実行できるようになります。

**従来の方法との比較**

従来のリアルタイムマッチングでは、単純な完全一致やパターンマッチングなど基本的なルールのみが許可されていました。複数の属性を組み合わせた条件や、多対多の関連性をチェックする処理は、バッチワークフローでのみ可能でした。新機能では、GenerateMatchId APIを使用し、enableRealTimeMatchingパラメータをtrueに設定するだけで、バッチ処理と同等の複雑なルールセットをリアルタイムで実行できます。

**具体的な活用シーン**

不正検知のシナリオでは、購入前に顧客情報を複数のデータソースと照合し、住所・電話番号・メールアドレスなど複数の属性の組み合わせで既知の不正パターンと一致するかを瞬時に判定できます。ExactManyToMany演算子を使用すれば、一人の顧客が複数のアカウントを持つケースや、逆に複数の顧客が同じデバイスを使用するケースなど、多対多の関係性も正確に検出できます。

ウェブサイトパーソナライゼーションでは、訪問ユーザーの複数の属性（ブラウザフィンガープリント、IPアドレス、Cookie情報など）をAND/ORロジックで組み合わせて既存顧客と照合し、ミリ秒単位で個別化されたコンテンツを配信できます。従来は単純なCookie照合のみでリアルタイム判定し、より精度の高いマッチングは後からバッチ処理で実行していたところを、一度のAPI呼び出しで完結できるようになります。

**導入の考慮点**

新しいエンドポイントの追加や既存アプリケーションの大規模な再構築は不要です。既存のシンプルなリアルタイムワークフローから高度なワークフローへの移行は、ルール定義の更新とパラメータ設定の変更のみで実現できます。ただし、より複雑なルールセットはAPI応答時間に影響する可能性があるため、本番環境への適用前にレイテンシー要件を満たすか検証することが推奨されます。

### AWS Network Load Balancer - リスナールールによるIPv4/IPv6の自動振り分け

AWS Network Load Balancer（NLB）がリスナールール機能をサポートしました。この機能により、送信元のIPアドレスタイプ（IPv4またはIPv6）に基づいて、接続を異なるターゲットグループに自動的にルーティングできるようになります。

**背景と課題**

IPv4とIPv6の両クライアントに対応する場合、従来は2つの選択肢がありました。1つ目は、IPv4用とIPv6用にNLBを2つ用意してDNSで分割する方法です。これはインフラの二重管理とコスト増を招きます。2つ目は、すべてのトラフィックを1つのターゲットグループに送信し、プロトコル変換を行う方法です。この場合、クライアント元IPアドレスが失われ、ログやセキュリティ監査で正確な情報が取得できなくなります。

**リスナールールによる解決**

新しいリスナールール機能は、単一のデュアルスタックNLBから、IPv6クライアントはIPv6ターゲットへ、IPv4クライアントはIPv4ターゲットへ自動的に振り分けます。レイヤー3での条件付きルーティングにより、プロトコル変換なしで同じアドレスファミリーのターゲットグループへ接続を送信するため、クライアント元IPアドレスが両アドレスファミリー全体で保持されます。

**運用上のメリット**

従来の2 NLB構成では、各NLBに対して個別のヘルスチェック、モニタリング設定、ターゲット管理が必要でしたが、リスナールール方式では単一のNLBで一元管理できます。DNS構成もシンプルになり、IPv4とIPv6で異なるエンドポイントを管理する必要がなくなります。

インフラコスト面では、NLB自体の課金が1台分になり、クロスゾーン負荷分散やデータ処理量に関する課金も統合されます。ログやメトリクスも単一のリソースに集約されるため、監視やトラブルシューティングの効率が向上します。

**導入と設定の考慮点**

リスナールールは既存のNLBに追加できるため、無停止での導入が可能です。ただし、ターゲットグループはIPv4とIPv6でそれぞれ適切なアドレスタイプを持つインスタンスで構成する必要があります。TCP、UDP、TLS いずれのプロトコルでも利用可能ですが、ターゲットグループのヘルスチェック設定は各アドレスファミリーに適した形式で構成する必要があります。

クライアント元IPの保持により、アプリケーションログやセキュリティグループのルール、WAF（Web Application Firewall）との連携など、IPアドレスベースの制御が正確に機能します。金融やヘルスケア業界のように、コンプライアンス要件で正確なクライアントIP追跡が求められる環境では、特に重要な改善となります。

### AWS Secrets Manager - EventBridge統合によるイベント駆動型シークレット管理

AWS Secrets ManagerがAmazon EventBridgeにシークレット更新イベントを自動的に発行するようになりました。シークレット値が変更されるたびにイベントがEventBridgeに直接パブリッシュされるため、CloudTrailを経由した複数のAPIイベント（RotationSuccess、PutSecretValue、UpdateSecretValueなど）を手動でマッチングする複雑なロジックが不要になります。

**従来のアプローチの課題**

これまでシークレットの更新を検知するには、CloudTrailログから複数の関連APIイベントを収集し、それらを突き合わせて「実際にシークレット値が変更された」イベントを特定する必要がありました。ローテーションの成功イベントと実際の値更新イベントは別々に記録されるため、タイミングのズレやイベントの欠損を考慮した堅牢な処理が求められ、運用の複雑性とレイテンシーが増大していました。

**EventBridge統合の仕組み**

新機能では、Secrets Managerがactiveなシークレット値の変更を検出すると、自動的にデフォルトイベントバスにイベントをパブリッシュします。追加設定やopt-inは不要で、すべてのシークレットに対して自動的に有効化されています。EventBridgeルールを作成し、このイベントパターンにマッチするルールを定義することで、Lambda、SNS、SQS、Step Functionsなどの任意のターゲットにイベントをルーティングできます。

**具体的な活用シーン**

アプリケーションのキャッシュリフレッシュでは、データベース認証情報がローテーションされた際に、Lambdaをトリガーして各アプリケーションサーバーのメモリキャッシュをクリアし、次回のDB接続時に新しい認証情報を取得させることができます。従来はアプリケーション側でポーリングするか、定期的な再起動に頼る必要がありましたが、イベント駆動で即座に対応できるようになります。

マイクロサービス環境では、APIキーが更新された際にStep Functionsワークフローを起動し、依存する複数のサービスを順次再起動したり、ヘルスチェックを実行して更新が正常に反映されたことを確認したりできます。SNS通知と組み合わせれば、セキュリティチームへのリアルタイム通知とコンプライアンス監査証跡の自動作成も実現できます。

**運用上の利点**

イベントはミリ秒単位で配信されるため、CloudTrailログの遅延（通常数分）に比べて大幅に応答性が向上します。また、EventBridgeのイベントパターンマッチング機能を使えば、特定のシークレットやタグ条件に基づいてフィルタリングでき、不要なトリガーを削減できます。すべてのSecrets Manager提供リージョンで追加費用なしで利用可能で、EventBridgeの標準課金のみが適用されます。

## SRE視点での活用ポイント

今回のアップデートは、SREの日常業務における複数の課題を解決する要素を含んでいます。

**リアルタイム処理とバッチ処理の統合**

AWS Entity Resolutionのリアルタイム高度マッチング機能は、従来「リアルタイム性」と「処理の複雑性」のトレードオフで別々のシステムを構築していたシーンを統合できます。不正検知システムを例にとると、シンプルなルールベースのリアルタイム判定と、複雑なマッチングを行うバッチ分析を並行運用していた場合、インフラコストだけでなく、ルールセットの二重管理やバージョン整合性の維持が運用負荷となります。単一のワークフローに統合することで、Terraformで管理するインフラリソースも削減でき、変更管理とデプロイメントプロセスがシンプルになります。ただし、リアルタイム処理のレイテンシー要件が厳しい場合は、複雑なルールセットがSLAを満たすか事前検証が必要です。

**ネットワーク構成の簡素化とトラブルシューティング効率化**

Network Load Balancerのリスナールール機能は、IPv4/IPv6デュアルスタック環境での障害対応を大幅に簡素化します。従来の2 NLB構成では、どちらのNLBで問題が発生しているのか、IPv4とIPv6のどちらのクライアントが影響を受けているのかを切り分ける必要がありましたが、単一NLBに統合されることで、CloudWatchメトリクスやVPCフローログの分析対象が一元化されます。障害対応のランブックに「IPv4/IPv6別にNLBを確認」というステップを記載する必要がなくなり、オンコール対応の認知負荷が下がります。Terraformで管理しているインフラであれば、リスナールールの追加は既存リソースの変更のみで済み、リソースの削除・再作成が不要なため、安全にロールアウトできます。

**イベント駆動型の自動化によるMTTR短縮**

AWS Secrets ManagerのEventBridge統合は、シークレットローテーション後の自動化シナリオを大幅に改善します。CloudTrailベースの従来方式では、イベント検出までに数分の遅延があり、その間にアプリケーションが古い認証情報でアクセスを試みて失敗するケースがありました。EventBridgeの即時配信により、ローテーション完了とほぼ同時にアプリケーション側の更新処理を開始できるため、Mean Time To Repair（MTTR）が短縮されます。Lambda関数でヘルスチェックを実行し、新しいシークレットで正常に接続できることを確認してからトラフィックを流す、といった段階的なロールアウトもイベント駆動で実装できます。ただし、EventBridgeルールとLambda関数自体が新たな監視対象となるため、これらのコンポーネントの可用性とエラーハンドリングも設計に含める必要があります。

**リージョン拡大と災害復旧戦略**

AWS Elastic Disaster Recoveryの6リージョン追加は、地理的に分散した災害復旧戦略を構築する選択肢を広げます。アジア太平洋地域（バンコク、マレーシア、ニュージーランド、台北）でのDRS利用が可能になることで、オーストラリアや日本のプライマリリージョンから地理的に離れたセカンダリリージョンを選択でき、リージョン全体の障害リスクを低減できます。RTO/RPOの目標設定時には、リージョン間のネットワークレイテンシーとデータ転送コストを考慮した上で、復旧訓練を定期的に実施し、実際の復旧時間を測定することが重要です。Terraformでインフラをコード管理している場合、DRSの設定もIaCで定義し、復旧後のインフラ再構築を自動化することで、手動作業によるヒューマンエラーを排除できます。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon EC2 | [M8a instances now available in Asia Pacific (Hyderabad)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-m8a-instances-asia-pacific-hyderabad-region/) | 第5世代 AMD EPYC プロセッサ（Turin）搭載の M8a インスタンスがハイデラバードリージョンで利用可能に。M7aと比較して最大30%のパフォーマンス向上と最大19%の価格性能比改善を実現。 |
| AWS Entity Resolution | [Advanced real-time matching support](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-entity-resolution/) | 複雑な条件演算子とAND/ORロジックを組み合わせた高度なルールセットをミリ秒単位で実行可能に。GenerateMatchId APIを使用してリアルタイム高精度マッチングを実現。 |
| AWS Lambda | [Durable Functions supports customer managed key encryption](https://aws.amazon.com/about-aws/whats-new/2026/07/durablefunctions-cmk/) | Lambda Durable Functionsの実行データをAWS KMSのカスタマーマネージドキーで暗号化可能に。金融・ヘルスケアなど規制業界のガバナンス要件に対応。 |
| AWS Network Load Balancer | [Listener Rules for custom traffic routing](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-network-load-balancer-supports-listener-rules/) | 送信元IPアドレスタイプ（IPv4/IPv6）に基づいて異なるターゲットグループへルーティング可能に。単一デュアルスタックNLBでクライアント元IPを保持しながら振り分けを実現。 |
| Amazon Corretto | [July 2026 Quarterly Updates](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-corretto-july-2026-quarterly-updates) | セキュリティと重要な修正を含む四半期アップデート。デフォルトDockerイメージがAmazon Linux 2023ベースに移行。Corretto 8からJavaFXバイナリが廃止。 |
| AWS Secrets Manager | [Secret update notifications to EventBridge](https://aws.amazon.com/about-aws/whats-new/2026/07/secrets-manager-update-notifications) | シークレット更新イベントをEventBridgeに自動発行。CloudTrail経由の複数APIイベントマッチングが不要になり、Lambda/SNS/SQS/Step Functionsへ即座にルーティング可能に。 |
| AWS Direct Connect | [100G expansion in Lima, Peru](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-direct-connect-100g-lima/) | ペルー・リマのCirionデータセンターに100Gbps専用接続を拡張。ペルー初の100Gbps接続とMACsec暗号化対応Direct Connectロケーション。 |
| Amazon EKS | [EFA and placement groups support on Auto Mode and Karpenter](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-eks-efa-placement-groups/) | EKS Auto ModeとKarpenterでEFA（Elastic Fabric Adapter）とプレイスメントグループをサポート。分散学習など高パフォーマンスワークロードに最適化。 |
| AWS Elastic Disaster Recovery | [Now available in six additional regions](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-drs-additional-regions/) | バンコク、マレーシア、ニュージーランド、台北、カルガリー、メキシコ中央の6リージョンで利用可能に。対応リージョン数が全36に拡大。 |
| Amazon ECS | [Advanced deployment strategies in EU Sovereign Cloud](https://aws.amazon.com/about-aws/whats-new/2026/07/ecs-adv-deployments-eu-sovereign-cloud/) | AWS European Sovereign CloudでBlue/Green、Linear、Canaryの高度なデプロイメント戦略に対応。Lambda hooksやCloudWatchアラーム連携による安全な更新が可能に。 |

## まとめ

今回紹介したアップデートは、AWSの継続的な機能改善と地理的拡大の両面を示しています。Entity ResolutionやSecrets Managerのような既存サービスの機能拡張は、リアルタイム処理とイベント駆動アーキテクチャへの対応を強化し、運用の自動化と効率化を推進する方向性が明確です。

Network Load Balancerのリスナールール機能は、IPv4/IPv6デュアルスタック環境という現実的な課題に対する実用的な解決策を提供しており、インフラの簡素化とコスト削減に直結します。Lambda Durable Functionsのカスタマーマネージドキー対応は、規制業界での採用障壁を下げる重要な一歩です。

リージョン拡大（M8aインスタンスのハイデラバード、DRSの6リージョン、Direct Connectのリマ）は、グローバルなワークロード配置とデータレジデンシー要件への対応を容易にします。EKSのEFAサポートやECSの高度なデプロイメント戦略のSovereign Cloud対応は、コンテナ基盤での高度なユースケースを標準機能で実現できる範囲を広げています。

これらのアップデートを活用することで、運用の複雑性を削減しながら、セキュリティとパフォーマンスを向上させることができるでしょう。各組織の要件に応じて、段階的に導入を検討することをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)