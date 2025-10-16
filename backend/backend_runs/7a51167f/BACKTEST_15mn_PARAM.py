
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BACKTEST 5F — OPR 15MN — NQ front-month (CME roll) — 1 trade / jour
Variante: **ENTRY_BUFFER_TICKS = 2**  → entrée à ORH + 1 tick / ORL − 1 tick.
(UTC, sans attente de close M1, tout le reste identique à ta base 5F)
"""

import calendar
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Optional, Literal, Tuple
from datetime import date, datetime, timedelta

# ==========================
# ======== CONFIG =========
# ==========================

CSV_PATH = r"C:/Users/elieb/Desktop/Dashboard/backend_runs/7a51167f/filtered_data.csv"  # ← adapte à ton chemin
SYMBOL_FILTER_REGEX = r"^NQ[HMUZ][0-9]$"

OUTPUT_TRADES_CSV = "opr_trades_utc_front_month_entry_buffer.csv"
OUTPUT_PICKLOG_CSV = "front_month_selection_log.csv"

# Time settings (all UTC)
OPR_START_UTC = "13:30:00"
OPR_MINUTES   = 15                      # 13:30:00 -> 13:44:59
FLAT_TIME_UTC = "20:00:00"

# Instrument settings (NQ)
TICK_SIZE     = 0.25
POINT_VALUE   = 20.0                    # $/pt
SL_MULTIPLIER = 0.5                     # SL = OPR * 0.5

# Entry buffer (nouveau paramètre)
ENTRY_BUFFER_TICKS = 2                  # <<< entrée = ORH + 1 tick / ORL - 1 tick

# --- TP proportional rules ---
R_TARGET         = 0.12                 # keeps ~5/40 ratio for small SLs
TP_MIN_POINTS    = 2.5
TP_MAX_POINTS    = 5.0
SL_TP_FIXED_5_AT = 40.0                 # if SL >= this, TP = 5.0

# --- Skip & sizing ---
SL_SKIP_LT       = 15.0                 # skip when SL < 15
SL_TWO_CONTRACTS_MAX = 40.0             # threshold for sizing tiers

# === doubled size + risk cap ===
SIZE_MULTIPLIER = 2                     # double previous sizes (2->4, 1->2)
RISK_CAP_USD    = 3000.0                # skip trade if potential loss exceeds this

# Costs
SLIPPAGE_TICKS = 0
COMMISSION_RT  = 0.0

# Constraints
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
    direction: Optional[str]                # "long" or "short"
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
    result: str                             # "TP","SL","EOD","no_fill","skip_sl","skip_risk_cap","no_data"
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
MONTH_CODE = {3:"H", 6:"M", 9:"U", 12:"Z"}
CODE_MONTH = {"H":3, "M":6, "U":9, "Z":12}

def third_friday(year: int, month: int) -> date:
    c = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [d for d in c.itermonthdates(year, month) if d.weekday() == calendar.FRIDAY and d.month == month]
    return fridays[2]  # third Friday

def roll_date(year: int, month: int) -> date:
    """CME roll date = Thursday prior to 3rd Friday of (H/M/U/Z) month."""
    tf = third_friday(year, month)
    return tf - timedelta(days=1)  # Thursday before

def front_month_for_day(d: date) -> Tuple[str, int]:
    """Return (month_code_letter, year_yy) for the front-month on date d per CME roll rule."""
    y = d.year
    # Build roll events from Dec of previous year through Dec of current year
    events = []
    # previous Dec -> front becomes H of current year
    rd_prev_dec = roll_date(y-1, 12)
    events.append((rd_prev_dec, "H", y))  # from this day inclusive -> H of year y

    for m, nxt in [(3,"M"), (6,"U"), (9,"Z"), (12,"H")]:
        rd = roll_date(y, m)
        ny = y+1 if m == 12 else y
        events.append((rd, nxt, ny))

    # sort by roll date
    events.sort(key=lambda x: x[0])
    # find the last event <= d
    last = None
    for ev in events:
        if ev[0] <= d:
            last = ev
        else:
            break
    if last is None:
        # before previous Dec roll: still front is H of current year
        return ("H", y)
    letter, yy = last[1], last[2]
    # convert to 1-digit year code (e.g., 2025 -> '5')
    yy_digit = yy % 10
    return (letter, yy_digit)

def active_symbol_for_day(d: date) -> str:
    letter, yy_digit = front_month_for_day(d)
    return f"NQ{letter}{yy_digit}"

def day_bounds(the_date) -> Tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    tz = "UTC"
    opr_start = pd.Timestamp.combine(the_date, pd.to_datetime(OPR_START_UTC).time()).tz_localize(tz)
    opr_end   = opr_start + pd.Timedelta(minutes=OPR_MINUTES) - pd.Timedelta(seconds=1)  # inclusive end :44:59
    flat_time = pd.Timestamp.combine(the_date, pd.to_datetime(FLAT_TIME_UTC).time()).tz_localize(tz)
    return opr_start, opr_end, flat_time

def compute_or_window(day_df: pd.DataFrame, opr_start: pd.Timestamp, minutes: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
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

def tp_points_from_stop(stop_pts: float) -> float:
    if stop_pts >= SL_TP_FIXED_5_AT:
        return 5.0
    raw = R_TARGET * stop_pts
    tp = round_to_tick(raw, 0.25)
    tp = max(TP_MIN_POINTS, min(tp, TP_MAX_POINTS))
    return tp

def base_contracts_from_stop(stop_pts: float) -> int:
    if stop_pts < SL_SKIP_LT:
        return 0
    return 2 if stop_pts < SL_TWO_CONTRACTS_MAX else 1

def doubled_contracts(stop_pts: float) -> int:
    base = base_contracts_from_stop(stop_pts)
    return base * SIZE_MULTIPLIER

def simulate_day(day_df: pd.DataFrame, symbol_label: str, assume: str) -> List[Trade]:
    trades: List[Trade] = []
    if day_df.empty:
        return trades

    the_date = day_df["timestamp"].dt.date.iloc[0]
    opr_start, opr_end, flat_time = day_bounds(the_date)

    # keep only chosen symbol and session window
    mask_session = (day_df["timestamp"] >= opr_start) & (day_df["timestamp"] <= flat_time) & (day_df["symbol"] == symbol_label)
    s_df = day_df.loc[mask_session].reset_index(drop=True)
    if s_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    or_df, post_df = compute_or_window(s_df, opr_start, OPR_MINUTES)
    if or_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            0.0, 0.0, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    post_df = post_df[post_df["timestamp"] <= flat_time].copy()
    if post_df.empty:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            float(or_df["high"].max()), float(or_df["low"].min()),
                            0.0, 0.0, 0, 0.0, None, None, None, None, "no_fill", 0.0, 0.0))
        return trades

    or_high = float(or_df["high"].max())
    or_low  = float(or_df["low"].min())
    or_range = or_high - or_low
    if or_range <= 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            or_high, or_low, 0.0, 0.0, 0, 0.0, None, None, None, None, "no_data", 0.0, 0.0))
        return trades

    stop_pts = or_range * SL_MULTIPLIER

    # Skip small SL first
    contracts_for_day = doubled_contracts(stop_pts)
    if contracts_for_day == 0:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            or_high, or_low, stop_pts, 0.0, 0, 0.0, None, None, None, None, "skip_sl", 0.0, 0.0))
        return trades

    # Risk cap check
    risk_usd = stop_pts * POINT_VALUE * contracts_for_day
    if risk_usd > RISK_CAP_USD:
        trades.append(Trade(symbol_label, pd.Timestamp(the_date), None, None, None,
                            or_high, or_low, stop_pts, 0.0, 0, float(risk_usd), None, None, None, None, "skip_risk_cap", 0.0, 0.0))
        return trades

    # === ENTRY BUFFER APPLIQUÉ ICI ===
    buffer = ENTRY_BUFFER_TICKS * TICK_SIZE
    buy_stop = or_high + buffer
    sell_stop = or_low  - buffer
    slip = SLIPPAGE_TICKS * TICK_SIZE

    # TP dynamic
    tp_pts = tp_points_from_stop(stop_pts)

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
            touch = choose_first_touch(bar, level_high=buy_stop, level_low=sell_stop, assume=assume)
            if touch == "high":
                in_position = True
                direction = "long"
                entry_price = buy_stop + slip
                entry_time = bar["timestamp"]
                tp = entry_price + tp_pts
                sl = entry_price - stop_pts
            elif touch == "low":
                in_position = True
                direction = "short"
                entry_price = sell_stop - slip
                entry_time = bar["timestamp"]
                tp = entry_price - tp_pts
                sl = entry_price + stop_pts
            else:
                continue

            # Immediate same-bar exit check
            if direction == "long":
                exit_touch = choose_first_touch(bar, level_high=tp, level_low=sl, assume=assume)
                if exit_touch is not None:
                    if exit_touch == "high":
                        exit_price = tp + slip; result = "TP"; points = (exit_price - entry_price)
                    else:
                        exit_price = sl - slip; result = "SL"; points = (exit_price - entry_price)
                    pnl = points * POINT_VALUE * contracts_for_day - COMMISSION_RT * contracts_for_day
                    trades.append(Trade(
                        symbol=symbol_label, date=pd.Timestamp(entry_time.date()),
                        entry_time=entry_time, exit_time=bar["timestamp"], direction=direction,
                        or_high=or_high, or_low=or_low, stop_pts=stop_pts, tp_pts=tp_pts, contracts=contracts_for_day,
                        risk_usd=float(risk_usd),
                        entry=entry_price, tp=tp, sl=sl, exit=exit_price, result=result, points=points, pnl_usd=pnl
                    ))
                    in_position = False; direction=None; trades_done += 1
            else:
                exit_touch = choose_first_touch(bar, level_high=sl, level_low=tp, assume=assume)
                if exit_touch is not None:
                    if exit_touch == "low":
                        exit_price = tp - slip; result = "TP"; points = (entry_price - exit_price)
                    else:
                        exit_price = sl + slip; result = "SL"; points = (entry_price - exit_price)
                    pnl = points * POINT_VALUE * contracts_for_day - COMMISSION_RT * contracts_for_day
                    trades.append(Trade(
                        symbol=symbol_label, date=pd.Timestamp(entry_time.date()),
                        entry_time=entry_time, exit_time=bar["timestamp"], direction=direction,
                        or_high=or_high, or_low=or_low, stop_pts=stop_pts, tp_pts=tp_pts, contracts=contracts_for_day,
                        risk_usd=float(risk_usd),
                        entry=entry_price, tp=tp, sl=sl, exit=exit_price, result=result, points=points, pnl_usd=pnl
                    ))
                    in_position = False; direction=None; trades_done += 1
            continue

        # Manage exits on subsequent bars
        if in_position and direction == "long":
            exit_touch = choose_first_touch(bar, level_high=tp, level_low=sl, assume=assume)
            if exit_touch is None:
                continue
            if exit_touch == "high":
                exit_price = tp + slip; result = "TP"; points = (exit_price - entry_price)
            else:
                exit_price = sl - slip; result = "SL"; points = (exit_price - entry_price)
            pnl = points * POINT_VALUE * contracts_for_day - COMMISSION_RT * contracts_for_day
            trades.append(Trade(
                symbol=symbol_label, date=pd.Timestamp(entry_time.date()),
                entry_time=entry_time, exit_time=bar["timestamp"], direction=direction,
                or_high=or_high, or_low=or_low, stop_pts=stop_pts, tp_pts=tp_pts, contracts=contracts_for_day,
                risk_usd=float(risk_usd),
                entry=entry_price, tp=tp, sl=sl, exit=exit_price, result=result, points=points, pnl_usd=pnl
            ))
            in_position = False; direction=None; trades_done += 1

        elif in_position and direction == "short":
            exit_touch = choose_first_touch(bar, level_high=sl, level_low=tp, assume=assume)
            if exit_touch is None:
                continue
            if exit_touch == "low":
                exit_price = tp - slip; result = "TP"; points = (entry_price - exit_price)
            else:
                exit_price = sl + slip; result = "SL"; points = (entry_price - exit_price)
            pnl = points * POINT_VALUE * contracts_for_day - COMMISSION_RT * contracts_for_day
            trades.append(Trade(
                symbol=symbol_label, date=pd.Timestamp(entry_time.date()),
                entry_time=entry_time, exit_time=bar["timestamp"], direction=direction,
                or_high=or_high, or_low=or_low, stop_pts=stop_pts, tp_pts=tp_pts, contracts=contracts_for_day,
                risk_usd=float(risk_usd),
                entry=entry_price, tp=tp, sl=sl, exit=exit_price, result=result, points=points, pnl_usd=pnl
            ))
            in_position = False; direction=None; trades_done += 1

    # Flat forcé si encore en position
    if in_position:
        eod_bars = post_df[post_df["timestamp"] <= flat_time]
        if not eod_bars.empty:
            last_bar = eod_bars.iloc[-1]
            exit_price = float(last_bar["close"])
            result = "EOD"
            points = (exit_price - entry_price) if direction == "long" else (entry_price - exit_price)
            pnl = points * POINT_VALUE * contracts_for_day - COMMISSION_RT * contracts_for_day
            trades.append(Trade(
                symbol=symbol_label, date=pd.Timestamp(entry_time.date()),
                entry_time=entry_time, exit_time=last_bar["timestamp"], direction=direction,
                or_high=or_high, or_low=or_low, stop_pts=stop_pts, tp_pts=tp_pts, contracts=contracts_for_day,
                risk_usd=float(risk_usd),
                entry=entry_price, tp=tp, sl=sl, exit=exit_price, result=result, points=points, pnl_usd=pnl
            ))

    if len(trades) == 0:
        trades.append(Trade(
            symbol=symbol_label, date=pd.Timestamp(the_date),
            entry_time=None, exit_time=None, direction=None,
            or_high=0.0, or_low=0.0, stop_pts=0.0, tp_pts=0.0,
            contracts=0, risk_usd=0.0,
            entry=None, tp=None, sl=None, exit=None,
            result="no_fill", points=0.0, pnl_usd=0.0
        ))

    return trades

def run_backtest(df: pd.DataFrame, assume: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Split by UTC date; pick the **CME front-month** symbol for each day
    df["utc_date"] = df["timestamp"].dt.date
    all_trades: List[Trade] = []
    picks = []  # selection log
    for d, day_df in df.groupby("utc_date", sort=True):
        pick = active_symbol_for_day(d)
        mask_sym = day_df["symbol"] == pick
        has_data = bool(mask_sym.any())
        picks.append({"date": d, "picked_symbol": pick, "has_data": int(has_data)})
        if not has_data:
            t = Trade(pick, pd.Timestamp(d), None, None, None, 0.0, 0.0, 0.0, 0.0, 0, 0.0,
                      None, None, None, None, "no_data", 0.0, 0.0)
            all_trades.append(t)
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
    print(f"Rows total: {len(df):,} | Symbols available: {sorted(df['symbol'].astype(str).unique())[:8]} ...")

    print(f"Backtest with ENTRY_BUFFER_TICKS = {ENTRY_BUFFER_TICKS} ...")
    trades, picklog = run_backtest(df, assume=INTRABAR_SEQUENCE)
    trades.to_csv(OUTPUT_TRADES_CSV, index=False)
    picklog.to_csv(OUTPUT_PICKLOG_CSV, index=False)
    print(f"Saved trades to: {OUTPUT_TRADES_CSV}")
    print(f"Saved selection log to: {OUTPUT_PICKLOG_CSV}")

    stats = kpis(trades)
    print_stats("RESULTS (front-month + entry buffer)", stats)

    alt = "low_first" if INTRABAR_SEQUENCE == "high_first" else "high_first"
    trades_alt, _ = run_backtest(df, assume=alt)
    stats_alt = kpis(trades_alt)
    print_stats(f"ALT ({alt})", stats_alt)

if __name__ == "__main__":
    main()

