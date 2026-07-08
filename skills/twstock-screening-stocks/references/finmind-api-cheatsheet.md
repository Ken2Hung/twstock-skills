# 資料集速查（本專案用到的 7 種：6 FinMind + 1 TDCC）

> 方法名與 dataset key 對齊 `skills/twstock-module/scripts/finmind_fetcher.py`（`FINMIND_METHODS` / `FINANCIAL_METHODS`）。
> 欄位取自實際回傳（2330 實測）。透過 `twstock-module` 取用，**L3 場景不得直接呼叫**。
> 共通參數：`stock_id`、`start_date`、`end_date`（`YYYY-MM-DD`）。共通欄位：`date`、`stock_id`。
> 例外：`shareholding` 源自 **TDCC 官方開放資料**（非 FinMind），不吃日期區間，欄位為中文，見下方專節。

## daily — 日K

- **DataLoader 方法**：`taiwan_stock_daily`
- **欄位**：`Trading_Volume`、`Trading_money`、`open`、`max`、`min`、`close`、`spread`、`Trading_turnover`
- **範例**：`--stock-id 2330 --dataset daily --start-date 2024-01-01 --end-date 2024-06-30`
- 註：**唯一可降級 yfinance** 的資料集（FinMind 402/429/逾時時）。

## per_pbr — 本益比／股價淨值比

- **DataLoader 方法**：`taiwan_stock_per_pbr`
- **欄位**：`dividend_yield`（殖利率）、`PER`、`PBR`
- **範例**：`--stock-id 2330 --dataset per_pbr ...`

## institutional — 三大法人買賣超

- **DataLoader 方法**：`taiwan_stock_institutional_investors`
- **欄位**：`name`（法人別）、`buy`、`sell`
- **`name` 法人別值**：`Foreign_Investor`（外資）、`Foreign_Dealer_Self`、`Investment_Trust`（投信）、`Dealer_self`（自營商自行買賣）、`Dealer_Hedging`（自營商避險）
- **註**：長格式，每日每法人別一列（單日約 5 列）；買賣超 = `buy - sell`。
- **範例**：`--stock-id 2330 --dataset institutional ...`

## margin — 融資融券

- **DataLoader 方法**：`taiwan_stock_margin_purchase_short_sale`
- **欄位**：融資 `MarginPurchaseBuy`／`MarginPurchaseSell`／`MarginPurchaseTodayBalance`／`MarginPurchaseYesterdayBalance`／`MarginPurchaseCashRepayment`／`MarginPurchaseLimit`；融券 `ShortSaleBuy`／`ShortSaleSell`／`ShortSaleTodayBalance`／`ShortSaleYesterdayBalance`／`ShortSaleCashRepayment`／`ShortSaleLimit`；`OffsetLoanAndShort`（資券互抵）、`Note`
- **範例**：`--stock-id 2330 --dataset margin ...`

## revenue — 月營收

- **DataLoader 方法**：`taiwan_stock_month_revenue`
- **欄位**：`country`、`revenue`（當月營收）、`revenue_month`、`revenue_year`、`create_time`
- **註**：YoY 年增率須自行以 `revenue` 對去年同月計算（FinMind 不直接給 YoY）。
- **範例**：`--stock-id 2330 --dataset revenue ...`

## shareholding — 集保戶股權分散（TDCC 開放資料，非 FinMind）

- **來源**：TDCC 集保結算所開放資料 `https://opendata.tdcc.com.tw/getOD.ashx?id=1-5`（免費，避開 FinMind 付費層）。`twstock-module` 直接讀 CSV、過濾單檔（`證券代號` 有空白 padding，比對前 strip）。
- **欄位（中文，實測 2330）**：`資料日期`（YYYYMMDD）、`證券代號`、`持股分級`（`1`~`17`）、`人數`、`股數`、`占集保庫存數比例%`
- **持股分級對照**：`1`=1–999 股、`2`=1,000–5,000…遞增至 `14`=800,001–1,000,000、**`15`=1,000,001 股以上（大戶）**、`16`=差異數調整、`17`=合計。籌碼面「大戶持股」= 追蹤分級 `15` 的 `占集保庫存數比例%`；評分以其**產業內百分位（snapshot level）**計，見 `scoring-model.md`。
- **註**：**僅最新一週快照**（`id=1-5` 無歷史區間），`start_date`/`end_date` 不適用；取數失敗或查無證券 → fail-open 進 `data_gaps`、`source: none`。
- **範例**：`--stock-id 2330 --dataset shareholding`（日期參數會被忽略）

## financial — 財報三表（組合資料集）

- **DataLoader 方法**：`taiwan_stock_financial_statement`（綜合損益表）、`taiwan_stock_balance_sheet`（資產負債表）、`taiwan_stock_cash_flows_statement`（現金流量表）
- **共通欄位（長格式）**：`type`（科目代碼，如 `EPS`、`GrossProfit`、`CostOfGoodsSold`、`OperatingExpenses`、`IncomeAfterTaxes`…）、`value`（數值）、`origin_name`（科目原始中文名）
- **註**：季度資料，日期須落在財報公布區間才有資料（如 Q1 約 5 月中公布）。三表分三次呼叫、缺表各自進 `data_gaps`。
- **範例**：`--stock-id 2330 --dataset financial --start-date 2024-01-01 --end-date 2024-06-30`

---

## 市場別（TaiwanStockInfo）

- **DataLoader 方法**：`taiwan_stock_info`（回傳全市場清單）
- **關鍵欄位**：`stock_id`、`stock_name`、`industry_category`、`type`
- **`type` 值**：`twse`（上市 → `.TW`）、`tpex`（上櫃 → `.TWO`）、`emerging`（興櫃，不在本專案範圍）
- **用途**：市場別判斷、產業別；`twstock-module` 僅在日K降級組 yfinance ticker 時呼叫。
