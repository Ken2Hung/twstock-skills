"""每日選股前濾（v2.0-alpha C 混合 step 1）：對 watchlist 逐檔算今日可算訊號，回 shortlist。

資料一律經 twstock-module；訊號重用 twstock-backtesting 之 `signal_ma_bull`（單一可算訊號
來源，不漂移）。逐檔 fail-open（某檔取不到 → 跳過 + data_gaps，不中斷）。此為快篩，
後續由 Claude 本體對 shortlist 做決策看板、再委派 twstock-notifying-line 推播。

用法：
    python -X utf8 daily_screen.py --watchlist 2330,2454,2317,2412
    python -X utf8 daily_screen.py --selftest      # 離線自我檢查（不碰 API）
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", "..", "twstock-backtesting", "scripts"))
from backtest import _load_daily, signal_ma_bull  # noqa: E402  重用可算訊號，不另定義


DISCLAIMER = "⚠️ 僅供研究參考，不構成投資建議，請自行判斷並自負風險。"


def _is_picked(df, signal_fn):
    """今日（最後一根）是否入選。live 選股用當日資料選當日，非回測，無 look-ahead 疑慮。"""
    s = signal_fn(df)
    if not len(s):
        return False
    x = s.iloc[-1]
    return bool(x) if x == x else False   # x == x 為 False 表 NaN，防邊界 NaN


def screen(watchlist, asof=None, signal_fn=signal_ma_bull):
    asof = asof or date.today().isoformat()
    start = (date.fromisoformat(asof) - timedelta(days=200)).isoformat()  # 60MA 暖身
    picks, gaps = [], []
    for sid in watchlist:
        try:
            df, g = _load_daily(sid, start, asof)
            gaps += [f"{sid}: {x}" for x in g]
            if df is None:
                continue
            if _is_picked(df, signal_fn):
                picks.append({"stock_id": sid,
                              "close": round(float(df["close"].iloc[-1]), 2),
                              "date": str(df["date"].iloc[-1])})
        except Exception as exc:  # noqa: BLE001 - 逐檔 fail-open，單檔異常不中斷整體
            gaps.append(f"{sid}: 例外 {type(exc).__name__}: {str(exc)[:80]}")
    return {"asof": asof, "strategy": signal_fn.__name__,
            "screened": len(watchlist), "picks": picks, "data_gaps": gaps}


def format_picks(result):
    """把 screen 結果組成可推播文字（合規：恆附免責、data_gaps 非空明示不完整）。"""
    header = f"【每日選股 {result['asof']}｜{result['strategy']}】"
    picks = result["picks"]
    body = ("今日入選：" + "、".join(f"{p['stock_id']}({p['close']})" for p in picks)
            if picks else "今日無標的入選。")
    lines = [header, body]
    if result["data_gaps"]:
        lines.append(f"※ 以下基於不完整資料（{len(result['data_gaps'])} 項缺口）")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def _selftest():
    import pandas as pd
    inc = [float(p) for p in range(80, 150)]                 # 遞增 → 5MA>20MA>60MA 多頭
    df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=len(inc)).astype(str), "close": inc})
    assert _is_picked(df, signal_ma_bull) is True, "遞增應入選"
    dec = [float(p) for p in range(150, 80, -1)]             # 遞減 → 非多頭
    df2 = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=len(dec)).astype(str), "close": dec})
    assert _is_picked(df2, signal_ma_bull) is False, "遞減不應入選"
    short = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=10).astype(str),
                          "close": [float(p) for p in range(10)]})
    assert _is_picked(short, signal_ma_bull) is False, "短序列(不足MA)應安全回 False、不拋錯"
    # format_picks：恆附免責、無保證語；空/缺口
    r = {"asof": "2024-12-31", "strategy": "signal_ma_bull", "screened": 2,
         "picks": [{"stock_id": "2330", "close": 1075.0, "date": "2024-12-31"}], "data_gaps": []}
    t = format_picks(r)
    assert "2330" in t and "自負風險" in t and "保證" not in t and "必賺" not in t, t
    t2 = format_picks({**r, "picks": [], "data_gaps": ["2317: x"]})
    assert "無標的" in t2 and "不完整資料" in t2, t2
    print("selftest OK")


def main():
    p = argparse.ArgumentParser(description="每日選股前濾（watchlist）")
    p.add_argument("--watchlist", help="逗號分隔股票清單，如 2330,2454,2317")
    p.add_argument("--asof", default=None, help="截止日 YYYY-MM-DD（預設今日）")
    p.add_argument("--format", action="store_true", help="輸出可推播文字（含免責）而非 JSON")
    p.add_argument("--selftest", action="store_true", help="離線自我檢查，不碰 API")
    a = p.parse_args()
    if a.selftest:
        _selftest()
        return
    if not a.watchlist:
        p.error("--watchlist 為必填（或用 --selftest）")
    wl = [s.strip() for s in a.watchlist.split(",") if s.strip()]
    result = screen(wl, a.asof)
    print(format_picks(result) if a.format else json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
