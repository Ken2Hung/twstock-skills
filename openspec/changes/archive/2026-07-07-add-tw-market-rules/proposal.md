## Why

台股在地化規則（交易成本、漲跌停、處置股）與 FinMind 資料集用法目前散落在 CLAUDE.md 與各人腦中。若讓下游選股／回測各自硬編碼成本數字，會出現魔術數字散落、參數漂移。本 change 把這些沉澱成 `references/` 知識層，並確立「損益計算一律引用單一成本來源」的規則。本 change **無程式碼**，只建知識文件與其引用規範。

## What Changes

- 新增 `twstock-screening-stocks/references/` 三份文件（取代 `.gitkeep` 佔位）：
  - `tw-market-rules.md`：交易成本（買 0.1425%、賣 0.4425% 含證交稅 0.3%）、漲跌停 ±10%、處置股警示規則、上市/上櫃市場別
  - `finmind-api-cheatsheet.md`：本專案用到的 FinMind 資料集速查（dataset key、對應方法、欄位名、參數、範例），源自 FinMind 官方文件
  - `strategy-presets.md`：動能／價值／成長／高股息／法人籌碼五個 preset 的**空骨架模板**，內容留待 v0.2
- 確立規範：所有涉及損益計算的下游能力 SHALL 引用 `tw-market-rules.md` 的成本參數，禁止在程式碼散落魔術數字

**Out of scope**：preset 的實際策略邏輯與門檻值（v0.2）、回測引擎、任何程式碼。

## Capabilities

### New Capabilities
- `tw-market-reference`: 台股在地化規則與 FinMind 資料集的知識基準層——交易成本／漲跌停／處置股／市場別為下游損益計算的單一真相來源，外加資料集速查與策略 preset 骨架。

### Modified Capabilities
<!-- 無。既有 twstock-data-fetching / twstock-data-resilience 行為不變。 -->

## Impact

- **新增檔案**：`twstock-screening-stocks/references/{tw-market-rules,finmind-api-cheatsheet,strategy-presets}.md`（取代 `references/.gitkeep`）
- **無新增依賴、無程式碼變更**
- **下游關聯**：未來 L3 選股場景與回測（Change 3+、v1.0）的損益計算 SHALL 引用 `tw-market-rules.md`，不得自行硬編碼成本
- **紅線關聯**：落實「交易成本等參數不散落魔術數字」；preset 骨架保持空模板，避免過早堆砌（Ponytail 階梯 1）
