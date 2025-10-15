#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le système de catégories des stratégies.
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

# Ajouter le chemin vers les services backend
import sys
BACKEND_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_PATH / "services" / "backtest"))

from services.backtest.discover import StrategyDiscovery


class TestStrategyCategorization(unittest.TestCase):
    """Tests pour la catégorisation des stratégies"""

    def setUp(self):
        """Configuration des tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)

        # Créer un dossier strategies de test
        self.strategies_dir = self.base_path / "strategies"
        self.strategies_dir.mkdir()

        # Créer un catalog de test
        self.catalog_path = self.base_path / "strategies_catalog.json"
        self.test_catalog = {
            "BACKTEST_30sec_1R_PARAM": {
                "category": "OPR",
                "tags": ["30 secondes", "1R"]
            },
            "BACKTEST_SuperTrend_ScaleIn_NoCut": {
                "category": "SuperTrend",
                "tags": ["Multi-timeframe", "Scale-In"]
            }
        }
        with open(self.catalog_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_catalog, f, indent=2)

    def tearDown(self):
        """Nettoyage après tests"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_category_from_catalog(self):
        """Test récupération catégorie depuis le catalog"""
        discovery = StrategyDiscovery(self.base_path)

        # Créer un fichier de stratégie fictif
        strategy_file = self.strategies_dir / "BACKTEST_30sec_1R_PARAM.py"
        strategy_file.write_text("# Test strategy\n")

        strategies = discovery.discover_all()
        self.assertEqual(len(strategies), 1)

        strategy = strategies[0]
        self.assertEqual(strategy.category, "OPR")
        self.assertEqual(strategy.tags, ["30 secondes", "1R"])

    def test_category_deduction_fallback(self):
        """Test déduction catégorie par nommage (fallback)"""
        discovery = StrategyDiscovery(self.base_path)

        # Créer un fichier sans entry dans le catalog
        strategy_file = self.strategies_dir / "BACKTEST_SimpleCandle_Test.py"
        strategy_file.write_text("# Test SimpleCandle strategy\n")

        strategies = discovery.discover_all()
        # Trouver notre stratégie dans la liste
        test_strategy = None
        for s in strategies:
            if 'SimpleCandle' in s.name:
                test_strategy = s
                break

        self.assertIsNotNone(test_strategy)
        self.assertEqual(test_strategy.category, "SimpleCandle")
        self.assertEqual(test_strategy.tags, ["30 minutes", "SimpleCandle"])

    def test_unknown_strategy_category(self):
        """Test catégorie pour stratégie inconnue"""
        discovery = StrategyDiscovery(self.base_path)

        # Créer un fichier sans pattern connu
        strategy_file = self.strategies_dir / "BACKTEST_Unknown_Strategy.py"
        strategy_file.write_text("# Unknown strategy\n")

        strategies = discovery.discover_all()
        test_strategy = None
        for s in strategies:
            if 'Unknown' in s.name:
                test_strategy = s
                break

        self.assertIsNotNone(test_strategy)
        self.assertEqual(test_strategy.category, "Autres")
        self.assertEqual(test_strategy.tags, ["Non catégorisé"])

    def test_supertrend_category_deduction(self):
        """Test déduction catégorie SuperTrend"""
        discovery = StrategyDiscovery(self.base_path)

        # Créer un fichier SuperTrend sans entry dans le catalog
        strategy_file = self.strategies_dir / "BACKTEST_New_SuperTrend.py"
        strategy_file.write_text("# New SuperTrend strategy\n")

        strategies = discovery.discover_all()
        test_strategy = None
        for s in strategies:
            if 'SuperTrend' in s.name:
                test_strategy = s
                break

        self.assertIsNotNone(test_strategy)
        self.assertEqual(test_strategy.category, "SuperTrend")
        self.assertEqual(test_strategy.tags, ["Multi-timeframe", "Scale-In"])

    def test_no_catalog_file(self):
        """Test comportement sans fichier catalog"""
        # Supprimer le fichier catalog
        if self.catalog_path.exists():
            self.catalog_path.unlink()

        discovery = StrategyDiscovery(self.base_path)

        # Créer une stratégie OPR
        strategy_file = self.strategies_dir / "BACKTEST_15mn_5R_PARAM.py"
        strategy_file.write_text("# OPR strategy\n")

        strategies = discovery.discover_all()
        test_strategy = None
        for s in strategies:
            if '15mn' in s.name:
                test_strategy = s
                break

        self.assertIsNotNone(test_strategy)
        self.assertEqual(test_strategy.category, "OPR")


if __name__ == "__main__":
    unittest.main()
