#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get('http://localhost:8000/api/strategies')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Nombre de stratégies: {len(data.get("strategies", []))}')
        for s in data.get('strategies', [])[:3]:
            print(f'ID: {s["id"]}, Name: {s["name"]}, Category: {s.get("category", "MISSING")}')
    else:
        print(f'Erreur: {response.text}')
except Exception as e:
    print(f'Exception: {e}')
