"""
カスタム例外クラス

このモジュールはTrending Paper Dashboard固有の例外クラスを定義します。
"""


class PaperFetchError(Exception):
    """
    論文データ取得時の基底例外

    論文データの取得に関連する全てのエラーの基底クラスです。
    """

    pass


class RateLimitError(PaperFetchError):
    """
    レート制限エラー

    APIまたはWebサイトのレート制限に達した場合に発生します。
    """

    pass


class SummaryFetchError(PaperFetchError):
    """
    要約取得エラー

    論文の要約（Abstract）の取得に失敗した場合に発生します。
    """

    pass
