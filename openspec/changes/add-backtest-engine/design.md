## Context

專案首個計算引擎。回測無法由 Claude 本體逐日執行，故需確定性 Python code。約束見 proposal「範圍評估」：純 pandas、不重寫評分、單檔 MVP、資料經 twstock-module。

## Goals / Non-Goals

**Goals:** 單檔 long-only 回測、忠實台股成本、無 look-ahead、核心績效指標、L3 報告。
**Non-Goals:** 多檔投組、完整三面向評分回測、快取、參數優化/walk-forward、放空。

## Decisions

- **向量化 pandas，不用回測框架**（階梯 4）。
- **執行時序（防 look-ahead）**：`position = signal.shift(1)`——第 T 日收盤訊號決定第 T+1 日起持倉；報酬以 **close-to-close** 計（持倉日 `close[t]/close[t-1]`）。訊號只用 rolling 過去窗，`shift(1)` 確保決策資料嚴格早於報酬期，天然無未來資訊。
- **成本模型**：買 `max(成交額×0.1425%, 20)`；賣 `max(成交額×0.1425%, 20) + 成交額×0.3%`。參數不硬編碼，集中一處常數並註明引用 tw-market-rules.md（該檔為魔術數字真相來源；引擎以具名常數對應）。
- **參考訊號（可插拔）**：均線多頭排列 `5MA>20MA>60MA` 為在場、否則空手。訊號函式簽名固定，未來可換其他訊號。
- **MDD**：權益曲線 `cummax` 回撤取最小。**年化**：`(1+總報酬)^(252/交易日數)-1`。**勝率**：獲利平倉筆數 / 總平倉筆數。
- **fail-open**：twstock-module 回 data_gaps／空 → 不 crash，結果標註、回報無法回測。

## Risks / Trade-offs

- [look-ahead bias（回測頭號 bug）] → `position=signal.shift(1)` + T+1 open 成交 + 訊號只用 rolling 過去窗；並以 workflow 對抗式驗證
- [成本雙重計算或漏算] → 成本只在部位變動日（買/賣）套用一次，selftest 斷言成本方向與量級
- [單檔非投組，代表性有限] → 明列 MVP，引擎可延伸投組（future）
- [252 交易日年化假設] → 台股約 240-250 日；用實際交易日數年化，非寫死 252（用資料實際 bar 數）

## Migration Plan
- 新增 backtest.py + SKILL.md；無既有行為變更
## Open Questions
- 無（MVP 範圍已定）。
