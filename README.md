# Session Interval Analysis

このスクリプトは、セッションログファイル（`.dat`）内で各操作がどの程度の間隔で行われているかを分析します。

## 環境構築

Python で必要なモジュールは `requirements.txt` に記載してあります。以下でインストールしてください。

```bash
pip install -r requirements.txt
```

## 使い方

```
python analyze_session_intervals.py <ログファイル.dat> [--delimiter DELIM]
```

- `<ログファイル.dat>`: セッションログを含むファイルへのパス。
- `--delimiter`: 区切り文字（デフォルトはカンマ）。

ファイルには少なくとも `session_id`, `operation`, `timestamp` の各列が必要です。`timestamp` は日時として解釈可能な文字列である必要があります。

実行すると、各セッション内での操作間隔（秒）のヒストグラムが表示され、平均や信頼区間などの統計量が出力されます。
