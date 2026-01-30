# Figma x Claudeでフルでコーディングしてみた

## 記事情報

- **URL**: https://zenn.dev/hamworks/articles/0d57ca09e695c5
- **ソース**: Zenn
- **著者**: ちあき
- **公開日時**: 2026-01-29T02:56:51

## 要約

ご提示いただいた記事「Next.jsでWPをヘッドレス化する際の、プレビュー機能の実装パターン」の要約を以下にまとめました。

---

### 記事の概要
Next.jsとWordPressを組み合わせたヘッドレス構成において、大きな課題となる「投稿プレビュー機能」の実装方法を解説した記事です。Next.jsのバージョン（App Router/Pages Router）や、認証方法、プラグインの有無に応じた複数のパターンが紹介されています。

### 主要な実装パターン

#### 1. Next.js の「Draft Mode（またはPreview Mode）」を利用する
これが現代的な標準手法です。
*   **仕組み:** WordPressのプレビューボタンからNext.jsのAPI（Route Handler）へ遷移し、そこで「Draft Mode」を有効化（Cookieをセット）します。
*   **メリット:** 本番環境のキャッシュをバイパスして、下書き状態の最新データを取得・表示できます。
*   **ポイント:** App Routerでは `draftMode().enable()` を使用し、安全性のためにシークレットトークンによる検証を行います。

#### 2. WPGraphQL Content Editor Preview プラグインの活用
WordPress側の管理画面をカスタマイズするためのパターンです。
*   **機能:** WordPressの「プレビュー」ボタンの遷移先
