# Dataset

This project uses historical daily data for Reliance Industries Ltd. (`RELIANCE.NS`), downloaded using the `yfinance` Python package.

- **Date range:** 2016–2024
- **Fields used:** Open, High, Low, Close, and Volume
- **Price adjustment:** Adjusted OHLC prices from the data download are used in the analysis.

## Chronological splits

- **Development:** 2016–2022
- **Validation:** 2023
- **Final test:** 2024

The 2024 final-test period was reserved for evaluation after developing the strategy. Raw data files are not included in this repository; the notebook contains the data-loading code.

Historical results are for educational research and do not predict future performance.
