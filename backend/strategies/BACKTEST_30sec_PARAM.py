#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BACKTEST — OPR 30 sec — NQ front-month (CME roll) — 1 trade / jour
Variante: ENTRY_BUFFER_TICKS = 2 → entrée à ORH + buffer / ORL − buffer.
Entrées autorisées dès **13:30:30 UTC** (fin de l’OPR 30s).

⚙️ Sizing automatique avec bascule E-mini/Micro:
- On cherche une combinaison NQ (20 $/pt) et MNQ (2 $/pt) pour que le
  risque/trade ∈ [2 000 ; 2 500] USD (ciblé à 2 250 USD).
- Si 1 NQ est “trop gros”, on passe en micro et on ajuste la taille.
- La colonne `size_label` indique la répartition: p.ex. "NQ=0;MNQ=125".
"""

import calendar
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict
from typing import List, Optional, Literal, Tuple
from datetime import timedelta
import sys
from pathlib import Path

# Ajouter le chemin du backend pour importer config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_CSV_FULL_PATH


# ==========================
# ========= CONFIG =========
# ==========================

CSV_PATH = str(DATA_CSV_FULL_PATH)  # Chargé depuis config.py
SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"  # NQ front month

OUTPUT_TRADES_CSV   = "opr_trades_utc_front_month_entry_buffer_30secOPR.csv"
OUTPUT_PICKLOG_CSV  = "front_month_selection_log_30secOPR.csv"

# Time settings (all UTC)
OPR_START_UTC = "13:30:00"        # OPR démarre 13:30:00
OPR_SECONDS   = 30                # … et dure 30 secondes → 13:30:00..13:30:29
FLAT_TIME_UTC = "20:00:00"        # flat forcé si encore en position

# Instrument settings (NQ)
TICK_SIZE     = 0.25
EMINI_PV      = 20.0              # $/pt (NQ)
MICRO_PV      = 2.0               # $/pt (MNQ)

SL_MULTIPLIER = 0.5               # SL = 0.5 * (ORH-ORL)
ENTRY_BUFFER_TICKS = 2            # entrée = ORH + 0.5 / ORL - 0.5

# TP rules
R_TARGET         = 0.12
TP_MIN_POINTS    = 2
TP_MAX_POINTS    = 4
SL_TP_FIXED_5_AT = 40.0           # si SL >= 40 pts → TP = 5.0

# Trading costs
SLIPPAGE_TICKS = 0
COMMISSION_RT_EMINI = 0.0
COMMISSION_RT_MICRO = 0.0

# Constraints
MAX_TRADES_PER_DAY = 1
INTRABAR_SEQUENCE: Literal["high_first","low_first"] = "high_first"

# === Risk band sizing (USD) + bornes de tailles ===
RISK_MIN_USD     = 1000.0
RISK_MAX_USD     = 1500.0
RISK_TARGET_USD  = 1250.0
MAX_EMINI        = 7
MAX_MICRO        = 70

# ==========================
# ====== END CONFIG ========
# ==========================

@dataclass
class Trade:
    symbol: str
    date: pd.Timestamp
    entry_time: Optional[pd.Timestamp]
    exit_time: Optional[pd.Timestamp]
    direction: Optional[str]                # "long" or "short"
    or_high: float
    or_low: float
    stop_pts: float
    tp_pts: float
    emini_qty: int
    micro_qty: int
    size_label: str
    risk_usd: float
    entry: Optional[float]
    tp: Optional[float]
    sl: Optional[float]
    exit: Optional[float]
    result: str                             # "TP","SL","EOD","no_fill","skip_risk_band","no_data"
    points: float
    pnl_usd: float

# --------- IO / data prep ----------
def load_data(csv_path: str, symbol_regex: Optional[str]) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    cols = {c.lower(): c for c in df.columns}
    required = ["ts_event","open","high","low","close","symbol"]
    for r in required:
        if r not in cols:
            raise ValueError(f"Missing required column: {r}")
    df = df.rename(columns={
        cols["ts_event"]: "timestamp",
        cols["open"]:     "open",
        cols["high"]:     "high",
        cols["low"]:      "low",
        cols["close"]:    "close",
        cols["symbol"]:   "symbol",
    })
    if "volume" in cols:
        df = df.rename(columns={cols["volume"]: "volume"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if symbol_regex:
        df = df[df["symbol"].astype(str).str.match(symbol_regex)]
    df = df.sort_values(["timestamp","symbol"]).reset_index(drop=True)
    return df

# --------- Symbol front-month (CME rolls) ----------
def third_friday(year: int, month: int):
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [d for d in cal.itermonthdates(year, month)
               if d.weekday() == calendar.FRIDAY and d.month == month]
    return fridays[2]

def roll_date(year: int, month: int):
    return third_friday(year, month) - pd.Timedelta(days=1)  # jeudi avant 3e vendredi

def front_month_for_day(d) -> Tuple[str, int]:
    y = d.year
    events = []
    events.append((roll_date(y-1, 12), "H", y))
    for m, nxt in [(3,"M"), (6,"U"), (9,"Z"), (12,"H")]:
        events.append((roll_date(y, m), nxt, y+1 if m == 12 else y))
    events.sort(key=lambda x: x[0])
    last = None
    for ev in events:
        if ev[0] <= d: last = ev
        else: break
    if last is None:
        return ("H", y % 10)
    letter, yy = last[1], last[2]
    return (letter, yy % 10)

def active_symbol_for_day(d) -> str:
    letter, yy_digit = front_month_for_day(d)
    return f"NQ{letter}{yy_digit}"

# --------- Time windows ----------
def day_bounds(the_date) -> Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    tz = "UTC"
    opr_start = pd.Timestamp.combine(the_date, pd.to_datetime(OPR_START_UTC).time()).tz_localize(tz)
    opr_end   = opr_start + pd.Timedelta(seconds=OPR_SECONDS) - pd.Timedelta(seconds=1)  # 13:30:29
    flat_time = pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)
    return opr_start, opr_end, flat_time

def compute_or_window_seconds(day_df: pd.DataFrame, opr_start: pd.Timestamp, seconds: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    end = opr_start + pd.Timedelta(seconds=seconds) - pd.Timedelta(seconds=1)
    or_mask   = (day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= end)   # 13:30:00..13:30:29
    post_mask =  day_df["timestamp"] > end                                         # entrée dès 13:30:30
    return day_df.loc[or_mask], day_df.loc[post_mask]

# --------- Helpers ----------
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

def tp_points_from_stop(stop_pts: float) -> float:
    if stop_pts >= SL_TP_FIXED_5_AT:
        return 5.0
    raw = R_TARGET * stop_pts
    tp = round_to_tick(raw, 0.25)
    tp = max(TP_MIN_POINTS, min(tp, TP_MAX_POINTS))
    return tp

# --------- Risk band sizing with E-mini + Micro ----------
def size_for_risk(stop_pts: float) -> tuple[int, int, float, str]:
    """
    Trouve (n_emini, n_micro, risk_usd, size_label) s.t.
    risk_usd = stop_pts * (EMINI_PV*n_emini + MICRO_PV*n_micro) ∈ [RISK_MIN_USD, RISK_MAX_USD]
    et le plus proche de RISK_TARGET_USD.
    """
    if not np.isfinite(stop_pts) or stop_pts <= 0:
        return 0, 0, 0.0, "NQ=0;MNQ=0"

    # Parcours raisonnable des E-mini possibles puis ajuste MNQ
    best = None
    max_e = min(MAX_EMINI, int(np.floor(RISK_MAX_USD / (stop_pts * EMINI_PV))) + 1)
    for e in range(0, max_e + 1):
        risk_e = stop_pts * (EMINI_PV * e)
        # Reste de marge pour micro
        rem_min = max(RISK_MIN_USD - risk_e, 0.0)
        rem_max = max(RISK_MAX_USD - risk_e, 0.0)

        # Si même sans micro on dépasse déjà le max -> stop
        if risk_e > RISK_MAX_USD:
            continue

        # Borne micro
        if stop_pts * MICRO_PV > 0:
            m_min = int(np.ceil(rem_min / (stop_pts * MICRO_PV))) if rem_min > 0 else 0
            m_max = int(np.floor(rem_max / (stop_pts * MICRO_PV)))
        else:
            m_min, m_max = 0, 0

        m_min = max(0, m_min)
        m_max = min(MAX_MICRO, max(0, m_max))

        if m_min > m_max:
            # Pas de combinaison exacte dans la bande avec ce e-mini
            # On peut quand même tester le meilleur m dans [0..MAX_MICRO] en visant target (sous contrainte <= max)
            if stop_pts * MICRO_PV > 0:
                m_target = int(np.floor((RISK_TARGET_USD - risk_e) / (stop_pts * MICRO_PV)))
                m_target = max(0, min(m_target, MAX_MICRO))
                risk_try = stop_pts * (EMINI_PV * e + MICRO_PV * m_target)
                if risk_try <= RISK_MAX_USD:
                    score = abs(risk_try - RISK_TARGET_USD)
                    cand = (e, m_target, risk_try, f"NQ={e};MNQ={m_target}")
                    if (best is None) or (score < best[0]):
                        best = (score, cand)
            continue

        # Il existe un intervalle m ∈ [m_min, m_max] qui tient la bande -> viser target
        m_target = int(np.round((RISK_TARGET_USD - risk_e) / (stop_pts * MICRO_PV))) if stop_pts*MICRO_PV > 0 else 0
        m_target = max(m_min, min(m_target, m_max))

        # Vérifie quelques voisins pour se rapprocher du target
        for m in {m_min, m_max, m_target, max(m_target-1, m_min), min(m_target+1, m_max)}:
            risk = stop_pts * (EMINI_PV * e + MICRO_PV * m)
            if RISK_MIN_USD <= risk <= RISK_MAX_USD:
                score = abs(risk - RISK_TARGET_USD)
                cand = (e, m, risk, f"NQ={e};MNQ={m}")
                if (best is None) or (score < best[0]):
                    best = (score, cand)

    if best is None:
        # Aucune combinaison parfaite dans la bande -> prendre le plus proche sous le max si possible
        return 0, 0, 0.0, "NQ=0;MNQ=0"
    _, (e, m, risk, label) = best
    return e, m, float(risk), label

# --------- Simulate one day ----------
def simulate_day(day_df: pd.DataFrame, symbol_label: str, assume: str) -> List[Trade]:
    trades: List[Trade] = []
    if day_df.empty:
        return trades

    the_date = day_df["timestamp"].dt.date.iloc[0]
    tz = "UTC"
    opr_start = pd.Timestamp.combine(the_date, pd.to_datetime(OPR_START_UTC).time()).tz_localize(tz)
    opr_end   = opr_start + pd.Timedelta(seconds=OPR_SECONDS) - pd.Timedelta(seconds=1)
    flat_time = pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)

    # keep only chosen symbol and session window
    mask_session = (day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= flat_time) & (day_df["symbol"] == symbol_label)
    s_df = day_df.loc[mask_session].reset_index(drop=True)
    if s_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            0.0, 0.0, 0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                            0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    # === OPR 30s ===
    end = opr_start + pd.Timedelta(seconds=OPR_SECONDS) - pd.Timedelta(seconds=1)
    or_mask   = (s_df["timestamp"] >= opr_start) & (s_df["timestamp"] <= end)
    post_mask =  s_df["timestamp"] > end
    or_df, post_df = s_df.loc[or_mask], s_df.loc[post_mask]

    if or_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            0.0, 0.0, 0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                            0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    post_df = post_df[post_df["timestamp"] <= flat_time].copy()
    if post_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            float(or_df["high"].max()), float(or_df["low"].min()),
                            0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                            0.0, None, None, None, None, "no_fill", 0.0, 0.0))
        return trades

    or_high = float(or_df["high"].max())
    or_low  = float(or_df["low"].min())
    or_range = or_high - or_low
    if or_range <= 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            or_high, or_low, 0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                            0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    stop_pts = or_range * SL_MULTIPLIER
    tp_pts   = (5.0 if stop_pts >= SL_TP_FIXED_5_AT else
                max(TP_MIN_POINTS, min(round((R_TARGET * stop_pts)/0.25)*0.25, TP_MAX_POINTS)))

    # === sizing mix emini/micro pour rester dans la bande de risque ===
    emini_qty, micro_qty, risk_usd, size_label = size_for_risk(stop_pts)
    if (emini_qty + micro_qty) <= 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            or_high, or_low, stop_pts, tp_pts, 0, 0, "NQ=0;MNQ=0",
                            float(risk_usd), None, None, None, None, "skip_risk_band", 0.0, 0.0))
        return trades

    buffer = ENTRY_BUFFER_TICKS * TICK_SIZE
    buy_stop  = or_high + buffer
    sell_stop = or_low  - buffer
    slip = SLIPPAGE_TICKS * TICK_SIZE

    # PnL par point effectif (mix)
    pv_mix = EMINI_PV * emini_qty + MICRO_PV * micro_qty
    comm_mix = emini_qty * COMMISSION_RT_EMINI + micro_qty * COMMISSION_RT_MICRO

    trades_done = 0
    in_position = False
    direction = None
    entry_price = None
    entry_time = None
    tp = None
    sl = None

    for _, bar in post_df.iterrows():
        if trades_done >= MAX_TRADES_PER_DAY:
            break

        if not in_position:
            touch = choose_first_touch(bar, level_high=buy_stop, level_low=sell_stop, assume=INTRABAR_SEQUENCE)
            if touch == "high":
                in_position = True; direction = "long"
                entry_price = buy_stop + slip; entry_time = bar["timestamp"]
                tp = entry_price + tp_pts; sl = entry_price - stop_pts
            elif touch == "low":
                in_position = True; direction = "short"
                entry_price = sell_stop - slip; entry_time = bar["timestamp"]
                tp = entry_price - tp_pts; sl = entry_price + stop_pts
            else:
                continue

            # Exit same bar si touch
            if direction == "long":
                exit_touch = choose_first_touch(bar, level_high=tp, level_low=sl, assume=INTRABAR_SEQUENCE)
                if exit_touch is not None:
                    if exit_touch == "high":
                        exit_price = tp + slip; result = "TP"; points = (exit_price - entry_price)
                    else:
                        exit_price = sl - slip; result = "SL"; points = (exit_price - entry_price)
                    pnl = points * pv_mix - comm_mix
                    trades.append(Trade(symbol_label, pd.Timestamp(entry_time.date()), entry_time, bar["timestamp"], direction,
                                        or_high, or_low, stop_pts, tp_pts,
                                        emini_qty, micro_qty, size_label, float(risk_usd),
                                        entry_price, tp, sl, exit_price, result, points, float(pnl)))
                    in_position = False; direction=None; trades_done += 1
            else:
                exit_touch = choose_first_touch(bar, level_high=sl, level_low=tp, assume=INTRABAR_SEQUENCE)
                if exit_touch is not None:
                    if exit_touch == "low":
                        exit_price = tp - slip; result = "TP"; points = (entry_price - exit_price)
                    else:
                        exit_price = sl + slip; result = "SL"; points = (entry_price - exit_price)
                    pnl = points * pv_mix - comm_mix
                    trades.append(Trade(symbol_label, pd.Timestamp(entry_time.date()), entry_time, bar["timestamp"], direction,
                                        or_high, or_low, stop_pts, tp_pts,
                                        emini_qty, micro_qty, size_label, float(risk_usd),
                                        entry_price, tp, sl, exit_price, result, points, float(pnl)))
                    in_position = False; direction=None; trades_done += 1
            continue

        # Manage exits (bar suivantes)
        if in_position and direction == "long":
            exit_touch = choose_first_touch(bar, level_high=tp, level_low=sl, assume=INTRABAR_SEQUENCE)
            if exit_touch is None: continue
            if exit_touch == "high":
                exit_price = tp + slip; result = "TP"; points = (exit_price - entry_price)
            else:
                exit_price = sl - slip; result = "SL"; points = (exit_price - entry_price)
            pnl = points * pv_mix - comm_mix
            trades.append(Trade(symbol_label, pd.Timestamp(entry_time.date()), entry_time, bar["timestamp"], direction,
                                or_high, or_low, stop_pts, tp_pts,
                                emini_qty, micro_qty, size_label, float(risk_usd),
                                entry_price, tp, sl, exit_price, result, points, float(pnl)))
            in_position = False; direction=None; trades_done += 1

        elif in_position and direction == "short":
            exit_touch = choose_first_touch(bar, level_high=sl, level_low=tp, assume=INTRABAR_SEQUENCE)
            if exit_touch is None: continue
            if exit_touch == "low":
                exit_price = tp - slip; result = "TP"; points = (entry_price - exit_price)
            else:
                exit_price = sl + slip; result = "SL"; points = (entry_price - exit_price)
            pnl = points * pv_mix - comm_mix
            trades.append(Trade(symbol_label, pd.Timestamp(entry_time.date()), entry_time, bar["timestamp"], direction,
                                or_high, or_low, stop_pts, tp_pts,
                                emini_qty, micro_qty, size_label, float(risk_usd),
                                entry_price, tp, sl, exit_price, result, points, float(pnl)))
            in_position = False; direction=None; trades_done += 1

    # Flat forcé si encore en position
    if in_position:
        eod_bars = post_df[post_df["timestamp"] <= flat_time]
        if not eod_bars.empty:
            last_bar = eod_bars.iloc[-1]
            exit_price = float(last_bar["close"])
            result = "EOD"
            points = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
            pnl = points * pv_mix - comm_mix
            trades.append(Trade(symbol_label, pd.Timestamp(entry_time.date()), entry_time, last_bar["timestamp"], direction,
                                or_high, or_low, stop_pts, tp_pts,
                                emini_qty, micro_qty, size_label, float(risk_usd),
                                entry_price, tp, sl, exit_price, result, points, float(pnl)))

    if len(trades) == 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            0.0, 0.0, 0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                            0.0, None, None, None, None, "no_fill", 0.0, 0.0))

    return trades

# --------- Run all days ----------
def run_backtest(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df["utc_date"] = df["timestamp"].dt.date
    all_trades: List[Trade] = []
    picks = []
    for d, day_df in df.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        has_data = bool((day_df["symbol"] == pick).any())
        picks.append({"date": d, "picked_symbol": pick, "has_data": int(has_data)})
        if not has_data:
            all_trades.append(Trade(pick, pd.Timestamp(d), None, None, None,
                                    0.0, 0.0, 0.0, 0.0, 0, 0, "NQ=0;MNQ=0",
                                    0.0, None, None, None, None, "no_data", 0.0, 0.0))
            continue
        all_trades.extend(simulate_day(day_df, pick, assume=INTRABAR_SEQUENCE))
    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date","entry_time"], na_position="last").reset_index(drop=True)
    return trades_df, picklog_df

# --------- KPIs quick ----------
def kpis(trades: pd.DataFrame) -> dict:
    real = trades[trades["result"].isin(["TP","SL","EOD"])]
    if real.empty:
        return {"trades": 0, "win_rate": np.nan, "profit_factor": np.nan,
                "avg_win_usd": np.nan, "avg_loss_usd": np.nan,
                "expectancy_usd": np.nan, "net_pnl_usd": 0.0,
                "max_dd_usd": 0.0, "days": int(trades["date"].nunique() if not trades.empty else 0)}
    wins   = real[real["result"] == "TP"]["pnl_usd"]
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

# --------- main ----------
def main():
    print("Loading data (UTC)...")
    df = load_data(CSV_PATH, SYMBOL_FILTER_REGEX)
    print(f"Rows total: {len(df):,} | Symbols sample: {sorted(df['symbol'].astype(str).unique())[:8]}")

    print(f"Backtest OPR 30 sec (Entry buffer = {ENTRY_BUFFER_TICKS} ticks, risk band with NQ/MNQ)...")
    trades, picklog = run_backtest(df)
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"Saved trades to: {OUTPUT_TRADES_CSV}")
    print(f"Saved selection log to: {OUTPUT_PICKLOG_CSV}")

    stats = kpis(trades)
    print_stats("RESULTS (front-month + OPR 30s + entry buffer + risk band NQ/MNQ)", stats)

if __name__ == "__main__":
    main()

