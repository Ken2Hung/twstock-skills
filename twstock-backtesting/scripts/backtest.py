"""twstock-backtesting：台股 long-only 歷史回測引擎。

資料一律經 twstock-module 取得（不直接碰 FinMind／yfinance）。純 pandas，
忠實套用台股交易成本，無 look-ahead bias（position = signal.shift(1)）。

用法：
    python -X utf8 backtest.py --stock-id 2330 --start 2022-01-01 --end 2024-12-31
    python -X utf8 backtest.py --selftest      # 離線自我檢查（不碰 API）
"""
import argparse
import json
import os
import sys

import pandas as pd

# 台股交易成本（真相來源：twstock-screening-stocks/references/tw-market-rules.md，
# 此處為對應之具名常數，勿於他處另編魔術數字）
FEE_RATE = 0.001425   # 手續費 0.1425%（買、賣皆收）
TAX_RATE = 0.003      # 證交稅 0.3%（僅賣出）
FEE_MIN = 20.0        # 手續費單筆低消 20 元
CAPITAL = 1_000_000.0
TRADING_DAYS = 252    # 年化基準（台股約 240–250，取 252 常規值）


def _load_daily(stock_id, start, end):
    """經 twstock-module 取歷史日K。回 (df, data_gaps)；不足回 (None, gaps)。"""
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "..", "twstock-module", "scripts"))
    from finmind_fetcher import FinmindFetcher

    out = FinmindFetcher().fetch(stock_id, "daily", start, end)
    gaps = list(out.get("data_gaps", []))
    data = out.get("data")
    if not isinstance(data, list) or not data:
        gaps.append("daily: 無資料，無法回測")
        return None, gaps
    df = pd.DataFrame(data)[["date", "close"]].copy()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df[df["close"] > 0].sort_values("date").reset_index(drop=True)  # 濾 NaN/0/負，杜絕除零
    if len(df) < 60:
        gaps.append("daily: 有效日K不足 60 筆，無法回測（60MA 需暖身）")
        return None, gaps
    return df, gaps


def signal_ma_bull(df):
    """參考訊號（可插拔）：均線多頭 5MA>20MA>60MA → 在場。
    僅用 rolling 過去窗（截至當日收盤），無未來資訊。"""
    c = df["close"]
    ma5, ma20, ma60 = c.rolling(5).mean(), c.rolling(20).mean(), c.rolling(60).mean()
    return (ma5 > ma20) & (ma20 > ma60)


def _simulate(close, hold, capital=CAPITAL):
    """核心模擬（純函式、離線可測）。
    close: list[float]；hold: list[bool]，hold[t]=該日是否持倉（已 shift，無 look-ahead）。
    成本於部位變動日套用一次。回 metrics dict。"""
    n = len(close)
    assert len(hold) == n, f"close/hold 長度不符：{n} vs {len(hold)}"
    assert n == 0 or not hold[0], "hold[0] 必須為 False（部位由 signal.shift(1) 決定）"
    eq_net = eq_gross = peak = capital
    mdd = 0.0
    trades = []            # 每筆平倉之淨損益
    entry_eq = None
    for t in range(1, n):
        if hold[t] and not hold[t - 1]:               # 買進日：先扣手續費（成本基準＝進場額）
            eq_net -= max(eq_net * FEE_RATE, FEE_MIN)
            entry_eq = eq_net
        if hold[t]:                                   # 持倉日：close-to-close 計酬
            r = close[t] / close[t - 1] - 1.0
            eq_net *= (1.0 + r)
            eq_gross *= (1.0 + r)
        if hold[t - 1] and not hold[t]:               # 賣出日：扣手續費 + 證交稅（皆按成交額）
            eq_net -= max(eq_net * FEE_RATE, FEE_MIN) + eq_net * TAX_RATE
            if entry_eq is not None:
                trades.append(eq_net - entry_eq)
                entry_eq = None
        peak = max(peak, eq_net)
        mdd = min(mdd, eq_net / peak - 1.0)
    if hold[n - 1] and entry_eq is not None:          # 期末仍持倉 → 概念平倉
        eq_net -= max(eq_net * FEE_RATE, FEE_MIN) + eq_net * TAX_RATE
        trades.append(eq_net - entry_eq)
        peak = max(peak, eq_net)
        mdd = min(mdd, eq_net / peak - 1.0)

    total_net = eq_net / capital - 1.0
    total_gross = eq_gross / capital - 1.0
    wins = sum(1 for p in trades if p > 0)
    return {
        "total_return_net": round(total_net, 4),
        "total_return_gross": round(total_gross, 4),
        "cost_drag": round(total_gross - total_net, 4),
        "annualized_return_net": round((1.0 + total_net) ** (TRADING_DAYS / n) - 1.0, 4) if n else 0.0,
        "max_drawdown": round(mdd, 4),
        "win_rate": round(wins / len(trades), 4) if trades else 0.0,
        "n_trades": len(trades),
        "bars": n,
    }


def run_backtest(stock_id, start, end, signal_fn=signal_ma_bull, capital=CAPITAL):
    df, gaps = _load_daily(stock_id, start, end)
    if df is None:
        return {"stock_id": stock_id, "start": start, "end": end,
                "tradable": False, "data_gaps": gaps, "metrics": None}
    sig = signal_fn(df).fillna(False)
    hold = sig.shift(1).fillna(False).astype(bool).tolist()      # 防 look-ahead
    m = _simulate(df["close"].astype(float).tolist(), hold, capital)
    return {"stock_id": stock_id, "start": start, "end": end,
            "signal": signal_fn.__name__, "tradable": True,
            "data_gaps": gaps, "metrics": m}


def _selftest():
    # 1) 成本方向：淨 < 毛（有交易時），且成本侵蝕 > 0
    close = [100, 101, 102, 103, 104, 103]
    hold = [False, True, True, True, True, False]
    m = _simulate(close, hold)
    assert m["total_return_gross"] > m["total_return_net"], m
    assert m["cost_drag"] > 0 and m["n_trades"] == 1, m
    # 2) 空手 → 零報酬、零交易
    m0 = _simulate(close, [False] * len(close))
    assert m0["total_return_net"] == 0.0 and m0["n_trades"] == 0, m0
    # 3) 無 look-ahead：改「最後一日訊號」不得影響先前部位（shift(1) 保證）
    s = pd.Series([False, False, True, True, False, True])
    h1 = s.shift(1).fillna(False).tolist()
    s2 = s.copy(); s2.iloc[-1] = not s2.iloc[-1]
    h2 = s2.shift(1).fillna(False).tolist()
    assert h1[:-1] == h2[:-1], "未來訊號影響了先前部位（look-ahead）"
    # 4) 指標形狀 + MDD ≤ 0
    for k in ("total_return_net", "annualized_return_net", "max_drawdown", "win_rate", "n_trades", "bars"):
        assert k in m
    assert m["max_drawdown"] <= 0.0
    # 5) 契約防呆：close/hold 長度不符 MUST 擋下
    ok = False
    try:
        _simulate([1.0, 2.0], [False])
    except AssertionError:
        ok = True
    assert ok, "未擋下 close/hold 長度不符"
    print("selftest OK")


def main():
    p = argparse.ArgumentParser(description="twstock 台股 long-only 回測引擎")
    p.add_argument("--stock-id")
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default="2024-12-31")
    p.add_argument("--selftest", action="store_true", help="離線自我檢查，不碰 API")
    args = p.parse_args()
    if args.selftest:
        _selftest()
        return
    if not args.stock_id:
        p.error("--stock-id 為必填（或用 --selftest）")
    print(json.dumps(run_backtest(args.stock_id, args.start, args.end), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
