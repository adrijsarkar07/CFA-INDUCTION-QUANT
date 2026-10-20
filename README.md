# Dataset

Yahoo Finance daily adjusted OHLCV for Reliance Industries (`RELIANCE.NS`).
Source: https://finance.yahoo.com/quote/RELIANCE.NS/history/
Downloaded through yfinance with `auto_adjust=True`, `actions=True`,
`start="2016-01-01"`, and exclusive `end="2025-01-01"`.

`reliance_prices.csv` is the 2,221-row research snapshot downloaded on
20 October 2026 for this completion. It enables offline replication.
The generator records the canonical data hash in `outputs/run_metadata.json`.
Fields: Open, High, Low, Close, Volume, Dividends, Stock Splits.
OHLC prices are retrospectively adjusted; see the adjusted-price limitation
in the main README. Action columns are retained but no separate dividend
cash flows or share-split events are processed in the portfolio.

Development: 2016-2022. Validation: 2023 (original continuous-run slice).
Final test: 2024, with 29 December 2023 as the baseline/prior signal date.
Exploration included validation data. New sensitivity and risk experiments
are development-only and were added after viewing the baseline 2024 result.

Data checks reject duplicates, missing/non-finite values, non-positive
prices and invalid OHLC ordering. Large returns are not automatically removed.
Provider revisions can change later downloads; use the supplied snapshot
for reproduction of this report.
