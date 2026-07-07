## 1. SKILL.md 骨架與編排流程

- [ ] 1.1 建立 `twstock-screening-stocks/SKILL.md`，採 11 區塊骨架 + YAML frontmatter（`name: twstock-screening-stocks`、`description` 含觸發語）
- [ ] 1.2 命名符合 L3 場景 `${domain}-${gerund}-${noun}`（`twstock-screening-stocks`）
- [ ] 1.3 編排流程：解析自然語言選股條件 → 委派 `twstock-module` 取得資料 → 套用篩選 → 輸出決策看板
- [ ] 1.4 明列禁令：SHALL NOT 直接呼叫 FinMind/yfinance，所有取數委派 `twstock-module` 的 dataset key

## 2. 決策看板輸出契約

- [ ] 2.1 固定七欄位：評分(0-100)｜信號(買進/持有/觀望/賣出)｜目標價｜止損價｜核心理由(≤3 點)｜風險提示｜data_gaps
- [ ] 2.2 目標價／止損價的損益基準引用 `tw-market-reference`（交易成本），不散落魔術數字
- [ ] 2.3 附一則看板範例（示範七欄位格式）

## 3. 合規（紅線）

- [ ] 3.1 `data_gaps` 非空時，看板明示「以下判讀基於不完整資料」
- [ ] 3.2 每檔標的必附免責聲明；禁止「保證獲利/必漲」表述
- [ ] 3.3 權重佔位標註：基本面 30 / 技術面 30 / 籌碼面 40，指標細節見 Change 4

## 4. 觸發語與驗證

- [ ] 4.1 `description` 觸發語涵蓋「幫我篩選…」「找出…的股票」「用 XX 策略挑…」
- [ ] 4.2 核對 spec 各 scenario 的 WHEN/THEN：委派邊界、看板七欄位、data_gaps 明示、免責、觸發語
- [ ] 4.3 抽驗一條委派流程（以 2330 為例，確認流程指示走 twstock-module 取數、非直呼 API）
