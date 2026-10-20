# Backtest results

The authoritative full table is `outputs/performance_metrics.csv` and the
PDF is `outputs/quant_technical_report.pdf`.

## Development 2016–2022

- Cumulative return: +2.70%; CAGR: +0.38%.
- Sharpe: 0.28; Sortino: 0.40; drawdown: -3.32%.
- 24 completed trades; 75% win rate; profit factor: 1.97.
- Buy-and-hold: +428.52%; average strategy exposure: 1.68%.
- Eight adjusted-price units remain held at this period's end.

## Original 2023 validation slice

- Strategy: +0.26%; buy-and-hold: +9.11%; drawdown: -0.75%.
- Five completed trades had entry dates in 2023.

This is the 2023 slice of a continuous 2016–2023 portfolio, measured
first 2023 close to last 2023 close; it is not restarted in 2023.
Exploratory analysis included validation, so it was not fully unseen.

## Final test 2024

- Strategy return marked to market: -0.56%; hypothetical liquidation: -0.58%.
- Buy-and-hold: -5.64%; maximum strategy drawdown: -1.31%.
- Sharpe: -0.61; Sortino: -0.85; profit factor: 0.41.
- Three completed trades; win rate: 33.33%; eight units remain held.
- Average strategy exposure: 2.42%.

The portfolio starts flat with INR 100,000 and uses 29 December 2023 as
the baseline/prior signal date. The strategy lost less in this period,
but was not profitable. The sample is too small for strong conclusions.

## Additional development experiments

A 3x3 grid uses windows 15/20/25 and entry thresholds -2.5/-2/-1.5.
Development returns range from +0.48% to +8.40%. Baseline stays 20/-2.
A 5% close-based stop plus a 20-session limit gives +1.56% return and
-3.95% drawdown versus +2.70% / -3.32% baseline. Added exits did not help
these metrics in this sample; they are not adopted as a revised strategy.

Regimes use prior-day trailing 60-session returns: rising above +5%,
falling below -5%, sideways otherwise. Conditional daily averages are
in `outputs/development_regimes.csv`; they are descriptive, not independent
investable backtests. Baseline strategy mean daily return is positive on
rising/falling-labelled days and slightly negative on sideways-labelled days.
A lagged falling label does not imply that the following day's return is negative.

## Conventions and limitations

Ratios use daily portfolio returns, sqrt(252) scaling, zero risk-free rate
and zero minimum acceptable return. Sortino downside deviation uses all
daily observations, not just negative days. CAGR uses actual days / 365.25.
Trade metrics include completed trades and net costs; equity includes open
positions. N/A denotes absent applicable trades or a zero denominator.

The full-exposure buy-and-hold adjusted-close ratio excludes costs; strategy
returns include costs and have much lower exposure. Adjusted-price quantities
are simulated units, not reconstructed real historical share holdings.
Splits/dividends are not separately processed. New development experiments
were added after observing the baseline final test; no new variant has an
untouched 2024 test. See the PDF for all caveats and suggested improvements.
