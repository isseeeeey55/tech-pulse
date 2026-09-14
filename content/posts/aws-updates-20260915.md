---
title: "【AWS】2026/09/15 のアップデートまとめ"
date: 2026-09-15T08:02:25+09:00
draft: true
tags: ["aws", "end-user-messaging", "sagemaker", "cloudfront", "connect", "entity-resolution", "private-ca", "eks", "ebs", "quick", "marketplace", "evs", "storage-gateway", "ecs", "rds", "kms", "rekognition", "kinesis", "ram", "organizations"]
categories: ["AWS Updates"]
summary: "2026/09/15 のAWSアップデートまとめ"
---

# 直近のAWSアップデート情報（2026年9月版）

## はじめに

今回は、直近で発表された19件のAWSアップデートを紹介します。Amazon ECSのIAM条件キー拡張やEBS Volume Clonesのクロスアカウント対応といったインフラ基盤の機能強化から、Amazon QuickのモバイルおよびデスクトップアプリGA、SageMaker JumpStartへの新しい基盤モデル追加、AWS End User MessagingのWhatsAppダイナミックフロー対応まで、幅広い領域での機能拡充が行われています。特に注目すべきは、エンタープライズのマルチアカウント運用を支援する機能や、AI/MLモデルの選択肢拡大、そしてコミュニケーション体験の向上を図る新機能群です。

---

## 注目アップデート深掘り

### Amazon ECS の RunTask / StartTask API での IAM 条件キー拡張

Amazon ECS が RunTask と StartTask API でも IAM 条件キー `ecs:task-cpu` および `ecs:task-memory` をサポートするようになりました。これまでこれらの条件キーは RegisterTaskDefinition、CreateService、UpdateService API でのみ利用可能でしたが、今回の拡張により、タスクを起動するあらゆる経路で統一的なリソース制限を IAM ポリシーレベルで適用できるようになります。

#### なぜこのアップデートが重要なのか

ECS 環境では、開発者や CI/CD パイプラインが RunTask API を使って直接タスクを起動するケースが多くあります。従来は RegisterTaskDefinition でタスク定義を作成する際には CPU・メモリの上限を IAM ポリシーで制御できましたが、RunTask の段階ではこの制御が効きませんでした。その結果、誤って大規模なリソースを割り当てたタスクを起動してしまい、予期しないコスト増加が発生するリスクがありました。

今回の拡張により、組織全体のリソースポリシーを IAM ポリシーで一元管理し、どの API 経由でもポリシーを強制できるようになります。これにより、複数チームが異なる方法でタスクを起動する環境でも、リソース使用量を統一的に制御できます。

#### 実装の詳細

IAM ポリシーに以下のような条件を追加することで、RunTask / StartTask 実行時のリソース制限を設定できます。公式ドキュメントには条件キーの仕様が記載されており、CPU・メモリの値を数値で制限できます。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:RunTask",
        "ecs:StartTask"
      ],
      "Resource": "*",
      "Condition": {
        "NumericLessThanEquals": {
          "ecs:task-cpu": "2048",
          "ecs:task-memory": "4096"
        }
      }
    }
  ]
}
```

この設定により、RunTask / StartTask で 2 vCPU・4 GB メモリを超えるタスクを起動しようとした場合、IAM ポリシー違反として拒否されます。これにより、開発環境で誤って本番級のリソースを割り当ててしまうミスを未然に防ぐことができます。

#### 従来との比較

従来は RegisterTaskDefinition の段階でリソース制限を設けても、RunTask で別のタスク定義を指定されるとポリシーが回避される可能性がありました。今回の拡張により、タスク定義作成時と起動時の両方で統一的なガードレールを設けることができ、組織全体のリソースガバナンスが大幅に強化されます。

---

### AWS End User Messaging の WhatsApp ダイナミックフロー対応

AWS End User Messaging が WhatsApp のダイナミックフロー機能に対応しました。これにより、WhatsApp のチャット内で予約申し込み、リード獲得、ユーザー登録、アンケート、決済などのインタラクティブな体験を完結させることができるようになります。

#### 背景と重要性

従来のチャットボット体験では、ユーザーを外部ウェブサイトやフォームに誘導する必要があり、その過程で離脱が発生するという課題がありました。特にモバイルユーザーにとって、チャットからブラウザに遷移し、再びチャットに戻るという体験は煩雑で、コンバージョン率の低下につながっていました。

ダイナミックフローは、Meta が提供するテンプレートまたはゼロから構築した独自フローを使用し、テキスト入力、日付ピッカー、ドロップダウン、ボタンなどの構成要素をチャット内に直接表示します。各画面はリアルタイムに独自の HTTPS エンドポイントを呼び出せるため、ライブの在庫状況や予約可能枠を表示したり、ユーザーごとにパーソナライズされた提案を行うことができます。

#### 実装の流れ

フローは JSON スキーマで定義し、メッセージテンプレート経由で配信します。AWS End User Messaging Social のコンソール画面または API を使用して、フローの作成・管理が可能です。リアルタイムエンドポイント連携により、バックエンドシステムと統合しながら動的なユーザー体験を提供できます。

#### ユースケース例

飲食店の予約システムでは、WhatsApp 内で営業時間内のライブ予約状況を表示し、日付・時間・人数を選択してもらい、そのままチャット内で予約を完結させることができます。BtoB のリード獲得では、ホワイトペーパー申請フォームを WhatsApp で完結させ、即座に資料を配信できます。eコマースでは、商品確認から支払いまで WhatsApp 内で完結させることで、購入プロセスの離脱を大幅に削減できます。

---

### Amazon EBS Volume Clones のクロスアカウントコピー対応

Amazon EBS Volume Clones がアカウント間でのボリュームコピー機能に対応しました。暗号化の再設定にも対応し、ソースアカウントの EBS ボリュームをターゲットアカウントの AWS KMS キーで暗号化しながらコピーできるようになりました。

#### なぜこの機能が重要なのか

マルチアカウント戦略を採用している企業では、本番環境と開発環境を異なるアカウントで管理するのが一般的です。開発者が本番データベースと同等のデータでテストを行いたい場合、従来は複雑な手順を踏む必要がありました。今回のアップデートにより、本番データベースボリュームを隔離された開発アカウントにクローンし、開発者が安全に実験用データとして利用できるようになります。

また、環境ごとに異なる暗号化キーの管理が必要な場合（本番用と非本番用で異なる KMS キーを使用するなど）にも対応しており、セキュリティとコンプライアンスの要件を満たしながらデータを共有できます。

#### 実装方法

コピー方法は、まず AWS Resource Access Manager (RAM) でボリュームをターゲットアカウントと共有し、その後ターゲットアカウント側で共有ボリュームのコピーを同じアベイラビリティゾーン内に作成します。AWS Management Console、CLI、SDK で利用可能です。

#### 従来との比較

従来は、ボリュームのスナップショットを作成し、それを別アカウントと共有してから、ターゲットアカウント側で新しいボリュームを作成する必要がありました。この方法では、スナップショット作成とボリューム作成の2段階のプロセスが必要で、時間もコストもかかりました。Volume Clones のクロスアカウント対応により、より迅速かつ効率的にボリュームを共有できるようになりました。

---

## SRE視点での活用ポイント

### ECS IAM 条件キー拡張の活用

Terraform で ECS タスク定義を管理している環境では、CI/CD パイプラインから RunTask を実行する際に、IAM ポリシーレベルでリソース上限を設定することで、誤った設定変更による予期しないコスト増加を防げます。特に複数のマイクロサービスを運用している場合、各サービスごとに異なるリソース上限を IAM ロールで管理することで、きめ細かいコスト管理が可能になります。

導入時の注意点として、既存の運用で意図的に大きなリソースを割り当てているタスクがある場合、IAM ポリシーを適用する前にそれらを洗い出し、ポリシーの例外を設定するか、リソース割り当てを見直す必要があります。段階的な導入として、まず CloudTrail で RunTask の実行履歴を分析し、現状のリソース使用パターンを把握してからポリシーを設計することを推奨します。

### クロスアカウント EBS コピーの活用

災害復旧計画として、本番アカウントから定期的に DR 用アカウントにボリュームをコピーし、別リージョンで待機させる構成を組むことで、アカウントレベルの障害にも対応できるようになります。AWS Backup と組み合わせることで、クロスアカウント・クロスリージョンのバックアップ戦略を自動化できます。

導入時のリスクとして、KMS キーの権限設定を誤ると、ターゲットアカウント側でボリュームを復号できない問題が発生する可能性があります。事前に AWS RAM と KMS キーのポリシーを十分にテストし、アクセス権限を検証しておくことが重要です。

### WhatsApp ダイナミックフローの活用

カスタマーサポートの運用改善として、障害対応のランブックに WhatsApp フローを組み込むことで、ユーザーが自己解決できる範囲を広げることができます。例えば、ネットワーク接続トラブルシューティングのフローをチャット内で提供し、各ステップの結果に応じて次のアクションを動的に提示することで、サポートチケットの削減が期待できます。

導入時の判断基準として、ユーザーベースが WhatsApp を主要なコミュニケーション手段として利用しているかどうかを確認する必要があります。また、HTTPS エンドポイントのレスポンス速度がユーザー体験に直結するため、バックエンドシステムの可用性と応答速度の監査が重要です。

---

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **メッセージング** | [AWS End User Messaging SMS の自動フェイルオーバー](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-improves-deliverability>) | SMS 配信の信頼性を強化する自動フェイルオーバー機能を追加 |
| **メッセージング** | [AWS End User Messaging WhatsApp ダイナミックフロー対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-whatsapp-dynamic-flows>) | WhatsApp チャット内で予約、決済、アンケートなどを完結可能に |
| **AI/ML** | [SageMaker JumpStart に Granite Speech、Kanana、OpenFold3 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/granite-speech-4.1-2b-edge-kanana-2-30b-a3b-instruct-openfold3-jumpstart/) | IBM、Kakao、OpenFold の最新基盤モデルが利用可能に |
| **AI/ML** | [SageMaker JumpStart に Gemma-4-31B 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/gemma-4-31b-it-assistant-gemma-4-31b-it-nvfp4-jumpstart/) | Google DeepMind の Gemma-4-31B フル精度版と NVIDIA 最適化版を提供 |
| **AI/ML** | [SageMaker JumpStart に Ministral-3 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/ministral-3-3b-instruct-2512-ministral-3-8B-Instruct-2512-jumpstart/) | Mistral AI のコンパクトなマルチモーダルモデルがエッジデバイスに対応 |
| **AI/ML** | [SageMaker JumpStart に Qwen3.6 と Wan2.1 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/qwen3.6-35b-a3b-nvfp4-wan2.1-t2v-1.3B-diffusers-jumpstart/) | NVIDIA の量子化版エージェント型モデルとアリババのテキスト動画生成モデルを提供 |
| **CDN** | [CloudFront Dynamic Image Transformation 新機能追加](https://aws.amazon.com/about-aws/whats-new/2026/08/dynamic-image-transformation-adds-new-features/) | スマート切り抜き強化、自動最適化強化、テストプレイグラウンド、ECS/Lambda 機能パリティを実現 |
| **CRM** | [Amazon Connect Customer Profiles セグメントイベント機能](https://aws.amazon.com/about-aws/whats-new/2026/09/connect-customer-profiles-segment-events/) | 顧客がセグメントに入った/出た時にリアルタイム通知を Kinesis に送信 |
| **データ管理** | [AWS Entity Resolution レコードレベル信頼度スコア](https://aws.amazon.com/about-aws/whats-new/2026/09/entity-resolution-record-confidence/) | ML マッチングで各レコードが個別の信頼度スコアを持つように進化 |
| **セキュリティ** | [AWS Private CA EKS アドオンと AD コネクタが GovCloud 対応](https://aws.amazon.com/about-aws/whats-new/2026/09/private-ca-eks-addon-ad-govcloud/) | Kubernetes と Active Directory 向けの証明書管理を GovCloud で利用可能に |
| **ストレージ** | [EBS Volume Clones クロスアカウントコピー対応](https://aws.amazon.com/about-aws/whats-new/2026/09/ebs-volume-clones-cross-account-copy/) | アカウント間でのボリュームコピーと暗号化再設定に対応 |
| **アプリケーション** | [Amazon Quick デスクトップアプリ GA リリース](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-desktop-app-generally-available-macos-windows/) | macOS・Windows でローカルファイル統合とバックグラウンドエージェントを提供 |
| **アプリケーション** | [Amazon Quick モバイルアクティビティフィード](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-activity-feed-available-ios-android-mobile-devices/) | iOS・Android で企業全体のコミュニケーションツールを一元表示 |
| **アプリケーション** | [Amazon Quick 常時稼働エージェントと管理機能強化](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-always-on-agents-sharper-feed-enterprise-controls/) | クラウド上で常時実行されるエージェント、改善されたフィード、エンタープライズ管理機能を追加 |
| **マーケットプレイス** | [AWS Marketplace デモ/オファー要求の自動審査](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-marketplace-demo-private-offer-requests-qualification>) | AI ワークフローで顧客要求を自動評価し、数分以内に出品者に届ける |
| **コンピューティング** | [Amazon EVS 4リージョン拡大](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-evs-available-in-additional-regions/) | VMware Cloud Foundation を大阪、台北、スペイン、テルアビブで利用可能に |
| **ストレージ** | [Storage Gateway FIPS プライベート接続対応](https://aws.amazon.com/about-aws/whats-new/2026/09/storage-gateway-fips-privatelink-s3/) | S3 File Gateway が PrivateLink 経由の FIPS 140-3 準拠接続に対応 |
| **コンテナ** | [Amazon ECS IAM 条件キー拡張](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-expands-condition-key-support/) | RunTask / StartTask API で CPU・メモリの IAM 条件キーをサポート |
| **データベース** | [RDS for Oracle July 2026 SPB 対応](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-oracle-supports-spatial-patch-bundle-jul-2026-ru/) | Oracle 19c・26ai で Supplemental Patch Bundle と段階的アップグレードロールアウトに対応 |

---

## まとめ

今回紹介したアップデート群は、エンタープライズのマルチアカウント運用、AI/ML モデルの民主化、コミュニケーション体験の向上という3つの軸で AWS の機能拡充が進んでいることを示しています。

特に ECS の IAM 条件キー拡張や EBS のクロスアカウントコピーは、マルチアカウント戦略を採用している組織にとって、セキュリティとガバナンスを保ちながら柔軟な運用を実現する重要な機能です。SageMaker JumpStart への新しい基盤モデル追加は、組織が特定のユースケース（音声認識、多言語対応、生物分子構造予測など）に最適化されたモデルを迅速に評価・導入できる環境を提供します。

AWS End User Messaging の WhatsApp ダイナミックフローや Amazon Quick の常時稼働エージェントは、ユーザー体験の向上と業務自動化を両立させる新しいアプローチを提示しており、カスタマーサポートやマーケティングオートメーションの領域での活用が期待されます。

今後も AWS は、既存サービスの機能強化とリージョン拡大を継続的に進めており、グローバル展開を行う組織にとって、データレジデンシーや低遅延を実現する選択肢が増えています。これらのアップデートを活用することで、運用効率の向上、コスト最適化、セキュリティ強化を同時に実現できる可能性が広がっています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)