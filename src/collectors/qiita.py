"""Qiita RSS取得モジュール"""

from datetime import datetime
from typing import Any

import feedparser

from src.utils.config import MAX_ARTICLES_PER_SOURCE, QIITA_RSS_URL


def fetch_trending_articles() -> list[dict[str, Any]]:
    """Qiitaのトレンド記事を取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース）
    """
    feed = feedparser.parse(QIITA_RSS_URL)
    articles = []

    for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
        # タグの取得（Atomフィードのcategory）
        tags = []
        if hasattr(entry, "tags"):
            tags = [tag.term for tag in entry.tags]

        # 公開日時のパース
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6]).isoformat()

        article = {
            "title": entry.title,
            "url": entry.link,
            "author": entry.author if hasattr(entry, "author") else "",
            "published": published,
            "tags": tags,
            "source": "qiita",
        }
        articles.append(article)

    return articles
