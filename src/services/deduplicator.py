"""重複チェックモジュール"""

import fcntl
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.config import HISTORY_FILE
from src.utils.logger import get_logger

logger = get_logger("services.deduplicator")


class Deduplicator:
    """記事の重複チェックを行うクラス"""

    def __init__(self):
        self._history: dict[str, Any] = {"articles": []}
        self._urls: set[str] = set()
        self._lock_file: Path | None = None

    def _get_backup_path(self) -> Path:
        """バックアップファイルのパスを取得"""
        return HISTORY_FILE.with_suffix(".json.bak")

    def _create_backup(self) -> None:
        """履歴ファイルのバックアップを作成"""
        if HISTORY_FILE.exists():
            backup_path = self._get_backup_path()
            try:
                shutil.copy2(HISTORY_FILE, backup_path)
                logger.debug(f"バックアップ作成: {backup_path}")
            except Exception as e:
                logger.warning(f"バックアップ作成に失敗: {e}")

    def _restore_from_backup(self) -> bool:
        """バックアップから履歴を復元

        Returns:
            復元成功した場合True
        """
        backup_path = self._get_backup_path()
        if backup_path.exists():
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
                    self._urls = {article["url"] for article in self._history["articles"]}
                logger.info("バックアップから履歴を復元しました")
                return True
            except Exception as e:
                logger.error(f"バックアップからの復元に失敗: {e}")
        return False

    def _acquire_lock(self) -> bool:
        """ファイルロックを取得

        Returns:
            ロック取得成功した場合True
        """
        lock_path = HISTORY_FILE.with_suffix(".lock")
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            self._lock_file = open(lock_path, "w")
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.debug("ファイルロックを取得しました")
            return True
        except (IOError, OSError) as e:
            logger.warning(f"ファイルロックの取得に失敗（別プロセスが実行中の可能性）: {e}")
            if self._lock_file:
                self._lock_file.close()
                self._lock_file = None
            return False

    def _release_lock(self) -> None:
        """ファイルロックを解放"""
        if self._lock_file:
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
                self._lock_file.close()
                self._lock_file = None
                logger.debug("ファイルロックを解放しました")
            except Exception as e:
                logger.warning(f"ファイルロックの解放に失敗: {e}")

    def load_history(self) -> bool:
        """履歴ファイルを読み込む

        Returns:
            読み込み成功した場合True
        """
        # ロック取得
        if not self._acquire_lock():
            logger.warning("ロック取得に失敗しましたが、処理を続行します")

        if not HISTORY_FILE.exists():
            logger.info("履歴ファイルが存在しません。新規作成します。")
            return True

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self._history = json.load(f)

            # データ構造の検証
            if not isinstance(self._history, dict):
                raise ValueError("履歴ファイルの形式が不正です（辞書ではありません）")
            if "articles" not in self._history:
                raise ValueError("履歴ファイルに'articles'キーがありません")
            if not isinstance(self._history["articles"], list):
                raise ValueError("'articles'がリストではありません")

            self._urls = {article["url"] for article in self._history["articles"]}
            logger.info(f"履歴ファイルを読み込みました（{len(self._urls)}件）")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"履歴ファイルのJSONパースに失敗: {e}")
            if self._restore_from_backup():
                return True
            logger.warning("空の履歴で再作成します")
            self._history = {"articles": []}
            self._urls = set()
            return True

        except ValueError as e:
            logger.error(f"履歴ファイルの形式エラー: {e}")
            if self._restore_from_backup():
                return True
            logger.warning("空の履歴で再作成します")
            self._history = {"articles": []}
            self._urls = set()
            return True

        except Exception as e:
            logger.error(f"履歴ファイルの読み込みに失敗: {e}")
            self._history = {"articles": []}
            self._urls = set()
            return False

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
        logger.debug(f"履歴に追加: {article['title'][:40]}...")

    def save_history(self) -> bool:
        """履歴ファイルを保存する

        Returns:
            保存成功した場合True
        """
        try:
            # バックアップ作成
            self._create_backup()

            # ディレクトリ作成
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

            # 一時ファイルに書き込み後リネーム（アトミック操作）
            temp_file = HISTORY_FILE.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)

            temp_file.rename(HISTORY_FILE)
            logger.info(f"履歴ファイルを保存しました（{len(self._history['articles'])}件）")
            return True

        except Exception as e:
            logger.error(f"履歴ファイルの保存に失敗: {e}")
            return False

        finally:
            # ロック解放
            self._release_lock()

    def __del__(self):
        """デストラクタ: ロックを確実に解放"""
        self._release_lock()
