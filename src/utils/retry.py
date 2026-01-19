"""リトライ機構モジュール"""

import time
from functools import wraps
from typing import Any, Callable, Tuple, Type

from src.utils.logger import get_logger

logger = get_logger("retry")


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """リトライデコレータ

    指数バックオフでリトライを行う。
    デフォルト: 1秒 → 2秒 → 4秒

    Args:
        max_attempts: 最大試行回数（デフォルト: 3）
        backoff_factor: バックオフ係数（デフォルト: 2.0）
        initial_delay: 初回リトライまでの待機時間（秒）
        exceptions: リトライ対象の例外タプル

    Returns:
        デコレータ関数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} 失敗 (試行 {attempt}/{max_attempts}): {e}"
                        )
                        logger.info(f"{delay:.1f}秒後にリトライします...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} 最終失敗 ({max_attempts}回試行): {e}"
                        )

            raise last_exception  # type: ignore

        return wrapper

    return decorator
