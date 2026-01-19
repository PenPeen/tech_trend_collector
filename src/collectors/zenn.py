"""Zenn RSS取得モジュール"""

from datetime import datetime
from typing import Any

import feedparser

from src.utils.config import MAX_ARTICLES_PER_SOURCE, ZENN_RSS_URL


def fetch_trending_articles() -> list[dict[str, Any]]:
    """Zennのトレンド記事を取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース）
    """
    feed = feedparser.parse(ZENN_RSS_URL)
    articles = []

    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        # 公開日時のパース
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).isoformat()

        # Zennの著者情報取得
        author = ""
        if hasattr(entry, "author"):
            author = entry.author

        article = {
            "title": entry.title,
            "url": entry.link,
            "author": author,
            "published": published,
            "tags": [],  # ZennのRSSにはタグ情報がない
            "source": "zenn",
        }
        articles.append(article)

    return articles
