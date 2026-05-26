---
title: "【New Relic】2026/05/26 のアップデートまとめ"
date: 2026-05-26T08:01:09+09:00
draft: false
tags: ["newrelic", "sre", "ebpf", "monitoring", "observability", "devops", "sli", "slo"]
categories: ["New Relic Updates"]
summary: "2026/05/26 のNew Relicアップデートまとめ"
---

![](/images/newrelic-updates-20260526/header.png)

## はじめに

2026年5月26日のNew Relicアップデートとして、5月25日に公開された技術解説記事2件を取り上げる。今回は製品リリースの告知ではなく、eBPFを使ったオブザーバビリティと、従来型の監視からサービスレベル中心の運用へ移行する考え方がテーマだ。

1つ目の記事では、New Relic eBPFを含むeBPFベースのオブザーバビリティが、アプリケーションコードの変更や言語別エージェントの導入なしに、Webトランザクションや外部サービス呼び出しの状況を把握する入口になり得ることが説明されている。2つ目の記事では、死活監視やリソース閾値だけに頼る運用から、ユーザー価値やビジネス影響を起点にした監視設計へ移る必要性が語られている。

## 注目アップデート深掘り

### eBPFによるオブザーバビリティの実現

eBPF（extended Berkeley Packet Filter）を活用したオブザーバビリティ技術の解説記事が公開された。記事では、OSが把握している通信や処理の情報をeBPFプログラムで収集し、ユーザー空間のエージェント経由でNew Relicのようなオブザーバビリティプラットフォームへ送る仕組みが説明されている。

> **Note:** eBPFはLinuxカーネル内で安全にプログラムを実行できる仕組みで、システムコールやネットワークパケット、ファイルI/Oなどのイベントを低オーバーヘッドで捕捉できます。

**なぜこのアップデートが重要なのか**

従来、アプリケーション単位の監視を深めるには、言語別APMエージェントの導入やアプリケーション側の設定変更が必要になることが多かった。これは、複数言語・レガシーアプリ・Kubernetes環境が混在する組織では導入のハードルになりやすい。

New Relic eBPFは、言語別エージェントなしでWebトランザクションや外部サービス呼び出しを把握する選択肢を提供する。公式ドキュメントでも、KubernetesやLinuxホスト向けにeBPF Agentを導入でき、コード変更なしでアプリケーションパフォーマンスの可視性を得られると説明されている。一方で、アプリケーション内部の詳細分析やエラー解析まで通常のAPMと同等に置き換えるものではないため、まず全体像の把握やAPM導入前の足場として捉えるのが現実的だ。

**SREの日常業務への具体的な影響**

SRE視点では、まず「どのサービスのどのトランザクションが遅いのか」「外部APIやデータベースとのやり取りでどこが詰まっているのか」を素早く把握する用途に向いている。特に、言語別エージェントの導入が難しいレガシーシステムや、複数チームが管理するKubernetes環境では、監視導入の初速を上げられる。

ただし、導入可否はLinuxカーネル、Kubernetes環境、対応データベース、必要な権限やエンドポイント接続に依存する。AWSではEKSのような対応Kubernetes環境で検討しやすい一方、Lambda関数のようにカーネルレベルのエージェントを配置できない実行環境にはそのまま適用できない。既存のInfrastructure AgentやAPM Agentを単純に置き換えるのではなく、対象ワークロードごとに役割を分けて設計するのが安全だ。

### モダンなシステム運用における監視の見直し

従来の死活監視中心の運用から、ビジネス成果と直結した監視体制への転換の必要性を説く解説記事も公開された。クラウド化・マイクロサービス化により複雑化したシステムでは、単なる稼働状況の把握だけでは不十分であり、ユーザー体験やビジネス影響に基づいた監視・アラート設計が重要になる、という内容だ。

**なぜこのアップデートが重要なのか**

多くの組織では、CPU使用率やディスク容量といった技術的な閾値ベースのアラートが増え、真に対応が必要なインシデントとノイズの区別がつきにくくなる。この記事は、監視の目的を「システムが動いているか」から「ユーザーに価値が届いているか」へ広げることの重要性を提言している。

この方向性は、New RelicのService Level Managementとも相性がよい。公式ドキュメントでは、SLI/SLOを定義し、エラーバジェットの消費やバーンレートに基づいたアラートを設定できる。単純なリソース閾値ではなく、サービスレベルの悪化を起点に通知を絞ることで、対応すべき問題に集中しやすくなる。

**SRE視点での具体的な影響**

SLI（Service Level Indicator）とSLO（Service Level Objective）の設計を監視戦略の中心に据えると、アラートの見直しが進めやすい。例えば、従来は「CPUが80%を超えたら通知」としていたものを、APIの成功率、レスポンスタイム、主要トランザクションのエラー率など、ユーザー体験に近い指標へ寄せられる。

AWS環境でも、ALB、ECS、EKS、RDS、LambdaなどのメトリクスをNew Relic側のAPMデータやカスタムイベントと組み合わせれば、サービス単位の健全性を見やすくなる。Auto ScalingやELBヘルスチェックそのものをビジネス指標化するわけではないが、ユーザー影響を測るSLIとインフラ指標を同じダッシュボードで見られると、障害対応時の判断材料が増える。

## SRE視点での活用ポイント

### 監視・アラート・ダッシュボードの改善

eBPFベースの監視は、言語別APMエージェントを入れにくい環境で、サービス間通信やWebトランザクションの状況をつかむための入口になる。New Relic eBPF AgentやPixieのような仕組みを使うと、Kubernetesワークロードのサービスレベルメトリクスやリクエスト情報を自動収集しやすくなる。

一方、アラート設計は技術指標だけで完結させず、SLI/SLOに寄せたい。New RelicのService Level Managementでは、SLOの達成状況、エラーバジェット消費、バーンレートをもとにアラートを作れるため、ユーザー影響が大きい問題を優先して通知する設計に移行しやすい。

### AWS環境でのNew Relicエージェント運用における影響

AWSでは、まずEKSやLinuxホストのようにeBPF Agentの要件を満たせる環境を候補にするのがよい。対応カーネル、Kubernetes要件、必要なLinuxヘッダー、送信先エンドポイントへの疎通などを事前に確認する必要がある。

ECS、EC2、Lambdaなどのワークロードでは、既存のAPM Agent、Infrastructure Agent、Lambda Extension、CloudWatch連携も引き続き選択肢になる。eBPFは「すべてのAWS実行環境を同じ方法で計装できる魔法」ではないため、ワークロードごとの制約を見ながら、New Relicに集約したいテレメトリを整理するのが重要だ。

### すぐに試せるTips

- New Relic eBPF Agentの互換性要件を確認し、検証用のLinuxホストまたはKubernetesクラスターで導入可否を確認する
- eBPFで見えるトランザクションや外部サービス呼び出しと、既存APMで見えている情報を比較する
- 既存のアラートポリシーを棚卸しし、CPU・メモリ・ディスク容量だけでなく、エラー率、レスポンスタイム、トランザクション成功率などのユーザー体験指標が含まれているか確認する
- New Relic Service Levelsで、主要APIや重要なユーザージャーニーに対するSLI/SLOを小さく作ってみる

### アップグレード時の注意点やリスク

eBPF Agentは、LinuxカーネルやKubernetes環境の条件に依存する。古いカーネル、制限の強いホスト、権限を絞ったKubernetesクラスターでは利用できない、または追加準備が必要になる可能性があるため、公式の互換性要件を確認したい。

監視戦略の見直しも、一度にすべてのアラートを置き換えないほうがよい。既存のリソース監視を残しながら、SLI/SLOベースのアラートを並行運用し、通知精度や見逃しリスクを確認してから段階的に切り替えるのが安全だ。

## 全アップデート一覧

| カテゴリ | 概要 | リンク |
|---------|------|--------|
| 技術解説 | eBPFによるオブザーバビリティ：New Relic eBPFを含むeBPFベースの可視化の考え方 | [記事リンク](https://qiita.com/ashimada83/items/28b7d4cdd46d2717d48f) |
| 技術解説 | モダンなシステム運用への道標：死活監視からユーザー価値起点の監視へ移行する考え方 | [記事リンク](https://qiita.com/h_shinonome/items/6cec52fd07de55661160) |
| 公式ドキュメント | New Relic eBPF Agentの導入と互換性要件 | [eBPF Kubernetes](https://docs.newrelic.com/docs/kubernetes-pixie/kubernetes-integration/installation/eapm) / [Requirements](https://docs.newrelic.com/docs/ebpf/requirements/) |
| 公式ドキュメント | Service Level ManagementとSLOベースのアラート設計 | [Service Levels](https://docs.newrelic.com/docs/service-level-management/intro-slm/) / [Alerting](https://docs.newrelic.com/docs/service-level-management/alerts-slm/) |

## まとめ

今回の更新は、個別機能のGA告知というより、New Relicを使った監視設計をどう進めるかを考えるための技術解説だ。

eBPFは、言語別エージェントを入れにくい環境でもサービスのふるまいを把握するための選択肢になる。ただし、導入にはLinuxカーネルやKubernetes環境の条件があり、通常のAPMやInfrastructure Agentを完全に置き換えるものではない。まずは検証環境で、見えるデータと見えないデータを確認するのがよい。

監視設計については、CPUやメモリの閾値だけでなく、SLI/SLOやエラーバジェットを中心に据える流れがより重要になる。New Relic Service Level Managementを使えば、ユーザー体験に近い指標をもとにアラートを設計できる。SREとしては、既存アラートの棚卸しと、主要サービスの小さなSLO定義から始めたい。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)
