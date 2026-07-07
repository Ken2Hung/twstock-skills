## MODIFIED Requirements

### Requirement: FinMind→yfinance 日K降級鏈

模組 SHALL 以 FinMind 為主資料源。**僅日K** SHALL 可於 FinMind 失效時降級至 yfinance；當 FinMind 回應 402、429 或逾時，模組 SHALL 改由 yfinance 取日K，並在輸出標註 `source: "yfinance"` 與延遲報價警示。PER/PBR、三大法人、融資融券、月營收、財報三表 SHALL NOT 降級——取不到時 MUST 直接將對應欄位列入 `data_gaps`。

股權分散（`shareholding`）SHALL 取自 TDCC 官方開放資料（非 FinMind 端點，免費），SHALL NOT 走 FinMind→yfinance 降級鏈；其取數失敗（網路／格式錯誤）或查無證券時 MUST fail-open：將缺漏列入 `data_gaps`、`source` 標為 `none`，主鏈路不中斷、SHALL NOT 讓例外中斷腳本。

#### Scenario: 日K 降級成功
- **GIVEN** FinMind 對日K請求回 429
- **WHEN** 模組執行降級
- **THEN** 改用 yfinance 取得日K，`source` MUST 為 `"yfinance"`，並在輸出標註「台股報價延遲約 20 分鐘」

#### Scenario: 籌碼面資料不降級
- **GIVEN** FinMind 對三大法人買賣超請求逾時
- **WHEN** 模組處理該失敗
- **THEN** SHALL NOT 嘗試 yfinance；三大法人相關欄位 MUST 列入 `data_gaps`，主鏈路不中斷（fail-open）

#### Scenario: 股權分散 TDCC 取數失敗時 fail-open
- **GIVEN** TDCC 開放資料取數失敗或查無證券
- **WHEN** 模組處理該失敗
- **THEN** 模組 MUST NOT crash；SHALL NOT 走 yfinance 降級；缺漏 MUST 列入 `data_gaps`、`source` 標為 `none`，主鏈路不中斷
