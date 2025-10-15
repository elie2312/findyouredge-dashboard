from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path
from typing import List
import pandas as pd

def scan_candidates(base: Path) -> List[Path]:
    cands: List[Path] = []
    cands += list((base / "data" / "outputs").glob("*trades*.csv"))
    cands += list((base / "data" / "outputs").glob("*selection_log*.csv"))
    cands += list((base / "backtests").glob("trades_details*.csv"))
    cands += list((base / "backtests").glob("opr_trades_*.csv"))
    cands += list(base.glob("*trades*.csv"))
    if not cands:
        cands = list(base.rglob("*trades*.csv")) + list(base.rglob("*selection_log*.csv"))
    return [c for c in cands if c.is_file()]

def score(path: Path) -> int:
    n = path.name.lower()
    if "trades_details_executed" in n: return 100
    if "trades_details_full"     in n: return 90
    if "opr_trades"              in n: return 80
    return 10

def main():
    ap = argparse.ArgumentParser(description="Copie le meilleur CSV de trades vers data/outputs/trades_detail.csv (aperçu).")
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--dest", type=Path, default=None)
    ap.add_argument("--preview-rows", type=int, default=20)
    args = ap.parse_args()

    base = args.base.expanduser().resolve()
    if not base.exists():
        sys.exit(f"[ERREUR] Base inexistante: {base}")

    dest = (args.dest or (base / "data" / "outputs" / "trades_detail.csv")).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    cands = scan_candidates(base)
    if not cands:
        sys.exit("Aucun fichier de trades trouvé. Exécute d'abord le backtest.")

    cands = sorted(cands, key=lambda p: (score(p), p.stat().st_mtime), reverse=True)
    src = cands[0]

    shutil.copy2(src, dest)
    print("Fichier de trades copié :")
    print("source :", src)
    print("cible  :", dest)

    try:
        df = pd.read_csv(dest, nrows=args.preview_rows)
        pd.set_option("display.max_columns", None)
        print(df)
    except Exception as e:
        print("Aperçu indisponible :", e)

if __name__ == "__main__":
    main()
