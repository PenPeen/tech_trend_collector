# 実行計画書 03: Resend 通知機能

## 概要

| 項目 | 内容 |
|------|------|
| フェーズ | Phase 3: 通知機能 |
| 目的 | 記事収集完了後にResend APIでメール通知を送信する |
| 前提条件 | Phase 2（PR #02）がマージ済みであること |

---

## スコープ

### 含まれるもの
- Resend API連携
- メール通知サービス
- 成功/失敗時の通知内容
- GitHub Secrets設定ドキュメント

### 含まれないもの
- エラーハンドリング強化（Phase 4）
- Slack通知対応（スコープ外）

---

## 実装タスク

### 1. 依存関係追加

- [ ] `requirements.txt` に追加
  - resend

### 2. 設定追加

- [ ] `src/utils/config.py` 更新
  - `RESEND_API_KEY` 環境変数読み込み追加
  - `NOTIFICATION_EMAIL` 環境変数読み込み追加
- [ ] `.env.example` 更新
  - `RESEND_API_KEY=your_api_key_here` 追加
  - `NOTIFICATION_EMAIL=your_email@example.com` 追加

### 3. 通知サービス実装

- [ ] `src/services/notifier.py` 作成
  - `send_success_notification(articles, date)` 関数
    - 件名: `[TechTrend] YYYY-MM-DD のトレンド記事`
    - 本文:
      - 取得記事数サマリー（Qiita: X件, Zenn: Y件）
      - 各記事のタイトルとURL（HTML形式でリンク付き）
      - GitHubリポジトリへのリンク
    - 送信元: `onboarding@resend.dev`（Resend無料プラン）
  - `send_failure_notification(error_message, date)` 関数
    - 件名: `[TechTrend] YYYY-MM-DD 実行エラー`
    - 本文: エラー内容
  - `_build_success_email_html(articles)` 関数（メール本文HTML生成）

### 4. メインスクリプト更新

- [ ] `src/main.py` 更新
  - 処理完了後に成功通知を送信
  - 全ソース失敗時にエラー通知を送信
  - RESEND_API_KEY/NOTIFICATION_EMAIL未設定時はスキップ（警告表示）

### 5. GitHub Actions更新

- [ ] `.github/workflows/daily-collect.yml` 更新
  - `RESEND_API_KEY` 環境変数を追加
  - `NOTIFICATION_EMAIL` 環境変数を追加

---

## 作成/変更ファイル一覧

| パス | 操作 | 説明 |
|------|------|------|
| `src/services/notifier.py` | 新規 | メール通知サービス |
| `src/main.py` | 更新 | 通知処理追加 |
| `src/utils/config.py` | 更新 | 環境変数追加 |
| `requirements.txt` | 更新 | resend追加 |
| `.env.example` | 更新 | 環境変数追加 |
| `.github/workflows/daily-collect.yml` | 更新 | 環境変数追加 |

---

## メール本文フォーマット

### 成功時

```html
<h2>📰 本日のトレンド記事</h2>

<p><strong>取得件数:</strong> Qiita 5件 / Zenn 5件</p>

<h3>Qiita</h3>
<ul>
  <li><a href="https://qiita.com/xxx/items/yyy">記事タイトル1</a></li>
  <li><a href="https://qiita.com/xxx/items/zzz">記事タイトル2</a></li>
  ...
</ul>

<h3>Zenn</h3>
<ul>
  <li><a href="https://zenn.dev/xxx/articles/yyy">記事タイトル1</a></li>
  <li><a href="https://zenn.dev/xxx/articles/zzz">記事タイトル2</a></li>
  ...
</ul>

<hr>
<p>
  <a href="https://github.com/your-username/tech-trend-collector/tree/main/articles/2025-01-19">
    📁 GitHubで詳細を見る
  </a>
</p>
```

### 失敗時

```html
<h2>⚠️ TechTrendCollector 実行エラー</h2>

<p><strong>日時:</strong> 2025-01-19</p>

<p><strong>エラー内容:</strong></p>
<pre>{error_message}</pre>

<hr>
<p>
  <a href="https://github.com/your-username/tech-trend-collector/actions">
    GitHub Actionsログを確認する
  </a>
</p>
```

---

## GitHub Secrets設定

PRマージ前に以下のSecretを設定する必要があります。

| Secret名 | 説明 | 取得方法 |
|----------|------|----------|
| `RESEND_API_KEY` | Resend APIキー | [Resend Dashboard](https://resend.com/api-keys) から取得 |
| `NOTIFICATION_EMAIL` | 通知先メールアドレス | 自分のメールアドレス |

---

## 完了条件

1. `python src/main.py` がローカルで正常に実行できる（RESEND設定時）
2. 処理成功時に記事一覧を含むメールが送信される
3. 全ソース失敗時にエラーメールが送信される
4. メール内のリンクが正しく機能する
5. RESEND未設定時でもエラーなく動作する（通知スキップ）
6. GitHub Actionsが正常に動作する

---

## PRテンプレート

```markdown
## 概要
TechTrendCollector Phase 3: Resend通知機能追加

記事収集完了後にメールで通知する機能を追加しました。

## 変更内容
- Resend API連携
- 成功時: 記事一覧を含むメール送信
- 失敗時: エラー内容を含むメール送信

## 設定が必要なSecrets
- `RESEND_API_KEY`: Resend APIキー
- `NOTIFICATION_EMAIL`: 通知先メールアドレス

## テスト方法
1. `.env` に `RESEND_API_KEY` と `NOTIFICATION_EMAIL` を設定
2. `pip install -r requirements.txt`
3. `python src/main.py`
4. 指定したメールアドレスに通知が届くことを確認

## 関連Issue
なし
```

---

## 備考

- Resend無料プランでは送信元は `onboarding@resend.dev` 固定
- 月3000通まで無料（1日1通なら十分）
- メールはHTML形式で送信（リンクをクリック可能にするため）
- 独自ドメインからの送信は有料プランが必要
