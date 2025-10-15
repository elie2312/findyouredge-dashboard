"""
TEMPLATE BACKTEST - Template de strategie de backtest
======================================================
Ce template gere correctement:
- Selection du symbole front month (CME roll)
- Agregation OHLC propre
- Timestamps precis
- Tous les champs remplis correctement

STRATEGIE EXEMPLE: Buy & Hold journalier
- Entry: Open de la premiere barre de la session
- Exit: Close de la derniere barre de la session
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from datetime import date, timedelta
import calendar

# ==========================
# ======== CONFIG ==========
# ==========================

CSV_PATH = r"C:/Users/elieb/Desktop/Dashboard/backend/data/filtered_data.csv"
SYMBOL_FILTER_REGEX = r"^NQ[A-Z][0-9]{1,2}$"

OUTPUT_TRADES_CSV = "template_trades.csv"
OUTPUT_PICKLOG_CSV = "template_symbol_selection.csv"

# Fenetres horaires (UTC)
SESSION_START_UTC = "10:00:00"  # Debut de session
SESSION_END_UTC = "20:00:00"    # Fin de session

# Instrument
TICK_SIZE = 0.25
POINT_VALUE = 20.0

# Couts
SLIPPAGE_TICKS = 1
COMMISSION_RT = 4.5

# Contraintes
MAX_RISK_USD = 1000.0

# ==========================
# === FRONT MONTH LOGIC ====
# ==========================

def third_friday(year: int, month: int) -> date:
    """Trouve le 3eme vendredi du mois (CME expiration)"""
    c = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [d for d in c.itermonthdates(year, month) 
               if d.weekday() == calendar.FRIDAY and d.month == month]
    return fridays[2]

def roll_date(year: int, month: int) -> date:
    """Date de roll = jeudi avant le 3eme vendredi"""
    tf = third_friday(year, month)
    return tf - timedelta(days=1)

def front_month_for_day(d: date) -> Tuple[str, int]:
    """Determine le contrat front month pour une date donnee"""
    MONTHS = [3, 6, 9, 12]  # H, M, U, Z
    CODES = {3: "H", 6: "M", 9: "U", 12: "Z"}
    
    events = []
    # Ajouter le roll de decembre de l'annee precedente
    rd_prev_dec = roll_date(d.year - 1, 12)
    events.append((rd_prev_dec, "H", d.year))
    
    # Ajouter tous les rolls de l'annee courante
    for m in MONTHS:
        rd = roll_date(d.year, m)
        ny = d.year + 1 if m == 12 else d.year
        nxt = {3: "M", 6: "U", 9: "Z", 12: "H"}[m]
        events.append((rd, nxt, ny))
    
    events.sort(key=lambda x: x[0])
    
    # Trouver le dernier roll avant ou egal a la date
    last = None
    for ev in events:
        if ev[0] <= d:
            last = ev
        else:
            break
    
    if last is None:
        return ("H", d.year % 10)
    
    letter, yy = last[1], last[2] % 10
    return (letter, yy)

def active_symbol_for_day(d: date) -> str:
    """Retourne le symbole front month pour une date (ex: NQZ5)"""
    letter, yy = front_month_for_day(d)
    return f"NQ{letter}{yy}"

# ==========================
# ====== DATA LOADING ======
# ==========================

def load_data(csv_path: str, symbol_regex: Optional[str]) -> pd.DataFrame:
    """Charge les donnees tick par tick"""
    df = pd.read_csv(csv_path)
    cols = {c.lower(): c for c in df.columns}
    required = ["ts_event", "open", "high", "low", "close", "symbol"]
    for r in required:
        if r not in cols:
            raise ValueError(f"Missing required column: {r}")
    
    df = df.rename(columns={
        cols["ts_event"]: "timestamp",
        cols["open"]: "open",
        cols["high"]: "high",
        cols["low"]: "low",
        cols["close"]: "close",
        cols["symbol"]: "symbol",
    })
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    
    if symbol_regex:
        df = df[df["symbol"].astype(str).str.match(symbol_regex)]
    
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    return df

def resample_ohlc(df: pd.DataFrame, timeframe: str = "1h") -> pd.DataFrame:
    """
    Agrege les donnees par symbole et timeframe
    timeframe: '1h', '30min', '15min', etc.
    """
    df = df.copy()
    df.set_index("timestamp", inplace=True)
    res = []
    
    for sym, g in df.groupby("symbol"):
        ohlc = g[["open", "high", "low", "close"]].resample(
            timeframe, label="right", closed="right"
        ).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last"
        })
        
        if "volume" in g.columns:
            vol = g[["volume"]].resample(timeframe, label="right", closed="right").sum()
            ohlc = ohlc.join(vol, how="left")
        
        ohlc["symbol"] = sym
        res.append(ohlc.reset_index())
    
    out = pd.concat(res, ignore_index=True).dropna(subset=["open", "high", "low", "close"])
    out = out.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    return out

# ==========================
# ======= TRADES ===========
# ==========================

@dataclass
class Trade:
    symbol: str
    date: pd.Timestamp
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    direction: str
    entry: float
    exit: float
    tp: float
    sl: float
    points: float
    pnl_usd: float
    contracts: int
    result: str

def round_to_tick(x: float, tick: float = TICK_SIZE) -> float:
    """Arrondit au tick le plus proche"""
    return round(x / tick) * tick

# ==========================
# ==== STRATEGY LOGIC ======
# ==========================

def simulate_day(day_df: pd.DataFrame, symbol: str, the_date: date) -> List[Trade]:
    """
    STRATEGIE: Buy & Hold journalier
    - Entry: Open de la premiere barre de session
    - Exit: Close de la derniere barre de session
    - 1 trade par jour maximum
    """
    trades = []
    
    # Filtrer le symbole
    s_df = day_df[day_df["symbol"] == symbol].copy()
    if s_df.empty:
        return trades
    
    # Filtrer les heures de session
    start_hour = int(SESSION_START_UTC.split(":")[0])
    end_hour = int(SESSION_END_UTC.split(":")[0])
    
    # Prendre EXACTEMENT les barres de start_hour et end_hour
    entry_bar = s_df[s_df["timestamp"].dt.hour == start_hour]
    exit_bar = s_df[s_df["timestamp"].dt.hour == end_hour]
    
    if entry_bar.empty or exit_bar.empty:
        return trades
    
    entry_bar = entry_bar.iloc[0]
    exit_bar = exit_bar.iloc[0]
    
    # Parametres du trade
    direction = "long"
    slip = SLIPPAGE_TICKS * TICK_SIZE
    contracts = 1
    
    entry_price = round_to_tick(entry_bar["open"] + slip)
    exit_price = round_to_tick(exit_bar["close"] - slip)
    
    # TP/SL fictifs (a adapter selon votre strategie)
    tp = round_to_tick(entry_price + 50.0)  # +50 points
    sl = round_to_tick(entry_price - 25.0)  # -25 points
    
    # Calcul P&L
    points = exit_price - entry_price
    pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
    
    # Determiner le resultat
    if exit_price >= tp:
        result = "TP"
    elif exit_price <= sl:
        result = "SL"
    else:
        result = "EOD"
    
    # Debug pour les 3 premiers trades
    if len(trades) < 3:
        print(f"[TRADE] {the_date} {symbol}")
        print(f"  Entry: {entry_bar['timestamp']} @ {entry_price:.2f}")
        print(f"  Exit:  {exit_bar['timestamp']} @ {exit_price:.2f}")
        print(f"  Points: {points:.2f}, P&L: ${pnl:.2f}, Result: {result}")
    
    trades.append(Trade(
        symbol=symbol,
        date=pd.Timestamp(the_date),
        entry_time=entry_bar["timestamp"],
        exit_time=exit_bar["timestamp"],
        direction=direction,
        entry=float(entry_price),
        exit=float(exit_price),
        tp=float(tp),
        sl=float(sl),
        points=float(points),
        pnl_usd=float(pnl),
        contracts=contracts,
        result=result
    ))
    
    return trades

# ==========================
# ========= RUN ============
# ==========================

def run_backtest(df_raw: pd.DataFrame, timeframe: str = "1h", max_days: int = None):
    """
    Execute le backtest
    timeframe: '1h', '30min', '15min', etc.
    max_days: Limiter le nombre de jours (None = tous)
    """
    # Agregation OHLC
    print(f"Agregation en {timeframe}...")
    df_ohlc = resample_ohlc(df_raw, timeframe)
    df_ohlc["utc_date"] = df_ohlc["timestamp"].dt.date
    
    all_trades = []
    picks = []
    
    # Obtenir les dates uniques
    unique_dates = sorted(df_ohlc["utc_date"].unique())
    if max_days:
        unique_dates = unique_dates[:max_days]
    
    print(f"Simulation sur {len(unique_dates)} jours...")
    
    for d in unique_dates:
        # Determiner le symbole front month
        pick = active_symbol_for_day(d)
        
        # Verifier si on a des donnees pour ce symbole
        day_df = df_ohlc[df_ohlc["utc_date"] == d]
        has_data = bool((day_df["symbol"] == pick).any())
        
        picks.append({
            "date": d,
            "picked_symbol": pick,
            "has_data": int(has_data)
        })
        
        if not has_data:
            continue
        
        # Simuler la journee
        all_trades.extend(simulate_day(day_df, pick, d))
    
    # Convertir en DataFrame
    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date", "entry_time"]).reset_index(drop=True)
    
    return trades_df, picklog_df

# ==========================
# ======= METRICS ==========
# ==========================

def calculate_metrics(trades: pd.DataFrame) -> dict:
    """Calcule les metriques de performance"""
    if trades.empty:
        return {"trades": 0, "net_pnl_usd": 0.0}
    
    wins = trades[trades["pnl_usd"] > 0]
    losses = trades[trades["pnl_usd"] <= 0]
    
    net_pnl = trades["pnl_usd"].sum()
    win_rate = len(wins) / len(trades) if len(trades) > 0 else 0.0
    
    avg_win = wins["pnl_usd"].mean() if len(wins) > 0 else 0.0
    avg_loss = losses["pnl_usd"].mean() if len(losses) > 0 else 0.0
    
    gross_profit = wins["pnl_usd"].sum() if len(wins) > 0 else 0.0
    gross_loss = -losses["pnl_usd"].sum() if len(losses) > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf
    
    expectancy = net_pnl / len(trades)
    
    # Drawdown
    equity = trades["pnl_usd"].cumsum()
    roll_max = equity.cummax()
    drawdown = equity - roll_max
    max_dd = drawdown.min()
    
    return {
        "trades": int(len(trades)),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "avg_win_usd": float(avg_win),
        "avg_loss_usd": float(avg_loss),
        "expectancy_usd": float(expectancy),
        "net_pnl_usd": float(net_pnl),
        "max_dd_usd": float(max_dd),
        "days": int(trades["date"].nunique())
    }

def print_stats(title: str, stats: dict):
    """Affiche les statistiques"""
    print(f"\n=== {title} ===")
    for k, v in stats.items():
        if isinstance(v, float):
            if "rate" in k:
                print(f"{k:>16}: {v:.2%}")
            elif "factor" in k:
                print(f"{k:>16}: {'inf' if np.isinf(v) else f'{v:.2f}'}")
            else:
                print(f"{k:>16}: {v:,.2f}")
        else:
            print(f"{k:>16}: {v}")

# ==========================
# ========= MAIN ===========
# ==========================

def main():
    print("="*60)
    print("TEMPLATE BACKTEST - Buy & Hold Journalier")
    print("="*60)
    
    print("\nLoading data (UTC)...")
    df = load_data(CSV_PATH, SYMBOL_FILTER_REGEX)
    print(f"Rows total: {len(df):,}")
    print(f"Symbols: {sorted(df['symbol'].unique())[:5]}...")
    
    # Tous les jours disponibles
    trades, picklog = run_backtest(df, timeframe="1h", max_days=None)
    
    # Sauvegarder
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"\nSaved trades to: {OUTPUT_TRADES_CSV}")
    print(f"Saved symbol selection log to: {OUTPUT_PICKLOG_CSV}")
    
    # Statistiques
    if not trades.empty:
        stats = calculate_metrics(trades)
        print_stats("RESULTATS", stats)
        
        print(f"\n=== VERIFICATION DES CHAMPS ===")
        print(f"Colonnes: {list(trades.columns)}")
        print(f"\nPremier trade:")
        first = trades.iloc[0].to_dict()
        for k, v in first.items():
            print(f"  {k}: {v}")
    else:
        print("\n=== Aucun trade genere ===")

if __name__ == "__main__":
    main()
