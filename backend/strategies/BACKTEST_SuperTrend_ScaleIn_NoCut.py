#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST — SuperTrend ScaleIn NoCut — NQ front-month
Stratégie basée sur l'indicateur SuperTrend avec scale-in et pas de cut
- Calcule l'indicateur SuperTrend (ATR + bandes)
- SCALE IN: Ajoute un contrat à chaque cross up
- NE COUPE JAMAIS: Les signaux vendeurs sont ignorés, position reste ouverte
- Sizing = Risk$ / (|Close - STLine| * PointValue) par ajout
(UTC, même logique de roll CME + sélection du front-month)
"""

import calendar
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Optional, Literal, Tuple
from datetime import date, datetime, timedelta
import sys
from pathlib import Path

# Ajouter le chemin du backend pour importer config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_CSV_FULL_PATH


# ==========================
# ======== CONFIG =========
# ==========================

CSV_PATH = str(DATA_CSV_FULL_PATH)  # Chargé depuis config.py
SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"  # NQ front month

OUTPUT_TRADES_CSV = "supertrend_scalein_trades.csv"
OUTPUT_PICKLOG_CSV = "front_month_selection_log.csv"

# Time settings (UTC) - Session complète de trading NQ
# NQ trade presque 24h/24, utilisons une session large pour capturer plus de données
SESSION_START_UTC = "00:00:00"  # Début de journée
SESSION_END_UTC = "23:59:59"    # Fin de journée

# SuperTrend parameters
ATR_PERIOD = 10  # Valeur originale du script C#
MULTIPLIER = 3.0  # Valeur originale du script C#

# Risk management
RISK_PER_TRADE_USD = 100.0          # Risk $ par ajout de contrat
MAX_CONTRACTS_TOTAL = 10            # Maximum de contrats total
MAX_SCALE_IN_COUNT = 5              # Maximum de scale-in (ajouts)

# Instrument settings
TICK_SIZE = 0.25
POINT_VALUE = 20.0                  # $/pt (NQ)

# Coûts
SLIPPAGE_TICKS = 0
COMMISSION_RT = 0.0

# Contraintes
TIMEFRAME_MINUTES = 15              # Agrégation en barres 15min
INTRABAR_SEQUENCE: Literal["high_first","low_first"] = "high_first"

# ==========================
# ====== END CONFIG ========
# ==========================

@dataclass
class Trade:
    symbol: str
    date: pd.Timestamp
    entry_time: Optional[pd.Timestamp]
    exit_time: Optional[pd.Timestamp]
    direction: Optional[str]
    st_line_at_entry: float
    scale_in_number: int
    risk_usd: float
    contracts: int
    entry: Optional[float]
    exit: Optional[float]
    result: str
    points: float
    pnl_usd: float

def load_data(csv_path: str, symbol_regex: Optional[str]) -> pd.DataFrame:
    """Charge et prépare les données avec agrégation en timeframe"""
    print(f"Loading raw data from: {csv_path}")
    
    # Charger toutes les données (le filtrage est fait par le runner)
    print("Loading data...")
    df = pd.read_csv(csv_path)
    
    print(f"Columns found: {list(df.columns)}")
    print(f"Sample symbols: {df['symbol'].unique()[:10]}")
    
    # Normalisation des colonnes
    cols = {c.lower(): c for c in df.columns}
    required = ["ts_event","open","high","low","close","symbol"]
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
    
    if "volume" in cols:
        df = df.rename(columns={cols["volume"]: "volume"})
    
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    if symbol_regex:
        print(f"Filtering with regex: {symbol_regex}")
        before_filter = len(df)
        df = df[df["symbol"].astype(str).str.match(symbol_regex)]
        print(f"After symbol filter: {len(df):,} rows (was {before_filter:,})")
        print(f"Symbols after filter: {sorted(df['symbol'].unique())}")
    
    df = df.sort_values(["timestamp","symbol"]).reset_index(drop=True)
    
    print(f"Raw data loaded: {len(df):,} rows")
    
    # Agrégation par timeframe
    if TIMEFRAME_MINUTES > 1:
        print(f"Resampling to {TIMEFRAME_MINUTES}min timeframe...")
        
        # Grouper par symbole et agréger
        resampled_dfs = []
        for symbol, symbol_df in df.groupby('symbol'):
            print(f"  Processing symbol {symbol}: {len(symbol_df)} rows")
            symbol_df = symbol_df.set_index('timestamp')
            
            # Agrégation OHLC
            resampled = symbol_df.resample(f'{TIMEFRAME_MINUTES}T').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum' if 'volume' in symbol_df.columns else 'first'
            }).dropna()
            
            resampled['symbol'] = symbol
            resampled.reset_index(inplace=True)
            print(f"    -> {len(resampled)} bars after resampling")
            resampled_dfs.append(resampled)
        
        df = pd.concat(resampled_dfs, ignore_index=True)
        df = df.sort_values(["timestamp","symbol"]).reset_index(drop=True)
        print(f"Resampled data: {len(df):,} bars")
    
    return df

# === Calendar helpers (CME roll) - Identique aux autres scripts ===
def third_friday(year: int, month: int) -> date:
    import calendar
    c = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [d for d in c.itermonthdates(year, month) if d.weekday() == calendar.FRIDAY and d.month == month]
    return fridays[2]

def roll_date(year: int, month: int) -> date:
    tf = third_friday(year, month)
    return tf - timedelta(days=1)  # Thursday prior

def front_month_for_day(d: date) -> Tuple[str, int]:
    MONTHS = [3,6,9,12]
    CODES  = {3:"H",6:"M",9:"U",12:"Z"}
    events = []
    rd_prev_dec = roll_date(d.year-1, 12)
    events.append((rd_prev_dec, "H", d.year))
    for m in MONTHS:
        rd = roll_date(d.year, m)
        ny = d.year+1 if m==12 else d.year
        nxt = {3:"M",6:"U",9:"Z",12:"H"}[m]
        events.append((rd, nxt, ny))
    events.sort(key=lambda x: x[0])
    last = None
    for ev in events:
        if ev[0] <= d: last = ev
        else: break
    if last is None: return ("H", d.year%10)
    letter, yy = last[1], last[2]%10
    return (letter, yy)

def active_symbol_for_day(d: date) -> str:
    """
    Retourne le symbole actif pour un jour donné
    Adapté aux symboles réels dans les données (NQU4, NQZ4, etc.)
    """
    letter, yy = front_month_for_day(d)
    
    # Mapping des codes de mois vers les symboles réels
    # H=Mars, M=Juin, U=Septembre, Z=Décembre
    month_mapping = {
        "H": "H",  # Mars
        "M": "M",  # Juin  
        "U": "U",  # Septembre
        "Z": "Z"   # Décembre
    }
    
    mapped_letter = month_mapping.get(letter, letter)
    return f"NQ{mapped_letter}{yy}"

def day_bounds(the_date) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Retourne les bornes de session pour un jour donné"""
    tz = "UTC"
    session_start = pd.Timestamp.combine(the_date, pd.to_datetime(SESSION_START_UTC).time()).tz_localize(tz)
    session_end = pd.Timestamp.combine(the_date, pd.to_datetime(SESSION_END_UTC).time()).tz_localize(tz)
    return session_start, session_end

def round_to_tick(x: float, tick: float = TICK_SIZE) -> float:
    return round(x / tick) * tick

# === SuperTrend calculation ===
def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calcule l'Average True Range (ATR)"""
    high = df["high"]
    low = df["low"]
    close = df["close"]
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_supertrend(df: pd.DataFrame, atr_period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
    """
    Calcule l'indicateur SuperTrend selon la logique exacte du script C#
    Retourne un DataFrame avec les colonnes: final_upper, final_lower, st_line
    """
    result = df.copy()
    
    # Calcul ATR
    atr = calculate_atr(df, atr_period)
    
    # Calcul des bandes de base (identique au C#)
    mid_hl2 = (df["high"] + df["low"]) / 2
    basic_upper = mid_hl2 + multiplier * atr
    basic_lower = mid_hl2 - multiplier * atr
    
    # Initialisation des colonnes avec NaN
    result["final_upper"] = np.nan
    result["final_lower"] = np.nan
    result["st_line"] = np.nan
    
    # Commencer après la période ATR (quand ATR est disponible)
    start_idx = atr_period
    
    if len(df) > start_idx:
        # Initialisation à la première barre valide
        result.loc[start_idx, "final_upper"] = basic_upper.iloc[start_idx]
        result.loc[start_idx, "final_lower"] = basic_lower.iloc[start_idx]
        result.loc[start_idx, "st_line"] = basic_lower.iloc[start_idx]  # Commencer en mode haussier
    
    # Calcul itératif à partir de start_idx + 1
    for i in range(start_idx + 1, len(df)):
        # Vérifier que les valeurs précédentes existent
        if pd.isna(result.loc[i-1, "final_upper"]) or pd.isna(basic_upper.iloc[i]):
            continue
            
        # Final bands (logique exacte du C#)
        if basic_upper.iloc[i] < result.loc[i-1, "final_upper"] or df["close"].iloc[i-1] > result.loc[i-1, "final_upper"]:
            result.loc[i, "final_upper"] = basic_upper.iloc[i]
        else:
            result.loc[i, "final_upper"] = result.loc[i-1, "final_upper"]
        
        if basic_lower.iloc[i] > result.loc[i-1, "final_lower"] or df["close"].iloc[i-1] < result.loc[i-1, "final_lower"]:
            result.loc[i, "final_lower"] = basic_lower.iloc[i]
        else:
            result.loc[i, "final_lower"] = result.loc[i-1, "final_lower"]
        
        # SuperTrend line switches between bands (logique exacte du C#)
        if result.loc[i-1, "st_line"] == result.loc[i-1, "final_upper"]:
            if df["close"].iloc[i] <= result.loc[i, "final_upper"]:
                result.loc[i, "st_line"] = result.loc[i, "final_upper"]
            else:
                result.loc[i, "st_line"] = result.loc[i, "final_lower"]
        else:
            if df["close"].iloc[i] >= result.loc[i, "final_lower"]:
                result.loc[i, "st_line"] = result.loc[i, "final_lower"]
            else:
                result.loc[i, "st_line"] = result.loc[i, "final_upper"]
    
    return result

def detect_cross_above(close: pd.Series, st_line: pd.Series) -> pd.Series:
    """
    Détecte les croisements du prix au-dessus de la ligne SuperTrend
    Équivalent à CrossAbove(Close, stLine, 1) dans NinjaScript
    """
    return (close > st_line) & (close.shift(1) <= st_line.shift(1))

def calculate_position_size(close_price: float, st_line: float, risk_usd: float, point_value: float, tick_size: float) -> int:
    """
    Calcule la taille de position basée sur le risque
    Size = Risk$ / (|Close - STLine| * PointValue)
    """
    distance = abs(close_price - st_line)
    
    # Si trop proche, ne pas entrer
    if distance <= tick_size:
        return 0
    
    contracts = int(np.floor(risk_usd / (distance * point_value)))
    return max(1, contracts)

@dataclass
class SuperTrendState:
    """État de la position SuperTrend avec scale-in"""
    is_open: bool = False
    total_contracts: int = 0
    scale_in_counter: int = 0
    entries: List[dict] = None
    
    def __post_init__(self):
        if self.entries is None:
            self.entries = []

def simulate_day(day_df: pd.DataFrame, symbol_label: str, assume: str) -> List[Trade]:
    """Simule une journée de trading avec la stratégie SuperTrend Scale-In"""
    trades: List[Trade] = []
    if day_df.empty: 
        return trades

    the_date = day_df["timestamp"].dt.date.iloc[0]
    session_start, session_end = day_bounds(the_date)

    # Filtrer les données de la session
    mask_session = (
        (day_df["timestamp"] >= session_start) & 
        (day_df["timestamp"] <= session_end) & 
        (day_df["symbol"] == symbol_label)
    )
    s_df = day_df.loc[mask_session].reset_index(drop=True)
    
    if s_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0, 0.0, 0, None, None, "no_data", 0.0, 0.0))
        return trades

    # Vérifier qu'on a assez de données pour SuperTrend
    if len(s_df) < ATR_PERIOD + 10:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0, 0.0, 0, None, None, "insufficient_data", 0.0, 0.0))
        return trades

    # Calcul SuperTrend
    try:
        st_df = calculate_supertrend(s_df, ATR_PERIOD, MULTIPLIER)
        cross_up = detect_cross_above(st_df["close"], st_df["st_line"])
        
        total_signals = cross_up.sum()
        
        if total_signals == 0:
            trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0, 0.0, 0, None, None, "no_signals", 0.0, 0.0))
            return trades
            
    except Exception as e:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0, 0.0, 0, None, None, f"calc_error_{str(e)[:20]}", 0.0, 0.0))
        return trades

    # État de la position
    state = SuperTrendState()
    slip = SLIPPAGE_TICKS * TICK_SIZE

    # Simulation bar par bar
    for i in range(ATR_PERIOD, len(st_df)):  # Commencer après la période ATR
        bar = st_df.iloc[i]
        
        # Signal cross up = Ajouter un contrat (SCALE IN)
        if cross_up.iloc[i]:
            # Vérification du nombre maximum de scale-in
            if state.scale_in_counter >= MAX_SCALE_IN_COUNT:
                continue
            
            # Vérification du nombre total de contrats
            if state.total_contracts >= MAX_CONTRACTS_TOTAL:
                continue
            
            # Calcul de la taille de position
            contracts = calculate_position_size(
                bar["close"],
                bar["st_line"],
                RISK_PER_TRADE_USD,
                POINT_VALUE,
                TICK_SIZE
            )
            
            if contracts == 0:
                continue
            
            # Limite pour ne pas dépasser le max total
            remaining_contracts = MAX_CONTRACTS_TOTAL - state.total_contracts
            if contracts > remaining_contracts:
                contracts = remaining_contracts
            
            if contracts > 0:
                # Ajout du contrat (scale-in)
                entry_price = bar["close"] + slip  # Slippage sur l'entrée
                distance = abs(entry_price - bar["st_line"])
                risk_usd = distance * POINT_VALUE * contracts
                
                # Enregistrement de l'entrée
                state.is_open = True
                state.total_contracts += contracts
                state.scale_in_counter += 1
                
                state.entries.append({
                    "entry_time": bar["timestamp"],
                    "entry_price": entry_price,
                    "contracts": contracts,
                    "scale_in_number": state.scale_in_counter,
                    "st_line": bar["st_line"],
                    "risk_usd": risk_usd
                })

    # À la fin de la session, clôturer toutes les positions ouvertes
    # (Dans la stratégie réelle "NoCut", on garde la position indéfiniment)
    if state.is_open and len(state.entries) > 0:
        final_bar = st_df.iloc[-1]
        exit_price = final_bar["close"] - slip  # Slippage sur la sortie
        exit_time = final_bar["timestamp"]
        
        for entry in state.entries:
            points = exit_price - entry["entry_price"]
            pnl = points * POINT_VALUE * entry["contracts"] - COMMISSION_RT * entry["contracts"]
            
            trade = Trade(
                symbol=symbol_label,
                date=pd.Timestamp(the_date),
                entry_time=entry["entry_time"],
                exit_time=exit_time,
                direction="long",
                st_line_at_entry=entry["st_line"],
                scale_in_number=entry["scale_in_number"],
                risk_usd=entry["risk_usd"],
                contracts=entry["contracts"],
                entry=entry["entry_price"],
                exit=exit_price,
                result="EOD",  # End of Day
                points=points,
                pnl_usd=pnl
            )
            trades.append(trade)

    if len(trades) == 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0, 0.0, 0, None, None, "no_signals", 0.0, 0.0))
    
    return trades

def run_backtest(df: pd.DataFrame, assume: str):
    """Lance le backtest complet"""
    df["utc_date"] = df["timestamp"].dt.date
    all_trades: List[Trade] = []
    picks = []
    
    for d, day_df in df.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        mask_sym = day_df["symbol"] == pick
        has_data = bool(mask_sym.any())
        picks.append({"date": d, "picked_symbol": pick, "has_data": int(has_data)})
        
        if not has_data:
            all_trades.append(Trade(pick, pd.Timestamp(d), None, None, None, 0.0, 0, 0.0, 0, None, None, "no_data", 0.0, 0.0))
            continue
            
        all_trades.extend(simulate_day(day_df, pick, assume=assume))
    
    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date","entry_time"], na_position="last").reset_index(drop=True)
    
    return trades_df, picklog_df

def kpis(trades: pd.DataFrame) -> dict:
    """Calcule les KPIs de performance - Compatible avec le format des autres scripts"""
    real = trades[trades["result"].isin(["TP","SL","EOD"])]
    if real.empty:
        return {"trades": 0, "win_rate": np.nan, "profit_factor": np.nan,
                "avg_win_usd": np.nan, "avg_loss_usd": np.nan,
                "expectancy_usd": np.nan, "net_pnl_usd": 0.0,
                "max_dd_usd": 0.0, "days": int(trades["date"].nunique() if not trades.empty else 0)}
    
    # Utiliser la même logique que les autres scripts : result="TP" pour les gains
    # Mais pour SuperTrend, on utilise pnl_usd > 0 car tous les résultats sont "EOD"
    wins = real[real["pnl_usd"] > 0]
    losses = real[real["pnl_usd"] <= 0]
    
    net = real["pnl_usd"].sum()
    win_rate = len(wins) / len(real) if len(real) > 0 else 0.0
    
    # Moyennes des gains et pertes
    avg_win = wins["pnl_usd"].mean() if len(wins) > 0 else 0.0
    avg_loss = losses["pnl_usd"].mean() if len(losses) > 0 else 0.0
    
    # Profit factor
    gross_profit = wins["pnl_usd"].sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses["pnl_usd"].sum()) if len(losses) > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.99 if gross_profit > 0 else 0.0)
    
    expectancy = net / len(real) if len(real) > 0 else 0.0
    
    # Calcul du drawdown
    equity = real["pnl_usd"].cumsum()
    roll_max = equity.cummax()
    drawdown = equity - roll_max
    max_dd = drawdown.min()
    
    # S'assurer que toutes les valeurs sont des types Python standard (pas numpy)
    return {
        "trades": int(len(real)), 
        "win_rate": float(win_rate), 
        "profit_factor": float(profit_factor),
        "avg_win_usd": float(avg_win) if not np.isnan(avg_win) else 0.0,
        "avg_loss_usd": float(avg_loss) if not np.isnan(avg_loss) else 0.0,
        "expectancy_usd": float(expectancy), 
        "net_pnl_usd": float(net),
        "max_dd_usd": float(max_dd), 
        "days": int(trades["date"].nunique()),
        "winning_trades": int(len(wins)),  # Ajout pour compatibilité
        "losing_trades": int(len(losses)),  # Ajout pour compatibilité
        "gross_profit": float(gross_profit),  # Ajout pour compatibilité
        "gross_loss": float(gross_loss)  # Ajout pour compatibilité
    }

def print_stats(title: str, stats: dict):
    """Affiche les statistiques"""
    print(f"\n=== {title} ===")
    for k, v in stats.items():
        if isinstance(v, float):
            if "rate" in k:
                print(f"{k:>20}: {v:.2%}")
            elif "factor" in k:
                print(f"{k:>20}: {'inf' if np.isinf(v) else f'{v:.2f}'}")
            else:
                print(f"{k:>20}: {v:,.2f}")
        else:
            print(f"{k:>20}: {v}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("SuperTrend ScaleIn NoCut - Backtest")
    print("=" * 60)
    print(f"Parameters:")
    print(f"  - ATR Period: {ATR_PERIOD}")
    print(f"  - Multiplier: {MULTIPLIER}")
    print(f"  - Risk per Trade: ${RISK_PER_TRADE_USD}")
    print(f"  - Max Contracts Total: {MAX_CONTRACTS_TOTAL}")
    print(f"  - Max Scale-In Count: {MAX_SCALE_IN_COUNT}")
    print(f"  - Timeframe: {TIMEFRAME_MINUTES}min")
    print("=" * 60)
    
    try:
        # Chargement des données
        print("Loading data (UTC)...")
        df = load_data(CSV_PATH, SYMBOL_FILTER_REGEX)
        print(f"Rows total: {len(df):,} | Symbols example: {sorted(df['symbol'].astype(str).unique())[:8]} ...")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Lancement du backtest
        print(f"Running SuperTrend backtest with {INTRABAR_SEQUENCE} sequence...")
        trades, picklog = run_backtest(df, assume=INTRABAR_SEQUENCE)
        
        # Sauvegarde
        trades.to_csv(OUTPUT_TRADES_CSV, index=False)
        picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
        print(f"Saved trades to: {OUTPUT_TRADES_CSV}")
        print(f"Saved selection log to: {OUTPUT_PICKLOG_CSV}")
        
        # Calcul et affichage des KPIs
        stats = kpis(trades)
        print_stats("SUPERTREND SCALE-IN RESULTS", stats)
        
        # Affichage de quelques trades d'exemple
        real_trades = trades[trades["result"].isin(["TP","SL","EOD"])]
        if not real_trades.empty:
            print(f"\n=== SAMPLE TRADES (first 5) ===")
            sample = real_trades.head()
            for _, trade in sample.iterrows():
                print(f"{trade['date'].strftime('%Y-%m-%d')} | {trade['symbol']} | Scale-in #{trade['scale_in_number']} | "
                      f"{trade['contracts']} contracts @ {trade['entry']:.2f} -> {trade['exit']:.2f} | "
                      f"{trade['points']:.2f}pts | ${trade['pnl_usd']:.2f}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
