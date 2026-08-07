---
title: "【New Relic】2026/08/08 のアップデートまとめ"
date: 2026-08-08T08:00:56+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "security", "oci", "aws", "multicloud", "monitoring"]
categories: ["New Relic Updates"]
summary: "2026/08/08 のNew Relicアップデートまとめ"
---

![](/images/newrelic-updates-20260808/header.png)

# New Relic 2026年8月8日アップデート情報

## はじめに

2026年8月7日、New Relic Infrastructure Agent の新バージョン 1.79.0 がリリースされました。取り上げる対象は1リリースですが、リリース本文には 10 件の変更が含まれており、セキュリティ修正と機能追加の両方を含む内容になっています。主な内容は、パストラバーサル起因の RCE 脆弱性の修正、Trivy スキャンで検出された依存関係の CVE 対応、組み込み OHI（nri-docker / nri-flex / nri-prometheus）の CVE 対応バージョン更新、統合ディレクトリの既定スキャンを無効化する `disable_plugin_default_dir_scan` オプションの追加、OCI タグサポート（AWS タグ対応の Phase 1・2）、Agent Control が使用する環境変数の公開などです。特に脆弱性修正は複数の CVE を含むため、アップグレード計画の優先度は高くなります。

## 注目アップデート深掘り

### Infrastructure Agent 1.79.0 のセキュリティ強化と OCI タグサポート

今回の Infrastructure Agent 1.79.0 は、セキュリティと運用効率の両面で重要なアップデートです。

**セキュリティ面での重要性**

まず最も重要なのが、パストラバーサル脆弱性の修正（PR #2292）です。修正内容は「Unauthenticated TCP Integration Ingest Allows Root Arbitrary File Write via Path Traversal」と説明されており、未認証の TCP 経由の integration ingest から、パストラバーサルによって root 権限で任意のファイルを書き込める状態だった、というものです。任意ファイル書き込みが root 権限で成立する以上、影響は設定ファイルやサービス定義の改変を通じた RCE に至り得ます。エージェントを外部から到達可能なネットワークに置いている環境では、優先的な適用対象です。

依存関係側でも複数の CVE が解消されています。Trivy スキャンで検出された分（PR #2301）として CVE-2026-56852（`golang.org/x/text`）、CVE-2026-46600（`golang.org/x/net`）、および開発ツール配下の CVE-2026-39824（`golang.org/x/sys`）、GHSA-xmrv-pmrh-hhx2（`aws-sdk-go-v2`）が対応されました。加えて組み込み OHI のバージョンが引き上げられ（PR #2302）、nri-docker v2.8.2、nri-flex v1.18.10、nri-prometheus v2.30.2 でそれぞれ同系統の CVE が解消されています。なお gRPC の 1.79.3 → 1.82.1 更新はリリース本文上 `chore(deps)` 分類で、セキュリティに関する記載は付いていません。

**統合ディレクトリのスキャン制御**

新たに導入された `disable_plugin_default_dir_scan` オプション（環境変数 `NRIA_DISABLE_PLUGIN_DEFAULT_DIR_SCAN`、PR #2290）は、統合（integration）の**既定の配置場所**をスキャン対象から外す設定です。有効化すると、エージェントは明示的に設定された `custom_plugin_installation_dir`（バイナリ / v3 定義）と `plugin_dir`（設定）の 2 箇所からのみ統合をロードします。

このオプションの目的は、PR の説明にあるとおり、スタンドアロンインストールの残骸や他ユーザーが書き込み可能な場所に残った、古い・競合する統合が読み込まれるのを避けることにあります。既定値は `false` で従来どおりの挙動が維持されるため、後方互換性は保たれます。またリリースには、Agent Control 管理下のエージェントに対してこの設定を既定で有効化する変更（PR #2300）も含まれています。なお PR 上はこのオプションは内部利用向け（internal-only）と位置づけられています。

**マルチクラウド環境でのタグ管理**

OCI（Oracle Cloud Infrastructure）タグのサポートが追加されました（PR #2295）。リリース本文の表現は「AWS タグに合わせる形で OCI タグサポートを追加（Phase 1 + Phase 2）」であり、AWS で提供されているタグ取得の挙動を OCI 側にも揃えるものです。AWS と OCI を併用する環境では、両クラウドのリソースを同じタグの枠組みで扱えるようになります。具体的にどの属性がどう付与されるかはリリース本文では詳述されていないため、実際の適用時は取得されるタグ属性を実データで確認してください。

**Agent Control が使用する環境変数の公開**

Agent Control（AC）が使用する環境変数が公開されました（PR #2293）。これは AC のエージェントタイプ定義で参照している環境変数を公開扱いにするもので、New Relic 公式ドキュメント側の更新（docs-website PR #25087）を伴っています。AC 経由でエージェントを管理している環境では、どの環境変数が設定に効いているかをドキュメントで確認できるようになります。

## SRE視点での活用ポイント

**脆弱性対応の優先度づけ**

今回のリリースで最も優先度が高いのは PR #2292 の修正です。未認証の TCP integration ingest から root 権限で任意ファイル書き込みが可能という性質上、エージェントの ingest ポートがどこから到達可能かが被害範囲を決めます。まず自環境で当該ポートの到達範囲（セキュリティグループ、ホストファイアウォール、コンテナのネットワーク設定）を棚卸しし、外部から到達可能なホストを優先してアップグレード対象に並べるのが妥当な進め方です。

依存関係側の CVE は `golang.org/x/text` と `golang.org/x/net` が中心で、エージェント本体と組み込み OHI の双方に及びます。CVE スキャンを CI やコンテナレジストリで回している環境では、1.79.0 への更新でこれらの検出が解消されるかを再スキャンで確認しておくと、対応漏れの判断がしやすくなります。

**統合ディレクトリのスキャン制御を検討する場面**

`disable_plugin_default_dir_scan` は起動時間やリソース使用量の改善を目的とした設定ではなく、ロード対象の統合を明示的に設定した 2 ディレクトリに限定するためのものです。スタンドアロンインストールから Agent Control 管理へ移行した、あるいは複数の手段でエージェントを導入した履歴があるホストでは、意図しない古い統合が残っていないかを確認する価値があります。起動時には統合の管理モードが INFO レベルでログ出力されるため、まずはそのログでどのモードで動いているかを確認するところから始められます。

**アップグレード時の注意点**

Agent Control 向けアーティファクトから nri-flex が除外されました（PR #2291）。PR の説明によれば、これは nri-flex を独立してインストールできる OHI として提供する方針への移行によるもので、infrastructure-agent のアーティファクトに同梱する必要がなくなったためです。Agent Control 経由で nri-flex を利用している環境では、アップグレード後に flex の導入経路を別途確保する必要があるかを確認してください。スタンドアロンインストールへの影響についてはリリース本文に記載がないため、実環境での確認が必要です。

同じく Agent Control 管理下のエージェントでは `NRIA_DISABLE_PLUGIN_DEFAULT_DIR_SCAN` が既定で有効になります（PR #2300）。既定ディレクトリに統合を置いている場合は挙動が変わるため、アップグレード前に統合の配置場所を確認しておくと安全です。

## 全アップデート一覧

Infrastructure Agent 1.79.0（2026年8月7日リリース）に含まれる変更は以下の 10 件です。

| カテゴリ | 対象 | 概要 | リンク |
|---------|------|------|--------|
| security | パストラバーサル | 未認証の TCP integration ingest から root 権限で任意ファイル書き込みが可能だった問題を修正 | [PR #2292](https://github.com/newrelic/infrastructure-agent/pull/2292) |
| fix | Trivy 検出の依存関係 | CVE-2026-56852（x/text）、CVE-2026-46600（x/net）、CVE-2026-39824（x/sys、開発ツール）、GHSA-xmrv-pmrh-hhx2（aws-sdk-go-v2、開発ツール）を解消 | [PR #2301](https://github.com/newrelic/infrastructure-agent/pull/2301) |
| chore | 組み込み OHI | nri-docker v2.8.2 / nri-flex v1.18.10 / nri-prometheus v2.30.2 へ更新し CVE を解消 | [PR #2302](https://github.com/newrelic/infrastructure-agent/pull/2302) |
| chore(deps) | gRPC | `google.golang.org/grpc` を 1.79.3 から 1.82.1 へ更新 | [PR #2296](https://github.com/newrelic/infrastructure-agent/pull/2296) |
| feat | 統合ディレクトリのスキャン制御 | `disable_plugin_default_dir_scan`（env: `NRIA_DISABLE_PLUGIN_DEFAULT_DIR_SCAN`）で既定の統合配置場所のスキャンを無効化。既定値は `false` | [PR #2290](https://github.com/newrelic/infrastructure-agent/pull/2290) |
| ci | AC 管理エージェントの既定値 | Agent Control 管理下のエージェントで `NRIA_DISABLE_PLUGIN_DEFAULT_DIR_SCAN` を既定で有効化 | [PR #2300](https://github.com/newrelic/infrastructure-agent/pull/2300) |
| feat | OCI タグサポート | AWS タグに合わせる形で OCI タグのサポートを追加（Phase 1 + Phase 2） | [PR #2295](https://github.com/newrelic/infrastructure-agent/pull/2295) |
| feat | AC の環境変数公開 | Agent Control が使用する環境変数を公開扱いに変更（公式ドキュメントも更新） | [PR #2293](https://github.com/newrelic/infrastructure-agent/pull/2293) |
| feat | nri-flex の分離 | Agent Control 向けアーティファクトから nri-flex を除外（独立した OHI として提供する方針へ） | [PR #2291](https://github.com/newrelic/infrastructure-agent/pull/2291) |
| security | CI ワークフロー | GitHub Actions ワークフローに permissions を追加 | [PR #2232](https://github.com/newrelic/infrastructure-agent/pull/2232) |

リリース全体: [Infrastructure Agent 1.79.0](https://github.com/newrelic/infrastructure-agent/releases/tag/1.79.0)

## まとめ

Infrastructure Agent 1.79.0 は、セキュリティ修正・統合ロードの制御・マルチクラウド対応という3方向の変更を含むリリースです。中心はやはり PR #2292 のパストラバーサル修正で、未認証の TCP integration ingest から root 権限で任意ファイル書き込みが成立していたという内容である以上、適用の優先度は高くなります。加えて、エージェント本体と組み込み OHI の双方で `golang.org/x/text` / `golang.org/x/net` 系の CVE が解消されており、脆弱性スキャンを運用に組み込んでいる環境では検出結果にも反映されます。

運用面では、`disable_plugin_default_dir_scan` によって統合のロード元を明示した 2 ディレクトリに限定できるようになった点と、Agent Control 管理下でこれが既定有効になる点が、挙動の変わりうる箇所です。あわせて Agent Control 向けアーティファクトからの nri-flex 除外も、flex を使っている環境では導入経路の確認が必要になります。OCI タグサポートについては、AWS タグの挙動に揃える Phase 1・2 が入った段階であり、実際に取得される属性は実環境で確認するのが確実です。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)