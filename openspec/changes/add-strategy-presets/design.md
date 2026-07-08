## Context

Change 2 建 preset 空骨架、Change 4 定指標。v0.2 填 5 preset 參數。無 code（Claude 本體依 preset + scoring-model 執行）。

## Goals / Non-Goals

**Goals:** 5 preset 各具面向權重覆寫 + 強調指標；場景能套用指名 preset。
**Non-Goals:** 回測（v1.0）、新指標、硬門檻（保持 soft 連續評分）。

## Decisions

- **preset = 面向權重覆寫 + 強調指標挑選**，不重定義指標——算法一律引用 scoring-model.md（單一真相）。
- **面向權重（多視角設計、加總 100）**：動能 20/40/40、價值 55/20/25、成長 50/30/20、高股息 55/25/20、法人籌碼 15/30/55。經驗值，**v1.0 回測校準**。
- **強調指標為 soft**：影響面向得分高低，非「未達即剔除」的 filter（硬篩選屬 L3 使用者明訂條件）。
- **TaiwanStockInfo 非取數 dataset**：僅作產業百分位分組 universe。

## Risks / Trade-offs

- [權重為經驗值] → 集中 strategy-presets.md，回測後可調
- [preset 與使用者自訂條件衝突] → preset 只調面向權重與強調；使用者明講的硬條件仍優先

## Migration Plan
- 填 strategy-presets.md + SKILL.md §7 preset 註記；MODIFIED tw-market-reference、ADDED orchestration
## Open Questions
- 無（權重回測後再調）。
