import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import requests
import json
import time
import math

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Condor Screener",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* ── Force white on ALL metric text in main area ── */
  section.main [data-testid="stMetricLabel"],
  section.main [data-testid="stMetricLabel"] *,
  section.main [data-testid="stMetricLabel"] p { color: #ffffff !important; font-weight: 700 !important; font-size: 13px !important; }

  section.main [data-testid="stMetricValue"],
  section.main [data-testid="stMetricValue"] * { color: #ffffff !important; font-weight: 800 !important; font-size: 26px !important; }

  section.main [data-testid="stMetricDelta"],
  section.main [data-testid="stMetricDelta"] * { font-size: 12px !important; }

  /* ── Custom header above expander — connect visually ── */
  section.main details > summary {
    background: #0d1117 !important;
    border: 1px solid #2a3a4a !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 4px 18px !important;
    min-height: 28px !important;
    cursor: pointer !important;
  }
  section.main details[open] > summary {
    border-radius: 0 !important;
  }
  section.main details {
    background: #111318 !important;
    border: 1px solid #2a3a4a !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    margin-top: 0 !important;
    margin-bottom: 4px !important;
  }

  /* ── Tab button text ── */
  section.main button[data-baseweb="tab"],
  section.main button[data-baseweb="tab"] * { color: #ffffff !important; font-weight: 700 !important; font-size: 14px !important; }

  /* ── All paragraph text inside expanders ── */
  section.main [data-testid="stExpander"] p,
  section.main [data-testid="stExpander"] label,
  section.main [data-testid="stExpander"] span { color: #e8eaf0 !important; }

  /* ── Caption text ── */
  section.main [data-testid="stCaptionContainer"] p,
  section.main small { color: #b0b8c8 !important; font-size: 12px !important; }

  /* ── Markdown bold inside expanders ── */
  section.main [data-testid="stExpander"] strong { color: #ffffff !important; }

  /* ── Success/info/warning text ── */
  section.main [data-testid="stAlert"] p { color: #ffffff !important; font-weight: 600 !important; }

  /* ── Number inputs inside expanders ── */
  section.main [data-testid="stExpander"] input { color: #ffffff !important; background: #1e2430 !important; }

  /* ── Expander container ── */
  section.main [data-testid="stExpander"],
  section.main details {
    background-color: #111318 !important;
    border: 1px solid #2a3040 !important;
    border-radius: 10px !important;
  }

  .metric-card {
    background: #111318;
    border: 1px solid #1e2430;
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
  }
  .metric-card-top {
    height: 3px;
    border-radius: 2px 2px 0 0;
    position: absolute;
    top: 0; left: 0; right: 0;
  }
  .metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #a0a8b8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
    color: #ffffff;
  }
  .metric-signal {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    margin-bottom: 6px;
  }
  .metric-desc {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #8090a8;
    line-height: 1.5;
  }
  .regime-pill {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
  }
  .pill-favorable { background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
  .pill-caution   { background: rgba(255,215,64,0.12); color: #ffd740; border: 1px solid rgba(255,215,64,0.3); }
  .pill-hostile   { background: rgba(255,77,106,0.12); color: #ff4d6a; border: 1px solid rgba(255,77,106,0.3); }
  .pill-mixed     { background: rgba(255,145,0,0.12);  color: #ff9100; border: 1px solid rgba(255,145,0,0.3); }

  .score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 13px;
    border: 2px solid;
  }
  .score-a { border-color: #00e676; color: #00e676; }
  .score-b { border-color: #00e5ff; color: #00e5ff; }
  .score-c { border-color: #ffd740; color: #ffd740; }
  .score-d { border-color: #ff9100; color: #ff9100; }
  .score-f { border-color: #ff4d6a; color: #ff4d6a; }

  .rating-strong   { background: rgba(0,230,118,0.15);  color: #00e676; padding: 3px 10px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
  .rating-good     { background: rgba(0,229,255,0.10);  color: #00e5ff; padding: 3px 10px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
  .rating-marginal { background: rgba(255,215,64,0.10); color: #ffd740; padding: 3px 10px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
  .rating-avoid    { background: rgba(255,77,106,0.10); color: #ff4d6a; padding: 3px 10px; border-radius: 20px; font-family: 'Space Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: 1px; }

  .em-green  { color: #00e676; font-weight: 700; }
  .em-yellow { color: #ffd740; font-weight: 700; }
  .em-red    { color: #ff4d6a; font-weight: 700; }

  .section-header {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #a0a8b8;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2430;
    padding-bottom: 8px;
    margin-bottom: 14px;
  }

  div[data-testid="stExpander"] {
    border: 1px solid #1e2430 !important;
    border-radius: 10px !important;
    background: #111318 !important;
  }

  .stDataFrame { font-family: 'Space Mono', monospace; font-size: 11px; }

  /* ── Info/warning boxes inside expanders ── */
  [data-testid="stExpander"] [data-testid="stAlert"] p { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def safe_get(val, default=None):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    return val

def pct(val, decimals=1):
    return f"{val*100:.{decimals}f}%"

def dollar(val, decimals=2):
    return f"${val:.{decimals}f}"

# ─── Regime Data ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)  # Cache 15 min
def fetch_regime_data():
    regime = {}

    try:
        # VIX
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="5d")
        regime['vix'] = float(vix_hist['Close'].iloc[-1]) if not vix_hist.empty else 18.0

        # VVIX
        vvix = yf.Ticker("^VVIX")
        vvix_hist = vvix.history(period="5d")
        regime['vvix'] = float(vvix_hist['Close'].iloc[-1]) if not vvix_hist.empty else 95.0

        # SKEW
        skew = yf.Ticker("^SKEW")
        skew_hist = skew.history(period="5d")
        regime['skew'] = float(skew_hist['Close'].iloc[-1]) if not skew_hist.empty else 138.0

        # HYG as credit proxy (price drop = spread widening)
        hyg = yf.Ticker("HYG")
        hyg_hist = hyg.history(period="30d")
        if not hyg_hist.empty:
            hyg_now  = float(hyg_hist['Close'].iloc[-1])
            hyg_prev = float(hyg_hist['Close'].iloc[0])
            # Rough spread proxy: lower HYG = wider spreads
            # HYG near 80 = ~300bp, near 70 = ~500bp
            regime['credit_spread'] = max(100, int(800 - hyg_now * 6.5))
            regime['hyg_price'] = hyg_now
            regime['hyg_trend'] = 'widening' if hyg_now < hyg_prev else 'tightening'
        else:
            regime['credit_spread'] = 320
            regime['hyg_price'] = 77.0
            regime['hyg_trend'] = 'unknown'

        # Sector dispersion: std dev of recent returns across sector ETFs
        sectors = ['XLK','XLF','XLE','XLV','XLC','XLI','XLY','XLP','XLU','XLRE','XLB']
        returns = []
        for s in sectors:
            try:
                hist = yf.Ticker(s).history(period="5d")
                if len(hist) >= 2:
                    ret = (hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
                    returns.append(ret)
            except:
                pass
        regime['dispersion'] = float(np.std(returns)) if len(returns) > 3 else 1.2

        # Gap frequency — estimate from recent earnings reactions
        # Use a sample of names that recently reported
        recent_reporters = ['META','MSFT','GOOGL','AMZN','AAPL','NVDA','AMD','NFLX']
        gap_count = 0
        total_checked = 0
        for ticker in recent_reporters:
            try:
                t = yf.Ticker(ticker)
                cal = t.calendar
                hist = t.history(period="30d")
                if len(hist) >= 5:
                    # Look for large overnight gaps as proxy for earnings gaps
                    for i in range(1, min(5, len(hist))):
                        gap = abs(hist['Open'].iloc[i] / hist['Close'].iloc[i-1] - 1)
                        if gap > 0.03:  # >3% overnight gap
                            gap_count += 1
                            break
                    total_checked += 1
            except:
                pass
        regime['gap_frequency'] = int((gap_count / max(total_checked, 1)) * 100)

    except Exception as e:
        # Safe fallbacks
        regime.setdefault('vix', 18.0)
        regime.setdefault('vvix', 95.0)
        regime.setdefault('skew', 138.0)
        regime.setdefault('credit_spread', 320)
        regime.setdefault('hyg_price', 77.0)
        regime.setdefault('hyg_trend', 'unknown')
        regime.setdefault('dispersion', 1.2)
        regime.setdefault('gap_frequency', 30)

    return regime

def score_regime(r):
    signals = {}

    # VVIX: <85 good, 85-100 warn, >100 bad
    if r['vvix'] < 85:    signals['vvix'] = ('good', '#00e676', '✓ Calm')
    elif r['vvix'] < 100: signals['vvix'] = ('warn', '#ffd740', '⚠ Elevated')
    else:                 signals['vvix'] = ('bad',  '#ff4d6a', '✗ High')

    # VIX: <18 good, 18-25 warn, >25 bad
    if r['vix'] < 18:    signals['vix'] = ('good', '#00e676', '✓ Favorable (15-22 sweet spot)')
    elif r['vix'] < 25:  signals['vix'] = ('warn', '#ffd740', '⚠ Moderate')
    else:                signals['vix'] = ('bad',  '#ff4d6a', '✗ Elevated')

    # SKEW: <130 good, 130-145 warn, >145 bad
    if r['skew'] < 130:   signals['skew'] = ('good', '#00e676', '✓ Normal tail risk')
    elif r['skew'] < 145: signals['skew'] = ('warn', '#ffd740', '⚠ Elevated hedging')
    else:                 signals['skew'] = ('bad',  '#ff4d6a', '✗ Heavy tail hedging')

    # Credit: <300 good, 300-450 warn, >450 bad
    if r['credit_spread'] < 300:   signals['credit'] = ('good', '#00e676', '✓ Tight spreads')
    elif r['credit_spread'] < 450: signals['credit'] = ('warn', '#ffd740', f"⚠ Widening ({r['hyg_trend']})")
    else:                          signals['credit'] = ('bad',  '#ff4d6a', '✗ Wide — stress signal')

    # Dispersion: <1.0 good, 1.0-2.0 warn, >2.0 bad
    if r['dispersion'] < 1.0:   signals['dispersion'] = ('good', '#00e676', '✓ Low sector divergence')
    elif r['dispersion'] < 2.0: signals['dispersion'] = ('warn', '#ffd740', '⚠ Moderate dispersion')
    else:                       signals['dispersion'] = ('bad',  '#ff4d6a', '✗ High — macro bleed risk')

    # Gap freq: <30 good, 30-45 warn, >45 bad
    if r['gap_frequency'] < 30:   signals['gap_freq'] = ('good', '#00e676', '✓ EM mostly respected')
    elif r['gap_frequency'] < 45: signals['gap_freq'] = ('warn', '#ffd740', '⚠ Elevated gap risk')
    else:                         signals['gap_freq'] = ('bad',  '#ff4d6a', '✗ EM frequently blown out')

    bad_count  = sum(1 for s in signals.values() if s[0] == 'bad')
    good_count = sum(1 for s in signals.values() if s[0] == 'good')

    if bad_count >= 3:       verdict = ('HOSTILE — SIT OUT',    'pill-hostile')
    elif bad_count >= 2:     verdict = ('CAUTION — SIZE DOWN',  'pill-caution')
    elif good_count >= 4:    verdict = ('FAVORABLE — TRADE',    'pill-favorable')
    else:                    verdict = ('MIXED — BE SELECTIVE', 'pill-mixed')

    return signals, verdict

# ─── Market Cap Parser ───────────────────────────────────────────────────────
def parse_market_cap_billions(mc_str):
    """
    Parse Nasdaq market cap strings like '$14.2B', '$890M', '$1.2T' into billions.
    Returns None if unparseable.
    """
    if not mc_str or mc_str in ('', 'N/A', '--', 'NA'):
        return None
    try:
        s = mc_str.replace('$', '').replace(',', '').strip()
        if s.endswith('T'):
            return float(s[:-1]) * 1000
        elif s.endswith('B'):
            return float(s[:-1])
        elif s.endswith('M'):
            return float(s[:-1]) / 1000
        else:
            v = float(s)
            # Raw numbers from Nasdaq are in millions
            return v / 1000
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_earnings_calendar(days_ahead, min_market_cap_b=2.0):
    """Fetch upcoming earnings, filtered by market cap from Nasdaq API data."""

    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)
    found = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    date_cursor = today
    while date_cursor <= end_date:
        if date_cursor.weekday() < 5:
            try:
                url = f"https://api.nasdaq.com/api/calendar/earnings?date={date_cursor.strftime('%Y-%m-%d')}"
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    rows = data.get('data', {}).get('rows', [])
                    if rows:
                        for row in rows:
                            ticker = row.get('symbol', '').strip().upper()
                            if not ticker or '/' in ticker or '.' in ticker or len(ticker) > 5:
                                continue

                            # Try multiple possible field names for market cap
                            mc_raw = (row.get('marketCap') or row.get('mktCap') or
                                      row.get('market_cap') or row.get('mktcap') or '')
                            mc_b = parse_market_cap_billions(str(mc_raw))

                            # Only keep if market cap is parseable AND meets threshold
                            # This prevents unknown small caps from slipping through
                            if mc_b is None or mc_b < min_market_cap_b:
                                continue

                            time_str = row.get('time', '').lower()
                            timing = 'BMO' if 'before' in time_str else 'AMC'
                            found[ticker] = {
                                'date':         date_cursor,
                                'timing':       timing,
                                'market_cap':   mc_raw,
                                'market_cap_b': mc_b,
                            }
            except Exception:
                pass
        date_cursor += timedelta(days=1)
        time.sleep(0.2)

    # ── If Nasdaq market cap data is sparse, fall back to known liquid names ──
    if len(found) < 5:
        st.warning("Nasdaq market cap data unavailable — using curated liquid universe.")
        found = yfinance_calendar_fallback(today, end_date)
        return found

    # ── Sort by market cap descending so largest caps get scanned first ───────
    sorted_found = dict(
        sorted(found.items(), key=lambda x: x[1].get('market_cap_b') or 0, reverse=True)
    )

    # ── Hard cap: never scan more than 100 tickers regardless ────────────────
    if len(sorted_found) > 100:
        sorted_found = dict(list(sorted_found.items())[:100])

    return sorted_found


def yfinance_calendar_fallback(today, end_date):
    """Last resort: scan known liquid tickers via yfinance earnings_dates"""
    liquid_universe = [
        'AAPL','MSFT','GOOGL','AMZN','META','NVDA','TSLA','AMD','NFLX',
        'JPM','GS','BAC','V','MA','WMT','HD','DIS','UBER','COIN',
        'PLTR','SNOW','DDOG','CRWD','NET','SHOP','MELI','RIVN','SOFI'
    ]
    found = {}
    for ticker in liquid_universe:
        try:
            t = yf.Ticker(ticker)
            ed = t.earnings_dates
            if ed is not None and not ed.empty:
                for idx in ed.index:
                    d = idx.date() if hasattr(idx, 'date') else idx
                    if today <= d <= end_date:
                        found[ticker] = {'date': d, 'timing': 'AMC'}
                        break
            time.sleep(0.1)
        except:
            pass
    return found

# ─── BSM Greeks (always used as primary) ─────────────────────────────────────
from scipy.stats import norm as _norm

def bsm_call_price(S, K, T, sigma, r=0.05):
    """BSM call price — used inside the IV solver."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * _norm.cdf(d1) - K * math.exp(-r * T) * _norm.cdf(d2)


def implied_vol_from_mid(S, K, T, mid_price, r=0.05,
                          lo=0.001, hi=5.0, tol=1e-5, max_iter=100):
    """
    Back-solve BSM for IV given the bid-ask mid price.
    Uses bisection — robust, no risk of Newton divergence.
    Returns None if the mid is outside the valid BSM price range.
    """
    try:
        if mid_price <= 0 or T <= 0 or S <= 0 or K <= 0:
            return None
        intrinsic = max(S - K * math.exp(-r * T), 0)
        if mid_price < intrinsic:
            return None
        # Bisection
        for _ in range(max_iter):
            mid_sigma = (lo + hi) / 2
            price = bsm_call_price(S, K, T, mid_sigma, r)
            if abs(price - mid_price) < tol:
                return round(mid_sigma, 6)
            if price < mid_price:
                lo = mid_sigma
            else:
                hi = mid_sigma
        return round((lo + hi) / 2, 6)
    except Exception:
        return None


def bsm_greeks(S, K, T, sigma, r=0.05):
    """
    Full Black-Scholes-Merton Greeks for a call option.
    S     = underlying price
    K     = strike
    T     = time to expiry in years
    sigma = implied volatility (decimal)
    r     = risk-free rate
    Returns (delta, gamma, theta, vega)
    """
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0.50, 0.02, -0.10, 0.20
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        delta = _norm.cdf(d1)
        gamma = _norm.pdf(d1) / (S * sigma * math.sqrt(T))
        theta = (
            -(S * _norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
            - r * K * math.exp(-r * T) * _norm.cdf(d2)
        ) / 365
        vega = S * _norm.pdf(d1) * math.sqrt(T) / 100
        return (
            round(delta, 4),
            round(gamma, 4),
            round(theta, 4),
            round(vega,  4)
        )
    except Exception:
        return 0.50, 0.02, -0.10, 0.20


# ─── Options Data ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_options_data(ticker, em_min, em_max, min_oi):
    """
    Fetch live options chain. IV priority:
      1. Back-solve BSM from bid-ask mid (most accurate)
      2. Yahoo's impliedVolatility field (fallback)
      3. BSM approximation from last price (last resort)
    Never hard-fails on IV — always returns something usable.
    """
    result = {
        'ticker':        ticker,
        'price':         None,
        'front_iv':      None,
        'back_iv':       None,
        'slope':         None,
        'slope_pct':     None,
        'spline_slope':  None,   # ts_slope_0_45 from spline
        'spline_pass':   None,   # True/False vs -0.00406 threshold
        'rv30':          None,   # Yang-Zhang 30-day RV
        'iv_rv_ratio':   None,   # iv30 / rv30
        'iv_rv_pass':    None,   # True if >= 1.25
        'avg_volume':    None,
        'volume_pass':   None,   # True if >= 1.5M
        'delta':         None,
        'gamma':         None,
        'theta':         None,
        'vega':          None,
        'em':            None,
        'em_flag':       'unknown',
        'open_interest': None,
        'liquidity_ok':  False,
        'call_strikes':  [],
        'put_strikes':   [],
        'iv_source':     'unknown',
        'error':         None
    }

    try:
        t = yf.Ticker(ticker)

        # ── Price + 3-month history ───────────────────────────────────
        hist = t.history(period="3mo")
        if hist.empty:
            result['error'] = 'No price data'
            return result
        price = float(hist['Close'].iloc[-1])
        if price <= 0:
            result['error'] = 'Invalid price'
            return result
        result['price'] = price

        # ── Yang-Zhang Realized Volatility (30-day) ───────────────────
        if len(hist) >= 32:
            result['rv30'] = yang_zhang_rv(hist, window=30)

        # ── Average Volume (30-day) ───────────────────────────────────
        try:
            avg_vol = float(hist['Volume'].rolling(30).mean().dropna().iloc[-1])
            result['avg_volume']  = avg_vol
            result['volume_pass'] = avg_vol >= 1_500_000
        except Exception:
            pass

        # ── Expiries ──────────────────────────────────────────────────
        expiries = t.options
        if not expiries or len(expiries) < 2:
            result['error'] = 'No options listed'
            return result

        today = datetime.now().date()
        front_expiry = front_dte = None
        back_expiry  = back_dte  = None

        for exp in expiries:
            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
            dte = (exp_date - today).days
            if front_expiry is None and dte >= 0:
                front_expiry = exp
                front_dte    = max(dte, 1)
            elif back_expiry is None and dte >= 20:
                back_expiry = exp
                back_dte    = max(dte, 1)
            if front_expiry and back_expiry:
                break

        if not front_expiry or not back_expiry:
            result['error'] = 'Could not find suitable expiries'
            return result

        T_front = front_dte / 365.0
        T_back  = back_dte  / 365.0

        # ── Chains ────────────────────────────────────────────────────
        front_chain = t.option_chain(front_expiry)
        back_chain  = t.option_chain(back_expiry)
        front_calls = front_chain.calls
        front_puts  = front_chain.puts
        back_calls  = back_chain.calls

        if front_calls.empty:
            result['error'] = 'No front month calls'
            return result

        # ── Real strikes ──────────────────────────────────────────────
        result['call_strikes'] = sorted(front_calls['strike'].dropna().tolist())
        result['put_strikes']  = sorted(
            front_puts['strike'].dropna().tolist()
            if not front_puts.empty else result['call_strikes']
        )

        # ── ATM strike ────────────────────────────────────────────────
        atm_idx    = (front_calls['strike'] - price).abs().idxmin()
        atm_strike = float(front_calls.loc[atm_idx, 'strike'])
        atm_call   = front_calls.loc[atm_idx]

        # ── Open interest ─────────────────────────────────────────────
        result['open_interest'] = int(safe_get(atm_call.get('openInterest'), 0))
        result['liquidity_ok']  = result['open_interest'] >= min_oi

        # ── Front IV — three-tier fallback ────────────────────────────
        front_iv = None

        # Tier 1: back-solve from bid-ask mid
        try:
            bid = float(safe_get(atm_call.get('bid'), 0) or 0)
            ask = float(safe_get(atm_call.get('ask'), 0) or 0)
            if bid > 0 or ask > 0:
                mid = (bid + ask) / 2 if ask > 0 else bid
                front_iv = implied_vol_from_mid(price, atm_strike, T_front, mid)
                if front_iv and front_iv > 0:
                    result['iv_source'] = 'bsm_backsolved'
        except Exception:
            pass

        # Tier 2: Yahoo's pre-calculated IV
        if not front_iv or front_iv <= 0:
            try:
                yiv = safe_get(atm_call.get('impliedVolatility'), None)
                if yiv and float(yiv) > 0 and not math.isnan(float(yiv)):
                    front_iv = float(yiv)
                    result['iv_source'] = 'yahoo'
            except Exception:
                pass

        # Tier 3: BSM approximation from last price
        if not front_iv or front_iv <= 0:
            try:
                last = float(safe_get(atm_call.get('lastPrice'), 0) or 0)
                if last > 0:
                    front_iv = implied_vol_from_mid(price, atm_strike, T_front, last)
                    if front_iv and front_iv > 0:
                        result['iv_source'] = 'bsm_lastprice'
            except Exception:
                pass

        # Final guard
        if not front_iv or front_iv <= 0:
            result['error'] = 'Could not determine IV (market may be closed)'
            return result

        result['front_iv'] = round(float(front_iv), 4)

        # ── BSM Greeks ────────────────────────────────────────────────
        result['delta'], result['gamma'], result['theta'], result['vega'] = \
            bsm_greeks(price, atm_strike, T_front, front_iv)

        # ── Expected Move — straddle mid / price ─────────────────────
        em = None
        try:
            atm_put_rows = front_puts[front_puts['strike'] == atm_strike]
            if not atm_put_rows.empty:
                c_bid = float(safe_get(atm_call.get('bid'), 0) or 0)
                c_ask = float(safe_get(atm_call.get('ask'), 0) or 0)
                p_bid = float(safe_get(atm_put_rows.iloc[0].get('bid'), 0) or 0)
                p_ask = float(safe_get(atm_put_rows.iloc[0].get('ask'), 0) or 0)
                c_mid = (c_bid + c_ask) / 2 if (c_bid + c_ask) > 0 else float(safe_get(atm_call.get('lastPrice'), 0) or 0)
                p_mid = (p_bid + p_ask) / 2 if (p_bid + p_ask) > 0 else float(safe_get(atm_put_rows.iloc[0].get('lastPrice'), 0) or 0)
                if (c_mid + p_mid) > 0:
                    em = (c_mid + p_mid) / price
        except Exception:
            pass

        # Fallback: BSM ATM approximation
        if not em or em <= 0:
            em = 0.8 * front_iv * math.sqrt(T_front)

        result['em'] = round(float(em), 4)

        # ── Back month IV ─────────────────────────────────────────────
        back_iv = None
        if not back_calls.empty:
            try:
                back_atm_idx   = (back_calls['strike'] - price).abs().idxmin()
                back_atm_call  = back_calls.loc[back_atm_idx]
                back_strike    = float(back_atm_call['strike'])

                b_bid = float(safe_get(back_atm_call.get('bid'), 0) or 0)
                b_ask = float(safe_get(back_atm_call.get('ask'), 0) or 0)
                if b_bid > 0 or b_ask > 0:
                    b_mid  = (b_bid + b_ask) / 2 if b_ask > 0 else b_bid
                    back_iv = implied_vol_from_mid(price, back_strike, T_back, b_mid)

                if not back_iv or back_iv <= 0:
                    yiv2 = safe_get(back_atm_call.get('impliedVolatility'), None)
                    if yiv2 and float(yiv2) > 0:
                        back_iv = float(yiv2)
            except Exception:
                pass

        result['back_iv'] = round(float(back_iv) if back_iv and back_iv > 0 else front_iv * 0.65, 4)

        # ── Spline term structure across ALL expiries ─────────────────
        try:
            # Build dict of all available chains for spline
            all_chains = {}
            for exp in expiries[:8]:  # cap at 8 expiries for speed
                try:
                    all_chains[exp] = t.option_chain(exp)
                except Exception:
                    pass

            term_fn, spline_dtes, spline_ivs = build_spline_term_structure(
                all_chains, price, price  # use current price as underlying
            )
            if term_fn and spline_dtes:
                slope = ts_slope_0_45(term_fn, spline_dtes)
                result['spline_slope'] = slope
                result['spline_pass']  = slope is not None and slope <= -0.00406
        except Exception:
            pass

        # ── IV/RV Ratio ───────────────────────────────────────────────
        try:
            iv30 = result['back_iv']  # 30 DTE IV is our iv30
            rv30 = result['rv30']
            if iv30 and rv30 and rv30 > 0:
                ratio = round(iv30 / rv30, 3)
                result['iv_rv_ratio'] = ratio
                result['iv_rv_pass']  = ratio >= 1.25
        except Exception:
            pass

        # ── Simple slope (front - back, keep for display) ─────────────
        result['slope']     = round(result['front_iv'] - result['back_iv'], 4)
        result['slope_pct'] = round((result['slope'] / max(result['back_iv'], 0.01)) * 100, 2)

        # ── EM flag ───────────────────────────────────────────────────
        em = result['em']
        if em_min <= em <= em_max:
            result['em_flag'] = 'green'
        elif em < em_min * 0.7 or em > em_max * 1.4:
            result['em_flag'] = 'red'
        else:
            result['em_flag'] = 'yellow'

    except Exception as e:
        result['error'] = str(e)[:80]

    return result

# ─── Yang-Zhang Realized Volatility ──────────────────────────────────────────
def yang_zhang_rv(price_data, window=30, trading_periods=252):
    """
    Yang-Zhang volatility estimator — accounts for overnight gaps,
    opening jumps, and intraday range. More accurate than close-to-close RV.
    Returns annualized RV as a decimal (e.g. 0.32 = 32%).
    """
    try:
        log_ho = (price_data['High']  / price_data['Open']).apply(np.log)
        log_lo = (price_data['Low']   / price_data['Open']).apply(np.log)
        log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
        log_oc = (price_data['Open']  / price_data['Close'].shift(1)).apply(np.log)
        log_cc = (price_data['Close'] / price_data['Close'].shift(1)).apply(np.log)

        log_oc_sq = log_oc ** 2
        log_cc_sq = log_cc ** 2
        rs        = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)

        close_vol  = log_cc_sq.rolling(window=window).sum() * (1.0 / (window - 1.0))
        open_vol   = log_oc_sq.rolling(window=window).sum() * (1.0 / (window - 1.0))
        window_rs  = rs.rolling(window=window).sum()        * (1.0 / (window - 1.0))

        k      = 0.34 / (1.34 + ((window + 1) / (window - 1)))
        result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(trading_periods)

        val = float(result.iloc[-1])
        return val if not math.isnan(val) and val > 0 else None
    except Exception:
        return None


# ─── Spline Term Structure ────────────────────────────────────────────────────
def build_spline_term_structure(expiries, price, underlying_price):
    """
    Build a spline across all available expiries using ATM IV from each chain.
    Returns (spline_fn, dtes, ivs) or (None, [], []) on failure.
    The spline_fn takes a DTE and returns interpolated IV.
    """
    from scipy.interpolate import interp1d
    today = datetime.now().date()
    dtes, ivs = [], []

    for exp, chain in expiries.items():
        try:
            calls = chain.calls
            puts  = chain.puts
            if calls.empty or puts.empty:
                continue

            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
            dte = (exp_date - today).days
            if dte < 1:
                continue

            c_idx  = (calls['strike'] - underlying_price).abs().idxmin()
            p_idx  = (puts['strike']  - underlying_price).abs().idxmin()
            c_iv   = safe_get(calls.loc[c_idx, 'impliedVolatility'], None)
            p_iv   = safe_get(puts.loc[p_idx,  'impliedVolatility'], None)

            if c_iv and p_iv and float(c_iv) > 0 and float(p_iv) > 0:
                avg_iv = (float(c_iv) + float(p_iv)) / 2.0
                dtes.append(dte)
                ivs.append(avg_iv)
        except Exception:
            continue

    if len(dtes) < 2:
        return None, dtes, ivs

    # Sort by DTE
    pairs  = sorted(zip(dtes, ivs))
    dtes   = [p[0] for p in pairs]
    ivs    = [p[1] for p in pairs]

    try:
        spline = interp1d(dtes, ivs, kind='linear', fill_value='extrapolate')
        def term_fn(dte):
            if dte < dtes[0]:   return ivs[0]
            elif dte > dtes[-1]: return ivs[-1]
            return float(spline(dte))
        return term_fn, dtes, ivs
    except Exception:
        return None, dtes, ivs


def ts_slope_0_45(term_fn, dtes):
    """
    Slope between nearest expiry and 45 DTE.
    Threshold from original screener: <= -0.00406 passes.
    Negative slope = contango (front IV > back IV) = event premium loaded in front.
    """
    try:
        near_dte = dtes[0]
        if near_dte >= 45:
            return None
        slope = (term_fn(45) - term_fn(near_dte)) / (45 - near_dte)
        return round(slope, 6)
    except Exception:
        return None


# ─── Strike Snapping Helper ───────────────────────────────────────────────────
def snap_to_real_strike(target, available_strikes, direction='nearest'):
    """
    Snap a target price to the nearest real strike in the chain.
    direction: 'nearest' | 'above' | 'below'
    """
    if not available_strikes:
        return round(target / 0.5) * 0.5  # fallback if no chain
    strikes = sorted(available_strikes)
    if direction == 'above':
        above = [s for s in strikes if s >= target]
        return float(above[0]) if above else float(strikes[-1])
    elif direction == 'below':
        below = [s for s in strikes if s <= target]
        return float(below[-1]) if below else float(strikes[0])
    else:
        return float(min(strikes, key=lambda s: abs(s - target)))


# ─── Condor Strikes ───────────────────────────────────────────────────────────
def recommend_condor(price, em, iv, breach_count, breach_quarters, breach_avg_mag,
                     slope_threshold, call_strikes=None, put_strikes=None):
    """
    Recommend iron condor strikes, snapped to real available strikes.
    call_strikes / put_strikes: actual strike lists from the options chain.
    """
    # ── Input validation ──────────────────────────────────────────────────────
    try:
        price = float(price)
        em    = float(em)
        iv    = float(iv)
        if any(math.isnan(v) or math.isinf(v) for v in [price, em, iv]):
            raise ValueError("NaN/Inf")
        if price <= 0 or em <= 0:
            raise ValueError("Non-positive")
    except Exception:
        return {
            'short_call': 0, 'long_call': 0, 'short_put': 0, 'long_put': 0,
            'wing_width': 0, 'credit': 0, 'max_loss': 0,
            'prob_profit': 0, 'ev': 0, 'breach_rate': 0, 'buffer_used': 1.0,
            'strikes_real': False
        }

    call_strikes = call_strikes or []
    put_strikes  = put_strikes  or []

    # ── Breach-adjusted buffer ────────────────────────────────────────────────
    buffer     = 1.05
    breach_rate = 0.0

    if breach_count is not None and breach_quarters and int(breach_quarters) > 0:
        try:
            breach_rate = int(breach_count) / int(breach_quarters)
            if breach_rate > 0.5:    buffer = 1.35
            elif breach_rate > 0.25: buffer = 1.15
            else:                    buffer = 1.0
            if breach_avg_mag and not math.isnan(float(breach_avg_mag)):
                buffer += float(breach_avg_mag) * 0.4
        except Exception:
            pass

    # ── Ideal (mathematical) short strikes ───────────────────────────────────
    move_amount      = price * em * buffer
    ideal_short_call = price + move_amount
    ideal_short_put  = price - move_amount

    # ── Snap to nearest REAL strikes ─────────────────────────────────────────
    # Short call: snap to first real strike AT or ABOVE ideal
    # Short put:  snap to first real strike AT or BELOW ideal
    short_call = snap_to_real_strike(ideal_short_call, call_strikes, direction='above')
    short_put  = snap_to_real_strike(ideal_short_put,  put_strikes,  direction='below')

    # ── Wing width: next available strike beyond each short ───────────────────
    # Long call = next real strike above short call
    # Long put  = next real strike below short put
    long_call = snap_to_real_strike(short_call + 0.01, call_strikes, direction='above')
    long_put  = snap_to_real_strike(short_put  - 0.01, put_strikes,  direction='below')

    # Ensure long != short (edge case when at chain boundary)
    if long_call == short_call and call_strikes:
        above = [s for s in sorted(call_strikes) if s > short_call]
        long_call = float(above[0]) if above else short_call + 2.5
    if long_put == short_put and put_strikes:
        below = [s for s in sorted(put_strikes, reverse=True) if s < short_put]
        long_put = float(below[0]) if below else short_put - 2.5

    call_wing = round(long_call - short_call, 2)
    put_wing  = round(short_put - long_put,   2)
    wing_width = min(call_wing, put_wing)   # use the tighter side for conservative math

    # ── Credit and max loss estimate ─────────────────────────────────────────
    credit_pct = max(0.10, min(0.25, 0.10 + (iv - 0.25) * 0.3))
    credit     = round(wing_width * credit_pct * 2, 2)   # both sides combined
    max_loss   = round(wing_width - (credit / 2), 2)      # per side

    # ── Probability and EV ────────────────────────────────────────────────────
    prob_profit = max(40, min(90, int((1 - breach_rate) * 100 - 5)))
    ev = (credit * 100 * prob_profit / 100) - (max_loss * 100 * (1 - prob_profit / 100))

    return {
        'short_call':   short_call,
        'long_call':    long_call,
        'short_put':    short_put,
        'long_put':     long_put,
        'call_wing':    call_wing,
        'put_wing':     put_wing,
        'wing_width':   wing_width,
        'credit':       credit,
        'max_loss':     max_loss,
        'prob_profit':  prob_profit,
        'ev':           round(ev, 2),
        'breach_rate':  breach_rate,
        'buffer_used':  buffer,
        'strikes_real': bool(call_strikes and put_strikes)
    }

# ─── Scoring ──────────────────────────────────────────────────────────────────
def calculate_score(em, em_min, em_max, slope, slope_threshold,
                    breach_count, breach_quarters, liquidity_ok, front_iv,
                    spline_pass=None, iv_rv_pass=None, volume_pass=None):
    score = 0

    # EM in sweet spot (20 pts)
    if em_min <= em <= em_max:               score += 20
    elif em_min * 0.8 <= em <= em_max * 1.2: score += 10

    # Spline term structure slope (20 pts)
    # Use spline pass/fail if available, fall back to simple slope ratio
    if spline_pass is True:
        score += 20
    elif spline_pass is False:
        score += 0
    else:
        # Fallback: simple slope ratio against threshold
        slope_ratio = slope / max(slope_threshold, 0.001)
        score += min(20, int(slope_ratio * 20))

    # IV/RV ratio >= 1.25 (20 pts)
    if iv_rv_pass is True:
        score += 20
    elif iv_rv_pass is None:
        score += 10  # Unknown = neutral

    # Volume >= 1.5M (10 pts)
    if volume_pass is True:
        score += 10
    elif volume_pass is None:
        score += 5   # Unknown = neutral

    # Breach history (20 pts)
    if breach_count is not None and breach_quarters and breach_quarters > 0:
        rate = breach_count / breach_quarters
        if rate == 0:        score += 20
        elif rate <= 0.25:   score += 16
        elif rate <= 0.375:  score += 8
        elif rate <= 0.5:    score += 3
    else:
        score += 10  # Unknown = neutral

    # Liquidity / OI (10 pts)
    score += 10 if liquidity_ok else 3

    return min(100, score)

def get_rating(score):
    if score >= 75:   return 'strong'
    elif score >= 55: return 'good'
    elif score >= 35: return 'marginal'
    return 'avoid'

# ─── Breach Data Persistence ───────────────────────────────────────────────────
def load_breach_data():
    if 'breach_data' not in st.session_state:
        st.session_state.breach_data = {}
    return st.session_state.breach_data

def save_breach_entry(ticker, count, avg_mag, quarters):
    if 'breach_data' not in st.session_state:
        st.session_state.breach_data = {}
    st.session_state.breach_data[ticker] = {
        'count': count,
        'avg_mag': avg_mag / 100 if avg_mag else None,
        'quarters': quarters
    }

# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div style='margin-bottom:8px'>
      <div style='font-family:"Space Mono",monospace;font-size:10px;color:#00e5ff;letter-spacing:3px;text-transform:uppercase;margin-bottom:4px'>
        // Earnings Vol Intelligence
      </div>
      <div style='font-family:"Syne",sans-serif;font-size:32px;font-weight:800;letter-spacing:-1px;line-height:1'>
        Condor <span style='color:#00e5ff'>Screener</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Free data via yfinance · {datetime.now().strftime('%A, %B %d %Y')}")

    # ── Sidebar Controls ──────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Screener Settings")

        days_ahead = st.selectbox(
            "Earnings Window",
            [3, 7, 14, 30],
            index=1,
            format_func=lambda x: f"Next {x} days"
        )

        slope_threshold = st.slider(
            "Term Structure Threshold (%)",
            min_value=1.0, max_value=20.0, value=5.0, step=0.5,
            help="Minimum IV differential between front and 30DTE to pass the slope filter"
        ) / 100

        em_min = st.slider(
            "EM Sweet Spot — Min (%)",
            min_value=2.0, max_value=8.0, value=5.0, step=0.5
        ) / 100

        em_max = st.slider(
            "EM Sweet Spot — Max (%)",
            min_value=8.0, max_value=20.0, value=10.0, step=0.5
        ) / 100

        min_oi = st.selectbox(
            "Min Open Interest",
            [100, 500, 1000, 5000],
            index=1,
            format_func=lambda x: f"{x:,}+"
        )

        min_market_cap = st.selectbox(
            "Min Market Cap",
            [0.5, 1.0, 2.0, 5.0, 10.0],
            index=2,
            format_func=lambda x: f"${x:.1f}B+"
        )

        st.markdown("---")
        st.markdown("### 📋 Filter Results")
        rating_filter = st.multiselect(
            "Show ratings",
            ['strong', 'good', 'marginal', 'avoid'],
            default=['strong', 'good', 'marginal']
        )

        st.markdown("---")
        run_screener = st.button("▶ Run Screener", type="primary", use_container_width=True)
        if st.button("↻ Refresh Regime Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Regime Dashboard ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">// MACRO REGIME DASHBOARD</div>', unsafe_allow_html=True)

    with st.spinner("Loading regime indicators..."):
        regime = fetch_regime_data()
    signals, verdict = score_regime(regime)

    verdict_text, verdict_class = verdict
    st.markdown(
        f'<div style="margin-bottom:16px">Trade Regime: '
        f'<span class="regime-pill {verdict_class}">{verdict_text}</span></div>',
        unsafe_allow_html=True
    )

    # Six metric cards
    metric_defs = [
        ('vvix',       'VVICKS',            f"{regime['vvix']:.1f}",
         'Vol of vol — uncertainty about future vol. Under 85 = calm.'),
        ('vix',        'VICKS',             f"{regime['vix']:.1f}",
         'S&P 30-day implied vol. Strategy sweet spot: 15–22.'),
        ('skew',       'SKEW INDEX',        f"{regime['skew']:.1f}",
         'Tail risk demand. Elevated = institutions buying downside protection.'),
        ('credit',     'CREDIT SPREADS',    f"{regime['credit_spread']}bp",
         f"HY proxy via HYG (${regime['hyg_price']:.2f}, {regime['hyg_trend']}). Widening = stress signal."),
        ('dispersion', 'SECTOR DISPERSION', f"{regime['dispersion']:.2f}σ",
         'Cross-sector return std dev. High = macro bleed amplifying gaps.'),
        ('gap_freq',   'RECENT GAP FREQ',   f"{regime['gap_frequency']}%",
         '% of recent reporters with >3% overnight gap. Most direct strategy risk.'),
    ]

    cols = st.columns(6)
    for i, (key, name, value, desc) in enumerate(metric_defs):
        sig, color, label = signals[key]
        top_color = color
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-card-top" style="background:{top_color}"></div>
              <div class="metric-label">{name}</div>
              <div class="metric-value" style="color:{color}">{value}</div>
              <div class="metric-signal" style="color:{color}">{label}</div>
              <div class="metric-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Checklist
    flag_items = []
    flag_labels = {
        'vvix': 'VVICKS', 'vix': 'VICKS', 'skew': 'SKEW',
        'credit': 'CREDIT', 'dispersion': 'DISPERSION', 'gap_freq': 'GAP FREQ'
    }
    flag_html = '<div style="margin-top:14px;display:flex;gap:6px;flex-wrap:wrap;align-items:center">'
    flag_html += '<span style="font-family:\'Space Mono\',monospace;font-size:9px;color:#5a6070;letter-spacing:1px">CHECKLIST:</span>'
    for key, label in flag_labels.items():
        sig, color, _ = signals[key]
        icon = '✓' if sig == 'good' else '⚠' if sig == 'warn' else '✗'
        bg   = 'rgba(0,230,118,0.12)' if sig == 'good' else 'rgba(255,215,64,0.12)' if sig == 'warn' else 'rgba(255,77,106,0.12)'
        flag_html += f'<span style="background:{bg};color:{color};padding:2px 8px;border-radius:3px;font-family:\'Space Mono\',monospace;font-size:9px">{label} {icon}</span>'
    flag_html += '</div>'
    st.markdown(flag_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Manual Ticker Lookup ──────────────────────────────────────────────────
    st.markdown('<div class="section-header">// MANUAL TICKER LOOKUP</div>', unsafe_allow_html=True)

    col_input, col_date, col_timing, col_btn = st.columns([2, 1.5, 1, 1])
    with col_input:
        manual_ticker = st.text_input(
            "Ticker",
            placeholder="e.g. SNDK",
            label_visibility="collapsed"
        ).strip().upper()
    with col_date:
        manual_date = st.date_input(
            "Earnings Date",
            value=datetime.now().date() + timedelta(days=1),
            label_visibility="collapsed"
        )
    with col_timing:
        manual_timing = st.selectbox(
            "Timing",
            ["AMC", "BMO"],
            label_visibility="collapsed"
        )
    with col_btn:
        run_manual = st.button("🔍 Analyze", use_container_width=True)

    if run_manual and manual_ticker:
        # Check if already in results
        existing = [r for r in st.session_state.get('results', []) if r['ticker'] == manual_ticker]
        if existing:
            st.info(f"{manual_ticker} is already in your results.")
        else:
            with st.spinner(f"Fetching options data for {manual_ticker}..."):
                opts = fetch_options_data(manual_ticker, em_min, em_max, min_oi)

            if opts['error'] or opts['price'] is None or opts['em'] is None or opts['front_iv'] is None:
                st.error(f"{manual_ticker}: {opts.get('error', 'Could not fetch options data')}")
            else:
                breach = breach_data.get(manual_ticker, {'count': None, 'avg_mag': None, 'quarters': 8})
                score  = calculate_score(
                    opts['em'], em_min, em_max,
                    opts['slope'], slope_threshold,
                    breach['count'], breach.get('quarters', 8),
                    opts['liquidity_ok'], opts['front_iv'],
                    spline_pass=opts.get('spline_pass'),
                    iv_rv_pass=opts.get('iv_rv_pass'),
                    volume_pass=opts.get('volume_pass')
                )
                rating = get_rating(score)
                condor = recommend_condor(
                    opts['price'], opts['em'], opts['front_iv'],
                    breach['count'], breach.get('quarters', 8),
                    breach.get('avg_mag'), slope_threshold,
                    call_strikes=opts.get('call_strikes', []),
                    put_strikes=opts.get('put_strikes', [])
                )
                if 'results' not in st.session_state:
                    st.session_state.results = []
                st.session_state.results.append({
                    **opts,
                    'earnings_date': manual_date,
                    'timing':        manual_timing,
                    'breach_count':  breach['count'],
                    'breach_avg_mag': breach.get('avg_mag'),
                    'breach_quarters': breach.get('quarters', 8),
                    'condor':        condor,
                    'score':         score,
                    'rating':        rating,
                    'iv_source':     opts.get('iv_source', 'unknown')
                })
                st.success(f"{manual_ticker} added — Score {score}/100 · {rating.upper()}")

    st.markdown("---")

    # ── Screener Results ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">// EARNINGS CANDIDATES</div>', unsafe_allow_html=True)

    breach_data = load_breach_data()

    if 'results' not in st.session_state:
        st.session_state.results = []

    if run_screener:
        st.session_state.results = []

        with st.spinner("Fetching earnings calendar..."):
            earnings_map = fetch_earnings_calendar(days_ahead, min_market_cap)

        if not earnings_map:
            st.warning("No upcoming earnings found for this window. Try extending the date range.")
        else:
            st.info(f"Found {len(earnings_map)} candidates (market cap ≥ ${min_market_cap:.1f}B, max 100) — fetching options data...")
            progress = st.progress(0)
            tickers = list(earnings_map.keys())

            skipped = {}
            debug_shown = False
            debug_data = {}
            for i, ticker in enumerate(tickers):
                progress.progress((i + 1) / len(tickers), text=f"Analyzing {ticker}...")
                opts = fetch_options_data(ticker, em_min, em_max, min_oi)

                # Store debug for first ticker
                if not debug_shown:
                    debug_shown = True
                    debug_data = {
                        'ticker':     opts.get('ticker'),
                        'price':      opts.get('price'),
                        'front_iv':   opts.get('front_iv'),
                        'back_iv':    opts.get('back_iv'),
                        'em':         opts.get('em'),
                        'slope':      opts.get('slope'),
                        'error':      opts.get('error'),
                        'iv_source':  opts.get('iv_source'),
                        'oi':         opts.get('open_interest'),
                        'call_strikes_count': len(opts.get('call_strikes', [])),
                    }
                    st.session_state['_debug_ticker_data'] = debug_data

                if opts['error'] or opts['price'] is None or opts['em'] is None or opts['front_iv'] is None:
                    reason = opts.get('error') or 'missing data'
                    skipped[ticker] = reason
                    continue

                # Skip if any core value is NaN
                try:
                    if any(math.isnan(float(opts[k])) for k in ['price', 'em', 'front_iv', 'back_iv'] if opts[k] is not None):
                        skipped[ticker] = 'NaN in core values'
                        continue
                except:
                    skipped[ticker] = 'NaN check failed'
                    continue

                breach = breach_data.get(ticker, {'count': None, 'avg_mag': None, 'quarters': 8})
                score = calculate_score(
                    opts['em'], em_min, em_max,
                    opts['slope'], slope_threshold,
                    breach['count'], breach.get('quarters', 8),
                    opts['liquidity_ok'], opts['front_iv'],
                    spline_pass=opts.get('spline_pass'),
                    iv_rv_pass=opts.get('iv_rv_pass'),
                    volume_pass=opts.get('volume_pass')
                )
                rating = get_rating(score)
                condor = recommend_condor(
                    opts['price'], opts['em'], opts['front_iv'],
                    breach['count'], breach.get('quarters', 8),
                    breach.get('avg_mag'), slope_threshold,
                    call_strikes=opts.get('call_strikes', []),
                    put_strikes=opts.get('put_strikes', [])
                )

                st.session_state.results.append({
                    **opts,
                    'earnings_date': earnings_map[ticker]['date'],
                    'timing': earnings_map[ticker]['timing'],
                    'breach_count': breach['count'],
                    'breach_avg_mag': breach.get('avg_mag'),
                    'breach_quarters': breach.get('quarters', 8),
                    'condor': condor,
                    'score': score,
                    'rating': rating,
                    'iv_source': opts.get('iv_source', 'unknown')
                })

            progress.empty()
            st.success(f"Scan complete — {len(st.session_state.results)} tickers analyzed")
            st.session_state['skipped'] = skipped

    # ── Display Results ───────────────────────────────────────────────────────
    results = st.session_state.results
    if results:
        filtered = [r for r in results if r['rating'] in rating_filter]
        filtered.sort(key=lambda x: x['score'], reverse=True)

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Scanned",   len(results))
        c2.metric("Strong",    sum(1 for r in results if r['rating'] == 'strong'))
        c3.metric("Good",      sum(1 for r in results if r['rating'] == 'good'))
        c4.metric("Marginal",  sum(1 for r in results if r['rating'] == 'marginal'))
        c5.metric("Avoid",     sum(1 for r in results if r['rating'] == 'avoid'))
        c6.metric("Avg Score", f"{sum(r['score'] for r in results) / len(results):.0f}")

        st.markdown(f"Showing **{len(filtered)}** of {len(results)} results")

        def card(label, value, sub=None, color='#ffffff'):
            sub_html = f'<div style="font-size:11px;color:#a0b0c0;margin-top:3px">{sub}</div>' if sub else ''
            return (
                f'<div style="background:#1c2230;border:1px solid #2e3a4e;border-radius:8px;'
                f'padding:12px 14px;height:100%">'
                f'<div style="font-family:\'Space Mono\',monospace;font-size:9px;color:#6a7a8a;'
                f'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:5px">{label}</div>'
                f'<div style="font-family:\'Space Mono\',monospace;font-size:15px;font-weight:700;'
                f'color:{color}">{value}</div>{sub_html}</div>'
            )

        for r in filtered:
            em_color     = {'green':'#00e676','yellow':'#ffd740','red':'#ff4d6a'}.get(r['em_flag'],'#a0b0c0')
            slope_ok     = r['slope'] >= slope_threshold
            slope_color  = '#00e676' if slope_ok else '#ff4d6a'
            rating_color = {'strong':'#00e676','good':'#00e5ff','marginal':'#ffd740','avoid':'#ff4d6a'}.get(r['rating'],'#ffffff')
            rating_bg    = {'strong':'rgba(0,230,118,0.12)','good':'rgba(0,229,255,0.10)','marginal':'rgba(255,215,64,0.10)','avoid':'rgba(255,77,106,0.10)'}.get(r['rating'],'')
            dot          = {'strong':'🟢','good':'🔵','marginal':'🟡','avoid':'🔴'}.get(r['rating'],'⚪')

            # Custom readable header — rendered as HTML so we control every pixel
            st.markdown(f"""
<div style="background:#0d1117;border:1px solid #2a3a4a;border-radius:10px 10px 0 0;
padding:14px 18px;margin-top:12px;margin-bottom:0px;display:flex;align-items:center;
gap:12px;flex-wrap:wrap">
  <span style="font-size:18px">{dot}</span>
  <span style="font-family:'Space Mono',monospace;font-size:16px;font-weight:700;
  color:#ffffff;letter-spacing:0.5px">{r['ticker']}</span>
  <span style="font-family:'Space Mono',monospace;font-size:11px;color:#7090a8">
    {r['earnings_date']} · {r['timing']} · EM <span style="color:{em_color}">{pct(r['em'])}</span>
    · Score <span style="color:#ffffff;font-weight:700">{r['score']}/100</span>
  </span>
  <span style="margin-left:auto;background:{rating_bg};color:{rating_color};
  font-family:'Space Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1px;
  padding:3px 12px;border-radius:20px;border:1px solid {rating_color}40">
    {r['rating'].upper()}
  </span>
</div>
""", unsafe_allow_html=True)

            with st.expander("", expanded=False):
                tab1, tab2, tab3 = st.tabs(["📊 Greeks & IV", "🦅 Condor Setup", "📝 Breach History"])

                with tab1:
                    g1,g2,g3,g4 = st.columns(4)
                    with g1: st.markdown(card("Price",    dollar(r['price'])), unsafe_allow_html=True)
                    with g2: st.markdown(card("Front IV", pct(r['front_iv']), r.get('iv_source','?')), unsafe_allow_html=True)
                    with g3: st.markdown(card("30D IV",   pct(r['back_iv'])), unsafe_allow_html=True)
                    with g4: st.markdown(card("Slope",    pct(r['slope']),
                                              "✓ Meets threshold" if slope_ok else "✗ Below threshold",
                                              slope_color), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

                    g5,g6,g7,g8 = st.columns(4)
                    with g5: st.markdown(card("Delta", f"{r['delta']:.3f}"), unsafe_allow_html=True)
                    with g6: st.markdown(card("Gamma", f"{r['gamma']:.4f}"), unsafe_allow_html=True)
                    with g7: st.markdown(card("Theta", f"{r['theta']:.3f}", "per day", '#ff9060'), unsafe_allow_html=True)
                    with g8: st.markdown(card("Vega",  f"{r['vega']:.3f}",  "per 1% IV", '#60c8ff'), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

                    g9,g10,g11,g12 = st.columns(4)
                    with g9:  st.markdown(card("Exp Move", pct(r['em']),
                                               "Sweet spot ✓" if r['em_flag']=='green' else "Outside range" if r['em_flag']=='yellow' else "Extreme ✗",
                                               em_color), unsafe_allow_html=True)
                    with g10: st.markdown(card("Open Interest",
                                               f"{r['open_interest']:,}" if r['open_interest'] else "—",
                                               "✓ Liquid" if r['liquidity_ok'] else "✗ Thin",
                                               '#00e676' if r['liquidity_ok'] else '#ff4d6a'), unsafe_allow_html=True)
                    with g11: st.markdown(card("Score",  f"{r['score']}/100"), unsafe_allow_html=True)
                    with g12: st.markdown(card("Rating", r['rating'].upper(), color=rating_color), unsafe_allow_html=True)

                    # ── New signals row ───────────────────────────────
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
                    n1, n2, n3, n4 = st.columns(4)

                    # Spline slope
                    ss = r.get('spline_slope')
                    ss_color = '#00e676' if r.get('spline_pass') else '#ff4d6a' if r.get('spline_pass') is False else '#a0b0c0'
                    ss_label = f"{'✓ Pass' if r.get('spline_pass') else '✗ Fail' if r.get('spline_pass') is False else '— No data'} (threshold −0.00406)"
                    with n1: st.markdown(card("Spline Slope", f"{ss:.6f}" if ss is not None else "—", ss_label, ss_color), unsafe_allow_html=True)

                    # IV/RV ratio
                    ivr = r.get('iv_rv_ratio')
                    ivr_color = '#00e676' if r.get('iv_rv_pass') else '#ff4d6a' if r.get('iv_rv_pass') is False else '#a0b0c0'
                    ivr_label = f"{'✓ Pass' if r.get('iv_rv_pass') else '✗ Fail' if r.get('iv_rv_pass') is False else '— No data'} (threshold 1.25)"
                    with n2: st.markdown(card("IV/RV Ratio", f"{ivr:.2f}" if ivr else "—", ivr_label, ivr_color), unsafe_allow_html=True)

                    # Yang-Zhang RV
                    rv = r.get('rv30')
                    with n3: st.markdown(card("YZ RV30", pct(rv) if rv else "—", "Yang-Zhang realized vol"), unsafe_allow_html=True)

                    # Volume
                    vol = r.get('avg_volume')
                    vol_color = '#00e676' if r.get('volume_pass') else '#ff4d6a' if r.get('volume_pass') is False else '#a0b0c0'
                    vol_label = f"{'✓ Pass' if r.get('volume_pass') else '✗ Fail'} (threshold 1.5M)" if vol else "—"
                    with n4: st.markdown(card("Avg Volume 30D", f"{vol/1e6:.1f}M" if vol else "—", vol_label, vol_color), unsafe_allow_html=True)

                with tab2:
                    c = r['condor']
                    st.markdown('<div style="color:#ffffff;font-weight:700;font-size:14px;margin-bottom:10px">Recommended Iron Condor</div>', unsafe_allow_html=True)

                    sc1,sc2,sc3,sc4 = st.columns(4)
                    with sc1: st.markdown(card("Long Put",   dollar(c['long_put']),  "Buy — protection", '#60c8ff'), unsafe_allow_html=True)
                    with sc2: st.markdown(card("Short Put",  dollar(c['short_put']), "Sell — premium",   '#ff6080'), unsafe_allow_html=True)
                    with sc3: st.markdown(card("Short Call", dollar(c['short_call']),"Sell — premium",   '#ff6080'), unsafe_allow_html=True)
                    with sc4: st.markdown(card("Long Call",  dollar(c['long_call']), "Buy — protection", '#60c8ff'), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

                    m1,m2,m3,m4 = st.columns(4)
                    with m1: st.markdown(card("Est. Credit",      dollar(c['credit']*100,0)+"/contract",  color='#00e676'), unsafe_allow_html=True)
                    with m2: st.markdown(card("Max Loss",          dollar(c['max_loss']*100,0)+"/contract", color='#ff4d6a'), unsafe_allow_html=True)
                    with m3: st.markdown(card("Est. Prob Profit",  f"{c['prob_profit']}%"), unsafe_allow_html=True)
                    with m4: st.markdown(card("Expected Value",    dollar(c['ev'])+"/contract",
                                              color='#00e676' if c['ev']>0 else '#ff4d6a'), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

                    w1,w2,w3 = st.columns(3)
                    with w1: st.markdown(card("Call Wing", dollar(c['call_wing'])), unsafe_allow_html=True)
                    with w2: st.markdown(card("Put Wing",  dollar(c['put_wing'])),  unsafe_allow_html=True)
                    with w3: st.markdown(card("Strikes",   "✓ Real chain" if c.get('strikes_real') else "⚠ Estimated",
                                              color='#00e676' if c.get('strikes_real') else '#ffd740'), unsafe_allow_html=True)

                    st.markdown(f"""
<div style="background:#111827;border:1px solid #2e3a4e;border-radius:8px;padding:14px 16px;
margin-top:12px;font-family:'Space Mono',monospace;font-size:11px;color:#d0dce8;line-height:1.9">
<span style="color:#00e5ff;font-weight:700;letter-spacing:1px">EXIT RULES — pre-commit before entering:</span><br>
🟢 <b>Winner:</b> Close entire condor at 50% of max credit → buy back at <b>${c['credit']*50:.0f}</b><br>
🔴 <b>Loser:</b> Close threatened side at 2× total credit → <b>${c['credit']*200:.0f}</b><br>
⏰ <b>Time:</b> Close full position at market open morning after earnings — no exceptions
</div>""", unsafe_allow_html=True)

                    if c['breach_rate'] > 0.4:
                        st.warning(f"⚠️ High historical breach rate ({c['breach_rate']*100:.0f}%) — strikes placed {c['buffer_used']:.2f}× beyond EM. Consider skipping.")

                with tab3:
                    st.markdown('<div style="color:#ffffff;font-weight:600;margin-bottom:6px">Enter thinkBack data to improve score and strike accuracy</div>', unsafe_allow_html=True)
                    st.caption("TOS → Analyze → thinkBack → earnings eve → ATM straddle vs actual move")

                    saved = breach_data.get(r['ticker'], {})
                    col_a,col_b,col_c = st.columns(3)
                    with col_a:
                        b_count = st.number_input("Breaches (last N quarters)", min_value=0, max_value=12,
                            value=int(saved['count']) if saved.get('count') is not None else 0,
                            key=f"bc_{r['ticker']}")
                    with col_b:
                        b_mag = st.number_input("Avg breach magnitude (%)", min_value=0.0, max_value=50.0, step=0.1,
                            value=float(saved['avg_mag']*100) if saved.get('avg_mag') else 0.0,
                            key=f"bm_{r['ticker']}")
                    with col_c:
                        b_qtrs = st.number_input("Quarters checked", min_value=1, max_value=12,
                            value=int(saved.get('quarters',8)), key=f"bq_{r['ticker']}")

                    if st.button(f"💾 Save breach data for {r['ticker']}", key=f"save_{r['ticker']}"):
                        save_breach_entry(r['ticker'], b_count, b_mag if b_mag > 0 else None, b_qtrs)
                        st.success(f"Saved! Re-run screener to recalculate {r['ticker']}.")

    else:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px'>
          <div style='font-size:48px;margin-bottom:16px;opacity:0.3'>◈</div>
          <div style='font-family:"Syne",sans-serif;font-size:16px;font-weight:700;color:#ffffff;margin-bottom:8px'>No results yet</div>
          <div style='font-family:"Space Mono",monospace;font-size:11px;color:#7a8898'>Configure thresholds in the sidebar and click Run Screener</div>
        </div>""", unsafe_allow_html=True)

    # ── Debug / Skipped — bottom of page ────────────────────────────────────
    st.markdown("---")
    skipped = st.session_state.get('skipped', {})
    if skipped:
        with st.expander(f"⚠ {len(skipped)} tickers skipped — click to see why"):
            for t, reason in list(skipped.items())[:30]:
                st.caption(f"**{t}**: {reason}")
            if len(skipped) > 30:
                st.caption(f"...and {len(skipped)-30} more")

    st.caption("For informational and educational purposes only. Not financial advice. Always verify in TOS before trading.")

if __name__ == "__main__":
    main()
