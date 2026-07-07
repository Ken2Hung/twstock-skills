## Context

本 change 只建 `references/` 知識文件，無程式碼、無依賴。之所以仍寫 design，是要定調三份文件的邊界與「成本單一來源」規則，避免 apply 時把 v0.2 的策略內容提前堆進骨架。約束見 `openspec/project.md`（Ponytail full mode）。

## Goals / Non-Goals

**Goals:**
- 交易成本／漲跌停／處置股／市場別集中於 `tw-market-rules.md`，成為下游損益的單一真相來源
- cheatsheet 與 `twstock-module` 已實作的 6 資料集一致（不憑空列端點）
- preset 只給空骨架，模板欄位一致

**Non-Goals:**
- preset 實際策略邏輯、門檻值（v0.2）
- 回測引擎、成本計算程式碼（v1.0）
- 把 CLAUDE.md 既有內容整包搬進 references（只萃取下游會引用的部分）

## Decisions

- **cheatsheet 對齊實作而非官方全集**：只列本專案 6 資料集，方法名以 `finmind_fetcher.py` 為準，避免文件與碼漂移。
- **preset 空骨架**：五個 preset 只給一致模板欄位（名稱／面向權重／門檻／所需資料集），不填值——Ponytail 階梯 1，spec 未要求 v0.2 內容存在。
- **成本單一來源**：成本數字只寫在 `tw-market-rules.md`；下游 SHALL 引用，禁止散落。此規則是 spec requirement，不是實作細節。
- **採保守基準 + 現實性註記**：成本以牌告費率為保守基準（不臆測各券商折扣），並以知識備註標明折扣、手續費低消 20 元、當沖證交稅減半為時限制度「使用前查證」——註記不寫死可變政策，非 spec requirement。

## Risks / Trade-offs

- [文件與實作漂移（cheatsheet／成本數字）] → cheatsheet scenario 綁定「與 finmind_fetcher.py 一致」；未來改動走 change 流程同步
- [preset 空骨架被誤當成已完成] → 每個 preset 明確標註「v0.2 待填」

## Migration Plan

- 新增三檔，移除 `references/.gitkeep`；無既有行為變更、無 rollback 風險

## Open Questions

- 無。preset 內容延後至 v0.2 已為共識。
