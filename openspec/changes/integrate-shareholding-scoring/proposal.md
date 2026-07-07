## Why

`add-shareholding-dataset`（已 merge）為 twstock-module 加了 `shareholding`（TDCC 集保股權分散）資料集，但因它分支自 Change 4 之前，`scoring-model.md` 尚未把股權分散納入評分——導致 `scoring-model.md` 與 `CLAUDE.md` 仍標「股權分散 v-next」，與「dataset 已存在」的事實漂移。本 change 把股權分散正式納入評分籌碼面，並清掉 stale 標記。

## What Changes

- 籌碼面 40% 內部重新配置：**三大法人 50%、融資融券 30%、集保股權分散 20%**（原 60/40 兩分 → 三分）
- 股權分散評分：以 TDCC 集保**分級 15（≥1,000,001 股，大戶）之占集保庫存比例**計，因 TDCC `id=1-5` 僅最新週快照、無歷史，v1.0 以該比例之**產業內百分位（snapshot level）**評分——大戶持股比例高（產業內）→ 正向
- **趨勢評分列 v-next**：大戶增減趨勢需歷史快照累積，TDCC id=1-5 給不了，留待有歷史來源時再做
- 清除 stale：`scoring-model.md`、`CLAUDE.md` 移除「股權分散 v-next」，改為正式納入
- `finmind-api-cheatsheet.md` 補股權分散於評分的用法（大戶=分級 15）

**Out of scope**：股權分散趨勢評分（v-next，需歷史）、融資「結合股價位置」修正（另一 v-next，不動）。

## Capabilities

### New Capabilities
<!-- 無。 -->

### Modified Capabilities
- `twstock-scoring`: 修改「籌碼面配置與指標方向語意」requirement——籌碼面 40% 由 法人60/融資40 兩分改為 法人50/融資30/股權分散20 三分，新增股權分散（大戶持股比例產業內百分位，snapshot level）之方向語意。

## Impact

- **修改**：`references/scoring-model.md`（籌碼面三分 + 股權分散指標 + 清 v-next）、`CLAUDE.md`（籌碼面段落）、`references/finmind-api-cheatsheet.md`（股權分散評分用法）
- **spec**：MODIFIED `twstock-scoring` R2
- **無 code 變更**（fetcher 已由 merge 帶入 shareholding；評分由 Claude 本體依 scoring-model.md 執行）
- **關聯**：消除 Change 4 與 add-shareholding-dataset 分岔造成的文件漂移
