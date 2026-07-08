## Context

純一致性修正：Change 4 改了「目標價與止損價」requirement 但未同步「決策看板七欄位」，造成同 capability 內矛盾（價位：淨值 vs 市場價；評分：佔位 vs scoring-model 定義）。本 change 只對齊表述，無行為變更。

## Goals / Non-Goals

**Goals:** 消除 twstock-screening-orchestration 內部矛盾。
**Non-Goals:** 任何新行為、code、文件（SKILL.md 已正確）。

## Decisions

- 以已定案者為準：目標價/止損=**市場價**（Change 4 Req3）、評分=**scoring-model 權重 + preset 覆寫**（Change 4 + v0.2）。七欄位 Req 對齊之。

## Risks / Trade-offs
- 無（純表述對齊，spec 交叉引用「目標價與止損價」與 scoring-model）。
## Migration Plan
- MODIFIED 一個 requirement；sync 後即一致。
## Open Questions
- 無。
