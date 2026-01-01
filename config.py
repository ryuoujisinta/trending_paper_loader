"""
アプリケーション設定

このモジュールはアプリケーション全体で使用する定数を定義します。
環境変数から設定を読み込むことも可能です。
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """アプリケーション設定クラス"""

    # データ保存設定
    DATA_DIR: str = "data"

    # リクエスト設定
    DEFAULT_RETRIES: int = 3  # リトライ回数
    DEFAULT_RETRY_DELAY: int = 180  # リトライ遅延時間（秒）
    RATE_LIMIT_DELAY: float = 0.5  # レート制限回避のための遅延（秒）
    REQUEST_TIMEOUT: int = 10  # リクエストタイムアウト（秒）

    # スクレイピング設定
    CDN_THUMBNAIL_URL_TEMPLATE: str = "https://cdn-thumbnails.huggingface.co/social-thumbnails/papers/{paper_id}.png"

    # UI設定
    PAGE_TITLE: str = "Trending Paper Dashboard"
    PAGE_ICON: str = "📄"
    LAYOUT: str = "wide"

    # ロギング設定
    LOG_DIR: str = "logs"
    LOG_FILE: str = "trending_papers.log"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 1048576  # 1MB
    LOG_BACKUP_COUNT: int = 5

    @classmethod
    def from_env(cls) -> "Config":
        """
        環境変数から設定を読み込む

        Returns:
            環境変数から読み込んだ設定を持つConfigインスタンス
        """
        return cls(
            DATA_DIR=os.getenv("DATA_DIR", cls.DATA_DIR),
            DEFAULT_RETRIES=int(os.getenv("DEFAULT_RETRIES", str(cls.DEFAULT_RETRIES))),
            DEFAULT_RETRY_DELAY=int(os.getenv("DEFAULT_RETRY_DELAY", str(cls.DEFAULT_RETRY_DELAY))),
            RATE_LIMIT_DELAY=float(os.getenv("RATE_LIMIT_DELAY", str(cls.RATE_LIMIT_DELAY))),
            REQUEST_TIMEOUT=int(os.getenv("REQUEST_TIMEOUT", str(cls.REQUEST_TIMEOUT))),
            CDN_THUMBNAIL_URL_TEMPLATE=os.getenv("CDN_THUMBNAIL_URL_TEMPLATE", cls.CDN_THUMBNAIL_URL_TEMPLATE),
            PAGE_TITLE=os.getenv("PAGE_TITLE", cls.PAGE_TITLE),
            PAGE_ICON=os.getenv("PAGE_ICON", cls.PAGE_ICON),
            LAYOUT=os.getenv("LAYOUT", cls.LAYOUT),
            LOG_DIR=os.getenv("LOG_DIR", cls.LOG_DIR),
            LOG_FILE=os.getenv("LOG_FILE", cls.LOG_FILE),
            LOG_LEVEL=os.getenv("LOG_LEVEL", cls.LOG_LEVEL),
            LOG_FORMAT=os.getenv("LOG_FORMAT", cls.LOG_FORMAT),
            LOG_MAX_BYTES=int(os.getenv("LOG_MAX_BYTES", str(cls.LOG_MAX_BYTES))),
            LOG_BACKUP_COUNT=int(os.getenv("LOG_BACKUP_COUNT", str(cls.LOG_BACKUP_COUNT))),
        )


# グローバル設定インスタンス
config = Config.from_env()
