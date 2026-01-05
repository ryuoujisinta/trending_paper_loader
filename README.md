# Trending Paper Dashboard 📄

Hugging FaceのTrending Papersを取得・表示するStreamlitダッシュボードアプリケーション。

## 概要

研究者やAIエンジニアが最新のトレンド論文を効率的にキャッチアップできるダッシュボードです。Hugging Faceから論文情報を自動取得し、日付やUpvote数でソート・フィルタリングできます。

## 主な機能

- 📅 **日付選択**: 単一日付または期間指定でデータを表示
- 🔄 **自動データ取得**: 未取得の日付データを一括取得
- ❤️ **Upvote表示**: 各論文のUpvote数を表示
- 🔍 **キーワード検索**: タイトルや要約から論文を検索
- 📊 **並び替え**: 日付順またはUpvote数順でソート
- 💾 **ローカル保存**: 取得したデータをJSONで保存し再利用
- 🔄 **Upvote更新**: 既存データのUpvote数を最新に更新

## スクリーンショット

（アプリケーションのスクリーンショットをここに追加）

## インストール

### 必要な環境

- Python 3.13以上
- [uv](https://docs.astral.sh/uv/)

### セットアップ手順

1. **リポジトリのクローン**

```bash
git clone <repository-url>
cd trending_paper_loader
```

2. **環境構築と依存パッケージのインストール**

```bash
# 仮想環境の作成とパッケージのインストールを一括で行います
uv sync
```

## 使用方法

### アプリケーションの起動

```bash
uv run streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501`でアプリケーションにアクセスできます。

### 基本的な使い方

1. **日付選択**: サイドバーで「単一日付」または「期間指定」を選択
2. **データ取得**: 未取得のデータがある場合、「不足分のデータを取得・保存する」ボタンをクリック
3. **検索**: サイドバーの検索ボックスにキーワードを入力
4. **並び替え**: 「日付順」または「Upvote数順」を選択
5. **Upvote更新**: 「最新のUpvote数を取得」ボタンで既存データを更新

## プロジェクト構成

```
12-trending_paper/
├── app.py                  # メインアプリケーション
├── utils.py                # データ取得・保存のユーティリティ関数
├── data_processing.py      # データ処理関数（重複排除、ソート、フィルタリング）
├── config.py               # アプリケーション設定
├── exceptions.py           # カスタム例外クラス
├── pyproject.toml          # プロジェクト設定と依存関係管理
├── uv.lock                 # 依存関係のロックファイル
├── .flake8                 # Flake8設定
├── css/
│   └── style.css          # カスタムCSS
├── data/                   # 取得したデータの保存先（自動生成）
├── docs/
│   ├── requirements.md     # 要件定義書
│   └── development.md      # 開発者向けドキュメント
└── tests/                  # テストコード
    ├── __init__.py
    ├── test_utils.py
    ├── test_data_processing.py
    └── fixtures/
        └── sample_data.json
```

## 開発

### 開発環境のセットアップ

```bash
# 開発用パッケージを含むすべての依存関係を同期
uv sync
```

### コード品質チェック

```bash
# コードフォーマット
uv run black app.py utils.py data_processing.py config.py exceptions.py

# リンター
uv run flake8 app.py utils.py data_processing.py config.py exceptions.py

# 型チェック
uv run mypy app.py utils.py data_processing.py config.py exceptions.py
```

### テストの実行

```bash
# 全テスト実行
uv run pytest tests/ -v

# カバレッジ測定
uv run pytest --cov=. --cov-report=html tests/

# カバレッジレポートの確認
# htmlcov/index.html をブラウザで開く
```

詳細は[開発者向けドキュメント](docs/development.md)を参照してください。

## 技術スタック

- **言語**: Python 3.13
- **Webフレームワーク**: Streamlit 1.29.0
- **データ取得**: huggingface_hub
- **データ保存**: JSON
- **テスト**: pytest
- **コード品質**: black, flake8, mypy

## ライセンス

MIT License

## 謝辞

- [Hugging Face](https://huggingface.co/) - 論文データの提供
