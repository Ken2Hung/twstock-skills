## ADDED Requirements

### Requirement: 空結果誠實標註

當任一資料集（含財報三表之單表）在請求區間查詢**成功但回傳 0 筆**時，模組 MUST 於 `data_gaps` 標註該資料集為空（例如 `financial.balance_sheet: 空結果(0 筆)`），使下游能分辨「查無資料／不可得」與「查有資料但無變化」。此標註 SHALL 僅針對**整體 0 筆**之情形，SHALL NOT 對「有資料但個別欄位缺值」逐欄標註（避免「某日無融資券」式誤報）。空結果標註 SHALL NOT 更動 `source` 欄位（查詢成功者 source 仍為實際來源）。

#### Scenario: 成功但空的資料集標入 data_gaps

- **GIVEN** `financial` 的 `balance_sheet` 查詢成功但回傳 0 筆
- **WHEN** 組裝輸出 JSON
- **THEN** `data_gaps` MUST 含該表為空之標註（如 `financial.balance_sheet: 空結果(0 筆)`）
- **AND** `source` 欄位 SHALL NOT 因此變更

#### Scenario: 有資料不誤標為空

- **GIVEN** 某資料集回傳 1 筆以上資料
- **WHEN** 組裝輸出 JSON
- **THEN** SHALL NOT 因個別欄位缺值而將整體資料集標為空結果
