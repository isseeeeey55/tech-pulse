---
title: "【AWS】2026/07/07 のアップデートまとめ"
date: 2026-07-07T08:01:52+09:00
draft: true
tags: ["aws", "sagemaker", "cloudwatch", "vmware", "secrets-manager", "certificate-manager", "codepipeline", "ec2", "eks", "cloudtrail"]
categories: ["AWS Updates"]
summary: "2026/07/07 のAWSアップデートまとめ"
---

# 直近の AWS アップデート解説：SageMaker HyperPod の推論最適化から ACM の ACME 対応まで

## はじめに

今回は、直近で発表された 6 件の AWS アップデートを紹介します。機械学習の推論最適化、可観測性の自動化、証明書管理の標準化など、多岐にわたる領域で重要な機能拡張が行われています。特に注目すべきは、Amazon SageMaker HyperPod による推論処理の分離アーキテクチャと、AWS Certificate Manager の ACME プロトコル対応です。これらは運用効率とセキュリティの両面で大きな改善をもたらす可能性があります。また、CloudWatch Application Signals の自動キャプチャ機能により、アプリケーション監視の導入障壁が大きく下がりました。本記事では、これらのアップデートについて技術的な背景と活用シーンを深掘りしていきます。

## 注目アップデート深掘り

### Amazon SageMaker HyperPod：Disaggregated Prefill and Decode による推論最適化

Amazon SageMaker HyperPod が **Disaggregated Prefill and Decode (DPD)** に対応しました。これは大規模言語モデル（LLM）の推論処理における重要な課題を解決する機能です。

#### なぜこのアップデートが重要なのか

従来の LLM 推論では、プリフィル（入力処理）とデコード（出力生成）が同じ GPU 上で実行されていました。この構成では、長いコンテキストを持つ 1 つのリクエストが他のすべての並行リクエストのトークン生成をブロックしてしまう問題がありました。特に RAG システムや長文書分析では、数千トークンに及ぶプリフィル処理が発生するため、チャットアシスタントのような短い応答を期待するリクエストが著しく遅延する現象が起きていました。

#### DPD のアーキテクチャと動作原理

DPD は推論処理を 2 つの専用 GPU プールに分離します。プリフィルプールは計算量の多い入力処理を担当し、デコードプールはメモリ帯域幅に依存する出力生成を実行します。両者の間で KV キャッシュは **GPU-Direct RDMA** を使用して **Elastic Fabric Adapter (EFA)** 経由で効率的に転送されます。この分離により、リソース競合が排除され、より安定したトークンごとのレイテンシーと予測可能なスループットが実現されます。

インテリジェントルーターが自動的にリクエストを適切なパスに振り分けるため、短いプロンプトではオーバーヘッドなく直接デコーダーへ送信される仕組みになっています。これにより、リクエストの特性に応じた最適な処理経路が選択されます。

#### 実装のポイント

設定は `InferenceEndpointConfig` に `pdSpec` を追加することで行います。具体的な設定項目の詳細は、公式ドキュメントで確認することをお勧めします。この構成により、チャットアシスタント、エージェントパイプライン、RAG システムなど、トラフィック波動が大きく複雑な推論ワークフローを持つサービスにおいて、ピーク時のコスト効率化とレイテンシー保証を両立できます。

従来構成では、長いコンテキストのリクエストが到着すると、すべての並行処理が影響を受けましたが、DPD ではプリフィル専用プールで処理が独立するため、デコード中のリクエストは影響を受けません。この分離は、多数の同時ユーザーからのリクエストが混在する本番環境で特に威力を発揮します。

### AWS Certificate Manager の ACME プロトコル対応：証明書管理の自動化標準

AWS Certificate Manager (ACM) が ACME プロトコルに対応しました。これは TLS 証明書管理における重要な転換点となります。

#### 背景：短期証明書時代への対応

CA/Browser Forum は 2029 年に証明書の有効期限を 47 日間に義務化することを決定しました。従来の 1 年や 90 日の証明書を手動で管理する運用は、この短期化により実用的ではなくなります。ACME プロトコルは、証明書の発行と更新を完全に自動化するための業界標準であり、Let's Encrypt が普及させたこの仕組みが AWS でも利用可能になったことは、大規模な証明書管理の自動化を実現する上で極めて重要です。

#### ACME 統合の仕組み

ACM の ACME サポートにより、Certbot、Kubernetes の cert-manager、acme.sh など、ACME v2 互換のクライアントを使用して、Amazon Trust Services から 45 日間の有効期限を持つ公開 TLS 証明書を完全に自動管理できるようになりました。

特に注目すべきは、集中管理されたガバナンス機能です。PKI 管理者は ACME エンドポイントを作成し、各クライアントが発行できる証明書のドメイン範囲を定義したり、ワイルドカード使用ポリシーを適用したりできます。さらに、DNS 認証情報を配布することなくアプリケーションチームに証明書リクエストを委譲できる点は、セキュリティと運用の両面で優れています。

#### 運用モデルの変化

ドメイン検証はエンドポイントレベルで 1 回実行され、その後アプリケーションオーナーは標準 ACME クライアントを使用して証明書をリクエストします。すべてのアクティビティは ACM コンソールで表示でき、AWS CloudTrail ログと Amazon CloudWatch メトリクスで監査可能です。

この仕組みにより、Kubernetes クラスタで cert-manager を使用した自動証明書更新の完全な実装や、マイクロサービス環境での大規模な TLS 証明書管理の自動化が現実的になります。DevOps パイプラインへの証明書自動更新の統合も、標準的な ACME クライアントを用いることで容易になります。

## SRE 視点での活用ポイント

### 推論システムの安定性向上

SageMaker HyperPod の DPD 機能は、推論システムの運用において予測可能性を大きく向上させます。Terraform で管理している推論基盤があれば、既存の GPU インスタンス構成を見直し、プリフィル専用とデコード専用のプールを分離する構成に移行することで、レイテンシーのばらつきを抑制できるでしょう。特に複数のユースケースが混在する環境では、長いコンテキストを扱う分析系ワークロードと、低レイテンシーが求められるチャット系ワークロードを分離する判断材料になります。

導入時の注意点として、EFA を活用した KV キャッシュ転送のオーバーヘッドと、リクエストの特性（コンテキスト長の分布）を事前に把握しておく必要があります。CloudWatch メトリクスでプリフィル時間とデコード時間を個別に可視化し、どちらがボトルネックになっているかを継続的に監視する体制が重要です。

### 可観測性の導入障壁低減

CloudWatch Application Signals の Service Events 機能は、追加のコード変更なしでエラーとパフォーマンス異常を自動キャプチャします。ADOT SDK または CloudWatch Observability EKS add-on でインストルメント済みの環境であれば、デプロイメント直後の新規例外を即座に検出できるため、障害対応のランブックに「デプロイ後の Service Events 確認」ステップを組み込むことで、問題の早期発見が可能になります。

導入判断としては、既存の分散トレーシング環境がある場合、重複するデータ収集によるコスト増加と、統一された可観測性基盤によるトラブルシューティング効率化のトレードオフを評価する必要があります。CloudWatch アラームと組み合わせることで、デプロイメントイベントをトリガーとした自動検証やロールバック判断の自動化も視野に入ります。

### 証明書管理の自動化とガバナンス

ACM の ACME 対応により、Kubernetes 環境で cert-manager を用いた証明書自動更新パイプラインが AWS ネイティブに構築できるようになりました。既存の手動更新フローでは、証明書の有効期限切れに起因するインシデントが定期的に発生しがちですが、ACME により 45 日ごとの自動更新が標準化されることで、このリスクが大幅に低減します。

導入時のリスクとしては、DNS 認証の自動化が正しく動作しない場合に証明書更新が失敗するシナリオを想定し、更新失敗時のアラート設定と、証明書有効期限のマージンを考慮した監視閾値の設定が不可欠です。CloudTrail ログで証明書リクエストの監査証跡を保持することで、セキュリティ規制要件にも対応できます。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon SageMaker HyperPod | Disaggregated Prefill and Decode (DPD) 対応により、LLM 推論のプリフィルとデコードを分離し、GPU リソース競合を排除 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/7/amazon-sagemaker-hyperpod-dpd/) |
| CloudWatch Application Signals | Service Events 機能により、例外・レイテンシーイベント・デプロイメントイベントを追加コード変更なしで自動キャプチャ | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/cloudwatch-service-events/) |
| Amazon Elastic VMware Service | VMware Cloud Foundation (VCF) 9.0 および 9.1 に対応、EC2 ベアメタルインスタンス上で完全自己管理可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-evs-vcf9) |
| AWS Secrets Manager | Paddle API キーと GitLab アクセストークン（個人/グループ/プロジェクト）の管理外部シークレットに対応し、自動ローテーションをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/secrets-manager-managed-external-secrets-paddle-gitlab/) |
| AWS Certificate Manager | ACME プロトコルに対応、Certbot や cert-manager などの標準クライアントで 45 日間証明書の自動発行・更新が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-certificate-manager-acme/) |
| AWS CodePipeline | アジア太平洋（ニュージーランド）リージョン（ap-southeast-6）で利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-codepipeline-new-zealand/) |

## まとめ

今回のアップデート群は、運用自動化と標準化という一貫したテーマが見て取れます。SageMaker HyperPod の DPD は、LLM 推論における実運用上の課題を物理的なアーキテクチャレベルで解決するアプローチであり、大規模な推論基盤を運用する組織にとって検討価値の高い機能です。CloudWatch Application Signals の Service Events は、可観測性の導入における「計装コストの壁」を大きく下げる意味で、マイクロサービスアーキテクチャの監視成熟度を引き上げる可能性があります。

ACM の ACME 対応は、業界標準プロトコルの採用により、AWS 外のツールチェーンとの統合を容易にし、証明書管理の自動化を加速させるでしょう。2029 年の短期証明書義務化を見据えた準備として、今から ACME ベースの自動更新パイプラインを構築しておくことは、将来的な運用負荷の大幅削減につながります。

Secrets Manager の Paddle・GitLab 対応や、CodePipeline のニュージーランドリージョン展開は、それぞれ特定のユースケースやリージョン要件を持つ組織にとって即効性のあるアップデートです。VMware Cloud Foundation 9.0/9.1 対応は、ハイブリッドクラウド戦略を採用している企業にとって、既存スキルとツールチェーンを活かした AWS 移行の選択肢を広げるものです。

これらのアップデートに共通するのは、「自動化」「標準化」「ガバナンス」の 3 つの軸です。運用チームとしては、それぞれの機能が自組織のシステムアーキテクチャとどう組み合わせられるかを検証し、段階的に導入していくアプローチが現実的でしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)