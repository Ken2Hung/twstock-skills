---
name: twstock-module
description: >-
  台股資料取得業務模組（L2）。封裝 FinMind API，提供單檔證券的日K、PER/PBR、
  三大法人買賣超、融資融券、月營收、財報三表、集保戶股權分散取得，回傳結構化
  JSON（含 source / fetched_at / data_gaps）。這是專案唯一允許碰資料源 API 的
  地方，供 L3 選股／健檢場景委派取數。觸發語例句：「取得 2330 的日K」「抓台積電
  的三大法人買賣超」「給我 2454 近一年月營收」「查 2317 的融資融券」「撈某檔的
  財報三表」「幫我取台股某檔的 PER/PBR」「查 2330 的集保股權分散」。本模組只回
  結構化資料，不做分析判讀、不排版報告。
---

# twstock-module

## 1. 觸發時機

當任何流程需要「單檔台股證券的原始結構化資料」時委派本模組。典型情境：
L3 選股場景需日K與籌碼面資料、持股健檢需財報與法人動向。**L3 場景不得自己
碰 FinMind／yfinance，一律委派本模組**（專案紅線 #2）。

## 2. 能力總覽

| dataset key | 內容 | 資料來源 |
|---|---|---|
| `daily` | 日K（OHLCV） | FinMind `taiwan_stock_daily` |
| `per_pbr` | 本益比／股價淨值比 | FinMind `taiwan_stock_per_pbr` |
| `institutional` | 三大法人買賣超 | FinMind `taiwan_stock_institutional_investors` |
| `margin` | 融資融券 | FinMind `taiwan_stock_margin_purchase_short_sale` |
| `revenue` | 月營收 | FinMind `taiwan_stock_month_revenue` |
| `shareholding` | 集保戶股權分散（各持股分級人數／股數／占比，分級 15 = 大戶） | **TDCC 官方開放資料**（免費，最新週結快照） |
| `financial` | 財報三表（損益表／資產負債表／現金流量表） | FinMind 三個 statement 端點組合 |

## 3. 輸入契約

- `stock_id`：證券代碼（字串，如 `2330`）
- `dataset`：上表 key 之一（預設 `daily`）
- `start_date` / `end_date`：`YYYY-MM-DD`（預設近一年）。**`shareholding` 例外**：TDCC 開放資料僅最新週結快照，不吃日期區間（給了也忽略）。

## 4. 輸出契約

一律回傳結構化 JSON，**恆含** `source`、`fetched_at`、`data_gaps` 三欄（形狀穩定）：

```json
{
  "stock_id": "2330",
  "dataset": "daily",
  "start_date": "2024-01-01",
  "end_date": "2024-07-01",
  "source": "FinMind",
  "fetched_at": "2026-07-07T09:40:59Z",
  "market": null,
  "data": [ /* 資料列，financial 為三表物件 */ ],
  "data_gaps": []
}
```

`data_gaps` 即使為空也 MUST 以 `[]` 存在。缺漏欄位誠實列入，**禁止腦補或以舊資料填充**（紅線 #5）。

## 5. 資料源與降級

- 主源 **FinMind**。**僅 `daily`** 可於 FinMind 回 402/429/逾時時降級至 **yfinance**，輸出標 `source: "yfinance"` 並註明「台股報價延遲約 20 分鐘」。
- 其餘 4 種 FinMind 資料集（`per_pbr`／`institutional`／`margin`／`revenue`）與 `financial` 取不到 → 直接列入 `data_gaps`、**不降級**（yfinance 本就無台股籌碼／財報／月營收）。
- `shareholding` 走 **TDCC 官方開放資料**（免費，避開 FinMind 付費層），輸出標 `source: "TDCC"`；取數失敗或查無證券 → fail-open 進 `data_gaps`、`source: "none"`，不降級。
- fail-open：單一資料源失效不中斷主鏈路。

## 6. Rate limit 與憑證

- token 只從環境變數 `FINMIND_TOKEN` 讀，**腳本零寫死憑證**。
- 無 token 300 req/hr、有 token 600 req/hr；請求間以 `time.sleep` 節流（節奏 = 3600/上限 秒）。
- token **不進**任何輸出 JSON、log 或存檔。

## 7. 使用方式

```bash
# 環境變數提供 token（不寫入任何檔案；session-scoped 亦可）
export FINMIND_TOKEN=<your_token>

python -X utf8 twstock-module/scripts/finmind_fetcher.py --stock-id 2330 --dataset daily
python -X utf8 twstock-module/scripts/finmind_fetcher.py --stock-id 2330 --dataset financial \
  --start-date 2023-01-01 --end-date 2024-12-31
python -X utf8 twstock-module/scripts/finmind_fetcher.py --selftest   # 離線形狀自檢
```

## 8. 分層邊界（L2）

本模組 SHALL 僅回傳結構化資料。**不做**評分、決策看板、目標價／止損、投資建議或任何排版報告——那些屬 L3 企業場景職責。越界即破壞分層。

## 9. 錯誤與 data_gaps 處理

- 例外只處理 spec 定義情境（rate limit / 402 / 429 / timeout）：`daily` 觸發降級，其餘進 `data_gaps`。
- 非上述例外**不吞、往外拋**（不做 catch-all）。
- 市場別無法由 `TaiwanStockInfo` 判斷時列入 `data_gaps`，不猜測。

## 10. 範例

「取得 2330 近一年日K」→ `--stock-id 2330 --dataset daily`
「抓台積電三大法人買賣超」→ `--stock-id 2330 --dataset institutional`
「撈 2454 財報三表」→ `--stock-id 2454 --dataset financial`

## 11. 限制與免責

- 市場別、descriptors 以 FinMind `TaiwanStockInfo` 為準，不硬編碼股票清單。
- yfinance 報價延遲約 20 分鐘，降級輸出已標註。
- 本模組僅供資料取得；所有投資判讀與免責由上層 L3 場景負責。本專案輸出不構成投資建議。
