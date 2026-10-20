# Backtest Results

## Assumptions

- Signals use daily closing prices.
- Orders are simulated at the next trading session's open.
- The backtest includes 0.05% slippage and 0.1% transaction cost on each side.
- The 2024 final-test period was reserved for evaluation.

## 2023 validation

- Strategy return: approximately **+0.26%**
- Buy-and-hold return: approximately **+9.11%**
- Strategy maximum drawdown: approximately **−0.75%**
- Five trades were entered.

The strategy underperformed buy-and-hold during validation.

## 2024 final test

- Strategy return, marked to market: approximately **−0.56%**
- Strategy return after estimated liquidation costs: approximately **−0.58%**

These figures describe the 2023 portion of the continuous
2016–2023 backtest; the portfolio was not restarted in 2023.
Returns are measured from the first 2023 session's close
to the last session's close. The five trades counted are
completed trades whose entry dates fall in 2023.
- Buy-and-hold return: approximately **−5.64%**
- Strategy maximum drawdown: approximately **−1.31%**
- Three completed trades; eight shares remained open at year-end.

The strategy lost less than buy-and-hold during 2024, but still lost money. Its low drawdown should be considered alongside its low capital exposure. Results from one test year and a small number of trades are limited evidence; they do not establish future performance.

## Comparison and Simulation Limitations

The strategy allocates 10% of available cash per entry.
Buy-and-hold represents full exposure through an adjusted
closing-price ratio. Lower strategy drawdown must therefore
be considered alongside lower capital exposure.

Strategy returns include assumed transaction costs and
slippage; buy-and-hold returns exclude both.

The backtest uses adjusted prices for fills and valuation.
Reported quantities, including the eight units held at
year-end, are simulated adjusted-price units. Corporate
actions and dividend cash flows are not separately processed.
