## Why

專案已有「選股」入口（screening），但缺「持股健檢」——使用者手上已有的股票是否該續抱、有沒有警訊，目前無場景可回答。v0.3 建 L3 場景 `twstock-reviewing-portfolio`：輸入持股清單 → 委派 twstock-module → 掃法人動向與財報／籌碼警訊 → 輸出健檢看板。

## What Changes

- 新增 `twstock-reviewing-portfolio/SKILL.md`（L3 企業場景，編排型）
- 編排：解析使用者持股清單 → **委派 twstock-module 取得資料**（SHALL NOT 直接碰 API）→ 掃描警訊 → 輸出健檢看板
- 健檢看板（每檔持股）固定格式：**健康燈號（綠/黃/紅）｜警訊清單｜建議行動（續抱/留意/減碼）｜核心理由(≤3)｜風險提示｜data_gaps**
- 警訊偵測沿用 `scoring-model.md` 指標與 `tw-market-rules.md`（法人連續賣超、融資大增、EPS/月營收轉弱、觸及處置股/漲跌停）
- long-only 持有語意：建議為續抱/留意/減碼（非做空）；每檔附免責、data_gaps 非空明示

**Out of scope**：自動下單、回測（v1.0）、做空、新指標（沿用 scoring-model）。

## Capabilities

### New Capabilities
- `twstock-portfolio-review`: L3 持股健檢編排——解析持股、委派 twstock-module、掃財報與籌碼警訊、輸出健檢看板（燈號+警訊+建議行動），落實免責與 data_gaps 誠實揭露。

## Impact

- **新增檔案**：`twstock-reviewing-portfolio/SKILL.md`
- **無 code、無新增依賴**（L3 由 Claude 本體編排，取數委派 L2）
- **依賴**：`twstock-data-fetching`（取數）、`scoring-model.md`（警訊指標）、`tw-market-rules.md`（處置/漲跌停）
- **紅線關聯**：委派非直呼（#2）、免責（#3）、data_gaps 明示（#5）
