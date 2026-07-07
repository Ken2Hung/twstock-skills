## Why

專案已有 L2 取資料地基（`twstock-module`）與在地化規則知識層（`tw-market-reference`），但還沒有面向使用者的選股入口。使用者無法用自然語言選股。本 change 建立首個 L3 企業場景 `twstock-screening-stocks`，把「自然語言條件 → 委派取資料 → 篩選 → 決策看板」編排起來，且嚴守 L3 不碰 API 的分層鐵律（紅線 #2）。

## What Changes

- 新增 `twstock-screening-stocks/SKILL.md`（L3 企業場景，編排型）
- 編排行為：解析使用者自然語言選股條件 → **委派 `twstock-module` 取得資料**（SHALL NOT 直接呼叫 FinMind/yfinance）→ 套用篩選 → 輸出決策看板
- 決策看板固定格式：評分(0-100)｜信號(買進/持有/觀望/賣出)｜目標價｜止損價｜核心理由(≤3 點)｜風險提示｜data_gaps
- `data_gaps` 非空時看板明示「以下判讀基於不完整資料」；每檔標的必附免責聲明
- 評分權重先用固定佔位值 基本面 30% × 技術面 30% × 籌碼面 40%（指標細節留 Change 4）
- 觸發語涵蓋「幫我篩選…」「找出…的股票」「用 XX 策略挑…」

**Out of scope**：評分各面向的指標定義與門檻（Change 4）、回測、preset 實際策略邏輯（v0.2）、任何直接取數程式碼。

## Capabilities

### New Capabilities
- `twstock-screening-orchestration`: L3 選股編排場景——解析自然語言條件、委派 `twstock-module` 取得資料、套用篩選、輸出固定格式決策看板，並落實免責聲明與 `data_gaps` 誠實揭露。

### Modified Capabilities
<!-- 無。twstock-data-fetching / twstock-data-resilience / tw-market-reference 行為不變，本場景為其消費者。 -->

## Impact

- **新增檔案**：`twstock-screening-stocks/SKILL.md`（取代該目錄現無的 SKILL；references/ 已於 Change 2 建立）
- **無程式碼、無新增依賴**：L3 SKILL.md 為 Claude 本體執行的編排指示，取數委派 `twstock-module`
- **依賴既有 capability**：`twstock-data-fetching`（取數）、`tw-market-reference`（交易成本 → 目標價/止損計算）
- **紅線關聯**：本場景是紅線 #2 的正例（委派而非直呼 API）；免責聲明落實紅線 #3；`data_gaps` 明示落實紅線 #5
