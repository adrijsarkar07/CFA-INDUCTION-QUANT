# Reliance Mean-Reversion Backtest

A research project that tests a simple mean-reversion strategy on historical Reliance Industries price data. The project calculates rolling Z-scores, generates entry and exit signals, and evaluates simulated performance after transaction costs and slippage.

## Strategy

- Calculate the rolling mean and standard deviation of closing prices over 20 trading sessions.
- Enter when the Z-score falls below −2.
- Exit when the Z-score returns to 0 or above.
- Execute trades at the next session’s open.
- Include transaction costs and slippage in simulated fills.

## Data and Evaluation

The historical data is divided chronologically into development, validation, and final-test periods. The 2024 final-test period was kept separate from strategy development.

## 2024 Final-Test Result

The strategy returned approximately −0.56% marked to market, compared with −5.64% for buy-and-hold. After estimated liquidation costs for the remaining position, the strategy return was approximately −0.58%.

The strategy had three completed trades and held eight shares at year-end. It lost less than buy-and-hold during this period, but did not make a profit. This single year and small number of trades are limited evidence of future performance.
## Project Files

- [Research notebook](notebooks/reliance.ipynb) — data exploration,
  strategy implementation, backtesting, and evaluation.
- [Dataset documentation](data/README.md) — data source and
  chronological development, validation, and test splits.
- [Results and limitations](docs/results.md) — validation and
  final-test results with interpretation.

## Limitations

This study tests one stock and one strategy specification.
The final-test period contains only three completed trades,
which limits the strength of the conclusions.

The strategy invests only part of the available capital.
Its lower drawdown must therefore be considered alongside
its lower market exposure compared with buy-and-hold.

Transaction costs and slippage are simplified assumptions.
Actual execution costs may differ.
## How to Run

Download this repository as a ZIP and extract it.
Open a terminal in the extracted folder containing requirements.txt.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch Jupyter:

```bash
python -m notebook
```

Open notebooks/reliance.ipynb, restart the kernel, and run all cells
from top to bottom. Internet access is required to download price data.

Historical data may be revised by the provider, so a later download
may produce slightly different results.

## Backtest Assumptions

- Initial capital: ₹100,000.
- Each entry allocates 10% of available cash, including entry fees.
- Only one long position is held at a time.
- Uninvested cash earns no interest.
- Slippage: 0.05% per side.
- Transaction costs: 0.10% per side.

## Evaluation Details

The 2023 validation results are calculated from the 2023 portion
of a continuous 2016–2023 backtest. The portfolio is not reset
at the start of 2023. Returns are measured from the first
2023 session's close to the last session's close.

The 2024 final test starts with a fresh ₹100,000 cash balance.
The last trading session of 2023 supplies the preceding signal
and the baseline date.

Buy-and-hold is an adjusted closing-price ratio without
transaction costs or slippage. The strategy includes both.
The two approaches also have different capital exposure.

## Adjusted-Price Limitation

Adjusted OHLC prices are used for signals, simulated fills,
and portfolio valuation. Integer quantities therefore represent
units in an adjusted-price simulation, rather than a reconstruction
of actual historical share holdings. Corporate actions and
dividend cash flows are not separately processed.
