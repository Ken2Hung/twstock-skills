## Why

評分模型的籌碼面（權重 40%）規劃以「三大法人 / 融資融券 / 股權分散趨勢」三項構成，但 L2 業務模組 `twstock-module` 目前只提供 6 種資料集，缺「股權分散」這一項籌碼訊號。集保戶股權分散（大戶持股比例變化）是台股籌碼面的關鍵指標，須先在唯一允許碰資料源 API 的 L2 模組把取數能力補齊，後續的評分模型 change（`add-scoring-model`）才有資料可委派。

## What Changes

- `twstock-module` 新增第 7 個資料集 `shareholding`（集保戶股權分散），來源為 **TDCC 集保結算所官方開放資料**（`id=1-5`，免費、全市場、週更快照）。實作階段實測發現 FinMind 對應端點 `taiwan_stock_holding_shares_per` 為付費層專屬、free tier 取不到，故改採免費官方開放資料，符合專案「官方開放資料」降級哲學。
- 沿用既有輸出契約：輸出恆含 `source`/`fetched_at`/`data_gaps`；成功時 `source: "TDCC"`；取數失敗或查無證券 → fail-open 進 `data_gaps`、`source: none`、**不降級**。
- `shareholding` 僅回最新週結快照，不吃日期區間（`id=1-5` 無歷史），於文件明確標註。
- 更新 `twstock-module/SKILL.md` 能力總覽表與 `references/finmind-api-cheatsheet.md`（新增 `shareholding` TDCC 專節，速查標題由 6 種改 7 種＝6 FinMind + 1 TDCC）。

**非本 change 範圍（後續依賴）**：評分模型籌碼面權重重新分配、`scoring-model.md`、CLAUDE.md 評分模型段落——這些屬尚未提案的 `add-scoring-model`（Change 4）職責。本 change 僅補資料層取數能力，於 `tasks.md` 註記為其上游依賴。

## Capabilities

### New Capabilities
<!-- 無新增 capability：股權分散仍屬「單檔證券結構化資料取得」的既有契約範疇 -->

### Modified Capabilities
- `twstock-data-fetching`：「結構化多資料集取得」requirement 由 6 種資料集擴充為 7 種（新增股權分散，來源 TDCC 開放資料、僅最新週結快照、不吃日期區間），並明確取數失敗 fail-open 進 `data_gaps`、不降級的行為。
- `twstock-data-resilience`：「FinMind→yfinance 日K降級鏈」requirement 補充 `shareholding` 為非 FinMind 來源（TDCC）、取數失敗一律 fail-open 進 `data_gaps`（`source: none`），不降級、不中斷主鏈路。

## Impact

- **程式**：`twstock-module/scripts/finmind_fetcher.py`（新增 `_tdcc_shareholding` 分支 + TDCC 端點常數；`DATASETS` 加 `shareholding`）。
- **文件**：`twstock-module/SKILL.md`（能力總覽表、輸入契約、資料源段）、`twstock-screening-stocks/references/finmind-api-cheatsheet.md`（新增 TDCC 專節）。
- **Spec**：`twstock-data-fetching` 與 `twstock-data-resilience` 各一條 MODIFIED requirement。
- **依賴**：本 change 完成後，`add-scoring-model` 方可將股權分散（大戶持股水位）納入籌碼面。
- **資料源**：新增 TDCC 官方開放資料（免費 HTTP CSV，無憑證、無 rate limit 疑慮）；用既有 pandas 讀取，無新增第三方套件。
