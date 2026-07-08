"""twstock-backtesting：台股 long-only 歷史回測引擎（單檔 + 多檔等權投組）。

資料一律經 twstock-module 取得（不直接碰 FinMind／yfinance）。純 pandas，
忠實套用台股交易成本，無 look-ahead bias（position = signal.shift(1)）。

用法：
    python -X utf8 backtest.py --stock-id 2330 --start 2022-01-01 --end 2024-12-31
    python -X utf8 backtest.py --stock-id 2330,2454,2317 ...   # 逗號多檔 → 等權投組
    python -X utf8 backtest.py --selftest                       # 離線自我檢查（不碰 API）
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


def _hold_from_signal(df, signal_fn):
    """訊號 → 持倉序列：position = signal.shift(1)（無 look-ahead）。"""
    return signal_fn(df).fillna(False).shift(1).fillna(False).astype(bool).tolist()


def _equity_curves(close, hold, capital=CAPITAL):
    """逐日模擬（純函式、離線可測）。回 (net_list, gross_list, trades)，
    list 長度 == len(close)。成本於部位變動日套用一次。"""
    n = len(close)
    assert len(hold) == n, f"close/hold 長度不符：{n} vs {len(hold)}"
    assert n == 0 or not hold[0], "hold[0] 必須為 False（部位由 signal.shift(1) 決定）"
    eq_net = eq_gross = capital
    entry_eq = None
    net = [capital]
    gross = [capital]
    trades = []
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
        net.append(eq_net)
        gross.append(eq_gross)
    if n and hold[n - 1] and entry_eq is not None:    # 期末仍持倉 → 概念平倉（賣出成本套最後一日）
        eq_net -= max(eq_net * FEE_RATE, FEE_MIN) + eq_net * TAX_RATE
        trades.append(eq_net - entry_eq)
        net[-1] = eq_net
    return net, gross, trades


def _mdd(curve):
    peak = curve[0]
    mdd = 0.0
    for e in curve:
        peak = max(peak, e)
        mdd = min(mdd, e / peak - 1.0)
    return mdd


def _metrics(net, gross, trades, extra=None):
    bars = len(net)
    total_net = net[-1] / net[0] - 1.0
    total_gross = gross[-1] / gross[0] - 1.0
    wins = sum(1 for p in trades if p > 0)
    m = {
        "total_return_net": round(total_net, 4),
        "total_return_gross": round(total_gross, 4),
        "cost_drag": round(total_gross - total_net, 4),
        "annualized_return_net": round((1.0 + total_net) ** (TRADING_DAYS / bars) - 1.0, 4) if bars else 0.0,
        "max_drawdown": round(_mdd(net), 4),
        "win_rate": round(wins / len(trades), 4) if trades else 0.0,
        "n_trades": len(trades),
        "bars": bars,
    }
    if extra:
        m.update(extra)
    return m


def _align_sum(series_list, sleeve_capital):
    """按 union 日期對齊、ffill；某檔首日前的 NaN 以 sleeve 初始資本填（＝現金，無報酬）。
    逐日加總為投組權益曲線。"""
    idx = series_list[0].index
    for s in series_list[1:]:
        idx = idx.union(s.index)
    idx = idx.sort_values()
    total = None
    for s in series_list:
        aligned = s.reindex(idx).ffill().fillna(sleeve_capital)
        total = aligned if total is None else total + aligned
    return total


def run_backtest(stock_id, start, end, signal_fn=signal_ma_bull, capital=CAPITAL):
    df, gaps = _load_daily(stock_id, start, end)
    if df is None:
        return {"stock_id": stock_id, "start": start, "end": end,
                "tradable": False, "data_gaps": gaps, "metrics": None}
    hold = _hold_from_signal(df, signal_fn)
    net, gross, trades = _equity_curves(df["close"].astype(float).tolist(), hold, capital)
    return {"stock_id": stock_id, "start": start, "end": end, "signal": signal_fn.__name__,
            "tradable": True, "data_gaps": gaps, "metrics": _metrics(net, gross, trades)}


def run_portfolio_backtest(stock_ids, start, end, signal_fn=signal_ma_bull, capital=CAPITAL):
    """多檔等權固定 sleeve 投組回測：資本均分給可回測之 N 檔，各檔獨立模擬、
    按日期對齊加總為投組權益曲線。取不到之個股排除分母、列入 data_gaps。"""
    gaps_all = []
    loaded = []
    skipped = []
    for sid in stock_ids:
        df, gaps = _load_daily(sid, start, end)
        gaps_all += [f"{sid}: {g}" for g in gaps]
        if df is None:
            skipped.append(sid)
        else:
            loaded.append((sid, df))
    if not loaded:
        return {"stock_ids": stock_ids, "start": start, "end": end, "tradable": False,
                "included": 0, "skipped": skipped, "data_gaps": gaps_all, "metrics": None}
    sleeve = capital / len(loaded)
    net_series, gross_series, all_trades = [], [], []
    for sid, df in loaded:
        hold = _hold_from_signal(df, signal_fn)
        net, gross, trades = _equity_curves(df["close"].astype(float).tolist(), hold, sleeve)
        idx = pd.to_datetime(df["date"])
        net_series.append(pd.Series(net, index=idx))
        gross_series.append(pd.Series(gross, index=idx))
        all_trades += trades
    port_net = _align_sum(net_series, sleeve)
    port_gross = _align_sum(gross_series, sleeve)
    m = _metrics(port_net.tolist(), port_gross.tolist(), all_trades,
                 extra={"included": len(loaded), "skipped": skipped})
    return {"stock_ids": [s for s, _ in loaded], "start": start, "end": end,
            "signal": signal_fn.__name__, "tradable": True, "data_gaps": gaps_all, "metrics": m}


def _selftest():
    close = [100, 101, 102, 103, 104, 103]
    hold = [False, True, True, True, True, False]
    net, gross, trades = _equity_curves(close, hold)
    assert len(net) == len(close) == len(gross)
    m = _metrics(net, gross, trades)
    assert m["total_return_gross"] > m["total_return_net"] and m["cost_drag"] > 0, m
    assert m["n_trades"] == 1 and m["max_drawdown"] <= 0.0, m
    # 空手 → 零報酬、零交易
    n0, g0, t0 = _equity_curves(close, [False] * len(close))
    assert _metrics(n0, g0, t0)["total_return_net"] == 0.0, "空手應零報酬"
    # 契約防呆：長度不符 MUST 擋下
    ok = False
    try:
        _equity_curves([1.0, 2.0], [False])
    except AssertionError:
        ok = True
    assert ok, "未擋下 close/hold 長度不符"
    # 投組對齊加總：兩條不同日期範圍的 sleeve（首日前視為現金）
    s1 = pd.Series([50.0, 55.0, 60.0], index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
    s2 = pd.Series([50.0, 45.0], index=pd.to_datetime(["2024-01-02", "2024-01-03"]))
    tot = _align_sum([s1, s2], 50.0)
    assert abs(tot.loc["2024-01-01"] - 100.0) < 1e-9, tot          # s2 未開始 → 現金 50 + s1 50
    assert abs(tot.loc["2024-01-03"] - 105.0) < 1e-9, tot          # 60 + 45
    # 無 look-ahead：改最後一日訊號不得影響先前部位
    s = pd.Series([False, False, True, True, False, True])
    h1 = s.shift(1).fillna(False).tolist()
    s3 = s.copy(); s3.iloc[-1] = not s3.iloc[-1]
    assert h1[:-1] == s3.shift(1).fillna(False).tolist()[:-1], "look-ahead"
    print("selftest OK")


def main():
    p = argparse.ArgumentParser(description="twstock 台股 long-only 回測引擎（單檔 / 等權投組）")
    p.add_argument("--stock-id", help="單檔，或逗號多檔（如 2330,2454,2317）→ 等權投組")
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default="2024-12-31")
    p.add_argument("--selftest", action="store_true", help="離線自我檢查，不碰 API")
    args = p.parse_args()
    if args.selftest:
        _selftest()
        return
    if not args.stock_id:
        p.error("--stock-id 為必填（或用 --selftest）")
    ids = [s.strip() for s in args.stock_id.split(",") if s.strip()]
    out = run_backtest(ids[0], args.start, args.end) if len(ids) == 1 \
        else run_portfolio_backtest(ids, args.start, args.end)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
