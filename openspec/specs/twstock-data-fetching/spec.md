# twstock-data-fetching

## Purpose

台股單檔證券的結構化資料取得契約：6 種資料集、輸出 JSON 形狀恆定
（`source`/`fetched_at`/`data_gaps`）、`data_gaps` 誠實標註、上市/上櫃市場別判斷，
以及 L2 模組的封裝與觸發約定。由 `twstock-module` 實作，是專案唯一允許碰資料源 API 之處。
## Requirements
### Requirement: 結構化多資料集取得

模組 SHALL 提供對單檔台股證券的 7 種資料集取得能力：日K、PER/PBR、三大法人買賣超、融資融券、月營收、財報三表、股權分散（集保戶股權分散）。輸入 SHALL 為 `stock_id` 與日期區間（起訖日）。每次呼叫的輸出 SHALL 為結構化 JSON，且 MUST 恆含 `source`（實際使用的資料源）、`fetched_at`（取得時間戳）、`data_gaps`（缺漏欄位陣列）三個欄位——即使 `data_gaps` 為空，該欄位 MUST 仍以空陣列存在，以保證輸出形狀穩定。

股權分散資料集 SHALL 取自 TDCC 集保結算所官方開放資料（免費），回傳各持股分級的人數、股數與占集保庫存比例；成功時 `source` MUST 為 `"TDCC"`。此資料集 SHALL 僅提供最新週結快照，`start_date`/`end_date` SHALL 不適用（給定亦忽略）。股權分散於取數失敗或查無證券時 SHALL NOT 降級，MUST fail-open 將缺漏列入 `data_gaps` 並將 `source` 標為 `none`。

#### Scenario: 成功取得日K
- **GIVEN** FinMind 可用且 `stock_id` 有效
- **WHEN** 以 `--stock-id 2330 --dataset daily` 與日期區間呼叫
- **THEN** 回傳 JSON 含日K資料列、`source: "FinMind"`、`fetched_at` 時間戳、以及 `data_gaps: []`

#### Scenario: 成功取得股權分散
- **GIVEN** TDCC 開放資料可取得且 `stock_id` 於集保股權分散表中存在
- **WHEN** 以 `--stock-id 2330 --dataset shareholding` 呼叫
- **THEN** 回傳 JSON 含各持股分級資料列（含分級 15 大戶）、`source: "TDCC"`、`fetched_at` 時間戳、以及 `data_gaps: []`

#### Scenario: 股權分散不吃日期區間
- **GIVEN** 呼叫帶入 `start_date`/`end_date`
- **WHEN** 以 `--dataset shareholding` 呼叫
- **THEN** 模組 SHALL 回最新週結快照，SHALL 忽略日期區間（TDCC `id=1-5` 無歷史）

#### Scenario: 股權分散取不到 fail-open 不降級
- **GIVEN** TDCC 開放資料取數失敗（網路／格式錯誤）或查無該證券
- **WHEN** 以 `--dataset shareholding` 呼叫
- **THEN** 模組 MUST NOT crash，SHALL NOT 降級，MUST fail-open：將缺漏列入 `data_gaps`，且 `source` 標為 `none`

#### Scenario: 輸出形狀恆定
- **WHEN** 任一資料集被成功取得且無缺漏
- **THEN** 輸出 JSON 仍 MUST 含 `data_gaps` 欄位（值為 `[]`），不得省略該鍵

#### Scenario: 部分欄位缺漏誠實標註
- **GIVEN** 某資料集回傳但缺特定欄位
- **WHEN** 組裝輸出 JSON
- **THEN** 缺漏欄位 MUST 列入 `data_gaps`，且 SHALL NOT 以舊資料、預設值或推估值填充（紅線 #5）

### Requirement: 市場別判斷

模組 SHALL 以 FinMind `TaiwanStockInfo` 動態判斷證券市場別：上市證券於 yfinance ticker 加 `.TW`、上櫃加 `.TWO`。模組 SHALL NOT 硬編碼任何股票代碼清單。

#### Scenario: 上市證券 ticker
- **GIVEN** `stock_id` 於 `TaiwanStockInfo` 標記為上市
- **WHEN** 需要組 yfinance ticker（降級時）
- **THEN** ticker MUST 為 `<stock_id>.TW`

#### Scenario: 上櫃證券 ticker
- **GIVEN** `stock_id` 於 `TaiwanStockInfo` 標記為上櫃
- **WHEN** 需要組 yfinance ticker（降級時）
- **THEN** ticker MUST 為 `<stock_id>.TWO`

#### Scenario: 未知代碼
- **GIVEN** `stock_id` 不存在於 `TaiwanStockInfo`
- **WHEN** 判斷市場別
- **THEN** 模組 MUST 回報無法判斷（列入 `data_gaps` 或錯誤），SHALL NOT 猜測市場別

### Requirement: L2 模組封裝與觸發約定

模組 SHALL 以 `SKILL.md` 採 11 區塊標準骨架封裝，含 YAML frontmatter 的 `name` 與 `description`，且 `description` MUST 含自然語言觸發語例句供意圖路由。命名 SHALL 採本 repo 命名規範 `${domain}-${gerund}-${noun}`（L2 業務模組為 `${domain}-module` 例外，如 `twstock-module`）。作為 L2 業務模組，本模組 SHALL 僅回傳結構化資料，SHALL NOT 做分析判讀或排版報告。

#### Scenario: SKILL.md 骨架合規
- **WHEN** 檢視 `twstock-module/SKILL.md`
- **THEN** MUST 含 11 區塊骨架與 frontmatter（`name`、`description`），`description` 含至少一則觸發語例句，且命名符合 `${domain}-${gerund}-${noun}`（L2 模組為 `${domain}-module` 例外）

#### Scenario: 純取資料不越界
- **WHEN** 模組被呼叫取得任一資料集
- **THEN** 回傳 MUST 為結構化 JSON，SHALL NOT 含評分、決策看板、投資建議或任何排版後報告（越界屬 L3 場景職責）

