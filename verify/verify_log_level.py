import os
import sys
import logging
from io import StringIO

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_data


def test_load_data_logging():
    # ログ出力をキャプチャするためのストリーム
    log_stream = StringIO()

    # ロガーを取得してハンドラを設定
    logger = logging.getLogger("utils")
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # 存在しない日付を指定
    non_existent_date = "1900-01-01"
    load_data(non_existent_date)

    # ログの内容を確認
    log_output = log_stream.getvalue()
    print(f"Log Output: {log_output.strip()}")

    if "INFO: 対象日付のデータファイルが未取得です" in log_output:
        print("Verification SUCCESS: New log message correctly output at INFO level.")
    elif "INFO: ファイルが見つかりません" in log_output:
        print("Verification FAILED: Old log message found.")
    elif "WARNING: 対象日付のデータファイルが未取得です" in log_output:
        print("Verification FAILED: Message updated but level is still WARNING.")
    else:
        print("Verification FAILED: Expected log message not found.")


if __name__ == "__main__":
    test_load_data_logging()
