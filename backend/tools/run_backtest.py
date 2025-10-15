from __future__ import annotations
import argparse, re, sys, subprocess
from pathlib import Path
from datetime import datetime

def find_csvs(base: Path) -> list[Path]:
    cands = list((base / "data" / "raw").rglob("*.csv"))
    if not cands:
        cands = list(base.rglob("*.csv"))
    return sorted(cands)

def patch_csv_path(script_path: Path, csv_path: Path) -> None:
    code = script_path.read_text(encoding="utf-8")
    new_code, n = re.subn(
        r'CSV_PATH\s*=\s*[ru]?["\'].*?["\']',
        f'CSV_PATH = r"{csv_path.as_posix()}"',
        code,
        flags=re.DOTALL,
    )
    if n == 0:
        raise RuntimeError(f"Impossible de patcher CSV_PATH dans {script_path.name} (aucune assignation trouvée).")
    script_path.write_text(new_code, encoding="utf-8")

def run_script(script_path: Path) -> int:
    return subprocess.call([sys.executable, str(script_path)])

def main():
    p = argparse.ArgumentParser(description="Patch CSV_PATH dans le backtest et l'exécute (local).")
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--script-path", type=Path, default=None)
    p.add_argument("--csv", type=Path, default=None)
    args = p.parse_args()

    base = args.base.expanduser().resolve()
    if not base.exists():
        sys.exit(f"[ERREUR] Base inexistante: {base}")

    script_path = (args.script_path or base / "backtests" / "BACKTEST_07_ENTRY_BUFFER_2TICK.py").resolve()
    if not script_path.exists():
        sys.exit(f"[ERREUR] Script introuvable: {script_path}")

    if args.csv:
        csv_path = args.csv.expanduser().resolve()
        if not csv_path.exists():
            sys.exit(f"[ERREUR] CSV introuvable: {csv_path}")
    else:
        csvs = find_csvs(base)
        if not csvs:
            sys.exit("[ERREUR] Aucun CSV trouvé. Mets tes .csv dans data/raw/ ou indique --csv.")
        csv_path = max(csvs, key=lambda p: p.stat().st_mtime)

    print("=== Contexte ===")
    print("Base       :", base)
    print("Backtest   :", script_path)
    print("CSV choisi :", csv_path)
    print("Modifié le :", datetime.fromtimestamp(csv_path.stat().st_mtime))

    patch_csv_path(script_path, csv_path)
    print("CSV_PATH patché dans:", script_path.name)

    rc = run_script(script_path)
    if rc != 0:
        sys.exit(f"[ERREUR] Le script s'est terminé avec le code {rc}.")
    print("Backtest terminé avec succès.")

if __name__ == "__main__":
    main()
