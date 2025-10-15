#!/usr/bin/env python3
import sys
sys.path.append('services/backtest')
from discover import get_available_strategies

strategies = get_available_strategies('.')
supertrend_strategies = [s for s in strategies if 'SuperTrend' in s['name']]

print('SuperTrend strategies found:')
for s in supertrend_strategies:
    print(f'  - {s["name"]} -> {s["script_path"].split("/")[-1]}')

print(f'\nTotal strategies: {len(strategies)}')
