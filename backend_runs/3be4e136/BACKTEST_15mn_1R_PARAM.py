#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTEST — OPR 15MN — NQ front-month — 1 trade / jour
Variante: **SL = 1R paramétrable** (en points), TP = k * R paramétrable.
Entrées au break de l'OR avec buffer en ticks.
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


# ==========================
# ======== CONFIG =========
# ==========================

CSV_PATH = r"C:/Users/elieb/Desktop/Dashboard/backend_runs/3be4e136/filtered_data.csv"  # Chargé depuis config.py
SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"

OUTPUT_TRADES_CSV = "opr_trades_1R_param.csv"
OUTPUT_PICKLOG_CSV = "front_month_selection_log.csv"

# Time settings (UTC)
OPR_START_UTC = "13:30:00"
OPR_MINUTES   = 15                      # 13:30:00 -> 13:44:59
FLAT_TIME_UTC = "20:00:00"

# Instrument settings
TICK_SIZE     = 0.25
POINT_VALUE   = 20.0                    # $/pt

# ======== NOUVEAU: système 1R =========
# Choisis le mode d'arrêt:
#   - "fixed_r_points": SL = R_POINTS (constante, en points)
#   - "opr_fraction"  : SL = OPR * SL_MULTIPLIER (fallback à l'ancien comportement)
STOP_MODE       : Literal["fixed_r_points","opr_fraction"] = "fixed_r_points"
R_POINTS        = 12.0                 # 1R (points) — paramétrable
TP_IN_R         = 0.40                 # TP = k * R (ex: 0.40 -> 0.4R)
SL_MULTIPLIER   = 0.50                 # utilisé seulement si STOP_MODE="opr_fraction"

# Entry buffer
ENTRY_BUFFER_TICKS = 2                 # entrée = ORH + buffer / ORL − buffer

# Skip & sizing / risk
SL_SKIP_LT       = 6.0                 # on skip si SL < ce seuil (points)
SIZE_FOR_SMALL_R = 2                   # nb contrats quand R < THRESH_2C
THRESH_2C        = 40.0                # bascule sizing 2 -> 1 contrat au-dessus
SIZE_FOR_LARGE_R = 1
RISK_CAP_USD     = 3000.0              # skip si risque > cap

# Coûts
SLIPPAGE_TICKS   = 0
COMMISSION_RT    = 0.0

# Contraintes
MAX_TRADES_PER_DAY = 1
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
    or_high: float
    or_low: float
    stop_pts: float
    tp_pts: float
    contracts: int
    risk_usd: float
    entry: Optional[float]
    tp: Optional[float]
    sl: Optional[float]
    exit: Optional[float]
    result: str
    points: float
    pnl_usd: float

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

def day_bounds(the_date) -> Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    tz = "UTC"
    opr_start = pd.Timestamp.combine(the_date, pd.to_datetime(OPR_START_UTC).time()).tz_localize(tz)
    opr_end   = opr_start + pd.Timedelta(minutes=OPR_MINUTES) - pd.Timedelta(seconds=1)
    flat_time = pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)
    return opr_start, opr_end, flat_time

def compute_or_window(day_df: pd.DataFrame, opr_start: pd.Timestamp, minutes: int):
    end = opr_start + pd.Timedelta(minutes=minutes) - pd.Timedelta(seconds=1)
    or_mask = (day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= end)
    post_mask = day_df["timestamp"] > end
    return day_df.loc[or_mask], day_df.loc[post_mask]

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

def round_to_tick(x: float, tick: float = TICK_SIZE) -> float:
    return round(x / tick) * tick

def get_stop_and_tp(or_high: float, or_low: float) -> Tuple[float, float]:
    """Retourne (stop_pts, tp_pts) en points."""
    or_range = or_high - or_low
    if STOP_MODE == "fixed_r_points":
        stop_pts = float(R_POINTS)
    else:
        stop_pts = float(or_range) * float(SL_MULTIPLIER)
    if stop_pts <= 0:
        stop_pts = float(R_POINTS)

    tp_pts = float(TP_IN_R) * float(R_POINTS) if STOP_MODE == "fixed_r_points" else float(TP_IN_R) * stop_pts
    tp_pts = max(round_to_tick(tp_pts, 0.25), TICK_SIZE)  # arrondi + borne minimale
    return stop_pts, tp_pts

def contracts_for_stop(stop_pts: float) -> int:
    if stop_pts < SL_SKIP_LT:
        return 0
    return SIZE_FOR_SMALL_R if stop_pts < THRESH_2C else SIZE_FOR_LARGE_R

@dataclass
class SimState:
    in_position: bool = False
    direction: Optional[str] = None
    entry_price: Optional[float] = None
    entry_time: Optional[pd.Timestamp] = None
    tp: Optional[float] = None
    sl: Optional[float] = None

def simulate_day(day_df: pd.DataFrame, symbol_label: str, assume: str) -> List[Trade]:
    trades: List[Trade] = []
    if day_df.empty: return trades

    the_date = day_df["timestamp"].dt.date.iloc[0]
    opr_start, opr_end, flat_time = day_bounds(the_date)

    mask_session = (day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= flat_time) & (day_df["symbol"] == symbol_label)
    s_df = day_df.loc[mask_session].reset_index(drop=True)
    if s_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    or_df, post_df = compute_or_window(s_df, opr_start, OPR_MINUTES)
    if or_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades
    post_df = post_df[post_df["timestamp"] <= flat_time].copy()
    if post_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, float(or_df["high"].max()), float(or_df["low"].min()), 0.0, 0.0, 0, 0.0, None, None, None, None, "no_fill", 0.0, 0.0))
        return trades

    or_high = float(or_df["high"].max())
    or_low  = float(or_df["low"].min())
    stop_pts, tp_pts = get_stop_and_tp(or_high, or_low)

    # Check sizing / risk
    contracts = contracts_for_stop(stop_pts)
    if contracts == 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, or_high, or_low, stop_pts, tp_pts, 0, 0.0, None, None, None, None, "skip_sl", 0.0, 0.0))
        return trades
    risk_usd = stop_pts * POINT_VALUE * contracts
    if risk_usd > RISK_CAP_USD:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, or_high, or_low, stop_pts, tp_pts, 0, risk_usd, None, None, None, None, "skip_risk_cap", 0.0, 0.0))
        return trades

    # Levels
    buffer = ENTRY_BUFFER_TICKS * TICK_SIZE
    buy_stop  = or_high + buffer
    sell_stop = or_low  - buffer
    slip = SLIPPAGE_TICKS * TICK_SIZE

    state = SimState()
    trades_done = 0

    for _, bar in post_df.iterrows():
        if trades_done >= MAX_TRADES_PER_DAY:
            break

        if not state.in_position:
            touch = choose_first_touch(bar, level_high=buy_stop, level_low=sell_stop, assume=assume)
            if touch is None:
                continue
            state.in_position = True
            state.direction = "long" if touch == "high" else "short"
            state.entry_price = (buy_stop if touch == "high" else sell_stop) + (slip if touch == "high" else -slip)
            state.entry_time = bar["timestamp"]
            if state.direction == "long":
                state.tp = state.entry_price + tp_pts
                state.sl = state.entry_price - stop_pts
            else:
                state.tp = state.entry_price - tp_pts
                state.sl = state.entry_price + stop_pts

            # same-bar exit
            if state.direction == "long":
                exit_touch = choose_first_touch(bar, level_high=state.tp, level_low=state.sl, assume=assume)
                if exit_touch is not None:
                    if exit_touch == "high":
                        exit_price = state.tp + slip; result = "TP"; points = (exit_price - state.entry_price)
                    else:
                        exit_price = state.sl - slip; result = "SL"; points = (exit_price - state.entry_price)
                    pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
                    trades.append(Trade(symbol_label, pd.Timestamp(state.entry_time.date()), state.entry_time, bar["timestamp"], state.direction, or_high, or_low, stop_pts, tp_pts, contracts, risk_usd, state.entry_price, state.tp, state.sl, exit_price, result, points, pnl))
                    state = SimState(); trades_done += 1
            else:
                exit_touch = choose_first_touch(bar, level_high=state.sl, level_low=state.tp, assume=assume)
                if exit_touch is not None:
                    if exit_touch == "low":
                        exit_price = state.tp - slip; result = "TP"; points = (state.entry_price - exit_price)
                    else:
                        exit_price = state.sl + slip; result = "SL"; points = (state.entry_price - exit_price)
                    pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
                    trades.append(Trade(symbol_label, pd.Timestamp(state.entry_time.date()), state.entry_time, bar["timestamp"], state.direction, or_high, or_low, stop_pts, tp_pts, contracts, risk_usd, state.entry_price, state.tp, state.sl, exit_price, result, points, pnl))
                    state = SimState(); trades_done += 1
            continue

        # exits
        if state.in_position and state.direction == "long":
            exit_touch = choose_first_touch(bar, level_high=state.tp, level_low=state.sl, assume=assume)
            if exit_touch is None: 
                continue
            if exit_touch == "high":
                exit_price = state.tp + slip; result = "TP"; points = (exit_price - state.entry_price)
            else:
                exit_price = state.sl - slip; result = "SL"; points = (exit_price - state.entry_price)
            pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
            trades.append(Trade(symbol_label, pd.Timestamp(state.entry_time.date()), state.entry_time, bar["timestamp"], state.direction, or_high, or_low, stop_pts, tp_pts, contracts, risk_usd, state.entry_price, state.tp, state.sl, exit_price, result, points, pnl))
            state = SimState(); trades_done += 1

        elif state.in_position and state.direction == "short":
            exit_touch = choose_first_touch(bar, level_high=state.sl, level_low=state.tp, assume=assume)
            if exit_touch is None:
                continue
            if exit_touch == "low":
                exit_price = state.tp - slip; result = "TP"; points = (state.entry_price - exit_price)
            else:
                exit_price = state.sl + slip; result = "SL"; points = (state.entry_price - exit_price)
            pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
            trades.append(Trade(symbol_label, pd.Timestamp(state.entry_time.date()), state.entry_time, bar["timestamp"], state.direction, or_high, or_low, stop_pts, tp_pts, contracts, risk_usd, state.entry_price, state.tp, state.sl, exit_price, result, points, pnl))
            state = SimState(); trades_done += 1

    # Flat forcé
    if state.in_position:
        last_bar = post_df.iloc[-1]
        exit_price = float(last_bar["close"])
        result = "EOD"
        points = (exit_price - state.entry_price) if state.direction == "long" else (state.entry_price - exit_price)
        pnl = points * POINT_VALUE * contracts - COMMISSION_RT * contracts
        trades.append(Trade(symbol_label, pd.Timestamp(state.entry_time.date()), state.entry_time, last_bar["timestamp"], state.direction, or_high, or_low, stop_pts, tp_pts, contracts, risk_usd, state.entry_price, state.tp, state.sl, exit_price, result, points, pnl))

    if len(trades) == 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None, 0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_fill", 0.0, 0.0))
    return trades

def run_backtest(df: pd.DataFrame, assume: str):
    df["utc_date"] = df["timestamp"].dt.date
    all_trades: List[Trade] = []
    picks = []
    for d, day_df in df.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        mask_sym = day_df["symbol"] == pick
        has_data = bool(mask_sym.any())
        picks.append({"date": d, "picked_symbol": pick, "has_data": int(has_data)})
        if not has_data:
            all_trades.append(Trade(pick, pd.Timestamp(d), None, None, None, 0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
            continue
        all_trades.extend(simulate_day(day_df, pick, assume=assume))
    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date","entry_time"], na_position="last").reset_index(drop=True)
    return trades_df, picklog_df

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
    print(f"Backtest with STOP_MODE={STOP_MODE} | R_POINTS={R_POINTS} | TP_IN_R={TP_IN_R} ...")
    trades, picklog = run_backtest(df, assume=INTRABAR_SEQUENCE)
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"Saved trades to: {OUTPUT_TRADES_CSV}")
    print(f"Saved selection log to: {OUTPUT_PICKLOG_CSV}")
    stats = kpis(trades)
    print_stats("RESULTS (1R param)", stats)

if __name__ == "__main__":
    main()

