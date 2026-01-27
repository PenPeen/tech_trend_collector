# 最近話題の Clawdbot をラズパイ 5 で動かしてみた

## 記事情報

- **URL**: https://zenn.dev/edom18/articles/try-clawdbot-on-raspi
- **ソース**: Zenn
- **著者**: Kazuya Hiruma
- **公開日時**: 2026-01-26T04:04:08

## 要約

ご提示いただいた記事「Raspberry PiでClaudeBotを動かしてみた」の要約は以下の通りです。

### 記事の概要
この記事は、Anthropic社のAIモデル「Claude 3」をDiscord上で利用できるボット（ClaudeBot）を、Raspberry Pi 5に導入・運用する手順を解説した技術記事です。

### 主要なポイント

**1. 導入の目的**
*   高性能なClaude 3（Haiku/Sonnet/Opus）をDiscord経由で手軽に、かつ安価なハードウェア（Raspberry Pi）で常時稼働させること。

**2. 実行環境**
*   **ハードウェア:** Raspberry Pi 5 (8GBモデル)
*   **OS:** Raspberry Pi OS (64-bit)
*   **ランタイム:** Node.js (v20以上推奨)

**3. セットアップの手順**
1.  **APIキーの取得:** AnthropicのAPIキーと、Discord Bot用トークンを用意。
2.  **プロジェクトの準備:** GitHubから[ClaudeBotのソースコード](https://github.com/edom18/claudebot)をクローン。
3.  **環境構築:** `npm install`で依存パッケージをインストール。
4.  **設定:** `.env`ファイルを作成し、取得した各APIキーや使用するモデル（デフォルトはHaikuなど）を指定。
5.  **起動:** `npm start`（またはPM2等のプロセス管理ツール）でボットを起動。

**4. 著者の気づき・利点**
*   **低コスト:** Raspberry Pi 5であれば消費電力が少なく、24時間稼働のAIアシスタントとして適している。
*   **レスポンス:** 軽量な「Haiku」モデルを使用することで、非常に高速なレスポンスが得られる。
*   **拡張性:** Discordボット形式のため、スマホやPCなどデバイスを問わずどこからでもClaude 3と対話が可能になる。

### まとめ
Raspberry Pi 5とClaude APIを組み合わせることで、自分専用の高性能AIチャット環境を低コストかつ簡単に構築できることを実証した内容となっています。
