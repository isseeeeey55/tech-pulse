---
title: "【New Relic】2026年3月末〜4月のアップデートまとめ"
date: 2026-04-12T20:22:11+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "mfa", "go", "apm", "alerts", "flex", "sap"]
categories: ["New Relic Updates"]
summary: "Infrastructure Agent 1.73.0でWindows向け最小権限サービスアカウント対応を追加、1.74.0でrevert（Bad release）。標準MFA機能の追加、Go APM簡単計装ツールのリリース、アラート逆引き集とSAP GUI外形監視など計6件を紹介します。"
---

![](/images/newrelic-updates-20260412/header.png)

## はじめに

前回のまとめ（3月26日公開）以降、New Relicからは計6件のアップデートが出ています。Infrastructure Agent v1.73.0 と v1.74.0 の2リリースは同じ機能（Windows向け最小権限サービスアカウント対応）をめぐる実装とrevertで一対になっており、アップグレード先の選択に注意が必要です。加えて、標準MFA機能の追加、Go APMの簡単計装ツールのリリース、運用ナレッジ系のQiita記事2本（アラート逆引き集、SAP GUI外形監視）を取り上げます。

## 注目アップデート深掘り

### Infrastructure Agent 1.73.0 → 1.74.0 — revert されたWindows最小権限サポート

![Infrastructure Agent 1.72.9 → 1.73.0 → 1.74.0 のタイムライン](/images/newrelic-updates-20260412/infra-agent-revert-timeline.png)

3月末に連続で2リリース出ましたが、ペアで見ると理解しやすいです。

- **v1.73.0（2026-03-27）**: Windows向けに「最小権限サービスアカウント」サポートを追加（[PR #2152](https://github.com/newrelic/infrastructure-agent/pull/2152)）。加えて `nri-winservices` v1.4.6、`nri-prometheus` v2.28.0 への依存更新
- **v1.74.0（2026-03-31）**: その最小権限サポートを丸ごと revert（[PR #2211](https://github.com/newrelic/infrastructure-agent/pull/2211)）。リリース名自体が `1.74.0 - Bad release ⚠️` となっており、メンテナ側も注意喚起している状態です

1.73.0 でWindows環境のエージェントを Local System より狭い権限で動かす道が開けたものの、本番での問題が見つかり 1.74.0 で巻き戻された、という流れです。SREとしての現実的な選択肢は次の通りです。

| 現在のバージョン | 推奨アクション |
|---|---|
| v1.72.9 以下 | 1.74.0 はスキップ。次の安定版リリースまで待機 |
| v1.73.0（Windows） | 最小権限設定で運用中なら機能利用を一時停止、または 1.72.9 へダウングレード検討 |
| v1.74.0 | revert 済みなので機能差は 1.72.9 相当。Bad release タグに注意して、差し支えなければ次版まで据え置き |

Windowsパッケージマネージャー（Chocolatey等）でバージョン固定する場合の例を載せておきます。

```powershell
# Chocolatey での pin 例
choco pin add -n=newrelic-infra --version=1.72.9
# 後で解除する場合
choco pin remove -n=newrelic-infra
```

Linux側も同じく pin しておくと意図しないアップグレードを防げます。

```bash
# RHEL / Amazon Linux
sudo yum versionlock add newrelic-infra-1.72.9

# Debian / Ubuntu
sudo apt-mark hold newrelic-infra
```

### New Relic 標準MFA — メールリンク方式の多要素認証

標準MFA機能が追加され、外部SSOやサードパーティのIdPを経由しなくても、New Relic単体でメールリンク方式の多要素認証を有効化できるようになりました。Qiitaの公式記事（[MarthaS 氏の解説](https://qiita.com/MarthaS/items/3c98510eefa567ee2bdf)）で設定手順と挙動がまとまっています。

挙動はシンプルで、ログイン試行時に登録メールアドレス宛に認証リンクを送信し、リンククリックで本人確認を完了します。TOTP（Google Authenticator 等）ではなく、メールリンクというのがポイントで、既に組織で使っている SSO と排他にせず「SSOが未導入のユーザーだけMFAを有効化する」といった段階的な運用が組みやすいです。

運用上の注意点:

- 緊急障害対応で New Relic にログインする際、メール受信が遅延すると初動が遅れる可能性があるので、オンコール担当のメールフローは事前に確認しておく
- 共用アカウントに対して MFA を有効化すると複数人が同じメール箱を参照できる必要がある。組織ポリシーと矛盾しないか確認を
- 既に SSO（Okta, Azure AD等）経由のログインを強制している環境では、標準MFAは追加保険として位置付ける

### Go easy instrumentation tool — diff ベースのAPM計装自動化

![Go easy instrumentation tool のワークフロー](/images/newrelic-updates-20260412/go-easy-instrumentation-flow.png)

Goはコンパイル言語でランタイムフックによる自動計装が難しく、New Relic Go Agent は「SDKとしてコードに手を入れる」方式でした。transaction の開始終了、`http.Handler` のラップ、外部呼び出しの segment 記録などを手書きで入れる手間が、導入のハードルになっていました。

今回リリースされた `go-easy-instrumentation` は、ソースコードを静的解析して計装ポイントを検出し、**diff ファイルを生成**します。生成された diff を確認してから `git apply` で反映できるので、「AIが勝手にコードを書き換える」系のツールと違って、レビュー可能な形で差分を渡してくれます。

基本的なワークフローは3ステップです。

```bash
# 1. ツールをインストール
go install github.com/newrelic/go-easy-instrumentation@latest

# 2. 計装 diff を生成（対象ディレクトリを指定）
go-easy-instrumentation instrument ./cmd/myapp > newrelic.diff

# 3. 差分を確認してから適用
git apply newrelic.diff
go mod tidy
```

SRE視点では、「Go製マイクロサービスを複数抱えているチームが初めて New Relic APM を入れるときの初期コスト」が下がるのが効きます。既に計装済みのサービスには使えませんが、PoC段階のサービスや、オブザーバビリティ後付けの対象になっているレガシーGoコードへの導入で真価を発揮します。

## ナレッジ系アップデート

### New Relic アラート逆引き集 — 症状別トラブルシュート

Qiita の [knr2636 氏の記事](https://qiita.com/knr2636/items/aebf453d3c5ba09fa615) は、New Relic Alerts で実際に遭遇しがちな症状を「鳴らない」「止まらない」「遅延する」の3カテゴリに分けて、公式ブログへのリンク集として整理した参考ガイドです。

取り上げられている主なトピック:

- **Streaming method の違い**（Event flow と Event timer の使い分け、レイテンシ特性）
- **鳴らないアラートの原因**: NrAiSignal の確認、`for at least` と `at least once in` の挙動差
- **通知遅延の診断**: Streaming method ごとの発火遅延要因
- **Signal lost の誤検知**、自動クローズの失敗
- **通知内容のカスタマイズ**、除外設定の削除手順、メンテナンスウィンドウでの通知抑制

アラート設定でハマった経験があるSREなら、「あの症状はこれか」と気づける項目が並んでいます。チームの新人向けトレーニング資料としても使いやすい構成です。

### SAP GUI をユーザー視点で監視する — Panaya + New Relic Flex

Qiita の [naka34 氏の記事](https://qiita.com/naka34/items/b9101ed8da3154e8001d) は、デスクトップアプリである SAP GUI を外形監視する実装例です。SAP のようなクライアント/サーバー型アプリでは、従来の Infrastructure 監視や Synthetic（HTTP）では「ユーザーが実際の画面で体感しているレスポンス」を捉えきれません。

> **New Relic Flex とは？**
> Infrastructure Agent の拡張機構で、任意のコマンド実行結果やJSON/HTTP APIレスポンスをメトリクス・イベントとして New Relic に送信できる仕組みです。公式Integration がない独自システムを監視する際の定番アプローチになっています。

記事の構成は次の流れです。

1. **Panaya**（テスト自動化SaaS）で SAP GUI の操作シナリオをスクリプト化（ログイン→取引画面→特定操作）
2. Panaya の Test Automation API をシェルスクリプト経由で定期実行
3. 実行結果（成功/失敗、所要時間）を **New Relic Flex** で取り込み
4. Data Explorer / ダッシュボードで SLI として可視化

Synthetics でカバーできないクライアントアプリの外形監視を、既存の Flex + 外部テスト自動化サービスの組み合わせで成立させている点が参考になります。SLO 設計の文脈でも、ユーザー操作レベルの指標を拾う方法として引き出しを増やせる内容です。

## SRE視点での活用ポイント

今回6件の中で、運用優先度が高いのは Infrastructure Agent のバージョン選定です。Windows 環境で 1.73.0 に既にアップグレードして最小権限モードを使い始めていた場合、その機能は 1.74.0 以降では削除されているため、運用ドキュメントや Playbook の更新が要ります。Linux 環境では両バージョンとも実質的な機能差は小さいので、次の安定版を待つ判断が取りやすいです。

標準MFAは「SSO未導入の小さなチームで、とりあえずパスワード単独ログインから脱出したい」ケースにはまる機能です。逆に既に Okta や Azure AD で SSO を敷いている環境では、アカウント個別のオプションとして見ておけば十分でしょう。

Go easy instrumentation は、いま計装済みサービスには不要ですが、「Goで新しく書いたサービスに後から APM を足す」タイミングで選択肢に入れておくと工数を削れます。差分がファイルで出る設計なので、レビュー付きの導入フローに組み込みやすいのが利点です。

アラート逆引き集と SAP GUI 監視は、どちらも「困ったときに参照する引き出し」としてブックマークしておくタイプのコンテンツです。特にアラートの Streaming method まわりは、設計時の選択がその後の発火遅延に効いてくるので、新規アラート追加のたびに参照する価値があります。

## 全アップデート一覧

| カテゴリ | バージョン / 機能名 | 概要 |
|---------|------------------|------|
| Infrastructure Agent | 1.73.0 | Windows向け最小権限サービスアカウント対応を追加（PR #2152）、依存更新 |
| Infrastructure Agent | 1.74.0 ⚠️ Bad release | 1.73.0 の最小権限機能を revert（PR #2211） |
| Security / Auth | 標準MFA機能 | メールリンク方式の多要素認証を単体で有効化可能に |
| SDK / Tools | Go easy instrumentation tool | Go APM 計装を diff + `git apply` ベースで自動化 |
| Alerts / Knowledge | アラート逆引き集（Qiita） | 鳴らない/止まらない/遅延するの症状別トラブルシュートガイド |
| Monitoring / Flex | SAP GUI 外形監視（Qiita） | Panaya + New Relic Flex でデスクトップアプリを可視化 |

## まとめ

Infrastructure Agent 1.73.0/1.74.0 の一対リリースは、Windows で最小権限運用を狙っていたチームにとっては「一歩進んで半歩戻る」結果になりました。次の安定版が出るまで、現行バージョンを pin しておくのが無難です。標準MFAは SSO 未導入の組織に効く小粒な追加、Go easy instrumentation は Goアプリへの APM 導入コストを下げるツールで、どちらも使える場面が明確に決まっています。運用ナレッジ側は、アラート設定の引き出しを増やすのに役立つ2本でした。
