# Induction requirement mapping

| Requirement | File / implementation |
|---|---|
| Loading, checks, EDA | `notebooks/reliance.ipynb`, initial analysis cells |
| Indicators and rules | Notebook baseline; `complete_quant.py:backtest` |
| Position sizing and risk logic | 10% cash sizing; development stop/time-limit experiment |
| Portfolio and trade log | `outputs/development_trades.csv`, `outputs/final_trades.csv`, equity/event CSVs |
| Full metrics table | `outputs/performance_metrics.csv`; report page 2 |
| Technical PDF | `outputs/quant_technical_report.pdf` |
| Equity, drawdown and trade markers | `outputs/figures/`; report pages 3–4 |
| Justified alternative benchmark | Same-asset buy-and-hold; report page 4 and README |
| Nearby parameters / regimes | `outputs/development_sensitivity.csv`, `outputs/development_regimes.csv` |
| Sources and assistance | `docs/SOURCES.md`; report page 6 |
| Reproduction | README, requirements, supplied adjusted-price snapshot |

The baseline test was viewed before the additional development experiments.
A new strategy variant would need a genuinely unseen evaluation period.
The baseline has no explicit stop; the extra risk-control logic is demonstrated
only on development data and is not retroactively added to the final test.
