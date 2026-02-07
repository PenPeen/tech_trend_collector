"""メール通知サービスモジュール"""

import socket
from datetime import date
from typing import Any

import resend

from src.utils.config import NOTIFICATION_EMAIL, NOTIFICATION_TIMEOUT, RESEND_API_KEY
from src.utils.logger import get_logger

logger = get_logger("services.notifier")

# GitHubリポジトリURL（必要に応じて変更）
GITHUB_REPO_URL = "https://github.com/your-username/tech-trend-collector"


def is_notifier_enabled() -> bool:
    """通知機能が有効かどうかを確認"""
    return bool(RESEND_API_KEY and NOTIFICATION_EMAIL)


def _build_success_email_html(
    articles: list[dict[str, Any]], stats: dict[str, int], target_date: str
) -> str:
    """成功時のメール本文HTML生成"""
    # ソース別に記事を分類
    qiita_articles = [a for a in articles if a.get("source") == "qiita"]
    zenn_articles = [a for a in articles if a.get("source") == "zenn"]
    hn_articles = [a for a in articles if a.get("source") == "hackernews"]
    hatena_articles = [a for a in articles if a.get("source") == "hatena"]

    html_parts = [
        "<h2>📰 本日のトレンド記事</h2>",
        f"<p><strong>取得件数:</strong> Qiita {stats.get('qiita_fetched', 0)}件 / "
        f"Zenn {stats.get('zenn_fetched', 0)}件 / "
        f"Hacker News {stats.get('hn_fetched', 0)}件 / "
        f"はてなブックマーク {stats.get('hatena_fetched', 0)}件</p>",
        f"<p><strong>新規保存:</strong> {stats.get('new_articles', 0)}件</p>",
    ]

    # Qiita記事一覧
    if qiita_articles:
        html_parts.append("<h3>Qiita</h3>")
        html_parts.append("<ul>")
        for article in qiita_articles:
            html_parts.append(
                f'  <li><a href="{article["url"]}">{article["title"]}</a></li>'
            )
        html_parts.append("</ul>")

    # Zenn記事一覧
    if zenn_articles:
        html_parts.append("<h3>Zenn</h3>")
        html_parts.append("<ul>")
        for article in zenn_articles:
            html_parts.append(
                f'  <li><a href="{article["url"]}">{article["title"]}</a></li>'
            )
        html_parts.append("</ul>")

    # Hacker News記事一覧
    if hn_articles:
        html_parts.append("<h3>Hacker News</h3>")
        html_parts.append("<ul>")
        for article in hn_articles:
            html_parts.append(
                f'  <li><a href="{article["url"]}">{article["title"]}</a></li>'
            )
        html_parts.append("</ul>")

    # はてなブックマーク記事一覧
    if hatena_articles:
        html_parts.append("<h3>はてなブックマーク</h3>")
        html_parts.append("<ul>")
        for article in hatena_articles:
            bookmarks = article.get("bookmarks", 0)
            bookmark_label = f" ({bookmarks} users)" if bookmarks else ""
            html_parts.append(
                f'  <li><a href="{article["url"]}">{article["title"]}</a>{bookmark_label}</li>'
            )
        html_parts.append("</ul>")

    # フッター
    html_parts.extend(
        [
            "<hr>",
            "<p>",
            f'  <a href="{GITHUB_REPO_URL}/tree/main/articles/{target_date}">',
            "    📁 GitHubで詳細を見る",
            "  </a>",
            "</p>",
        ]
    )

    return "\n".join(html_parts)


def _build_failure_email_html(error_message: str, target_date: str) -> str:
    """失敗時のメール本文HTML生成"""
    return f"""<h2>⚠️ TechTrendCollector 実行エラー</h2>

<p><strong>日時:</strong> {target_date}</p>

<p><strong>エラー内容:</strong></p>
<pre>{error_message}</pre>

<hr>
<p>
  <a href="{GITHUB_REPO_URL}/actions">
    GitHub Actionsログを確認する
  </a>
</p>"""


def _send_email(subject: str, html_body: str) -> bool:
    """メールを送信する（共通処理）

    Args:
        subject: メール件名
        html_body: HTML本文

    Returns:
        送信成功した場合True
    """
    # タイムアウト設定
    socket.setdefaulttimeout(NOTIFICATION_TIMEOUT)

    try:
        resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": [NOTIFICATION_EMAIL],
                "subject": subject,
                "html": html_body,
            }
        )
        return True
    except socket.timeout:
        logger.error(f"メール送信タイムアウト ({NOTIFICATION_TIMEOUT}秒)")
        return False
    except resend.exceptions.ResendError as e:
        logger.error(f"Resend APIエラー: {e}")
        return False
    except Exception as e:
        logger.error(f"メール送信エラー: {e}")
        return False


def send_success_notification(
    articles: list[dict[str, Any]], stats: dict[str, int], target_date: str | None = None
) -> bool:
    """成功通知を送信

    Args:
        articles: 収集した記事リスト
        stats: 統計情報
        target_date: 対象日付（YYYY-MM-DD形式）。Noneの場合は今日の日付

    Returns:
        送信成功した場合True
    """
    if not is_notifier_enabled():
        logger.warning("通知機能が無効のため送信をスキップ")
        return False

    if target_date is None:
        target_date = date.today().isoformat()

    resend.api_key = RESEND_API_KEY

    subject = f"[TechTrend] {target_date} のトレンド記事"
    html_body = _build_success_email_html(articles, stats, target_date)

    logger.info("成功通知メールを送信中...")
    if _send_email(subject, html_body):
        logger.info("成功通知メールの送信完了")
        return True
    else:
        logger.warning("成功通知メールの送信に失敗しました")
        return False


def send_failure_notification(
    error_message: str, target_date: str | None = None
) -> bool:
    """失敗通知を送信

    Args:
        error_message: エラーメッセージ
        target_date: 対象日付（YYYY-MM-DD形式）。Noneの場合は今日の日付

    Returns:
        送信成功した場合True
    """
    if not is_notifier_enabled():
        logger.warning("通知機能が無効のため送信をスキップ")
        return False

    if target_date is None:
        target_date = date.today().isoformat()

    resend.api_key = RESEND_API_KEY

    subject = f"[TechTrend] {target_date} 実行エラー"
    html_body = _build_failure_email_html(error_message, target_date)

    logger.info("エラー通知メールを送信中...")
    if _send_email(subject, html_body):
        logger.info("エラー通知メールの送信完了")
        return True
    else:
        logger.warning("エラー通知メールの送信に失敗しました")
        return False
