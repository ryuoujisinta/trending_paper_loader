# 開発者向けドキュメント

## アーキテクチャ概要

### システム構成

```
┌─────────────┐
│   app.py    │  ← Streamlit UI
└──────┬──────┘
       │
       ├─→ data_processing.py  ← データ処理ロジック
       ├─→ utils.py            ← データ取得・保存
       ├─→ config.py           ← 設定管理
       └─→ exceptions.py       ← カスタム例外
```

### モジュール責務

#### `app.py`
- Streamlit UIの構築
- ユーザーインタラクションの処理
- データ表示ロジック

#### `utils.py`
- Hugging Faceからのデータスクレイピング
- ローカルJSONファイルへの保存・読み込み
- HTTPリクエストとリトライロジック
- ロギング

#### `data_processing.py`
- 論文データの重複排除
- ソート（日付順、Upvote数順）
- キーワードフィルタリング

#### `config.py`
- アプリケーション設定の集約
- 環境変数からの設定読み込み

#### `exceptions.py`
- プロジェクト固有の例外クラス定義

## コーディング規約

### PEP8準拠

- インポート順序: 標準ライブラリ → サードパーティ → ローカルモジュール
- 最大行長: 100文字
- インデント: スペース4つ

### 型ヒント

全ての関数に型ヒントを追加:

```python
def function_name(arg1: str, arg2: int = 0) -> Optional[List[Dict[str, Any]]]:
    """関数の説明"""
    pass
```

### docstring

Google Styleのdocstringを使用:

```python
def function_name(arg1: str, arg2: int) -> str:
    """
    関数の簡潔な説明

    Args:
        arg1: 引数1の説明
        arg2: 引数2の説明

    Returns:
        戻り値の説明

    Raises:
        ExceptionType: 例外が発生する条件

    Examples:
        >>> function_name("test", 42)
        "result"
    """
    pass
```

### ロギング

適切なログレベルを使用:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

## テストガイドライン

### テストの構成

```
tests/
├── __init__.py
├── test_utils.py              # utils.pyのテスト
├── test_data_processing.py    # data_processing.pyのテスト
└── fixtures/
    └── sample_data.json       # テスト用サンプルデータ
```

### テストの書き方

```python
import unittest
from utils import load_data

class TestUtils(unittest.TestCase):

    def test_load_data_existing_file(self):
        """既存ファイルの読み込みテスト"""
        data = load_data("2025-12-31")
        self.assertIsNotNone(data)
        self.assertIsInstance(data, list)

    def test_load_data_nonexistent_file(self):
        """存在しないファイルの読み込みテスト"""
        data = load_data("1900-01-01")
        self.assertIsNone(data)
```

### テストカバレッジ目標

- ユーティリティ関数: 80%以上
- データ処理関数: 90%以上
- 全体: 70%以上

## デプロイ手順

### ローカル環境

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 依存パッケージのインストール
pip install -r requirements.txt

# アプリケーションの起動
streamlit run app.py
```

### Streamlit Cloud

1. GitHubリポジトリにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud)にログイン
3. 「New app」をクリック
4. リポジトリ、ブランチ、メインファイル（`app.py`）を選択
5. 「Deploy」をクリック

### 環境変数の設定

Streamlit Cloudの場合、Secrets管理で以下を設定可能:

```toml
# .streamlit/secrets.toml
DATA_DIR = "data"
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 180
LOG_LEVEL = "INFO"
```

## トラブルシューティング

### よくある問題

#### 1. レート制限エラー（429）

**症状**: `RateLimitError: リトライ上限に達しました`

**解決策**:
- `config.py`の`DEFAULT_RETRY_DELAY`を増やす
- リクエスト間隔を空ける

#### 2. データが取得できない

**症状**: 空のリストが返される

**解決策**:
- Hugging FaceのWebサイト構造が変更されていないか確認
- ログファイル（`trending_papers.log`）を確認
- ネットワーク接続を確認

#### 3. 型チェックエラー

**症状**: `mypy`でエラーが発生

**解決策**:
- 型ヒントを追加
- 必要に応じて`# type: ignore`を使用（最小限に）

## パフォーマンス最適化

### 並列処理（将来的な実装）

要約取得を並列化することで高速化可能:

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_daily_papers_from_hf(target_date, max_workers=5):
    # ...
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_paper_summary, link) for link in links]
        summaries = [f.result() for f in futures]
```

**注意**: レート制限に注意が必要

### キャッシング

Streamlitの`@st.cache_data`を活用:

```python
@st.cache_data
def load_cached_data(date_str):
    return load_data(date_str)
```

## コントリビューション

### プルリクエストのワークフロー

1. フォークを作成
2. フィーチャーブランチを作成（`git checkout -b feature/amazing-feature`）
3. 変更をコミット（`git commit -m 'Add amazing feature'`）
4. ブランチにプッシュ（`git push origin feature/amazing-feature`）
5. プルリクエストを作成

### コードレビュー基準

- [ ] PEP8準拠
- [ ] 型ヒントが追加されている
- [ ] docstringが記述されている
- [ ] テストが追加されている
- [ ] テストが全て通過している
- [ ] コードカバレッジが低下していない

## リリースプロセス

1. バージョン番号を更新
2. CHANGELOG.mdを更新
3. テストを実行
4. タグを作成（`git tag v1.0.0`）
5. GitHubにプッシュ（`git push --tags`）
6. GitHubでリリースを作成

## 参考資料

- [Streamlit Documentation](https://docs.streamlit.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
