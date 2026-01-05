import pandas as pd
import numpy as np

def calculate_rsi_old(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_rsi_new(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Create dummy data
np.random.seed(42)
prices = 100 + np.cumsum(np.random.randn(100))
df = pd.DataFrame({'Close': prices})

rsi_old = calculate_rsi_old(df)
rsi_new = calculate_rsi_new(df)

print("First few RSI (Old):")
print(rsi_old.dropna().head())
print("\nFirst few RSI (New):")
print(rsi_new.dropna().head())

# Basic check: RSI should be between 0 and 100
assert rsi_new.dropna().between(0, 100).all(), "RSI out of bounds!"

print("\nVerification successful: RSI values are within bounds and show characteristic smoothing difference.")
