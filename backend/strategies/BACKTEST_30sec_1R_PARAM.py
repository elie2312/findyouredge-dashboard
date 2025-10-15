
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


# ============ CONFIG ============
CSV_PATH = str(DATA_CSV_FULL_PATH)  # Chargé depuis config.py
SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"  # NQ front month

OUTPUT_TRADES_CSV  = "opr_trades_utc_front_month_30secOPR_1R_opposite_bound.csv"
OUTPUT_PICKLOG_CSV = "front_month_selection_log_30secOPR_1R_opposite_bound.csv"

# Times (UTC)
OPR_START_UTC = "13:30:00"   # OPR start
OPR_SECONDS   = 30           # 13:30:00..13:30:29 -> entries eligible from 13:30:30
FLAT_TIME_UTC = "20:00:00"

# Instrument NQ
TICK_SIZE    = 0.25
POINT_VALUE  = 20.0          # $/pt (NQ)

# Entry / SL / TP
ENTRY_BUFFER_TICKS = 2       # breakout buffer (+0.5/-0.5 pt)
SL_AT_OPPOSITE_BOUND = True  # for clarity; stop is the opposite OPR bound
MIN_STOP_POINTS     = 15.0   # skip trades whose stop distance < 15 pts
# Risk sizing (1..7 contracts), strict cap <= MAX_RISK_USD
NQ_MIN = 1
NQ_MAX = 7
MAX_RISK_USD = 2500.0        # "risquer 2500 maximum"

# Costs / execution
SLIPPAGE_TICKS = 0
COMMISSION_RT  = 0.0
MAX_TRADES_PER_DAY = 1
INTRABAR_SEQUENCE: Literal["high_first","low_first"] = "high_first"

# Day filter
OPR_MIN_WIDTH_PTS  = 0.0     # keep all OPR sizes; rely on MIN_STOP_POINTS instead

# ============ DATA/UTILS ============
@dataclass
class Trade:
    symbol: str
    date: pd.Timestamp
    entry_time: Optional[pd.Timestamp]
    exit_time: Optional[pd.Timestamp]
    direction: Optional[str]        # "long"/"short"
    or_high: float
    or_low: float
    opr_width_pts: float
    stop_pts: float
    tp_pts: float
    qty_nq: int
    risk_usd: float
    entry: Optional[float]
    tp: Optional[float]
    sl: Optional[float]
    exit: Optional[float]
    result: str                     # "TP","SL","EOD","no_fill","skip_small_stop","no_data"
    points: float
    pnl_usd: float

def load_data(csv_path: str, symbol_regex: Optional[str]) -> pd.DataFrame:
    df = pd.read_csv(csv_path, low_memory=False)
    cols = {c.lower(): c for c in df.columns}
    req = ["ts_event","open","high","low","close","symbol"]
    for r in req:
        if r not in cols: raise ValueError(f"Missing column: {r}")
    df = df.rename(columns={
        cols["ts_event"]: "timestamp",
        cols["open"]:     "open",
        cols["high"]:     "high",
        cols["low"]:      "low",
        cols["close"]:    "close",
        cols["symbol"]:   "symbol",
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if symbol_regex:
        df = df[df["symbol"].astype(str).str.match(symbol_regex)]
    return df.sort_values(["timestamp","symbol"]).reset_index(drop=True)

MONTH_CODE = {3:"H", 6:"M", 9:"U", 12:"Z"}
def third_friday(year: int, month: int):
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [d for d in cal.itermonthdates(year, month) if d.weekday()==4 and d.month==month]
    return fridays[2]
def roll_date(year: int, month: int): return third_friday(year, month) - timedelta(days=1)
def front_month_for_day(d) -> Tuple[str,int]:
    y=d.year; ev=[(roll_date(y-1,12),"H",y)]
    for m,nxt in [(3,"M"),(6,"U"),(9,"Z"),(12,"H")]: ev.append((roll_date(y,m),nxt,y+1 if m==12 else y))
    ev.sort(key=lambda x:x[0]); last=None
    for e in ev:
        if e[0] <= d: last=e
        else: break
    letter,yy=(last[1], last[2]) if last else ("H", y)
    return (letter, yy%10)
def active_symbol_for_day(d)->str:
    letter,yy=front_month_for_day(d); return f"NQ{letter}{yy}"

def day_bounds(the_date):
    tz="UTC"
    opr_start = pd.Timestamp.combine(the_date, pd.to_datetime(OPR_START_UTC).time()).tz_localize(tz)
    opr_end   = opr_start + pd.Timedelta(seconds=OPR_SECONDS) - pd.Timedelta(seconds=1)
    flat_time = pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)
    return opr_start, opr_end, flat_time

def choose_first_touch(bar, level_high, level_low, assume: str) -> Optional[str]:
    hit_h = bar["high"] >= level_high if level_high is not None else False
    hit_l = bar["low"]  <= level_low  if level_low  is not None else False
    if hit_h and hit_l: return "high" if assume=="high_first" else "low"
    if hit_h: return "high"
    if hit_l: return "low"
    return None

def round_to_tick(x: float, tick: float=TICK_SIZE) -> float:
    return round(x/tick)*tick

def qty_for_max_risk(stop_pts: float) -> Tuple[int,float]:
    """NQ only (1..7). Risk/contract = stop_pts * POINT_VALUE. Must be <= MAX_RISK_USD."""
    rpc = float(stop_pts) * POINT_VALUE
    if not np.isfinite(rpc) or rpc <= 0: return 1, 0.0
    n = int(np.floor(MAX_RISK_USD / rpc))
    n = max(NQ_MIN, min(NQ_MAX, n))
    risk = n * rpc
    # If even 1 contract exceeds the cap, force 1 but mark risk (user can decide policy)
    if n < 1:
        n, risk = 1, rpc
    return n, risk

# ============ CORE ============
def simulate_day(day_df: pd.DataFrame, symbol_label: str) -> List[Trade]:
    trades: List[Trade] = []
    if day_df.empty: return trades
    the_date = day_df["timestamp"].dt.date.iloc[0]
    opr_start, opr_end, flat_time = day_bounds(the_date)

    # session window & symbol
    s = day_df[(day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= flat_time) & (day_df["symbol"] == symbol_label)]
    if s.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None,None,None,0,0,0,0,0,0,0,None,None,None,None,"no_data",0,0))
        return trades

    # OPR 30s
    or_mask   = (s["timestamp"] >= opr_start) & (s["timestamp"] <= opr_end)
    post_mask =  s["timestamp"] >  opr_end
    or_df, post_df = s.loc[or_mask], s.loc[post_mask]
    if or_df.empty or post_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None,None,None,0,0,0,0,0,0,0,None,None,None,None,"no_data",0,0))
        return trades

    or_high = float(or_df["high"].max())
    or_low  = float(or_df["low"].min())
    opr_w   = or_high - or_low

    # Keep day regardless of width, but we'll enforce min stop distance after computing entry.
    buf = ENTRY_BUFFER_TICKS * TICK_SIZE
    buy_stop  = or_high + buf
    sell_stop = or_low  - buf
    slip = SLIPPAGE_TICKS * TICK_SIZE

    trades_done=0; in_pos=False; side=None; entry=None; entry_t=None; tp=None; sl=None; stop_pts=None; tp_pts=None; qty=None; risk_usd=None

    for _, bar in post_df.iterrows():
        if trades_done >= MAX_TRADES_PER_DAY: break

        if not in_pos:
            touch = choose_first_touch(bar, buy_stop, sell_stop, INTRABAR_SEQUENCE)
            if touch == "high":
                # Long entry
                entry = buy_stop + slip
                sl    = or_low if SL_AT_OPPOSITE_BOUND else entry - opr_w
                stop_pts = entry - sl
                if stop_pts < MIN_STOP_POINTS:
                    trades.append(Trade(symbol_label, pd.Timestamp(the_date), None,None,"long",
                                        or_high, or_low, opr_w, float(stop_pts), 0.0, 0, 0.0,
                                        entry, None, sl, None, "skip_small_stop", 0.0, 0.0))
                    trades_done += 1  # counts as the day's decision
                    continue
                tp    = entry + stop_pts  # 1R
                tp_pts = stop_pts
                qty, risk_usd = qty_for_max_risk(stop_pts)
                in_pos=True; side="long"; entry_t=bar["timestamp"]

            elif touch == "low":
                # Short entry
                entry = sell_stop - slip
                sl    = or_high if SL_AT_OPPOSITE_BOUND else entry + opr_w
                stop_pts = sl - entry
                if stop_pts < MIN_STOP_POINTS:
                    trades.append(Trade(symbol_label, pd.Timestamp(the_date), None,None,"short",
                                        or_high, or_low, opr_w, float(stop_pts), 0.0, 0, 0.0,
                                        entry, None, sl, None, "skip_small_stop", 0.0, 0.0))
                    trades_done += 1
                    continue
                tp    = entry - stop_pts  # 1R
                tp_pts = stop_pts
                qty, risk_usd = qty_for_max_risk(stop_pts)
                in_pos=True; side="short"; entry_t=bar["timestamp"]
            else:
                continue

            # same-bar exit check
            if side=="long":
                ex_touch = choose_first_touch(bar, tp, sl, INTRABAR_SEQUENCE)
                if ex_touch is not None:
                    if ex_touch=="high":
                        exit_px=tp+slip; res="TP"; pts=exit_px-entry
                    else:
                        exit_px=sl-slip; res="SL"; pts=exit_px-entry
                    pnl = pts * POINT_VALUE * qty - COMMISSION_RT * qty
                    trades.append(Trade(symbol_label, pd.Timestamp(entry_t.date()), entry_t, bar["timestamp"], side,
                                        or_high, or_low, opr_w, float(stop_pts), float(tp_pts), int(qty), float(risk_usd),
                                        float(entry), float(tp), float(sl), float(exit_px), res, float(pts), float(pnl)))
                    in_pos=False; side=None; trades_done+=1
            else:
                ex_touch = choose_first_touch(bar, sl, tp, INTRABAR_SEQUENCE)
                if ex_touch is not None:
                    if ex_touch=="low":
                        exit_px=tp-slip; res="TP"; pts=entry-exit_px
                    else:
                        exit_px=sl+slip; res="SL"; pts=entry-exit_px
                    pnl = pts * POINT_VALUE * qty - COMMISSION_RT * qty
                    trades.append(Trade(symbol_label, pd.Timestamp(entry_t.date()), entry_t, bar["timestamp"], side,
                                        or_high, or_low, opr_w, float(stop_pts), float(tp_pts), int(qty), float(risk_usd),
                                        float(entry), float(tp), float(sl), float(exit_px), res, float(pts), float(pnl)))
                    in_pos=False; side=None; trades_done+=1
            continue

        # exits on subsequent bars
        if in_pos and side=="long":
            ex_touch = choose_first_touch(bar, tp, sl, INTRABAR_SEQUENCE)
            if ex_touch is None: continue
            if ex_touch=="high":
                exit_px=tp+slip; res="TP"; pts=exit_px-entry
            else:
                exit_px=sl-slip; res="SL"; pts=exit_px-entry
            pnl = pts * POINT_VALUE * qty - COMMISSION_RT * qty
            trades.append(Trade(symbol_label, pd.Timestamp(entry_t.date()), entry_t, bar["timestamp"], side,
                                or_high, or_low, opr_w, float(stop_pts), float(tp_pts), int(qty), float(risk_usd),
                                float(entry), float(tp), float(sl), float(exit_px), res, float(pts), float(pnl)))
            in_pos=False; side=None; trades_done+=1

        elif in_pos and side=="short":
            ex_touch = choose_first_touch(bar, sl, tp, INTRABAR_SEQUENCE)
            if ex_touch is None: continue
            if ex_touch=="low":
                exit_px=tp-slip; res="TP"; pts=entry-exit_px
            else:
                exit_px=sl+slip; res="SL"; pts=entry-exit_px
            pnl = pts * POINT_VALUE * qty - COMMISSION_RT * qty
            trades.append(Trade(symbol_label, pd.Timestamp(entry_t.date()), entry_t, bar["timestamp"], side,
                                or_high, or_low, opr_w, float(stop_pts), float(tp_pts), int(qty), float(risk_usd),
                                float(entry), float(tp), float(sl), float(exit_px), res, float(pts), float(pnl)))
            in_pos=False; side=None; trades_done+=1

    # flat at session end
    if in_pos:
        last = post_df[post_df["timestamp"] <= flat_time].iloc[-1]
        exit_px = float(last["close"])
        res="EOD"; pts = (exit_px-entry) if side=="long" else (entry-exit_px)
        pnl = pts * POINT_VALUE * qty - COMMISSION_RT * qty
        trades.append(Trade(symbol_label, pd.Timestamp(entry_t.date()), entry_t, last["timestamp"], side,
                            or_high, or_low, opr_w, float(stop_pts), float(tp_pts), int(qty), float(risk_usd),
                            float(entry), float(tp), float(sl), float(exit_px), res, float(pts), float(pnl)))

    if not trades:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None,None,None,0,0,0,0,0,0,0,None,None,None,None,"no_fill",0,0))
    return trades

def run_backtest(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df["utc_date"] = df["timestamp"].dt.date
    all_trades: List[Trade] = []
    picks=[]
    for d, day_df in df.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        picks.append({"date": d, "picked_symbol": pick, "has_data": int((day_df["symbol"]==pick).any())})
        if not (day_df["symbol"]==pick).any():
            all_trades.append(Trade(pick, pd.Timestamp(d), None,None,None,0,0,0,0,0,0,0,None,None,None,None,"no_data",0,0))
            continue
        all_trades.extend(simulate_day(day_df, pick))
    trades_df = pd.DataFrame([asdict(t) for t in all_trades])
    picklog_df = pd.DataFrame(picks)
    if not trades_df.empty:
        trades_df = trades_df.sort_values(["date","entry_time"], na_position="last").reset_index(drop=True)
    return trades_df, picklog_df

def kpis(trades: pd.DataFrame) -> dict:
    real = trades[trades["result"].isin(["TP","SL","EOD"])]
    if real.empty: return {"trades":0,"win_rate":np.nan,"profit_factor":np.nan,
                           "avg_win_usd":np.nan,"avg_loss_usd":np.nan,
                           "expectancy_usd":np.nan,"net_pnl_usd":0.0,
                           "max_dd_usd":0.0,"days": int(trades["date"].nunique() if not trades.empty else 0)}
    wins   = real[real["result"]=="TP"]["pnl_usd"]
    losses = real[real["result"]!="TP"]["pnl_usd"]
    net = real["pnl_usd"].sum()
    wr  = len(wins)/len(real)
    gp, gl = wins.sum(), -losses.sum()
    pf = (gp/gl) if gl>0 else np.inf
    exp = net/len(real)
    eq = real["pnl_usd"].cumsum(); dd = (eq - eq.cummax()).min()
    return {"trades":int(len(real)),"win_rate":float(wr),"profit_factor":float(pf),
            "avg_win_usd":float(wins.mean() if len(wins)>0 else 0.0),
            "avg_loss_usd":float(losses.mean() if len(losses)>0 else 0.0),
            "expectancy_usd":float(exp),"net_pnl_usd":float(net),
            "max_dd_usd":float(dd),"days": int(trades["date"].nunique())}

def print_stats(title:str, s:dict):
    print(f"\n=== {title} ===")
    for k,v in s.items():
        if isinstance(v,float):
            if "rate" in k: print(f"{k:>16}: {v:.2%}")
            elif "factor" in k: print(f"{k:>16}: {'inf' if np.isinf(v) else f'{v:.2f}'}")
            else: print(f"{k:>16}: {v:,.2f}")
        else:
            print(f"{k:>16}: {v}")

def main():
    print("Loading data (UTC)...")
    df = load_data(CSV_PATH, SYMBOL_FILTER_REGEX)
    print(f"Rows: {len(df):,} | Symbols sample: {sorted(df['symbol'].astype(str).unique())[:8]}")

    print("Backtest OPR 30s -> 1R (SL at opposite bound, TP=1R, min stop 15 pts, cap risk <= $2,500)")
    trades, picklog = run_backtest(df)
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"Saved trades -> {OUTPUT_TRADES_CSV}")
    print(f"Saved picks  -> {OUTPUT_PICKLOG_CSV}")

    stats = kpis(trades); print_stats("RESULTS", stats)

if __name__ == "__main__":
    main()

