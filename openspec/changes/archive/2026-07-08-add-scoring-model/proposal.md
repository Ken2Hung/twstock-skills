## Why

L3 選股場景（Change 3）已能編排與輸出決策看板，但評分權重僅有 30/30/40 佔位、各面向指標未定義。本 change 依 explore 結論建立評分模型：把權重與指標定義沉澱為知識層單一真相來源，讓權重調整不動選股流程；並修正目標價/止損價的成本語意。

## What Changes

- 新增 `twstock-screening-stocks/references/scoring-model.md`：綜合評分權重（基本面 30% × 技術面 30% × 籌碼面 40%）+ 各面向指標定義（方向語意、回看窗口、資料來源對應 twstock-module dataset）的**單一真相來源**
- **籌碼面 40% 配置**：三大法人買賣超連續性 60%（外資+投信，**排除自營避險** `Dealer_Hedging`/`Foreign_Dealer_Self`）、融資融券變化 40%；股權分散趨勢列 **v-next**
- **基本面**：以**同產業別內百分位**（用 `TaiwanStockInfo` 產業別）+ 二階改善評分，**非硬門檻**，避免砍掉成長股
- **技術面**：均線多頭排列 + 量價為核心；**乖離率移為風險 overlay**，輸出接決策看板風險提示欄，不計入評分
- **缺面向降權重算**：任一面向因 `data_gaps` 缺資料時 SHALL 重新正規化剩餘面向權重，SHALL NOT 以預設值填充缺失面向
- **v1.0 long-only**：信號「賣出/觀望」= 不建議買進/退出，非做空；做空方向語意列 future scope
- **修正目標價/止損價語意**：價位一律以**市場價**呈現（供觸價判定），交易成本**不扣進價位**；改在**預期報酬率**計算時扣除來回成本並引用 `tw-market-rules.md`

**Out of scope**：回測引擎、Python 評分計算引擎（分析由 Claude 本體依 scoring-model.md 執行）、股權分散（v-next）、做空語意（future）。

## Capabilities

### New Capabilities
- `twstock-scoring`: 台股選股評分模型——權重（30/30/40）與三面向指標定義（方向語意/回看窗口/資料來源）的知識層單一真相來源、缺面向降權重正規化規則、long-only 假設。權重調整只改此層、不動選股流程。

### Modified Capabilities
- `twstock-screening-orchestration`: 修正「目標價與止損價」requirement——價位以市場價呈現（觸價判定）、成本不入價位、改在預期報酬率計算扣除來回成本；並在 long-only 假設下寫回 止損 ≤ 現價 ≤ 目標。

## Impact

- **新增檔案**：`references/scoring-model.md`
- **修改**：`twstock-screening-stocks/SKILL.md`（看板目標價/止損價語意、乖離率 overlay 接風險提示、引用 scoring-model.md）；`CLAUDE.md` 評分段落已同步（技術面乖離、籌碼面股權分散 v-next）
- **無新增依賴、無計算引擎**（Claude 本體執行）
- **依賴**：`tw-market-reference`（成本）、`twstock-data-fetching`（各 dataset）
- **v-next 債務**：股權分散納入籌碼面（需先開 L2 change 加 dataset）
