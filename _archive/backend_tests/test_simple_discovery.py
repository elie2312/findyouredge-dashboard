#!/usr/bin/env python3
import sys
sys.path.append('services/backtest')
from discover import get_available_strategies

strategies = get_available_strategies('.')
simple_strategies = [s for s in strategies if 'SimpleCandle' in s['name'] or '30mn' in s['name']]

print('Simple Candle strategies found:')
for s in simple_strategies:
    print(f'  - {s["name"]} -> {s["script_path"].split("/")[-1]}')

print(f'\nAll strategies:')
for s in strategies:
    print(f'  - {s["name"]}')

print(f'\nTotal strategies: {len(strategies)}')
