# GitHub CopilotでClaude Code（とCodex CLI）が使えるようになるぞ！

## 記事情報

- **URL**: https://zenn.dev/nuits_jp/articles/2026-01-28-claude-code-on-agent-hq
- **ソース**: Zenn
- **著者**: Atsushi Nakamura
- **公開日時**: 2026-01-28T03:17:07

## 要約

ご提示いただいた記事「Claude CodeをAgent HQで動かしてみた」の要約です。

### 記事の概要
この記事は、Anthropic社がリリースした高性能なCLI開発エージェント**「Claude Code」**を、ブラウザベースの実行環境である**「Agent HQ」**上で動作させる方法とそのメリットを解説したものです。

---

### 主なポイント

#### 1. Claude Codeとは
*   Anthropicが公開した、ターミナルで動作するAI開発エージェント。
*   コードの理解、編集、テストの実行、Git操作などを高い精度で自動化できる。
*   通常はローカル環境のターミナルにインストールして使用する。

#### 2. Agent HQとは
*   ブラウザから利用できる、エージェント実行用のWebプラットフォーム。
*   MCP（Model Context Protocol）サーバーの管理や、セキュアなサンドボックス環境でのコード実行が可能。
*   Dockerコンテナをベースとした環境を提供している。

#### 3. 実装の背景と手順
*   **背景:** Claude Codeは強力だが、ローカル環境を汚したくない、あるいは実行環境をクラウド（Web）上で一元管理したいというニーズがある。
*   **手順:**
    1.  Agent HQのプロジェクトを作成（Dockerイメージをベースに構築）。
    2.  `npm install -g @anthropic-ai/claude-code` を実行してインストール。
    3.  `claude` コマンドを起動し、Anthropicの認証を行う。

#### 4. Agent HQで動かすメリット
*   **環境のポータビリティ:** ブラウザさえあれば、どのPCからでも同じ開発コンテキストでClaude Codeを継続利用できる。
*   **MCPとの親和性:** Agent HQが持つMCP管理機能と組み合わせることで、Claude Codeの能力をさらに拡張できる可能性がある。
*   **安全な実行環境:** ホストマシンから隔離されたコンテナ内でAIにコードを操作させることができる。

### 結論
Claude CodeをAgent
