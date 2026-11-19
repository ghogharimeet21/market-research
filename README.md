# BTCUSDT Rolling Regression Research

An exploratory quantitative-research project investigating whether the direction and goodness-of-fit of a short rolling linear regression are associated with the subsequent direction of BTCUSDT returns.

> **Research status:** Exploratory. This repository does not establish a profitable trading strategy or a validated predictive edge.

## Hypothesis

A linear regression fitted to the most recent 10 one-minute closing prices produces two features:

- **Normalized slope:** regression slope divided by the current close (`regression_m / close`). Its sign represents the direction of the fitted short-term trend.
- **R-squared:** the coefficient of determination for the 10-point regression window. It describes how closely the prices in that window fit a straight line; it is not, by itself, a probability of future continuation.

The research question is whether a positive normalized slope is associated with a positive forward return, and whether this relationship changes when the regression fit is stronger. The corresponding negative-slope condition is evaluated as well.

## Data and measurement

- **Instrument:** Binance spot `BTCUSDT`
- **Base interval:** 1-minute OHLCV candles
- **Included sample:** 129,600 candles spanning 90 days, from 2026-06-23 through 2026-09-20
- **Regression lookback:** 10 candles
- **Forward horizon:** 10 rows (10 minutes when the input contains consecutive one-minute candles)

The forward return is calculated as:

```python
future_return_10m = close.shift(-10) / close - 1
```

The analysis examines conditional directional probabilities for several R-squared cutoffs (`0.5`, `0.6`, `0.7`, `0.8`, and `0.9`):

```text
P(future_return_10m > 0 | normalized_slope > 0, R² > threshold)
P(future_return_10m < 0 | normalized_slope < 0, R² > threshold)
```

It also explores the relationship between normalized slope and forward return using correlation and scatter plots.

## Research workflow

1. Load BTCUSDT historical one-minute OHLCV data.
2. Fit an ordinary least-squares line to each trailing 10-close window.
3. Calculate the regression slope, intercept, and R-squared for each window.
4. Normalize the slope by the current closing price.
5. Calculate the forward 10-minute return.
6. Compare slope direction with forward-return direction, including conditional probabilities across R-squared thresholds.
7. Visualize selected regression windows and the relationship between features and forward returns.

All features are calculated from the current and preceding candles. A value for candle *t* is only available after that candle has closed; it must not be treated as known before the close.

## Repository contents

| File | Purpose |
|---|---|
| `app.ipynb` | Main exploratory analysis of normalized slope, R-squared, forward returns, and conditional directional probabilities |
| `test.ipynb` | Additional experiments with data loading, resampling, and regression calculations |
| `app2.ipynb` | Data loading and multi-timeframe resampling experiments |
| `hypothisis1.ipynb` | Regression-window visualization and related exploratory work (filename as currently present in the repository) |
| `feed.py` | Downloads historical klines from the Binance REST API and converts them to a DataFrame |
| `utils.py` | Date/time helpers, regression calculations, and OHLCV resampling utilities |
| `dataset.csv` | Included 90-day BTCUSDT one-minute OHLCV sample |
| `line_crosses_multiple_times.png`, `streght.png` | Reference chart screenshots from the exploration |

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib requests jupyterlab
jupyter lab
```

Open `app.ipynb` to follow the main analysis. The notebooks use `feed.py` to request historical data from Binance; this requires an internet connection and may fetch a different date range when run later.

To work from the included CSV instead, load it in a notebook and use that DataFrame in place of the API call:

```python
import pandas as pd

dataset = pd.read_csv("dataset.csv", index_col=0)
```

Before calculating rolling features, ensure the data is sorted chronologically and check for missing or duplicate one-minute candles. The forward-return formula uses row offsets, so gaps in the time series would change the effective horizon.

## Important limitations

- This is an exploratory feature study, not a complete trading strategy or backtest.
- Saved notebook outputs may come from a different data download or execution state. Re-run the notebooks against one pinned dataset before interpreting any cached metric. Do not treat old notebook output as a reproducible result.
- Adjacent 10-minute forward-return labels overlap, so observations are dependent. Naive counts and probabilities can overstate the amount of independent evidence.
- The current exploration does not provide walk-forward or held-out out-of-sample validation, confidence intervals, significance tests, or controls for multiple comparisons.
- Transaction fees, spread, slippage, market impact, funding, position sizing, and execution constraints are not modeled.
- A high R-squared only describes the linear fit within the lookback window; it does not guarantee continuation or imply a tradable edge.

## Next research steps

- Pin and document a single dataset snapshot and make the full analysis reproducible from a clean run.
- Validate timestamp continuity and explicitly handle missing candles.
- Use chronological train/test or walk-forward evaluation.
- Account for overlapping labels with non-overlapping samples or dependence-aware statistical methods (for example, block bootstrap or HAC-style errors).
- Compare against simple baselines and test sensitivity to lookback windows and forward horizons.
- Evaluate any eventual trading rule with fees, spread, slippage, and realistic execution assumptions.

## Disclaimer

This project is for educational and research purposes only. It is not investment advice and should not be used as the sole basis for trading decisions.
