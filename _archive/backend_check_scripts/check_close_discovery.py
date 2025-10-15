#!/usr/bin/env python3
import sys
sys.path.append('services/backtest')
from discover import get_available_strategies

strategies = get_available_strategies('.')
close_strategies = [s for s in strategies if 'CLOSE' in s['name'] or '30mn' in s['name']]

print('Close strategies found:')
for s in close_strategies:
    print(f'  - {s["name"]}')

print(f'\nTotal strategies: {len(strategies)}')
