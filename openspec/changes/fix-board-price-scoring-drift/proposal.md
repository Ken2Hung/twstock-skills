## Why

Change 4（add-scoring-model）MODIFIED 了「目標價與止損價」requirement 為市場價語意、並用 scoring-model 定義了權重，但**沒同步更新同一 capability 的「決策看板七欄位」requirement**——後者仍寫「目標價/止損價 SHALL 為扣除交易成本後的淨值基準」與「30/30/40 佔位、不定義指標細節」。這與已定案的語意**自相矛盾**（同一 spec 內兩處衝突）。本 change 收攏此漂移。

## What Changes

- MODIFIED「決策看板七欄位固定輸出契約」：
  - 目標價/止損價欄位改為**市場價**（成本不入價位），與「目標價與止損價」requirement 一致
  - 綜合評分改為**依 scoring-model.md 權重（預設 30/30/40，可由 strategy-presets.md preset 覆寫）**，移除「佔位/不定義指標」的 stale 表述

**Out of scope**：無行為新增，純一致性修正。

## Capabilities

### Modified Capabilities
- `twstock-screening-orchestration`: 修正「決策看板七欄位」requirement 的目標價語意與評分權重表述，消除與 Change 4 的內部矛盾。

## Impact

- **spec only**：MODIFIED twstock-screening-orchestration；無 code、無文件（SKILL.md §6/§7 已於 Change 4 更新為正確語意）
