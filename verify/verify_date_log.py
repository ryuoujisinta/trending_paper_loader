
import logging
import os
from datetime import date
from io import StringIO
from typing import Any

# ダミーのloggerとsession_stateを再現
class MockLogger:
    def __init__(self):
        self.output = StringIO()
        self.handler = logging.StreamHandler(self.output)
        self.logger = logging.getLogger("test_logger")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def info(self, msg):
        self.logger.info(msg)

    def get_logs(self):
        return self.output.getvalue()

mock_logger = MockLogger()

# セッション状態のシミュレーション
session_state: dict[str, Any] = {}

def check_and_log(start_date, end_date):
    if "last_date_range" not in session_state:
        session_state["last_date_range"] = (None, None)

    if session_state["last_date_range"] != (start_date, end_date):
        if start_date == end_date:
            mock_logger.info(f"日付が変更されました: {start_date}")
        else:
            mock_logger.info(f"日付が変更されました: {start_date} 〜 {end_date}")
        session_state["last_date_range"] = (start_date, end_date)

# テストケース1: 初回アクセス（単一日付）
print("Testing case 1: Initial access (single date)")
d1 = date(2025, 12, 31)
check_and_log(d1, d1)
print(f"Logs: {mock_logger.get_logs().strip()}")
assert "日付が変更されました: 2025-12-31" in mock_logger.get_logs()

# テストケース2: 同じ日付で再アクセス（ログが出力されないこと）
print("\nTesting case 2: Same date again")
check_and_log(d1, d1)
# ログが増えていないことを確認
print(f"Current Logs: {mock_logger.get_logs().strip()}")

# テストケース3: 日付変更（単一日付）
print("\nTesting case 3: Date change (single date)")
d2 = date(2025, 12, 30)
check_and_log(d2, d2)
print(f"Current Logs: {mock_logger.get_logs().strip()}")
assert "日付が変更されました: 2025-12-30" in mock_logger.get_logs()

# テストケース4: 期間指定に変更
print("\nTesting case 4: Change to range")
check_and_log(d2, d1)
print(f"Current Logs: {mock_logger.get_logs().strip()}")
assert "日付が変更されました: 2025-12-30 〜 2025-12-31" in mock_logger.get_logs()

print("\nVerification successful!")
