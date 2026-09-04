---
title: "【AWS】2026/09/05 のアップデートまとめ"
date: 2026-09-05T08:02:11+09:00
draft: true
tags: ["aws", "ecs", "sagemaker", "ec2", "mcp", "lambda", "transfer-family", "graviton", "nitro"]
categories: ["AWS Updates"]
summary: "2026/09/05 のAWSアップデートまとめ"
---

# 直近発表のAWSアップデート紹介：ECSデプロイメント改善とGraviton5インスタンス拡大

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。注目すべきは、Amazon ECSのデプロイメント機能が大きく進化し、Early Success Criteriaや非クリティカルデーモンといった柔軟な運用を支える機能が追加された点です。また、AWS Graviton5プロセッサを搭載したM9g/C9gインスタンスが東京を含むアジア太平洋リージョンで続々と利用可能になり、最大35%の性能向上を実現しています。さらに、AI/MLワークロード向けにP6シリーズのGPUインスタンスがジャカルタやハイデラバードで展開され、グローバルな推論・学習基盤の選択肢が広がりました。AWS Transfer FamilyやMCP Serverといった運用・開発支援ツールの機能強化も含め、エンタープライズ運用の安定性とパフォーマンスを両立するアップデートが揃っています。

---

## 注目アップデート深掘り

### Amazon ECS Early Success Criteria：デプロイメント完了判定の柔軟化

Amazon ECSは、ローリングデプロイメント時に**Early Success Criteria（早期成功判定基準）**を導入しました。この機能により、デプロイメント完了の定義を「すべてのタスクが正常起動」から「指定した割合のタスクが正常稼働」へと柔軟にカスタマイズできるようになります。

#### なぜこのアップデートが重要なのか

従来のECSローリングデプロイメントでは、目標タスク数すべてが正常に起動するまでデプロイメントが完了とみなされませんでした。これは理想的な状況では問題ありませんが、以下のようなケースでボトルネックとなっていました：

- **GPU専用インスタンスやFargate Spotなど、リソースに制約がある環境**では、タスクの起動に時間がかかるか、一部のタスクが起動待ちになることがある
- **長寿命接続（WebSocket、gRPCストリーミングなど）を持つサービス**では、旧リビジョンのタスクがすぐには終了しない
- **CI/CDパイプラインの待ち時間**が増大し、リリース頻度が下がる

Early Success Criteriaを使えば、例えば「90%のタスクが正常稼働した時点でデプロイ成功」と設定できます。残り10%のタスクは通常のサービススケーリングとは別に起動が続けられ、デプロイメント自体はブロックされません。

#### ソースリビジョンのクリーンアップ方法

新リビジョンへの移行時、旧リビジョンのタスクをどうクリーンアップするかは、**BLOCKING**（同期）と**DEFERRED**（非同期）の2モードから選択できます。

- **BLOCKING**：旧リビジョンのタスクが完全に停止・削除されるまで待ってから、デプロイメント成功を宣言する。従来の挙動に近く、確実性を重視する場合に有効。
- **DEFERRED**：指定した割合のタスクが正常稼働した時点でデプロイメント成功を宣言し、その後バックグラウンドで旧タスクを非同期にドレイン処理する。リリース速度を優先し、接続の自然なドレインを許容する場合に適している。

#### 検証すべきポイント

この機能を実務で活用する前に、以下のような検証を行うことで、自組織に最適な設定値を見極めることができます：

1. **デプロイメント所要時間の測定**：Early Success Criteriaを有効化する前後で、実際のデプロイメント完了までの時間を計測し、短縮効果を定量化する
2. **健全率の設定テスト**：50%、75%、90%など異なる成功判定比率で実験し、リスク（一部タスク起動失敗時の影響）とメリット（リリース速度向上）のバランスを分析
3. **BLOCKING vs DEFERRED の挙動確認**：実際のサービスで両モードを試し、接続ドレイン時間やエラーログを観察。長寿命接続を持つアプリケーションでは、DEFERRED モードで接続が適切に終了するか確認する
4. **GPU/専用ハードウェアワークロードでの効果測定**：リソース制約がある環境では、Early Success Criteriaによりデプロイメント待ち時間がどの程度短縮されるかを実測

この機能はAWS CommercialおよびGovCloud（US）の全リージョンで既に利用可能です。

---

### AWS Graviton5（M9g/C9g）インスタンスの東京リージョン提供開始

AWS Graviton5プロセッサを搭載した**M9g/M9gd**（汎用）および**C9g/C9gd**（コンピューティング最適化）インスタンスが、東京リージョンを含むアジア太平洋各地で利用可能になりました。これらは前世代のGraviton4ベース（M8g/C8g）と比べて、**最大25%のパフォーマンス向上**を実現しています。

#### 性能向上の内訳

- **データベース処理：最大30%高速化** — トランザクション処理やクエリ実行が高速化され、オープンソースDB（PostgreSQL、MySQL）やインメモリキャッシュ（Redis、Memcached）で効果を発揮
- **Webアプリケーション：最大35%高速化**（C9gの場合） — APIゲートウェイやバックエンドサービスのスループット向上に貢献
- **機械学習推論：最大35%高速化**（C9gの場合） — CPUベースの推論ワークロードで、レイテンシとコストの両面で改善

#### Nitro Isolation Engineによるセキュリティ強化

M9g/C9gは第6世代AWS Nitro Systemを採用し、新たに**Nitro Isolation Engine**を搭載しています。これは形式検証（Formal Verification）と呼ばれる数学的手法を用いて、顧客のワークロード間およびAWSオペレータとの間で、論理的に証明されたセキュリティ隔離を実現します。コンプライアンス要件が厳しい業界や、マルチテナント環境での利用において、より高い信頼性を提供します。

#### 東京リージョンでの活用シーン

東京リージョンでM9g/C9gが利用可能になったことで、日本国内の低レイテンシ要件を満たしつつ、コストとパフォーマンスを最適化できます。特に以下のようなワークロードで効果が期待できます：

- オンプレミスから移行中のオープンソースDBを、より高性能かつ低コストで運用
- リアルタイム分析基盤（Apache Spark、Hadoopなど）で、処理時間を短縮しながらコストを削減
- ローカルNVMe SSDを備えたM9gd/C9gdは、一時ファイル、ログバッファ、セッションキャッシュなど高速なローカルストレージを必要とするアプリケーションに最適

#### 検証のポイント

Graviton5インスタンスを本格導入する前に、以下のステップで評価することをおすすめします：

1. **既存M8g/C8gとのベンチマーク比較**：実際のワークロード（TPC-C、YCSB、Sysbench等）でCPU性能、メモリ帯域幅、ディスクI/Oを測定し、公称値との整合性を確認
2. **Nitro Isolation Engineの理解**：形式検証がどのようにセキュリティ保証を実現しているか、公式ドキュメントやWhite Paperで深掘りし、自組織のセキュリティポリシーとの整合性を検討
3. **移行パスの策定**：既存のGraviton3/4ベースインスタンスから段階的に移行するシナリオを設計。アプリケーションの互換性確認とリスク評価を実施

M9g/M9gdはSavings Plans、On-Demand、Spot、Dedicated Instances/Hostsで購入可能です。C9g/C9gdも同様の購入オプションに対応しています。

---

## SRE視点での活用ポイント

### デプロイメント戦略の最適化

ECSのEarly Success Criteriaは、CI/CDパイプラインの待ち時間を短縮し、リリース頻度を高めたいSREチームにとって有力な選択肢です。Terraformでインフラをコード管理している場合、デプロイメント設定に成功判定比率とクリーンアップモードを組み込むことで、環境ごとに異なるリスク許容度を反映できます。例えば、開発環境では90%成功でDEFERREDモード、本番環境では100%成功でBLOCKINGモードといった使い分けが可能です。

また、CloudWatchアラームと組み合わせることで、デプロイメント完了後に残りのタスクが正常に起動しているかを監視し、異常があれば自動ロールバックを発動するランブックに組み込むことも検討できます。ただし、Early Success Criteriaを適用する際は、部分的なタスク起動失敗が顧客体験に与える影響を事前に評価し、適切な閾値を設定することが重要です。

### Graviton5インスタンスによるコストとパフォーマンスの両立

Graviton5（M9g/C9g）インスタンスは、既存のx86ベースインスタンスと比較してコストパフォーマンスに優れています。SREチームがコスト最適化を進める中で、CPU集約的なワークロード（バッチ処理、CI/CDビルドエージェント、リアルタイム分析など）をGravitonベースに移行することで、同じ予算内でより高い処理能力を得られる可能性があります。

Terraformやクラウドコスト管理ツール（AWS Cost Explorer、Kubecost等）を活用して、インスタンスタイプ変更前後のコストとパフォーマンス指標を比較し、ROIを定量化することが推奨されます。また、Graviton5はARMアーキテクチャであるため、アプリケーションやライブラリの互換性を事前に検証する必要があります。Dockerイメージのマルチアーキテクチャビルドやコンテナレジストリの整備も、移行をスムーズにするための準備作業となります。

### AI/MLワークロードのリージョン戦略

P6-B200/B300インスタンスがアジア太平洋（ジャカルタ、ハイデラバード）で利用可能になったことで、地理的に近いリージョンで大規模なAI学習・推論を実行できるようになりました。SREチームがグローバルにサービスを展開している場合、レイテンシとデータ主権を考慮しながら、最適なリージョンを選定することが求められます。

機械学習パイプライン（学習、評価、推論）をTerraformやKubeflowで管理している環境では、リージョンごとのインスタンス可用性とコストを比較し、学習ジョブを適切に配置する戦略を立てることが有効です。また、EFAv4ネットワーク（3.2 Tbps）を活用した分散学習では、複数インスタンス間の通信が性能のボトルネックとなるため、ネットワーク監視とチューニングがSREの重要な役割となります。

---

## 全アップデート一覧

| サービス | アップデート概要 | リンク |
|---------|-----------------|--------|
| Amazon ECS | Early Success Criteria for service deployments — デプロイメント成功判定を柔軟にカスタマイズ可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-deployments-early-success/) |
| Amazon SageMaker | Batch Transform が G6e インスタンスに対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/sagemaker-batch-transform-g6e-instances/) |
| Amazon EC2 | AMI に互換性のあるインスタンスタイプを指定可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/ec2-images-supported-instances) |
| AWS MCP Server | Lambda 関数のサーバーレス診断機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-mcp-server-serverless/) |
| Amazon EC2 | M9g/M9gd インスタンス（Graviton5）がアイルランド、シンガポール、シドニー、東京で利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/ec2-m9g-m9gd-four-regions/) |
| Amazon EC2 | C9g/C9gd インスタンス（Graviton5）が東京リージョンで利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/ec2-c9g-c9gd-asia-pacific-tokyo/) |
| Amazon EC2 | C8g インスタンス（Graviton4）が台北、ニュージーランド、GovCloud（US-East）で利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ec2-c8g-instances-additional-regions/) |
| AWS Transfer Family | SFTP コネクタが認証情報ローテーション中もファイル転送を継続可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/transfer-family-sftp-credential-rotation/) |
| Amazon EC2 | P6-B300 インスタンス（NVIDIA Blackwell Ultra GPU）がジャカルタリージョンで利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ec2-p6-b300-instances-available-asia-pacific-jakarta) |
| Amazon EC2 | P6-B200 インスタンス（NVIDIA Blackwell GPU）がハイデラバードリージョンで利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ec2-p6-b200-instances-available-asia-pacific-hyderabad) |
| Amazon ECS | Managed Daemons が非クリティカルデーモンに対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/ecs-managed-daemons-non-critical/) |

---

## まとめ

今回紹介したアップデートは、大きく3つのテーマに分けられます。第一に、ECSのデプロイメント機能強化（Early Success Criteria、非クリティカルデーモン）により、コンテナベースのマイクロサービス運用がより柔軟で堅牢になりました。第二に、Graviton5（M9g/C9g）インスタンスの東京リージョン展開により、日本国内のワークロードで高いコストパフォーマンスと低レイテンシを両立できる環境が整いました。第三に、P6シリーズGPUインスタンスのアジア太平洋リージョン拡大は、グローバルなAI/ML開発・運用を支える基盤として注目に値します。

全体として、運用の安定性向上、パフォーマンスとコスト最適化、グローバル展開の柔軟性といった、エンタープライズのニーズに応えるアップデートが並んでいます。SREやDevOpsチームは、これらの新機能を段階的に検証し、自組織のワークロードに最適な構成を見極めることで、継続的な改善サイクルを加速できるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)