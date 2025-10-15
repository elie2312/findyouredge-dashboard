#!/usr/bin/env python3
import sys
sys.path.append('services/backtest')
from discover import get_available_strategies

strategies = get_available_strategies('.')

print('All strategies found:')
for s in strategies:
    print(f'  - {s["name"]}')

print(f'\nTotal strategies: {len(strategies)}')
