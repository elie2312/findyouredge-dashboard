#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST - 30mn Close Strategy - Simple Candle Direction
Regles:
- A la cloture de chaque barre 30mn:
    * bougie verte (close > open) => LONG
    * bougie rouge (close < open) => SHORT
- Entrees possibles dans la fenetre horaire configuree, max 4/jour
- Sizing: 1 contrat fixe
- SL: bas (long) / haut (short) de la bougie precedente (30mn)
- TP: 1R (meme distance que SL)
- Flat force a FLAT_TIME_UTC
Strategie simple pour tester la qualite des donnees et le timing.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Literal
from datetime import date, timedelta

# ==========================
# ======== CONFIG ==========
# ==========================

CSV_PATH = r"C:/Users/elieb/Desktop/Dashboard/backend_runs/9a02bd92/filtered_data.csv"
SYMBOL_FILTER_REGEX = r"^NQ[A-Z][0-9]{1,2}$"

OUTPUT_TRADES_CSV = "close30_trades.csv"
OUTPUT_PICKLOG_CSV = "front_month_selection_log.csv"

# Fenetres horaires (UTC)
ENTRY_WINDOW_START_UTC = "10:00:00"
ENTRY_WINDOW_END_UTC   = "16:00:00"
FLAT_TIME_UTC          = "20:00:00"   # flat force

# Instrument
TICK_SIZE   = 0.25
POINT_VALUE = 20.0       # $/pt

# Couts
SLIPPAGE_TICKS = 0
COMMISSION_RT  = 0.0

# Contraintes
MAX_TRADES_PER_DAY = 4
MAX_RISK_USD = 1000.0                 # Risque maximum par trade (pour decouverte)
INTRABAR_SEQUENCE: Literal["high_first","low_first"] = "high_first"  # si une barre touche TP & SL

# ==========================
# ====== HELPERS CSV =======
# ==========================

def load_data(csv_path: str, symbol_regex: Optional[str]) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
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
    if symbol_regex:
        df = df[df["symbol"].astype(str).str.match(symbol_regex)]
    df = df.sort_values(["timestamp","symbol"]).reset_index(drop=True)
    return df

# === Calendar helpers (CME roll) ===
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
    letter, yy = front_month_for_day(d)
    return f"NQ{letter}{yy}"

def day_bounds(the_date) -> Tuple[pd.Timestamp, pd.Timestamp]:
    tz = "UTC"
    start = pd.Timestamp.combine(the_date, pd.to_datetime(ENTRY_WINDOW_START_UTC).time()).tz_localize(tz)
    end   = pd.Timestamp.combine(the_date, pd.to_datetime(ENTRY_WINDOW_END_UTC).time()).tz_localize(tz)
    return start, end

def flat_time(the_date) -> pd.Timestamp:
    tz = "UTC"
    return pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)

# ==========================
# ==== RESAMPLE 30-MIN =====
# ==========================

def resample_30m(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège par symbole en 30 minutes (label/right-closed),
    avec timestamp = fin de la fenêtre (la clôture 30mn).
    """
    df = df.copy()
    df.set_index("timestamp", inplace=True)
    res = []
    for sym, g in df.groupby("symbol"):
        ohlc = g[["open","high","low","close"]].resample("30T", label="right", closed="right").agg({
            "open":"first", "high":"max", "low":"min", "close":"last"
        })
        if "volume" in g.columns:
            vol = g[["volume"]].resample("30T", label="right", closed="right").sum()
            ohlc = ohlc.join(vol, how="left")
        ohlc["symbol"] = sym
        res.append(ohlc.reset_index())
    out = pd.concat(res, ignore_index=True).dropna(subset=["open","high","low","close"])
    out = out.sort_values(["timestamp","symbol"]).reset_index(drop=True)
    return out

# ==========================
# ======= TRADES ===========
# ==========================

@dataclass
class Trade:
    symbol: str
    date: pd.Timestamp
    entry_time: Optional[pd.Timestamp]
    exit_time: Optional[pd.Timestamp]
    direction: Optional[str]
    entry: Optional[float]
    tp: Optional[float]
    sl: Optional[float]
    points: float
    pnl_usd: float
    contracts: int
    result: str

def round_to_tick(x: float, tick: float = TICK_SIZE) -> float:
    return round(x / tick) * tick

def choose_first_touch(bar, level_high, level_low, assume: str) -> Optional[str]:
    hit_high = bar["high"] >= level_high if level_high is not None else False
    hit_low  = bar["low"]  <= level_low  if level_low  is not None else False
    if hit_high and hit_low:
        return "high" if assume == "high_first" else "low"
    elif hit_high:
        return "high"
    elif hit_low:
        return "low"
    else:
        return None

def simulate_day(day_df_30: pd.DataFrame, symbol_label: str) -> List[Trade]:
    """
    day_df_30: barres 30mn (symbol=symbol_label) couvrant la journée en UTC.
    Entrées possibles aux clôtures dans [13:00, 14:00], soit barres se terminant à 13:30 et 14:00.
    Sorties: TP/SL sur barres suivantes (30mn), flat forcé à FLAT_TIME_UTC.
    """
    trades: List[Trade] = []
    if day_df_30.empty:
        return trades

    the_date = day_df_30["timestamp"].dt.date.iloc[0]
    start, end = day_bounds(the_date)
    flat = flat_time(the_date)

    # Filtre session (jusqu'au flat) et symbole
    s_df = day_df_30[(day_df_30["symbol"] == symbol_label) &
                     (day_df_30["timestamp"] >= start) &
                     (day_df_30["timestamp"] <= flat)].reset_index(drop=True)

    if s_df.empty:
        return trades

    # Indices des barres dont la clôture est dans la fenêtre d’entrées
    entry_mask = (s_df["timestamp"] >= start) & (s_df["timestamp"] <= end)
    entry_idx = list(s_df[entry_mask].index)

    contracts = 1
    slip = SLIPPAGE_TICKS * TICK_SIZE
    trades_done = 0

    # Pour SL on a besoin de la bougie précédente (30mn)
    for i in entry_idx:
        if trades_done >= MAX_TRADES_PER_DAY:
            break
        if i == 0:
            continue  # pas de précédente

        prev_bar = s_df.loc[i-1]
        bar = s_df.loc[i]

        # Déterminer la couleur de la bougie d’entrée
        if pd.isna(bar["open"]) or pd.isna(bar["close"]):
            continue
        if bar["close"] > bar["open"]:
            direction = "long"
            entry = bar["close"] + slip
            sl = prev_bar["low"]
            if pd.isna(sl) or sl >= entry:
                continue  # skip si SL invalide
            r_pts = round_to_tick(entry - sl, TICK_SIZE)
            tp = entry + r_pts
        elif bar["close"] < bar["open"]:
            direction = "short"
            entry = bar["close"] - slip
            sl = prev_bar["high"]
            if pd.isna(sl) or sl <= entry:
                continue
            r_pts = round_to_tick(sl - entry, TICK_SIZE)
            tp = entry - r_pts
        else:
            # doji: pas de trade
            continue

        # Parcours des barres suivantes jusqu’au flat pour TP/SL
        exit_time = None
        exit_price = None
        result = "EOD"
        points = 0.0

        for j in range(i+1, len(s_df)):
            b = s_df.loc[j]
            if direction == "long":
                touch = choose_first_touch(b, level_high=tp, level_low=sl, assume=INTRABAR_SEQUENCE)
                if touch == "high":
                    exit_price = tp + slip; exit_time = b["timestamp"]; result = "TP"; break
                elif touch == "low":
                    exit_price = sl - slip; exit_time = b["timestamp"]; result = "SL"; break
            else:
                touch = choose_first_touch(b, level_high=sl, level_low=tp, assume=INTRABAR_SEQUENCE)
                if touch == "low":
                    exit_price = tp - slip; exit_time = b["timestamp"]; result = "TP"; break
                elif touch == "high":
                    exit_price = sl + slip; exit_time = b["timestamp"]; result = "SL"; break

            if b["timestamp"] >= flat:
                break

        # Si pas touché TP/SL avant le flat: on clôture à la close de la dernière barre dispo <= flat
        if exit_time is None:
            last = s_df[s_df["timestamp"] <= flat].iloc[-1]
            exit_time = last["timestamp"]
            exit_price = last["close"]
            result = "EOD"

        if direction == "long":
            points = (exit_price - entry)
        else:
            points = (entry - exit_price)

        pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts

        trades.append(Trade(
            symbol=symbol_label,
            date=pd.Timestamp(the_date),
            entry_time=bar["timestamp"],
            exit_time=exit_time,
            direction=direction,
            entry=float(entry),
            tp=float(tp),
            sl=float(sl),
            points=float(points),
            pnl_usd=float(pnl),
            contracts=contracts,
            result=result
        ))
        trades_done += 1

    return trades

# ==========================
# ========= RUN ============
# ==========================

def run_backtest(df_raw: pd.DataFrame):
    # Agrégation 30mn
    df30 = resample_30m(df_raw)
    df30["utc_date"] = df30["timestamp"].dt.date

    all_trades: List[Trade] = []
    picks = []

    for d, day_df in df30.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        has_data = bool((day_df["symbol"] == pick).any())
        picks.append({"date": d, "picked_symbol": pick, "has_data": int(has_data)})
        if not has_data:
            continue
        all_trades.extend(simulate_day(day_df, pick))

    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date","entry_time"], na_position="last").reset_index(drop=True)
    return trades_df, picklog_df

# ==========================
# ======= METRICS ==========
# ==========================

def kpis(trades: pd.DataFrame) -> dict:
    real = trades[trades["result"].isin(["TP","SL","EOD"])]
    if real.empty:
        return {"trades": 0, "win_rate": np.nan, "profit_factor": np.nan,
                "avg_win_usd": np.nan, "avg_loss_usd": np.nan,
                "expectancy_usd": np.nan, "net_pnl_usd": 0.0,
                "max_dd_usd": 0.0, "days": int(trades["date"].nunique() if not trades.empty else 0)}
    wins = real[real["result"] == "TP"]["pnl_usd"]
    losses = real[real["result"] != "TP"]["pnl_usd"]
    net = real["pnl_usd"].sum()
    win_rate = len(wins) / len(real) if len(real) > 0 else np.nan
    avg_win = wins.mean() if len(wins) > 0 else 0.0
    avg_loss = losses.mean() if len(losses) > 0 else 0.0
    gross_profit = wins.sum() if len(wins) > 0 else 0.0
    gross_loss = -losses.sum() if len(losses) > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf
    expectancy = net / len(real)
    equity = real["pnl_usd"].cumsum()
    roll_max = equity.cummax()
    drawdown = equity - roll_max
    max_dd = drawdown.min()
    return {"trades": int(len(real)), "win_rate": float(win_rate), "profit_factor": float(profit_factor),
            "avg_win_usd": float(avg_win) if not np.isnan(avg_win) else 0.0,
            "avg_loss_usd": float(avg_loss) if not np.isnan(avg_loss) else 0.0,
            "expectancy_usd": float(expectancy), "net_pnl_usd": float(net),
            "max_dd_usd": float(max_dd), "days": int(trades["date"].nunique())}

def print_stats(title: str, stats: dict):
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

def main():
    print("Loading data (UTC)...")
    df = load_data(CSV_PATH, SYMBOL_FILTER_REGEX)
    print(f"Rows total: {len(df):,} | Symbols example: {sorted(df['symbol'].astype(str).unique())[:8]} ...")
    trades, picklog = run_backtest(df)
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"Saved trades to: {OUTPUT_TRADES_CSV}")
    print(f"Saved selection log to: {OUTPUT_PICKLOG_CSV}")
    stats = kpis(trades)
    print_stats("RESULTS (30mn close strategy - Simple Candle)", stats)

if __name__ == "__main__":
    main()
