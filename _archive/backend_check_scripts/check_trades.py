#!/usr/bin/env python3
import pandas as pd

# Charger les trades générés
df = pd.read_csv('supertrend_scalein_trades.csv')

print("=== ANALYSE DES TRADES SUPERTREND ===")
print(f"Total trades: {len(df)}")
print(f"\nSample trades:")
print(df[['result', 'pnl_usd', 'points', 'contracts']].head(10))

print(f"\nResults distribution:")
print(df['result'].value_counts())

print(f"\nPnL statistics:")
print(f"  Min PnL: ${df['pnl_usd'].min():.2f}")
print(f"  Max PnL: ${df['pnl_usd'].max():.2f}")
print(f"  Mean PnL: ${df['pnl_usd'].mean():.2f}")
print(f"  Total PnL: ${df['pnl_usd'].sum():.2f}")

# Analyser les trades réels (avec PnL)
real_trades = df[df['result'].isin(['TP','SL','EOD'])]
print(f"\nReal trades: {len(real_trades)}")

if len(real_trades) > 0:
    wins = real_trades[real_trades['pnl_usd'] > 0]
    losses = real_trades[real_trades['pnl_usd'] <= 0]
    
    print(f"  Winning trades: {len(wins)}")
    print(f"  Losing trades: {len(losses)}")
    print(f"  Win rate: {len(wins) / len(real_trades) * 100:.1f}%")
    
    if len(wins) > 0:
        print(f"  Avg win: ${wins['pnl_usd'].mean():.2f}")
    if len(losses) > 0:
        print(f"  Avg loss: ${losses['pnl_usd'].mean():.2f}")
