## 1. scoring-model.md（權重與指標定義單一真相來源）

- [ ] 1.1 建立 `twstock-screening-stocks/references/scoring-model.md`
- [ ] 1.2 綜合權重：基本面 30% × 技術面 30% × 籌碼面 40%，並註明「調權重只改此檔」
- [ ] 1.3 籌碼面 40%：法人連續性 60%（僅外資+投信、排除自營避險）、融資融券 40%（股權分散 v-next）；法人與融資融券一律以**佔同期成交量比**計，禁絕對張數/金額
- [ ] 1.4 每個籌碼指標定義方向語意（正/負向）+ 回看窗口**統一 5 日** + 融資「大增」量化門檻（增量佔成交量比 > 裁決值）
- [ ] 1.4b 限制段落註記：「融資增=負」為不分股價位置之 v1 簡化，低檔融資增常為反彈確認，v-next 結合位置資訊
- [ ] 1.5 基本面：同產業內百分位（TaiwanStockInfo 產業別）+ 二階改善；月營收 YoY（百分位近 6 月／二階近 3 月，**1+2 月合併計 YoY**）、EPS 成長（轉正加分）、ROE（近 4 季）
- [ ] 1.5b 農曆年規則寫入 scoring-model.md，並於 `references/tw-market-rules.md` 補一行交叉引用（1+2 月營收合併）
- [ ] 1.6 技術面核心：均線多頭排列 + 量價；乖離率標明為風險 overlay（不計分）
- [ ] 1.7 每個指標標明對應 twstock-module dataset

## 2. SKILL.md 更新（L3 消費 scoring-model）

- [ ] 2.1 看板目標價/止損價語意改為市場價（觸價判定），成本不入價位
- [ ] 2.2 預期報酬率計算引用 tw-market-rules.md 來回成本（買+賣）
- [ ] 2.3 乖離率 overlay 接風險提示欄位
- [ ] 2.4 評分引用 scoring-model.md（權重與指標定義），標註 long-only

## 3. 缺面向正規化與 long-only

- [ ] 3.1 缺面向降權重：剩餘面向權重重新正規化，禁止預設值填充
- [ ] 3.2 long-only：信號賣出/觀望=不建議買進/退出；止損 ≤ 現價 ≤ 目標；做空列 future

## 4. 驗證

- [ ] 4.1 核對 twstock-scoring 5 requirement 的 scenario（權重單一來源、籌碼方向語意、基本面百分位、乖離 overlay、缺面向正規化）
- [ ] 4.2 核對 twstock-screening-orchestration MODIFIED Req3 的 4 scenario（市場價、預期報酬扣成本、long-only 不等式、流動性風險）
- [ ] 4.3 確認 CLAUDE.md 評分段落與 scoring-model.md 一致（無漂移）
