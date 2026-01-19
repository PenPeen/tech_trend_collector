"""Gemini Pro 要約サービスモジュール"""

import google.generativeai as genai

from src.utils.config import GEMINI_API_KEY

# Geminiモデルインスタンス
_model = None


def initialize_gemini() -> bool:
    """Gemini Pro モデルを初期化する

    Returns:
        初期化成功時True、失敗時False
    """
    global _model

    if not GEMINI_API_KEY:
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-pro")
        return True
    except Exception as e:
        print(f"[Gemini] 初期化エラー: {e}")
        return False


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

    prompt = f"""以下の技術記事を要約してください。

【記事URL】
{url}
"""

    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini] 要約生成エラー: {e}")
        return ""
