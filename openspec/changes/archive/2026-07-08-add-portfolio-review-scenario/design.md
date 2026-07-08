## Context

第二個 L3 場景，模式鏡射 twstock-screening-orchestration（委派、看板、免責、data_gaps 已驗證）。差異：對象是**既有持股**，故輸出健檢看板（燈號/警訊/建議行動）而非選股決策看板。無 code。

## Goals / Non-Goals

**Goals:** 持股健檢編排、健檢看板六欄位、警訊沿用既有指標、long-only 持有語意。
**Non-Goals:** 自動下單、回測（v1.0）、做空、新指標／新成本（一律引用 scoring-model.md / tw-market-rules.md）。

## Decisions

- **健檢看板 vs 決策看板**：健檢用「燈號綠/黃/紅 + 建議行動 續抱/留意/減碼」，貼合「已持有、該不該續抱」的語意；不用 screening 的買進/賣出信號與目標/止損價（那是選股語意）。
- **警訊全部引用真相來源**：法人賣超/融資/EPS/營收警訊算法 → scoring-model.md；處置股/漲跌停 → tw-market-rules.md。場景零重定義、零硬編碼。
- **long-only 持有語意**：建議行動不含放空；減碼=退出，非做空。
- **SKILL.md 為編排指示、非 code**：與 screening 一致。

## Risks / Trade-offs

- [與 screening 場景觸發語混淆] → 觸發語聚焦「健檢/持股/還能抱嗎」，spec scenario 明訂路由至 review 而非 screening
- [健檢與選股共用指標但語意不同] → 指標算法共用 scoring-model，但輸出語意（燈號/建議）由本場景定義

## Migration Plan
- 新增 twstock-reviewing-portfolio/SKILL.md；新 capability twstock-portfolio-review；無 rollback 風險
## Open Questions
- 無。
