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
