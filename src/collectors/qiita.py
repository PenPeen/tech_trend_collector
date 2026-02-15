"""Qiita RSS取得モジュール"""

import json
import socket
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import feedparser

from src.utils.config import PRIORITY_TOPIC_LIMIT, QIITA_RSS_URL, RSS_TIMEOUT
from src.utils.logger import get_logger

logger = get_logger("collectors.qiita")


def _extract_item_id(url: str) -> str | None:
    """QiitaのURLからitem_idを抽出する

    例: https://qiita.com/user/items/abc123 → abc123
    """
    try:
        path = urlparse(url).path
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[1] == "items":
            return parts[2]
    except Exception:
        pass
    return None


def _fetch_likes_count(item_id: str) -> int:
    """Qiita APIからいいね数を取得する"""
    try:
        url = f"https://qiita.com/api/v2/items/{item_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "TechTrendCollector/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("likes_count", 0)
    except Exception as e:
        logger.debug(f"Qiita APIからいいね数の取得に失敗 (item_id={item_id}): {e}")
        return 0


def fetch_trending_articles() -> list[dict[str, Any]]:
    """Qiitaのトレンド記事を取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース）
        取得失敗時は空リスト
    """
    logger.info("Qiita トレンド記事の取得を開始")

    try:
        # タイムアウト付きでRSSを取得
        feed = feedparser.parse(
            QIITA_RSS_URL,
            request_headers={"User-Agent": "TechTrendCollector/1.0"},
        )

        # feedparserの内部でタイムアウトを設定
        socket.setdefaulttimeout(RSS_TIMEOUT)

        # フィードのステータスチェック
        if hasattr(feed, "bozo") and feed.bozo:
            if hasattr(feed, "bozo_exception"):
                logger.warning(f"RSSパースに問題がありました: {feed.bozo_exception}")

        if not feed.entries:
            logger.warning("Qiita RSSから記事が取得できませんでした")
            return []

        articles = []

        for entry in feed.entries:
            try:
                # タグの取得（Atomフィードのcategory）
                tags = []
                if hasattr(entry, "tags"):
                    tags = [tag.term for tag in entry.tags]

                # 公開日時のパース
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                # いいね数をAPIから取得
                likes = 0
                item_id = _extract_item_id(entry.link)
                if item_id:
                    likes = _fetch_likes_count(item_id)

                article = {
                    "title": entry.title,
                    "url": entry.link,
                    "author": entry.author if hasattr(entry, "author") else "",
                    "published": published,
                    "tags": tags,
                    "source": "qiita",
                    "likes": likes,
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"記事のパースに失敗: {e}")
                continue

        # いいね数で降順ソート
        articles.sort(key=lambda a: a["likes"], reverse=True)

        logger.info(f"Qiita から {len(articles)} 件の記事を取得完了")
        return articles

    except urllib.error.URLError as e:
        logger.error(f"ネットワークエラー: {e}")
        return []
    except socket.timeout:
        logger.error(f"タイムアウト ({RSS_TIMEOUT}秒)")
        return []
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return []


def fetch_articles_by_tag(tag: str) -> list[dict[str, Any]]:
    """Qiita API v2で指定タグの記事を取得する

    Args:
        tag: 取得対象のタグ名（例: "aws", "python"）

    Returns:
        記事情報のリスト（いいね数降順、上位PRIORITY_TOPIC_LIMIT件）
        取得失敗時は空リスト
    """
    logger.info(f"Qiita タグ '{tag}' の記事を取得開始")

    try:
        url = f"https://qiita.com/api/v2/tags/{tag}/items?page=1&per_page={PRIORITY_TOPIC_LIMIT}&sort=stock"
        req = urllib.request.Request(url, headers={"User-Agent": "TechTrendCollector/1.0"})

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        articles = []
        for item in data:
            tags = [t["name"] for t in item.get("tags", [])]
            likes = item.get("likes_count", 0)

            article = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "author": item.get("user", {}).get("id", ""),
                "published": item.get("created_at", ""),
                "tags": tags,
                "source": "qiita",
                "likes": likes,
            }
            articles.append(article)

        # いいね数で降順ソート
        articles.sort(key=lambda a: a["likes"], reverse=True)

        logger.info(f"Qiita タグ '{tag}' から {len(articles)} 件の記事を取得完了")
        return articles[:PRIORITY_TOPIC_LIMIT]

    except Exception as e:
        logger.error(f"Qiita タグ '{tag}' の記事取得に失敗: {e}")
        return []
