"""重複チェックモジュール"""

import json
from datetime import datetime
from typing import Any

from src.utils.config import HISTORY_FILE


class Deduplicator:
    """記事の重複チェックを行うクラス"""

    def __init__(self):
        self._history: dict[str, Any] = {"articles": []}
        self._urls: set[str] = set()

    def load_history(self) -> None:
        """履歴ファイルを読み込む"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self._history = json.load(f)
                self._urls = {article["url"] for article in self._history["articles"]}

    def is_duplicate(self, url: str) -> bool:
        """指定されたURLが既に取得済みかどうかを判定する

        Args:
            url: チェック対象のURL

        Returns:
            重複している場合はTrue
        """
        return url in self._urls

    def add_to_history(self, article: dict[str, Any]) -> None:
        """記事を履歴に追加する

        Args:
            article: 追加する記事情報
        """
        history_entry = {
            "url": article["url"],
            "title": article["title"],
            "source": article["source"],
            "collected_at": datetime.now().isoformat(),
        }
        self._history["articles"].append(history_entry)
        self._urls.add(article["url"])

    def save_history(self) -> None:
        """履歴ファイルを保存する"""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self._history, f, ensure_ascii=False, indent=2)
