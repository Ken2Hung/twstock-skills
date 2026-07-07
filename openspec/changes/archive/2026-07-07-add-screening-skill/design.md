## Context

首個 L3 企業場景。核心風險是分層鐵律（紅線 #2）：場景不得直接碰資料源 API，必須委派 `twstock-module`。本 change 只建 `SKILL.md`（Claude 本體執行的編排指示），無程式碼。約束見 `openspec/project.md`。

## Goals / Non-Goals

**Goals:**
- 把 NL 選股條件編排成「委派取資料 → 篩選 → 決策看板」，邊界可測
- 決策看板七欄位固定、格式穩定
- 免責聲明與 `data_gaps` 誠實揭露內建

**Non-Goals:**
- 評分各面向指標定義與門檻（Change 4）；本 change 權重用 30/30/40 佔位、不定義指標算法
- 目標價／止損價的實際計算方式（Change 4）。本 change 只要求「引用 tw-market-reference 單一成本來源、禁硬編碼」。**特記**：`止損價 ≤ 現價 ≤ 目標價` 不等式已刻意移出 spec——它隱含 **long-only** 假設，賣出（做空/減碼）信號下方向反轉，止損在上、目標在下。此方向性語意屬策略決策，留待 Change 4 explore 一併裁決，勿在此提前寫死。
- 回測、preset 策略邏輯（v0.2）
- 任何取數程式碼（一律委派 L2）

## Decisions

- **委派而非直呼**：所有資料需求 SHALL 經 `twstock-module` 的 dataset key 取得；SKILL.md 明列「禁止直接呼叫 FinMind/yfinance」。這是紅線 #2，不是風格選擇。
- **看板七欄位固定**：評分/信號/目標價/止損價/理由(≤3)/風險/data_gaps；目標價與止損價的損益基準 SHALL 引用 `tw-market-reference`（交易成本），不另定魔術數字。
- **權重佔位**：基本面 30 / 技術面 30 / 籌碼面 40 僅作佔位；指標細節不在本 change（避免與 Change 4 重工，Ponytail 階梯 1）。
- **SKILL.md 為編排指示、非程式碼**：L3 由 Claude 本體執行，故 SKILL.md 用結構化指示描述流程與輸出契約，不含 Python。

## Risks / Trade-offs

- [場景不慎自行取數（破壞分層）] → spec 以 scenario 鎖死「需要某資料 THEN 呼叫 twstock-module 而非 API」，SKILL.md 明列禁令
- [看板欄位漂移] → 固定七欄位寫進 spec requirement，並附範例；缺欄即違規
- [權重佔位被誤當定案] → SKILL.md 與 spec 標註「30/30/40 為佔位，指標定義見 Change 4」

## Migration Plan

- 新增 `SKILL.md`；無既有行為變更、無 rollback 風險（尚無下游依賴此場景）

## Open Questions

- 無阻斷項。指標細節、preset 內容已明確延後。
