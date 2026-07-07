## ADDED Requirements

### Requirement: FinMind→yfinance 日K降級鏈

模組 SHALL 以 FinMind 為主資料源。**僅日K** SHALL 可於 FinMind 失效時降級至 yfinance；當 FinMind 回應 402、429 或逾時，模組 SHALL 改由 yfinance 取日K，並在輸出標註 `source: "yfinance"` 與延遲報價警示。PER/PBR、三大法人、融資融券、月營收、財報三表 SHALL NOT 降級——取不到時 MUST 直接將對應欄位列入 `data_gaps`。

#### Scenario: 日K 降級成功
- **GIVEN** FinMind 對日K請求回 429
- **WHEN** 模組執行降級
- **THEN** 改用 yfinance 取得日K，`source` MUST 為 `"yfinance"`，並在輸出標註「台股報價延遲約 20 分鐘」

#### Scenario: 籌碼面資料不降級
- **GIVEN** FinMind 對三大法人買賣超請求逾時
- **WHEN** 模組處理該失敗
- **THEN** SHALL NOT 嘗試 yfinance；三大法人相關欄位 MUST 列入 `data_gaps`，主鏈路不中斷（fail-open）

### Requirement: Token-aware rate limit 節流

模組 SHALL 僅從環境變數 `FINMIND_TOKEN` 讀取 token；SHALL NOT 於任何原始碼、腳本或設定檔寫死憑證。無 token 時上限 SHALL 視為 300 req/hr；有 token 時 SHALL 視為 600 req/hr。請求之間 SHALL 以 `time.sleep` 節流以避免觸發封鎖。token MUST NOT 出現在任何回傳 JSON、log 或存檔輸出；任何驗證輸出存檔前 MUST 先確認內容不含 token（紅線 #4）。

#### Scenario: 無 token 節流
- **GIVEN** 環境無 `FINMIND_TOKEN`
- **WHEN** 連續發出多筆請求
- **THEN** 相鄰請求間 MUST 以 `time.sleep` 間隔，節流節奏對應 300 req/hr 上限

#### Scenario: 有 token 提升上限
- **GIVEN** 環境有有效 `FINMIND_TOKEN`
- **WHEN** 初始化取得器
- **THEN** rate limit 上限 SHALL 套用 600 req/hr

#### Scenario: 憑證不外洩
- **GIVEN** 取得器已載入 `FINMIND_TOKEN`
- **WHEN** 產生任何回傳 JSON、log 或驗證存檔
- **THEN** 輸出內容 MUST NOT 含 token 字串；腳本本身 MUST NOT 內嵌任何憑證
