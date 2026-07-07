# twstock-skills 開發 Prompts（OpenSpec × Ponytail）

依序在 Claude Code 中使用。每個 Change 走完整循環（propose → review → apply → ponytail-review → 驗證 → archive）才開下一個。

---

## Prompt 0：初始化後填 project.md

> ⚠️ OpenSpec 1.5.0 機制：`openspec init --tools claude` 只產生 `openspec/config.yaml`（context 放 `context:` 鍵），**不再自動產生 `openspec/project.md`**。本專案約定：`project.md` 為 context 的單一真相來源，`config.yaml` 的 `context:` 只放「先讀 project.md + CLAUDE.md」指針與最關鍵三條冗餘紅線，不全文鏡射。

```
讀取 repo 根目錄的 CLAUDE.md，據此填寫 openspec/project.md。必須包含：

1. 技術棧：Python 3.10+、FinMind 官方 SDK、pandas；skill 目標環境為 Claude Desktop / Claude Code（~/.claude/skills/）
2. 架構鐵律（原文照抄 CLAUDE.md 的兩層架構約束）：L3 企業場景不得直接呼叫任何資料源 API，必須委派 twstock-module；L2 模組不做分析判讀
3. CLAUDE.md「紅線」區塊全文照抄
4. 開發紀律：本專案採 Ponytail full mode，spec 未明列的抽象層、框架、快取、設定系統一律不建

寫完後停下來給我 review，不要繼續做其他事。
```

---

## Change 1：`add-finmind-fetcher`（L2 取資料地基）

### Propose

```
/opsx:propose add-finmind-fetcher

建立 twstock-module（L2 業務模組）：SKILL.md + scripts/finmind_fetcher.py。

範圍（spec 必須逐條寫成 requirement + scenario）：
1. 取資料能力：日K、PER/PBR、三大法人買賣超、融資融券、月營收、財報三表，輸入 stock_id + 日期區間，輸出結構化 JSON（含 source、fetched_at、data_gaps 欄位）
2. 降級鏈：FinMind → yfinance（僅日K可降級）。FinMind 回 402/429 或逾時，降級並在 data_gaps 列出 yfinance 無法提供的欄位。scenario 要寫 Given/When/Then
3. Rate limit：讀環境變數 FINMIND_TOKEN；無 token 300 req/hr、有 token 600 req/hr；請求間隔節流用 time.sleep
4. 市場別：上市 .TW / 上櫃 .TWO，以 FinMind TaiwanStockInfo 判斷，禁止硬編碼股票清單
5. SKILL.md 採 11 區塊骨架，description 含觸發語例句

明確排除（寫進 proposal 的 out-of-scope）：快取、資料庫、重試框架、任何分析判讀邏輯。

用 FinMind 官方 SDK 的 DataLoader，不要自建 HTTP 封裝。產出 proposal 後停下來等我 review，不要直接 apply。
```

### Apply（review 通過後）

```
/opsx:apply

依 tasks.md 逐項實作。實作紀律：
- Ponytail full mode：spec 沒要求的東西一行都不寫
- data_gaps 為空陣列時也必須存在於輸出 JSON（欄位形狀穩定）
- 例外處理只包 spec scenario 有定義的情境，不要 catch-all 吞錯
```

### Review + 驗證

```
/ponytail-review

對本次 diff 出 delete-list。處理完後執行：
python -X utf8 twstock-module/scripts/finmind_fetcher.py --stock-id 2330 --dataset daily
並逐條核對 specs 裡每個 scenario 的 WHEN/THEN 是否成立，給我核對表。
```

### Archive

```
/opsx:archive
```

---

## Change 2：`add-tw-market-rules`（純知識層）

```
/opsx:propose add-tw-market-rules

建立 twstock-screening-stocks/references/ 三份知識文件（本 change 無程式碼）：
1. tw-market-rules.md：交易成本（買 0.1425% / 賣 0.4425% 含證交稅）、漲跌停 ±10%、處置股警示規則、上市/上櫃市場別
2. finmind-api-cheatsheet.md：從 FinMind 官方 llms.txt 萃取本專案用到的資料集速查（欄位名、參數、範例）
3. strategy-presets.md：先建骨架（動能/價值/成長/高股息/法人籌碼五個 preset 的空模板），內容留待 v0.2

spec 重點：所有涉及損益計算的下游能力 SHALL 引用 tw-market-rules.md 的成本參數，禁止在程式碼中散落魔術數字。

產出後停下來等我 review。
```

---

## Change 3：`add-screening-skill`（L3 選股場景）

```
/opsx:propose add-screening-skill

建立 twstock-screening-stocks 的 SKILL.md（L3 企業場景，編排型）。

spec 必寫 requirement：
1. 編排行為：解析使用者自然語言選股條件 → 委派 twstock-module 取得資料 → 套用篩選 → 輸出決策看板。SHALL NOT 直接呼叫 FinMind/yfinance（寫成 scenario：WHEN 場景需要日K資料 THEN 呼叫 twstock-module 而非任何 API）
2. 看板輸出格式固定：評分(0-100)｜信號｜目標價｜止損價｜核心理由(≤3點)｜風險提示｜data_gaps
3. data_gaps 非空時，看板 SHALL 明示「以下判讀基於不完整資料」
4. 每檔標的必附免責聲明
5. 觸發語至少涵蓋：「幫我篩選…」「找出…的股票」「用XX策略挑…」

評分權重本 change 先用固定值 30/30/40 佔位，細部指標定義留給 Change 4。

產出後停下來等我 review。
```

---

## Change 4：`add-scoring-model`（評分模型，先 explore）

### Explore（權重與指標還沒定案，先磨需求）

```
/opsx:explore

我要定義台股選股評分模型，目前想法：綜合分 = 基本面30% + 技術面30% + 籌碼面40%（籌碼面加重是因為台股散戶佔比高、法人動向指標性強）。

幫我探討：
1. 籌碼面 40% 內部怎麼配：三大法人買賣超連續性 vs 融資融券變化 vs 股權分散趨勢，各佔多少合理？
2. 基本面用月營收 YoY / EPS / ROE，門檻值怎麼定才不會把成長股全篩掉？
3. 技術面均線多頭排列 + 乖離率 + 量價，有沒有哪個對台股是雜訊？
4. 評分模型放 L2 模組還是 L3 場景？（我的傾向：獨立成 scoring capability，讓權重調整不動選股流程）

不要寫任何 artifact，先討論到我說可以再 propose。
```

### Propose（explore 收斂後）

```
/opsx:propose add-scoring-model

依剛才 explore 的結論建立評分模型。spec 必寫：
1. 權重與各面向指標定義（含資料來源對應 twstock-module 的哪個取資料能力）
2. 任一面向因 data_gaps 缺資料時的降權重算規則（SHALL 重新正規化剩餘面向，SHALL NOT 以預設值填充缺失面向）
3. 損益相關計算 SHALL 引用 tw-market-rules.md 的交易成本
4. 權重定義集中在單一檔案，調整權重不需改動選股流程

產出後停下來等我 review。
```

---

## 週期性維護 Prompts

### 債務收割（每完成 2-3 個 change 執行一次）

```
/ponytail-debt

收割 ledger 後，逐條給我建議：哪些該轉成 openspec change proposal（附建議的 change-id 與一句話 proposal 摘要）、哪些直接棄置（附理由）。我裁決後你再動作。
```

### 全 repo 過度工程稽核（每個版本號發布前）

```
/ponytail-audit

稽核整個 repo。特別檢查：
1. 有沒有 spec 未要求卻存在的抽象層或設定項
2. 交易成本、rate limit 等參數有沒有在多處重複硬編碼
3. references/ 知識文件有沒有跟程式碼行為不一致的地方
出報告，不要直接改。
```

### 規格一致性檢查（懷疑 code 與 spec 漂移時）

```
讀 openspec/specs/ 全部 requirement，逐條對照現有程式碼與 SKILL.md，
列出「spec 有、實作沒有」與「實作有、spec 沒有」兩張清單。
後者每一項標註：該補 spec（走 change 流程）還是該刪 code（Ponytail delete-list）。
```
