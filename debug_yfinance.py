import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def check_period(ticker, period_label, period_yf, extra_period):
    print(f"--- Period: {period_label} ---")
    stock = yf.Ticker(ticker)
    
    # Current fetching logic (just the period)
    df_current = stock.history(period=period_yf)
    
    # Proposed fetching logic (extra data for baseline)
    df_extra = stock.history(period=extra_period)
    
    if df_current.empty or df_extra.empty:
        print("No data found")
        return

    current_close = df_current['Close'].iloc[-1]
    
    # 1. Dashboard Current: Close of first day in period
    baseline_close_p0 = df_current['Close'].iloc[0]
    pct_dashboard = (current_close - baseline_close_p0) / baseline_close_p0 * 100
    
    # 2. User Suggestion: Open of first day in period
    baseline_open_p0 = df_current['Open'].iloc[0]
    pct_open = (current_close - baseline_open_p0) / baseline_open_p0 * 100
    
    # 3. Proper Baseline: Close of day BEFORE the period
    # We find the first date of df_current in df_extra and take the row before it
    first_date_p0 = df_current.index[0]
    try:
        idx = df_extra.index.get_loc(first_date_p0)
        if idx > 0:
            baseline_prev_close = df_extra['Close'].iloc[idx - 1]
            pct_prev_close = (current_close - baseline_prev_close) / baseline_prev_close * 100
        else:
            pct_prev_close = None
    except:
        pct_prev_close = None
    
    print(f"Latest Price: {current_close:.2f}")
    print(f"1. Baseline [First Close]: {baseline_close_p0:.2f} -> {pct_dashboard:.2f}%")
    print(f"2. Baseline [First Open]:  {baseline_open_p0:.2f} -> {pct_open:.2f}%")
    if pct_prev_close is not None:
        print(f"3. Baseline [Prev Close]:  {baseline_prev_close:.2f} -> {pct_prev_close:.2f}%")
    else:
        print(f"3. Baseline [Prev Close]:  Not available in this fetch")
    
    # For comparison, get the info values if 52 week
    if period_yf == '1y':
        print(f"Yahoo Info 52W Change: {stock.info.get('52WeekChange', 'N/A')}")
    
    print()

ticker = "TSLA"
print(f"=== Ticker: {ticker} ===")
check_period(ticker, "1 Day", "1d", "5d")
check_period(ticker, "1 Week", "5d", "1mo")
check_period(ticker, "1 Month", "1mo", "3mo")
check_period(ticker, "1 Year", "1y", "2y")
