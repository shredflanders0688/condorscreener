# Condor Screener

Earnings iron condor screening tool built on free data via yfinance.
No API keys required. No paid subscriptions needed.

## What It Does

- Fetches upcoming earnings calendar from Yahoo Finance
- Pulls live options chains, IV, Greeks, and expected move per ticker
- Calculates term structure slope (front month vs 30 DTE)
- Flags EM sweet spot (configurable, default 5-10%)
- Recommends iron condor strikes balancing breach probability and credit
- Shows macro regime dashboard (VVIX, VIX, SKEW, credit spreads, dispersion, gap frequency)
- Scores and rates each candidate: Strong / Good / Marginal / Avoid
- Manual breach history entry from TOS thinkBack to improve accuracy

## Deploy to Streamlit Cloud (Free)

1. Fork or push this repo to your GitHub account
2. Go to share.streamlit.io
3. Click "New app"
4. Select your repo, branch (main), and set main file path to `app.py`
5. Click Deploy — it will be live in ~2 minutes
6. Access from any device via the Streamlit URL

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage Notes

- **Term structure threshold**: The minimum IV differential between front month and 30 DTE
  to pass the slope filter. Adjust to match your existing Python screener threshold.
- **EM sweet spot**: 5-10% is the default based on historical performance of the strategy.
  Tickers outside this range are flagged but not excluded.
- **Breach history**: Enter manually from TOS thinkBack for your top candidates.
  This is the most valuable input — improves strike recommendations significantly.
- **Regime dashboard**: Refreshes every 15 minutes. Check this before deciding
  whether to trade a given cycle at all.

## Exit Rules (Pre-Commit Before Every Trade)

- **Winner**: Close entire condor at 50% of max credit received
- **Loser**: Close threatened side when it reaches 2× total credit collected
- **Time**: Close full position at market open morning after earnings — no exceptions
- **Never leg out**: Exit as a spread order, not leg by leg

## Data Sources

All free, no API keys required:
- Yahoo Finance via yfinance library
- CBOE indices (VIX, VVIX, SKEW) via yfinance
- HYG ETF as high yield credit spread proxy

## Disclaimer

For informational and educational purposes only. Not financial advice.
Always verify data independently in TOS before placing any trade.
Historical breach data requires manual entry from TOS thinkBack.
