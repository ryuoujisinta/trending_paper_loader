import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

def test_log_rotation():
    print("Testing log rotation...")

    # テスト用の設定
    test_log_file = os.path.join(config.LOG_DIR, "rotation_test.log")
    if os.path.exists(test_log_file):
        os.remove(test_log_file)

    # 非常に小さいサイズでローテーションを構成
    max_bytes = 1024  # 1KB
    backup_count = 3

    handler = RotatingFileHandler(
        test_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )

    logger = logging.getLogger("rotation_test")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # ローテーションを発生させるために大量のログを出力
    print(f"Writing logs to {test_log_file}...")
    for i in range(100):
        logger.info(f"Test log message number {i:03d}: This is a long enough message to fill 1KB quickly.")

    # ファイルの存在を確認
    files = os.listdir(config.LOG_DIR)
    rotation_files = [f for f in files if f.startswith("rotation_test.log")]

    print(f"Found rotation files: {rotation_files}")

    if len(rotation_files) > 1:
        print("Verification SUCCESS: Log rotation triggered successfully.")
        # クリーンアップ
        handler.close()
        for f in rotation_files:
            try:
                os.remove(os.path.join(config.LOG_DIR, f))
            except PermissionError:
                pass # Windows may lock files
    else:
        print("Verification FAILED: Only one log file found.")

if __name__ == "__main__":
    test_log_rotation()
