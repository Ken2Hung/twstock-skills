"""twstock-module（L2）：FinMind 台股資料取得器。

本專案唯一允許碰資料源 API 的地方。輸出結構化 JSON，恆含
source / fetched_at / data_gaps 三欄。僅日K可於 FinMind 失效時降級至
yfinance；其餘資料集取不到就誠實進 data_gaps，不降級、不腦補。

用法：
    python -X utf8 finmind_fetcher.py --stock-id 2330 --dataset daily
    python -X utf8 finmind_fetcher.py --selftest      # 離線自我檢查（不碰 API）
"""
import argparse
import json
import os
import time
from datetime import date, datetime, timedelta, timezone

# dataset key -> FinMind DataLoader 方法名（簽名皆為 stock_id/start_date/end_date）
FINMIND_METHODS = {
    "daily": "taiwan_stock_daily",
    "per_pbr": "taiwan_stock_per_pbr",
    "institutional": "taiwan_stock_institutional_investors",
    "margin": "taiwan_stock_margin_purchase_short_sale",
    "revenue": "taiwan_stock_month_revenue",
}
# 財報三表：組合資料集，逐表取，缺表各自進 data_gaps
FINANCIAL_METHODS = {
    "income_statement": "taiwan_stock_financial_statement",
    "balance_sheet": "taiwan_stock_balance_sheet",
    "cash_flows": "taiwan_stock_cash_flows_statement",
}
DATASETS = list(FINMIND_METHODS) + ["financial"]


def _is_source_failure(exc):
    """判斷例外是否為 spec 定義的降級觸發（rate limit / 402 / 429 / timeout）。
    非此類例外不吞、往外拋——不做 catch-all。"""
    s = str(exc).lower()
    return (
        "upper limit" in s
        or "402" in s
        or "429" in s
        or "timeout" in s
        or "timed out" in s
    )


class FinmindFetcher:
    def __init__(self):
        # 憑證只從環境變數讀，腳本零寫死；token 不進任何輸出/log
        self.token = os.environ.get("FINMIND_TOKEN", "")
        from FinMind.data import DataLoader

        self.api = DataLoader()
        if self.token:
            self.api.login_by_token(api_token=self.token)
        # 節流節奏對應 rate limit 上限：3600/limit 秒/請求（無 token 300、有 token 600）
        # ponytail: 行程內全域節流，跨行程協調待全市場批量的新 change 再議
        self._min_interval = 3600.0 / (600 if self.token else 300)
        self._last_req = 0.0

    def _throttle(self):
        wait = self._min_interval - (time.monotonic() - self._last_req)
        if wait > 0:
            time.sleep(wait)
        self._last_req = time.monotonic()

    def _call(self, method, stock_id, start_date, end_date):
        self._throttle()
        return getattr(self.api, method)(
            stock_id=stock_id, start_date=start_date, end_date=end_date
        )

    def _market_type(self, stock_id):
        """查 TaiwanStockInfo 判市場別，回 'twse'/'tpex'/None。不硬編碼清單。
        來源失敗（rate limit 等）回 None → 由呼叫端列入 data_gaps，不猜測。"""
        self._throttle()
        try:
            info = self.api.taiwan_stock_info()
        except Exception as exc:  # noqa: BLE001 - 分類後決定吞或拋
            if _is_source_failure(exc):
                return None
            raise
        row = info[info["stock_id"] == stock_id]
        if row.empty:
            return None
        return row.iloc[0]["type"]  # 'twse'(上市) / 'tpex'(上櫃)

    def _yfinance_daily(self, stock_id, start_date, end_date, gaps):
        """日K降級至 yfinance。需先由 TaiwanStockInfo 定市場別組 ticker。"""
        mkt = self._market_type(stock_id)
        suffix = {"twse": ".TW", "tpex": ".TWO"}.get(mkt)
        if suffix is None:
            gaps.append("market_type: 無法由 TaiwanStockInfo 判斷，yfinance ticker 未組成")
            return None, None
        import yfinance as yf

        df = yf.download(
            f"{stock_id}{suffix}", start=start_date, end=end_date, progress=False
        )
        if df is None or df.empty:
            gaps.append("daily: yfinance 亦無資料")
            return None, mkt
        df = df.reset_index()
        df.columns = [
            "_".join(str(x) for x in c if x) if isinstance(c, tuple) else str(c)
            for c in df.columns
        ]
        return json.loads(df.to_json(orient="records", date_format="iso")), mkt

    def fetch(self, stock_id, dataset, start_date, end_date):
        gaps = []
        market = None
        source = "FinMind"
        if dataset == "financial":
            data = {}
            for key, method in FINANCIAL_METHODS.items():
                try:
                    df = self._call(method, stock_id, start_date, end_date)
                    data[key] = _records(df)
                except Exception as exc:  # noqa: BLE001 - 分類後決定吞或拋
                    if _is_source_failure(exc):
                        data[key] = []
                        gaps.append(f"{key}: FinMind 取不到（{_reason(exc)}），不降級")
                    else:
                        raise
        elif dataset in FINMIND_METHODS:
            try:
                df = self._call(FINMIND_METHODS[dataset], stock_id, start_date, end_date)
                data = _records(df)
            except Exception as exc:  # noqa: BLE001
                if not _is_source_failure(exc):
                    raise
                if dataset == "daily":
                    # 僅日K可降級
                    data, market = self._yfinance_daily(
                        stock_id, start_date, end_date, gaps
                    )
                    source = "yfinance" if data is not None else "none"
                    if source == "yfinance":
                        gaps.append("daily: 來源為 yfinance，台股報價延遲約 20 分鐘")
                    data = data or []
                else:
                    data = []
                    gaps.append(f"{dataset}: FinMind 取不到（{_reason(exc)}），不降級")
                    source = "none"
        else:
            raise ValueError(f"未知 dataset: {dataset}（可用：{', '.join(DATASETS)}）")

        return _assemble(stock_id, dataset, start_date, end_date, source, data, gaps, market)


def _records(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))


def _reason(exc):
    s = str(exc)
    return "rate limit" if "upper limit" in s.lower() else s[:60]


def _assemble(stock_id, dataset, start_date, end_date, source, data, gaps, market):
    """統一組裝輸出，保證 source/fetched_at/data_gaps 恆存在（形狀穩定）。"""
    return {
        "stock_id": stock_id,
        "dataset": dataset,
        "start_date": start_date,
        "end_date": end_date,
        "source": source,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "market": market,
        "data": data if data is not None else [],
        "data_gaps": gaps,
    }


def _selftest():
    """離線自我檢查：不碰 API，驗證輸出形狀契約。"""
    out = _assemble("2330", "daily", "2024-01-01", "2024-02-01", "FinMind", [{"x": 1}], [], None)
    for k in ("source", "fetched_at", "data_gaps", "data", "stock_id"):
        assert k in out, f"缺欄位 {k}"
    assert out["data_gaps"] == [], "data_gaps 空時仍須為 []"
    assert isinstance(out["data_gaps"], list)
    empty = _assemble("2330", "daily", "s", "e", "none", None, ["daily: 缺"], None)
    assert empty["data"] == [] and empty["data_gaps"] == ["daily: 缺"]
    assert _is_source_failure(Exception("Requests reach the upper limit"))
    assert _is_source_failure(Exception("read timed out"))
    assert not _is_source_failure(Exception("KeyError: foo"))
    print("selftest OK")


def main():
    p = argparse.ArgumentParser(description="twstock-module FinMind 取得器")
    p.add_argument("--stock-id")
    p.add_argument("--dataset", choices=DATASETS, default="daily")
    p.add_argument("--start-date", default=(date.today() - timedelta(days=365)).isoformat())
    p.add_argument("--end-date", default=date.today().isoformat())
    p.add_argument("--selftest", action="store_true", help="離線自我檢查，不碰 API")
    args = p.parse_args()

    if args.selftest:
        _selftest()
        return
    if not args.stock_id:
        p.error("--stock-id 為必填（或用 --selftest）")

    out = FinmindFetcher().fetch(
        args.stock_id, args.dataset, args.start_date, args.end_date
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
