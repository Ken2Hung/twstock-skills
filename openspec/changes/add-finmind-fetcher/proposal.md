## Why

專案目前沒有任何取資料地基——所有 L3 選股／健檢場景都依賴一個「唯一允許碰資料源 API」的 L2 模組來供數。沒有它，場景層要嘛無法運作、要嘛被迫自己碰 API（違反紅線 #2）。本 change 建立 `twstock-module`，作為整個專案的資料入口。

## What Changes

- 新增 `twstock-module/`（L2 業務模組）：`SKILL.md` + `scripts/finmind_fetcher.py`
- `finmind_fetcher.py` 提供 6 種台股資料的結構化取得：日K、PER/PBR、三大法人買賣超、融資融券、月營收、財報三表；輸入 `stock_id` + 日期區間，輸出固定形狀 JSON（含 `source` / `fetched_at` / `data_gaps`）
- 降級鏈：FinMind 為主，**僅日K**可降級到 yfinance；FinMind 回 402/429 或逾時時降級，其餘 5 種資料取不到就誠實進 `data_gaps`、不降級
- Rate limit：讀 `FINMIND_TOKEN` 環境變數（無 token 300 req/hr、有 token 600 req/hr），請求間隔以 `time.sleep` 節流
- 市場別：上市 `.TW` / 上櫃 `.TWO`，以 FinMind `TaiwanStockInfo` 動態判斷，不硬編碼股票清單
- `SKILL.md` 採 11 區塊骨架，`description` 含自然語言觸發語例句
- 新增依賴 `yfinance`（僅供日K降級 fallback）

**Out of scope（明確排除）**：快取、資料庫、重試框架、任何分析判讀或排版邏輯。這些留待 spec 明列時才建（Ponytail 階梯 1）。

## Capabilities

### New Capabilities
- `twstock-data-fetching`: 台股單檔證券的結構化資料取得——6 種資料集、輸出 JSON 形狀恆定（`source`/`fetched_at`/`data_gaps`）、`data_gaps` 誠實標註、上市/上櫃市場別判斷，以及模組的封裝與觸發約定。
- `twstock-data-resilience`: 取得過程的韌性保證——FinMind→yfinance 日K降級鏈（僅日K可降級）、token-aware rate limit 節流、憑證不外洩。與 `twstock-data-fetching` 分離，使降級策略與節流可獨立演進而不動取得契約。

### Modified Capabilities
<!-- 無。這是專案首個 spec，openspec/specs/ 目前為空。 -->

## Impact

- **新增檔案**：`twstock-module/SKILL.md`、`twstock-module/scripts/finmind_fetcher.py`（取代原 `.gitkeep` 佔位）
- **新增依賴**：`yfinance`（日K fallback）；沿用已裝的 FinMind SDK、pandas
- **環境變數**：`FINMIND_TOKEN`（選用，提升 rate limit）
- **紅線關聯**：本模組是紅線 #2 的守門人（唯一可碰 API 處）；輸出契約落實紅線 #5（`data_gaps` 不腦補）；不引入任何外部 LLM 依賴（紅線 #1）
- **下游**：後續所有 L3 場景（screening、reviewing-portfolio）委派本模組取得資料，不自行碰 API
