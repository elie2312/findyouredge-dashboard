#!/usr/bin/env python3
import sys
sys.path.append('services/backtest')
from discover import get_available_strategies
import json

strategies = get_available_strategies('.')
simple_strategy = [s for s in strategies if 'SimpleCandle' in s['name']]

if simple_strategy:
    strategy = simple_strategy[0]
    print(f'Name: {strategy["name"]}')
    print(f'Script path: {strategy["script_path"]}')
    print('Full strategy:')
    print(json.dumps(strategy, indent=2))
else:
    print('SimpleCandle strategy not found!')
    print('Available strategies:')
    for s in strategies:
        print(f'  - {s["name"]}')
