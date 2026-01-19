"""ロギング設定モジュール"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "tech_trend_collector", level: Optional[str] = None) -> logging.Logger:
    """ロガーを設定して返す

    Args:
        name: ロガー名
        level: ログレベル（INFO, DEBUG等）。Noneの場合はINFO

    Returns:
        設定済みのロガーインスタンス
    """
    logger = logging.getLogger(name)

    # 既に設定済みの場合は再設定しない
    if logger.handlers:
        return logger

    # ログレベル設定
    log_level = getattr(logging, level.upper()) if level else logging.INFO
    logger.setLevel(log_level)

    # コンソールハンドラー（GitHub Actions対応）
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # フォーマット: [YYYY-MM-DD HH:MM:SS] [LEVEL] message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# デフォルトロガーインスタンス
logger = setup_logger()


def get_logger(module_name: str) -> logging.Logger:
    """モジュール用のロガーを取得

    Args:
        module_name: モジュール名

    Returns:
        子ロガーインスタンス
    """
    return logging.getLogger(f"tech_trend_collector.{module_name}")
