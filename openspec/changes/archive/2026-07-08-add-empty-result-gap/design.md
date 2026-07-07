## Context

關閉 ponytail debt #3：`finmind_fetcher.py` 對成功但 0 筆的資料集不標 data_gaps，下游無法分辨無資料 vs 無變化（實測 `balance_sheet` 回 0 筆）。小範圍修正，仍寫 design 以定調「整體 0 筆 vs 個別欄位空」的界線。

## Goals / Non-Goals

**Goals:**
- 整體 0 筆的資料集／單表 → data_gaps 誠實標註
- 關閉 ponytail #3

**Non-Goals:**
- per-field 空值標註（維持現狀，避免「某日無融資券」噪音）
- 興櫃訊息（債務 #2，併股權分散 change）

## Decisions

- **只標整體 0 筆**：偵測 `len(records) == 0`（list 型）或財報單表 0 筆（dict 型逐表）。個別欄位缺值不標，避免噪音——這正是原 ponytail 註記顧慮的誤報。
- **不動 source**：查詢成功者 source 仍為實際來源；空結果是「有效但無資料」，非取數失敗。
- **實作落點**：`fetch` 的組裝路徑（`_records` 之後、`_assemble` 之前）統一偵測，形狀契約不變。

## Risks / Trade-offs

- [與 task_1ea7f266（股權分散）改同檔衝突] → 兩者 apply 不同時進行；本 change 只碰 `fetch`/組裝，股權分散碰 dataset 註冊，區塊不同、衝突面小
- [「無變化」誤判為「無資料」] → 標註文字用「空結果(0 筆)」中性描述，不斷言原因；下游自行判讀

## Migration Plan

- 改 `finmind_fetcher.py` 組裝邏輯 + 移除 :155 ponytail 註記；更新 selftest 涵蓋空結果標註
- Rollback：還原該段即可，形狀契約不變

## Open Questions

- 無。
