## Context

`add-shareholding-dataset` 分支自 Change 4 之前，merge 後 dataset 已在 module，但 `scoring-model.md`／`CLAUDE.md` 未整合、仍標 v-next。本 change 收攏此分岔漂移，把股權分散納入評分籌碼面。無 code 變更（fetcher 已含 shareholding；評分由 Claude 本體依 scoring-model.md 執行）。

## Goals / Non-Goals

**Goals:** 籌碼面納入股權分散、清除 stale v-next、文件與 spec 一致。
**Non-Goals:** 股權分散趨勢評分（v-next，需歷史快照）、融資結合股價位置修正（另一 v-next）。

## Decisions

- **籌碼面三分 50/30/20**（法人/融資融券/股權分散）：由原 60/40 調整；股權分散 20% 反映其為慢訊號但具籌碼集中度指標性。此為經驗起始值，**v1.0 回測校準**。
- **股權分散用 snapshot level 非趨勢**：TDCC `id=1-5` 僅最新週快照、無歷史，無法算趨勢。v1.0 以**分級 15（大戶）占集保比例之產業內百分位**評分（與基本面百分位一致的正規化），大戶持股高→正向。趨勢待歷史來源（v-next）。
- **清 stale**：`scoring-model.md:17,45` 與 `CLAUDE.md:86` 移除「股權分散 v-next」；保留 `scoring-model.md:44`（融資結合股價位置，另一個仍有效的 v-next）。

## Risks / Trade-offs

- [50/30/20 為經驗值] → 集中 scoring-model.md 單一來源，回測後可調
- [snapshot level 無法反映大戶增減動向] → 明列 v-next；v1.0 以水位百分位替代，honest 標註

## Migration Plan

- 改 3 份文件 + MODIFIED twstock-scoring R2；無 code、無 rollback 風險

## Open Questions
- 無（50/30/20 與 snapshot-level 為本 change 決策，回測後再調）。
