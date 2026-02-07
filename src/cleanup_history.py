"""history.json クリーンアップスクリプト"""

import sys

from src.services.deduplicator import Deduplicator
from src.utils.logger import get_logger

logger = get_logger("cleanup_history")


def main() -> int:
    """メイン処理

    Returns:
        終了コード（0: 正常, 1: エラー）
    """
    logger.info("history.json クリーンアップ開始")

    deduplicator = Deduplicator()

    if not deduplicator.load_history():
        logger.error("履歴ファイルの読み込みに失敗しました")
        return 1

    deleted_count = deduplicator.cleanup_old_entries(days=7)

    if not deduplicator.save_history():
        logger.error("履歴ファイルの保存に失敗しました")
        return 1

    logger.info(f"クリーンアップ完了: {deleted_count}件の古いエントリを削除しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
