---
title: "【New Relic】Infrastructure Agent 1.73.1 リリース"
date: 2026-04-14T08:00:43+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "docker", "windows", "nri-docker", "nri-flex"]
categories: ["New Relic Updates"]
summary: "Infrastructure Agent 1.73.1 がリリース。Docker base image の v28 → v29 更新、Windows 向け Docker image ビルド対応、nri-docker / nri-flex 更新など、5 つの変更点を解説します。"
---

![](/images/newrelic-updates-20260414/header.png)

## はじめに

Infrastructure Agent の新バージョン **1.73.1** が 2026-04-13 にリリースされました。先日取り上げた 1.73.0 / 1.74.0 のあとに続くパッチで、中身は 5 つの変更を含んでいます。Docker base image のメジャーアップデート（v28 → v29）、Windows 向け Docker image のビルド対応、`nri-docker` / `nri-flex` の更新、リリースワークフロー改善、リポジトリへの `claude files` 追加という内訳です。

なお、「1.74.0 の Bad release を受けたロールバック」ではない点に注意してください。1.73.0 で入った Windows 向け最小権限サービスアカウント対応を 1.74.0 が revert したあと、別のパッチとして 1.73.x 系の続編となるバージョンが 1.73.1 です。

## 注目アップデート深掘り

### 1.72.9 → 1.73.0 → 1.74.0 → 1.73.1 のリリース系譜

![Infrastructure Agent バージョン系譜](/images/newrelic-updates-20260414/release-lineage.png)

1.73.0 / 1.74.0 / 1.73.1 とバージョン番号が前後して混乱しやすいので、ここで一度並べ直しておきます。

- **1.72.9**（2026-03-23）: 安定版。`nr-control` メタデータサービス統合、Go 1.25.8、gRPC 1.79.3
- **1.73.0**（2026-03-27）: Windows 向け最小権限サービスアカウント対応を追加（PR #2152）
- **1.74.0**（2026-03-31）: **Bad release**。1.73.0 の最小権限対応を revert（PR #2211）
- **1.73.1**（2026-04-13）: **今回のリリース**。1.73.0 の続きとして Docker v29 対応、Windows Docker image、`nri-docker` / `nri-flex` 更新などを追加

1.73.1 は 1.73.0 をベースにした別系統のパッチで、1.74.0 の Bad release を直す類のものではありません。Windows 上で最小権限モードを運用していた方は、1.73.0 → 1.73.1 に上げても最小権限機能は引き続き含まれます（1.74.0 で revert された機能は 1.73.x 系では生きている前提）。判断時はリリースノートとリポジトリの git ログを合わせて確認してください。

### 1.73.1 の変更点 — 5 つのポイント

![1.73.1 Changes](/images/newrelic-updates-20260414/changes-1731.png)

公式リリースノートに挙げられている変更は次の 5 件です（PR 番号は [releases/tag/1.73.1](https://github.com/newrelic/infrastructure-agent/releases/tag/1.73.1) を参照）。

**1. `nri-docker` / `nri-flex` の更新、Docker base image を v28 → v29 に引き上げ**（PR #2220）

Infrastructure Agent がバンドルしている `nri-docker`（Docker 統合）と `nri-flex`（カスタム統合フレームワーク）のバージョンアップ、あわせてエージェント自体の Docker base image が v28 系から v29 系に切り替わりました。コンテナで動かしている環境では、image pull 時に v29 がベースになることを念頭に置いてください。

> **nri-docker / nri-flex とは？**
> Infrastructure Agent に同梱される on-host integration 群の一部です。`nri-docker` は Docker デーモンからコンテナ単位のメトリクスを収集し、`nri-flex` は任意のコマンド実行結果や HTTP/JSON レスポンスをカスタムメトリクスとして取り込む汎用フレームワークです。公式 integration がない内製システムの監視で使われることが多いです。

**2. Windows 向け Infrastructure Agent Docker image のビルド対応**（PR #2202）

これまで Linux ベースで提供されていた Infrastructure Agent の Docker image に、Windows コンテナ対応のビルドが加わりました。Windows Server ホスト上でコンテナ化された Infrastructure Agent を動かす構成が素直に組めるようになります。Windows Server Core / Nano Server ベースの image を ECS Windows クラスタや EKS Windows node group で運用しているチームに効く変更です。

**3. Windows image release workflow の更新**（PR #2213）

CI/CD 側の改善で、Windows image の自動リリースフローが整備されました。利用者側から見える変化は「新しい Windows image が遅延なく公開されるようになる」程度ですが、2.の Windows image 対応とセットで入っています。

**4. `claude files initial commit`**（PR #2216）

リポジトリに Claude Code 関連のファイル（`.claude/` 配下）が初めてコミットされました。Infrastructure Agent の開発チームが Claude Code を開発支援に取り入れ始めた兆しです。Agent のランタイム挙動に影響する変更ではありません。

**5. Changelog まとめ**

以上 4 点が利用者に影響する実体で、5 番目は 4 の「開発体制改善系」の注記です。全体としてランタイム挙動を変える系の変更は `nri-docker` / `nri-flex` / Docker base image 更新の 1 点で、残りは Windows image のパッケージング整備が主です。

## SRE視点での活用ポイント

**Linux / ECS / EKS で Infrastructure Agent コンテナを使っている場合**、Docker base image が v29 に上がる影響が最初に効きます。自前で Infrastructure Agent image を FROM で継承して拡張しているチームは、継承先の Dockerfile 側で古い v28 ベースのライブラリ互換を前提にしていないか確認してください。カスタム integration バイナリを同梱しているケースでは、OS ライブラリのバージョン差を踏みやすいポイントです。

**Windows Server で Infrastructure Agent を動かしている場合**、今回のリリースで初めて公式 Windows Docker image の継続ビルドが約束されました。これまで MSI インストーラで OS 直接インストールしていた環境でも、IIS や SQL Server と並べてコンテナ化する選択肢が取りやすくなります。

**`nri-flex` でカスタムメトリクスを取っている環境**は、リリースノートで `nri-flex` のバージョン差分を追って、既存の config YAML が新バージョンと互換か確認しておくのが無難です。`nri-flex` は YAML スキーマが割と変動するので、破壊的変更はないはずですがリグレッションテストの対象に入れておくと安全です。

**1.73.0 で Windows 最小権限モードを運用中のチーム**は、1.73.1 へのアップグレードはそのまま進めて問題ありません。最小権限対応は 1.73.0 で入り、1.74.0 でだけ revert されました。1.73.1 は 1.73.0 の続きなので機能は維持されています。ただし、本番投入前にステージングで 1 台だけ先行上げて、カスタム config と組み合わせた挙動を確認してください。

## 全アップデート一覧

| カテゴリ | 項目 | 概要 |
|---------|------|------|
| [Infrastructure Agent 1.73.1](https://github.com/newrelic/infrastructure-agent/releases/tag/1.73.1) | `nri-docker` / `nri-flex` / Docker v28→v29 | on-host integration 更新とエージェント base image 引き上げ |
| Infrastructure Agent 1.73.1 | Windows 向け Docker image ビルド | Windows コンテナ上で動かす Infrastructure Agent image を公式提供 |
| Infrastructure Agent 1.73.1 | Windows image release workflow 更新 | Windows image の自動リリースパイプライン整備 |
| Infrastructure Agent 1.73.1 | `claude files initial commit` | リポジトリに `.claude/` ファイル追加。Agent 挙動には非影響 |
| Infrastructure Agent 1.73.1 | リリース系譜の整理 | 1.73.0 → 1.74.0(revert) → 1.73.1 の関係を本文で解説 |

## まとめ

1.73.1 は Infrastructure Agent の Docker base image メジャー更新（v28 → v29）と Windows コンテナ対応が中心で、ランタイムの挙動はほぼ変わりません。1.74.0 の Bad release の後、「次の安定版はいつ？」と待っていたチームにとっては、1.73.0 ベースの素直な続編として素直に上げやすいパッチです。コンテナで動かしている環境では base image の差分、Windows 環境では新しい Docker image 選択肢、という 2 点を押さえておけば十分です。
