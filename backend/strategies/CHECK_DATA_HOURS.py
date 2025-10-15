#!/usr/bin/env python3
import pandas as pd

CSV_PATH = r"C:/Users/elieb/Desktop/Dashboard/backend/data/raw/glbx-mdp3-20240814-20250813.ohlcv-1s.csv"

print("Checking data hours...")
df = pd.read_csv(CSV_PATH, nrows=100000)
df['timestamp'] = pd.to_datetime(df['ts_event'], utc=True)

print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Hours available: {sorted(df['timestamp'].dt.hour.unique())}")

# Vérifier les données par jour
df['date'] = df['timestamp'].dt.date
for date, day_df in df.groupby('date'):
    hours = sorted(day_df['timestamp'].dt.hour.unique())
    print(f"{date}: hours {hours[0]}-{hours[-1]} ({len(hours)} different hours)")
    if len(day_df) > 1000:  # Seulement les jours avec beaucoup de données
        break
