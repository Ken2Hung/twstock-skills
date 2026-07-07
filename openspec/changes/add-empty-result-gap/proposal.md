## Why

`finmind_fetcher.py` 目前對「查詢成功但回傳 0 筆」的資料集，記為 `data:[]` 且 `data_gaps` 為空——下游無法分辨「查無資料／不可得」與「查有資料但無變化」。實測已見 `financial` 的 `balance_sheet` 回 0 筆卻無任何標註（ponytail debt #3）。這觸及紅線 #5 的誠實原則：空結果應誠實揭露，而非看似完整。

## What Changes

- `twstock-module`：當任一資料集（或財報三表之單表）在請求區間查詢**成功但回傳 0 筆**時，於 `data_gaps` 標註該資料集為空（如 `financial.balance_sheet: 空結果(0 筆)`）
- 標註**僅針對整體 0 筆**，不對「有資料但個別欄位缺值」逐欄標註（避免「某日無融資券」式誤報）
- 移除 `finmind_fetcher.py:155` 的 `ponytail:` 延後註記（債務關閉）

**Out of scope**：per-field 空值標註（維持現狀，避免噪音）、興櫃訊息修正（債務 #2，另併入股權分散 change）。

## Capabilities

### New Capabilities
<!-- 無新 capability。 -->

### Modified Capabilities
- `twstock-data-fetching`: 新增「空結果誠實標註」requirement——成功但 0 筆的資料集 MUST 於 `data_gaps` 標註，使下游可分辨無資料 vs 無變化。

## Impact

- **修改**：`twstock-module/scripts/finmind_fetcher.py`（`fetch` 組裝時偵測 0 筆 → data_gaps）
- **關閉債務**：ponytail #3（`finmind_fetcher.py:155`）
- **無新增依賴**
- ⚠️ **排程注意**：本 change 的 apply 會改 `finmind_fetcher.py`；`task_1ea7f266`（股權分散）亦改同檔，兩者 apply 需避免同時進行以免衝突
