"""Gemini Pro 要約サービスモジュール"""

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.utils.config import API_TIMEOUT, GEMINI_API_KEY
from src.utils.logger import get_logger
from src.utils.retry import retry

logger = get_logger("services.summarizer")

# Geminiモデルインスタンス
_model = None


def initialize_gemini() -> bool:
    """Gemini Pro モデルを初期化する

    Returns:
        初期化成功時True、失敗時False
    """
    global _model

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY が未設定です")
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-pro")
        logger.info("Gemini Pro モデルの初期化に成功")
        return True
    except Exception as e:
        logger.error(f"Gemini 初期化エラー: {e}")
        return False


@retry(
    max_attempts=3,
    backoff_factor=2.0,
    initial_delay=1.0,
    exceptions=(
        google_exceptions.ResourceExhausted,  # レート制限
        google_exceptions.ServiceUnavailable,  # サービス一時停止
        google_exceptions.DeadlineExceeded,  # タイムアウト
        ConnectionError,
    ),
)
def _call_gemini_api(prompt: str) -> str:
    """Gemini APIを呼び出す（リトライ対応）

    Args:
        prompt: プロンプト

    Returns:
        生成されたテキスト
    """
    global _model

    if _model is None:
        raise RuntimeError("Gemini モデルが初期化されていません")

    # タイムアウト設定
    generation_config = genai.GenerationConfig(
        max_output_tokens=1024,
    )

    response = _model.generate_content(
        prompt,
        generation_config=generation_config,
        request_options={"timeout": API_TIMEOUT},
    )
    return response.text.strip()


def summarize_article(url: str) -> str:
    """記事URLから要約を生成する

    Args:
        url: 記事のURL

    Returns:
        要約テキスト。失敗時は空文字列
    """
    global _model

    if _model is None:
        return ""

    logger.info(f"要約生成開始: {url}")

    prompt = f"""以下の技術記事を要約してください。

【記事URL】
{url}
"""

    try:
        summary = _call_gemini_api(prompt)
        logger.info(f"要約生成完了: {url}")
        return summary
    except google_exceptions.ResourceExhausted:
        logger.error("レート制限に達しました。しばらく待ってから再試行してください。")
        return ""
    except google_exceptions.InvalidArgument as e:
        logger.error(f"無効なリクエスト: {e}")
        return ""
    except Exception as e:
        logger.error(f"要約生成エラー: {e}")
        return ""
