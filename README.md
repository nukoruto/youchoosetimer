# Session Interval Analysis

このスクリプトは、CSV 形式のセッションログから各操作イベントの時間間隔を分析します。

## 環境構築

Python で必要なモジュールは `requirements.txt` に記載してあります。以下でインストールしてください。

```bash
pip install -r requirements.txt
```

## 使い方

```
python analyze_session_intervals.py <ログファイル.csv> [--delimiter DELIM]
```

  - `<ログファイル.csv>`: セッションログを含む CSV ファイルへのパス。
  - `--delimiter`: 区切り文字（デフォルトはカンマ）。
  - `--no-header`: ヘッダー行がないファイルを扱う際に指定します。省略時でも自動判別を試みます。

  ファイルには `timestamp`, `visitorid`, `event`, `itemid`, `transactionid` の各列が含まれている想定です。`timestamp` は日時として解釈可能な文字列である必要があります。

実行すると、各訪問者ごとにイベント遷移（例: READ→UPDATE）の区間が集計され、遷移ごとの統計値とヒストグラムが表示されます。
