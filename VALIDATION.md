# Execution and review record

The completion was run on 20 October 2026 using the included 2,221-row
adjusted-price snapshot. The regenerated final-test baseline matches the
original saved results to the reported precision: -0.56% return, -1.31%
drawdown, three completed trades and eight open adjusted-price units.

All notebook code cells were executed sequentially in a fresh in-process
IPython session and their outputs were saved. The environment could not
launch a socket-based Jupyter kernel; this is not a claim of a separate
browser-based Colab or Jupyter run. No code-cell errors remain. The notebook
also passes nbformat schema validation. Actual package versions and data
hash are in outputs/run_metadata.json.

Targeted synthetic checks passed for next-session stop execution, two-sided
fee arithmetic, a 20-session holding limit, undefined zero-variance/no-trade
metrics, and invariance of earlier equity to future data changes. The final
PDF was rendered and visually checked on all six pages; its table/chart
layout was inspected. README links were checked against the packaged files.

GitHub has not been modified by this delivery. Upload the package contents
to the existing repository after reviewing the assistance disclosure and
confirming that you can explain the implementation.
