#!/usr/bin/env python3
import sys
sys.path.append('.')
from services.backtest.discover import get_available_strategies

strategies = get_available_strategies('.')
print(f'Nombre de stratégies: {len(strategies)}')
for s in strategies:
    print(f'Nom: {s["name"]}, Category: {s.get("category", "MISSING")}, Tags: {s.get("tags", "MISSING")}')
