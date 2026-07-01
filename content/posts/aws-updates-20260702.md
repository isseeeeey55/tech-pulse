---
title: "【AWS】2026/07/02 のアップデートまとめ"
date: 2026-07-02T08:02:43+09:00
draft: true
tags: ["aws", "bedrock", "guardduty", "ec2", "eks", "ecs", "artifact", "appconfig", "lambda", "partner-central", "marketplace", "rds", "cloudformation", "cdk", "security-agent", "prometheus", "govcloud"]
categories: ["AWS Updates"]
summary: "2026/07/02 のAWSアップデートまとめ"
---

# 直近の AWS アップデート 11 件を SRE 視点で深掘り解説

## はじめに

今回は、直近で発表された AWS の 11 件のアップデートを紹介します。Amazon Bedrock AgentCore のクォータ拡張、GuardDuty の機密ファイル改ざん検知、EKS の Kubernetes バージョンロールバック機能、CloudFormation と CDK の Express Mode による最大 4 倍の高速化など、運用効率とセキュリティを大きく向上させるアップデートが揃っています。

特に注目すべきは、開発ライフサイクル全体を通じたセキュリティ強化と、運用における柔軟性の向上です。GuardDuty の新機能は攻撃者の侵害後活動を検出し、EKS のロールバック機能は本番環境での安全なアップグレードを可能にします。また、CloudFormation の Express Mode は開発サイクルの高速化に貢献します。

本記事では、これらのアップデートの中から特に運用インパクトの大きいものを深掘りし、SRE の視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon GuardDuty の機密ファイル改ざん検知機能

Amazon GuardDuty Runtime Monitoring に、EC2 インスタンスと EKS/ECS 上のコンテナワークロードにおける機密ファイルの改ざん検知機能が追加されました。この機能は、攻撃者による侵害後の活動を検出する上で重要な意味を持ちます。

従来のシグネチャベース検知では、攻撃者が難読化手法や新しい攻撃パターンを用いた場合、検出を回避される可能性がありました。今回追加された機能は、ファイル操作（書き込みオープン、名前変更、シンボリックリンク、ハードリンク、削除）を直接監視することで、攻撃手法に依存しない検知を実現しています。

#### なぜこのアップデートが重要なのか

攻撃者がシステムに侵入した後、多くの場合、永続化メカニズムの構築、権限昇格、防御回避のために重要なシステムファイルを改ざんします。具体的には、`/etc/shadow` や `/etc/passwd` などの認証情報ファイル、cron ジョブの設定ファイル、システムログなどが標的となります。これらの改ざんを早期に検出することで、攻撃の連鎖を断ち切ることができます。

#### 新しい脅威検知タイプの詳細

新たに追加される 3 つの脅威検知タイプは、それぞれ MITRE ATT&CK フレームワークの戦術にマッピングされています：

- **Persistence（永続化）**: 攻撃者が再起動後もアクセスを維持するために、起動スクリプトや cron ジョブを改ざんする行為を検知
- **PrivilegeEscalation（権限昇格）**: sudoers ファイルや setuid ビットの変更など、権限昇格に繋がる設定変更を検知
- **DefenseEvasion（防御回避）**: 監査ログの削除や改ざん、セキュリティツールの設定変更を検知

これらの検知では、相関分析により正規の管理操作と攻撃的な操作を区別します。例えば、定期的なパッチ適用プロセスによるシステムファイル更新は正常な操作として扱われる一方、通常とは異なるプロセスからの予期しないファイル操作は疑わしい活動としてフラグが立てられます。

#### 検証とラボ環境での実装

GuardDuty Runtime Monitoring を有効化するには、EC2 インスタンスまたはコンテナワークロードに対して機能を有効にする必要があります。30 日間の無料トライアルが提供されているため、本番環境に導入する前に検証環境で挙動を確認できます。

有効化後、GuardDuty は自動的にランタイムイベントの監視を開始し、機密ファイルへのアクセスパターンを学習します。検知が発生した場合、GuardDuty コンソールに詳細な情報（影響を受けたファイルパス、操作を行ったプロセス、タイムスタンプ）が表示され、改善提案とともに MITRE ATT&CK マッピングが提供されます。

#### 既存セキュリティツールとの連携

GuardDuty の検知結果は Amazon EventBridge 経由でルーティングできるため、既存の SIEM や SOAR ツールと統合可能です。例えば、検知イベントを Splunk や AWS Security Hub に送信し、他のセキュリティシグナルと相関分析することで、より包括的な脅威検知が実現できます。また、Lambda 関数を組み合わせて自動対応（該当インスタンスの隔離、スナップショット取得、セキュリティチームへの通知）を実装することも可能です。

### AWS CloudFormation と CDK の Express Mode

AWS CloudFormation と CDK に追加された Express Mode は、インフラストラクチャのデプロイ時間を最大 4 倍高速化する機能です。この改善は、特に開発環境での反復的なインフラ構築において大きな効果を発揮します。

#### 従来の課題と Express Mode の仕組み

従来の CloudFormation デプロイでは、各リソースが完全に安定化するまで待機する必要がありました。例えば、CloudFront ディストリビューションの場合、エッジロケーション全体への伝播が完了するまで 5～10 分かかることがあり、API Gateway や Route 53 などのグローバルサービスでも同様の待機時間が発生していました。

Express Mode では、CloudFormation がリソース設定の適用を確認した時点でデプロイが完了とみなされます。安定化チェックはバックグラウンドで継続されるため、ドメイン名や ARN などの出力値を数秒で取得でき、次の作業を即座に開始できます。

#### デプロイ時間の具体的な改善

CloudFront ディストリビューションを含むスタックを例にとると、従来モードでは完全なデプロイに 10 分以上を要していたものが、Express Mode では 1～2 分程度に短縮されます。これは、ディストリビューションの作成自体は数秒で完了し、エッジロケーションへの伝播はバックグラウンドで進行するためです。

Lambda 関数、DynamoDB テーブル、S3 バケットなどの比較的単純なリソースでも、複数リソースの並列処理最適化により、全体のデプロイ時間が短縮されます。

#### ロールバック動作の変更と運用への影響

Express Mode では、デフォルトでロールバックが無効になります。これは開発環境での迅速な反復を想定した設計で、エラーが発生した場合は即座に原因を修正して再デプロイできます。従来モードでは、エラー発生時にロールバックが完了するまで次のデプロイを開始できませんでしたが、Express Mode ではエラーを確認次第すぐに修正版をデプロイできます。

ただし、本番環境では慎重な判断が必要です。ロールバックが無効な場合、デプロイ失敗時にスタックが中途半端な状態で残るため、手動での復旧手順を用意しておく必要があります。本番環境では従来モードを使用するか、Express Mode を使用する場合は十分なテストと監視を組み合わせることが推奨されます。

#### CI/CD パイプラインへの統合

Express Mode は、CDK と組み合わせることで CI/CD パイプラインのフィードバック時間を大幅に短縮できます。開発者がコードをプッシュしてから、インフラの変更がデプロイされ、統合テストが実行されるまでの時間が短縮されることで、開発速度が向上します。

特に AI エージェントによる自動インフラストラクチャコード生成のユースケースでは、生成されたコードを即座にデプロイして検証し、結果をフィードバックするループが高速化されます。これにより、AI とのインタラクティブなインフラ開発が現実的になります。

### Amazon EKS の Kubernetes バージョンロールバック機能

Amazon EKS に追加された Kubernetes バージョンのロールバック機能は、本番環境での安全なアップグレード戦略を大きく変える可能性があります。アップグレード後 7 日以内であれば、前のマイナーバージョンに戻すことができるようになりました。

#### なぜロールバック機能が重要なのか

Kubernetes のバージョンアップグレードは、新機能の利用やセキュリティパッチの適用のために定期的に実施する必要があります。しかし、本番環境でのアップグレードには常にリスクが伴います。API の非互換性、アドオンの互換性問題、パフォーマンスの劣化など、事前のテスト環境では発見できなかった問題が本番環境で顕在化することがあります。

従来は、このような問題が発生した場合、クラスタを再構築するか、問題を修正するまで影響を受け入れるしかありませんでした。ロールバック機能により、問題が発生した場合の「脱出経路」が用意されたことで、より積極的にアップグレードを実施できるようになります。

#### ロールバック前の自動チェック

ロールバックを実行する前に、EKS は以下の項目を自動的にチェックします：

- **API 互換性**: 現在デプロイされているワークロードが、ロールバック先のバージョンの API と互換性があるかを確認
- **バージョンスキュー**: コントロールプレーンとワーカーノードのバージョン差が Kubernetes のサポート範囲内かを検証
- **アドオン互換性**: EKS アドオン（VPC CNI、kube-proxy、CoreDNS など）がロールバック先のバージョンで動作するかを確認
- **クラスタの健全性**: ロールバック実行前のクラスタ全体の健全性状態を評価

これらのチェックにより、ロールバック自体が新たな問題を引き起こすリスクを最小化しています。

#### EKS Auto Mode でのロールバック

EKS Auto Mode を使用している場合、ワーカーノードのロールバックも自動的に管理されます。コントロールプレーンのバージョンがロールバックされると、EKS は自動的にワーカーノードのバージョンも調整し、クラスタ全体の整合性を保ちます。

従来の管理型ノードグループや自己管理型ノードを使用している場合は、コントロールプレーンのロールバック後に、手動でノードグループのバージョンを調整する必要があります。

#### 運用への組み込み方

ロールバック機能を活用した安全なアップグレード戦略として、以下のようなフローが考えられます：

1. ステージング環境で新バージョンを十分にテスト
2. 本番環境でアップグレードを実施（メンテナンスウィンドウ内）
3. 7 日間の監視期間を設け、パフォーマンスメトリクス、エラーログ、ユーザーフィードバックを収集
4. 重大な問題が検出された場合、ロールバックを実行
5. 問題がなければ、7 日経過後にアップグレードを確定

この戦略により、アップグレードのリスクを受け入れ可能なレベルまで下げることができます。

## SRE 視点での活用ポイント

### セキュリティ監視の多層化

GuardDuty の機密ファイル改ざん検知機能は、既存のセキュリティ監視を補完する形で活用できます。CloudWatch アラームと組み合わせると、検知イベントをリアルタイムで通知し、オンコールエンジニアに即座にエスカレートできます。

ランブックに組み込む際は、検知されたファイル改ざんの種類に応じた対応手順を明確にしておくことが重要です。例えば、`/etc/shadow` の改ざんが検知された場合は即座にインスタンスを隔離し、フォレンジック調査を開始する、といった自動化された対応フローを構築できます。

導入時の判断基準としては、まず 30 日間の無料トライアルを活用し、環境内での検知頻度と誤検知率を評価することが推奨されます。特に、定期的なパッチ適用プロセスや設定管理ツール（Ansible、Chef など）が誤検知を引き起こす可能性があるため、これらの正常な操作を事前にベースライン化しておく必要があります。

### インフラのデプロイサイクル高速化

CloudFormation の Express Mode は、Terraform で管理しているインフラがある場合でも、CDK や CloudFormation への移行を検討する動機になる可能性があります。特に、開発環境やステージング環境で頻繁にインフラを作り直すワークフローでは、デプロイ時間の短縮が開発者体験の大幅な改善につながります。

導入にあたっては、まず開発環境から Express Mode を適用し、ロールバック無効化の影響を評価することが重要です。デプロイ失敗時のリカバリー手順をドキュメント化し、チーム内で共有しておくことで、万が一のトラブルにも迅速に対応できます。

本番環境への適用は慎重に判断すべきですが、カナリアデプロイや Blue-Green デプロイと組み合わせることで、リスクを最小化しながら高速化のメリットを享受できる可能性があります。例えば、新バージョンのスタックを Express Mode で素早くデプロイし、トラフィックを段階的に切り替えながら監視するアプローチが考えられます。

### Kubernetes アップグレードのリスク軽減

EKS のロールバック機能は、Kubernetes のバージョンアップグレード戦略を根本的に見直す機会を提供します。従来は、本番環境でのアップグレードを年に 1～2 回の大規模イベントとして扱い、慎重なテストと長時間のメンテナンスウィンドウを確保する必要がありました。

ロールバック機能により、より頻繁に、より小さな変更でアップグレードを実施するアプローチが現実的になります。四半期ごとに新バージョンを導入し、7 日間の監視期間で問題を検出するサイクルを確立することで、セキュリティパッチの適用遅延リスクを低減できます。

注意点としては、7 日間のロールバック期間は短いため、アップグレード後の監視を集中的に実施する必要があります。Prometheus や CloudWatch Container Insights でメトリクスを収集し、アップグレード前後でのパフォーマンス比較を自動化しておくことが推奨されます。また、ロールバック自体もメンテナンスウィンドウ内で実施すべきであり、完全なダウンタイムゼロを保証するものではない点に留意が必要です。

Istio や Karpenter などの複雑なアドオンを使用している環境では、アドオンの互換性マトリクスを事前に確認し、ロールバック時の挙動をステージング環境で検証しておくことが重要です。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Bedrock AgentCore increases default runtime quota limits](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-bedrock-agentcore-increases-default-runtime-quota-limits/) | AgentCore のデフォルトランタイムクォータが引き上げられ、米国東部/西部で最大 5,000 個、その他リージョンで 2,500 個のアクティブな同時セッションをサポート。1 秒あたり 200 個のエージェント相互作用と 25 個の新規セッション作成に対応し、大規模な AI エージェントワークロードのスケーリングが可能に。 |
| 2 | [Amazon GuardDuty adds sensitive file modification threat detections](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-guardduty-sfm/) | GuardDuty Runtime Monitoring に機密ファイルの改ざん検知機能が追加。EC2 と EKS/ECS 上のコンテナワークロードで、設定ファイル、認証情報、システムログなどの重要ファイルの改ざんを監視し、Persistence、PrivilegeEscalation、DefenseEvasion の 3 つの脅威検知タイプで攻撃者の侵害後活動を検出。 |
| 3 | [AWS Artifact now includes Assurance Assistant for compliance inquiries](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-artifact-assurance-assistant/) | AWS Artifact に AI 搭載の Assurance Assistant が追加され、セキュリティとコンプライアンスに関する質問に検証済みドキュメントに基づいた引用付きの回答を自動生成。単一質問モードと XLSX 形式の質問票一括処理モードがあり、DDQ 対応やベンダー評価を加速。 |
| 4 | [AWS AppConfig launches managed experimentation tools for A/B testing](https://aws.amazon.com/about-aws/whats-new/2026/6/aws-appconfig-experimentation/) | AWS AppConfig に実験管理ツールが正式リリース。別途実験インフラを構築せずに A/B テストや多変量実験を実施可能。Amazon の 25 年以上のベストプラクティスに基づき、AI 駆動のガイダンスで堅牢な実験設計をサポート。EC2、Lambda、ECS、EKS、オンプレミス環境全体で動作。 |
| 5 | [AWS Partner Central now supports AWS Marketplace listings for co-selling](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-marketplace-co-selling-support/) | AWS Partner Central が AWS Marketplace のリスティングをコセリング機会に直接関連付けることをサポート。最大 10 個の Marketplace ソリューションとプロダクトを 1 つの機会に紐付け可能。Partner Central Selling API 経由でプログラマティックにも実装できる。 |
| 6 | [Amazon RDS announces Cross-Region Automated Backups in four additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-cross-region-automated-backups-additional-aws-regions/) | RDS のクロスリージョン自動バックアップ機能が、メキシコ（中央）、台北、ニュージーランド、タイの 4 リージョンで利用可能に。スナップショットとトランザクションログを対象リージョンに自動レプリケートし、RPO を数分以内に抑えた災害復旧を実現。 |
| 7 | [Amazon EKS now supports Kubernetes version rollback](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-eks-version-rollback>) | EKS が Kubernetes バージョンのロールバック機能をサポート。アップグレード後 7 日以内であれば前のマイナーバージョンに戻すことが可能。ロールバック前に API 互換性、バージョンスキュー、アドオン互換性、クラスタ健全性を自動チェック。EKS Auto Mode ではワーカーノードのロールバックも自動管理。 |
| 8 | [Amazon Bedrock AgentCore now available in four additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-agentcore-four-additional-regions/) | Amazon Bedrock AgentCore がバンコク、マレーシア、ミラノ、スペインの 4 リージョンで利用可能に。AI エージェントを構築・接続・最適化するためのプラットフォームで、エンドユーザーに近い場所でのエージェント実行により低レイテンシーを実現。 |
| 9 | [AWS Security Agent now available in Asia Pacific (Mumbai), Asia Pacific (Singapore), and South America (São Paulo)](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-security-agent-asia-pacific/) | AWS Security Agent がムンバイ、シンガポール、サンパウロの 3 リージョンで利用可能に。STRIDE ベースの脅威モデリング、GitHub/GitLab/Bitbucket/Confluence 全体でのコードレビュー、IDE プラグインと MCP 統合、オンデマンド侵入テストを提供し、開発ライフサイクル全体を通じてアプリケーションを保護。 |
| 10 | [Amazon Managed Service for Prometheus achieves FedRAMP High and DoD IL-4/5 authorization in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-prometheus-fedramp-high/) | Amazon Managed Service for Prometheus が AWS GovCloud (US) で FedRAMP High および DoD CC SRG IL-4/5 認可を取得。連邦機関や厳格なコンプライアンス要件を持つ組織が、Prometheus 互換のモニタリング・アラート機能を規制基準を満たしながら利用可能に。 |
| 11 | [AWS CloudFormation and CDK express mode speeds up infrastructure deployments by up to 4x](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-cloudformation-cdk/) | CloudFormation と CDK に Express Mode が追加され、インフラのデプロイ時間が最大 4 倍高速化。リソース設定の適用確認時点でデプロイが完了し、安定化チェックはバックグラウンドで継続。ロールバックはデフォルトで無効になり、即座に修正と再試行が可能。 |

## まとめ

今回紹介した 11 件のアップデートは、AWS の進化の方向性を示しています。特に、セキュリティの強化、運用の柔軟性向上、開発サイクルの高速化という 3 つの軸が明確に見て取れます。

GuardDuty の機密ファイル改ざん検知機能は、セキュリティ監視を次のレベルに引き上げ、攻撃者の侵害後活動を早期に検出する能力を提供します。EKS のロールバック機能は、Kubernetes 運用における最大のリスクの 1 つであるバージョンアップグレードに対する「保険」を提供し、より積極的なアップグレード戦略を可能にします。CloudFormation の Express Mode は、開発者の待ち時間を削減し、フィードバックループを高速化することで、インフラストラクチャの反復開発を促進します。

また、Bedrock AgentCore のクォータ拡張とリージョン拡大は、AI エージェントを本番環境で大規模に運用する準備が整いつつあることを示唆しています。AppConfig の実験管理ツールは、A/B テストを民主化し、データ駆動型の意思決定を容易にします。

これらのアップデートを適切に活用することで、システムの信頼性、セキュリティ、開発速度を同時に向上させることができるでしょう。特に SRE の観点では、これらの新機能を既存の運用プラクティスに組み込み、継続的に改善していくアプローチが重要です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)