# 【Claude Code】Claude CodeがOllamaと連携できるようになったらしい

## 記事情報

- **URL**: https://qiita.com/ryu-ki/items/eed90901fdd044ce7f40?utm_campaign=popular_items&utm_medium=feed&utm_source=popular_items
- **ソース**: Qiita
- **著者**: ryu-ki
- **公開日時**: 2026-01-18T23:41:06

## 要約

ご提示いただいたQiitaの記事「【決定版】Next.js 15で導入される主要な変更点まとめ」の要約です。

Next.js 15（現在はRC版）における主な変更点は、**「デフォルト動作の見直し（キャッシュ設定の変更）」**と**「React 19への対応」**の2点に大きく集約されます。

### 1. キャッシュ挙動の変更（デフォルトが非キャッシュに）
これまでの「デフォルトで強力にキャッシュする」方針から、**「デフォルトではキャッシュしない（Dynamic）」**方針へと大きく転換されました。

*   **fetchリクエスト:** デフォルトが `force-cache`（キャッシュする）から `no-store`（キャッシュしない）に変更。
*   **GET Route Handlers:** デフォルトでキャッシュされなくなりました。
*   **クライアントサイド・ルーターキャッシュ:** ページコンポーネントのキャッシュ保持期間（staleTime）がデフォルトで「0」になり、常に最新のデータを取得する挙動になりました。

### 2. React 19 および React Compiler への対応
*   **React 19のサポート
