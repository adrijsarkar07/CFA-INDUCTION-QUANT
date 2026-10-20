# Reliance Mean-Reversion Backtest

CFA Club IIT Indore induction 2026 — Finance & Quant, Track 1.
Author: Adrij Sarkar. See the assistance disclosure below.

A daily, long-only mean-reversion research study on Reliance Industries.
The original fixed baseline uses a 20-session closing-price Z-score:
enter below -2 and exit at/above 0, using the previous session's signal
and the current session's Open. Initial capital is INR 100,000;
each entry uses 10% of cash including fees. Only one position is held.
Slippage is 0.05% and fees 0.10% on each side. Idle cash earns no interest.

## Deliverables

- [Technical report PDF](outputs/quant_technical_report.pdf)
- [Research notebook](notebooks/reliance.ipynb)
- [Full performance table](outputs/performance_metrics.csv)
- [Data source and snapshot](data/README.md)
- [Results and limitations](docs/results.md)
- [Sources and assistance](docs/SOURCES.md)
- [Requirement mapping](docs/DELIVERABLES.md)
- [Report and analysis generator](complete_quant.py)
- [All saved charts](outputs/figures/)

## Reproduce locally

Use Python 3.12 (the version family used to execute this package).
Download/extract the repository and open a terminal in its root folder.

```bash
python -m pip install -r requirements.txt
python complete_quant.py --csv data/reliance_prices.csv
```

This regenerates the PDF, charts, metrics and trade logs in `outputs/`.
To use a fresh Yahoo download instead, omit `--csv`; internet access is required.
Data providers may revise historical data, so results may change.

To use the notebook:

```bash
python -m notebook
```

Open `notebooks/reliance.ipynb`, restart the kernel, and run all cells.
Its first cell installs notebook dependencies if required. The data-loading
cell uses the repository snapshot when available and otherwise downloads data.
In Colab, upload the notebook; upload `reliance_prices.csv` to the session
for exact snapshot results. The final cells contain the generator code,
so no separate Python module upload is required.

## Results

2024 baseline: -0.56% return marked to market; -0.58% after hypothetical
last-close liquidation costs; -5.64% benchmark return; -1.31% drawdown.
There are three completed trades and eight adjusted-price units still held.
Sharpe is about -0.61 and Sortino -0.85 (daily returns, 252-session scaling,
0% risk-free rate / minimum acceptable return).
The full table reports development (2016-2022) separately from final test.

The strategy loses less in this final-test year but does not make money.
Its average exposure is much lower than buy-and-hold. One stock, one year
and three completed trades provide weak evidence for generalisation.

## Evaluation and benchmark

The original 2023 validation results are a slice of a continuous 2016-2023
portfolio, measured from first 2023 close to last 2023 close; the portfolio
is not reset. Exploratory work included validation observations, so that
period was not fully unseen. The 2024 baseline is reset to INR 100,000.
29 December 2023 supplies the baseline date and preceding signal.

Reliance buy-and-hold is justified as the passive alternative on the same
asset: it isolates the value of timing versus simply owning that stock.
It is a fully invested adjusted-close ratio before costs. The strategy is
partly invested and after costs. It is not an exposure-matched or broad-market
benchmark; the report explicitly states this limitation.

## Risk controls and additional experiments

The baseline limits position size, has no leverage, and holds one long
position. It has no stop-loss or holding limit and can remain in a losing
position for a long time. The new development-only experiment adds a 5%
close-triggered loss exit and a 20-session maximum hold, both filled at the
next open. Gaps can cause losses beyond the trigger. This variant worsened
development drawdown and is not adopted as the baseline.

The report also includes a 3x3 nearby-parameter grid and lagged trend-regime
analysis on development data only. These experiments were added after the
2024 baseline outcome was seen; no new variant has an untouched 2024 test.

## Adjusted-price limitation

Adjusted OHLC is used for signals, simulated fills and valuations. Integer
quantities are units in this adjusted-price simulation, not a reconstruction
of actual historical share holdings. Corporate actions and dividend cash
flows are not separately processed. Retrospective adjustments may affect
integer sizing; a realistic execution study needs raw fills and explicit
corporate-action accounting. This is an educational research model.

## Assistance disclosure

ChatGPT/Codex assisted with teaching, code drafting/debugging, repository
review, the metrics/charts extension and technical report. The student must
review the work, be able to explain it, and disclose any further resources.
See `docs/SOURCES.md` for resources actually used.
