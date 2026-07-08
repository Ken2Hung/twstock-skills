# twstock-portfolio-review

## Purpose

L3 持股健檢場景 twstock-reviewing-portfolio 的行為契約：解析使用者持股清單、委派 L2
twstock-module 取得資料（場景層絕不直接碰資料源 API）、掃描財報與籌碼警訊、輸出固定六欄位
健檢看板（健康燈號/警訊/建議行動），落實免責與 data_gaps 誠實揭露。警訊指標與市場規則一律引用
scoring-model.md 與 tw-market-rules.md。v1.0 long-only 持有語意。

## Requirements

### Requirement: 持股健檢編排委派模組取數

L3 場景 twstock-reviewing-portfolio SHALL 執行編排：解析使用者持股清單、委派 L2 twstock-module 取得每檔所需資料、掃描警訊、輸出健檢看板。凡本場景所需之任何資料，一律 MUST 委派 twstock-module 取得，場景 SHALL NOT 直接呼叫或撰寫任何取數邏輯（FinMind、yfinance、TWSE、TPEx 及任何未來資料源 API）。

#### Scenario: 端到端健檢一次持股清單

- **GIVEN** 使用者提供一份持股清單（一至多檔）
- **WHEN** 場景接收該請求
- **THEN** 場景 MUST 依序完成「解析持股 → 委派 twstock-module 取數 → 掃描警訊 → 輸出健檢看板」
- **AND** 場景 MUST NOT 於任一階段自行呼叫任何資料源 API 或撰寫取數邏輯

#### Scenario: 需要任何資料一律委派

- **GIVEN** 健檢某檔持股需要法人／財報／籌碼資料
- **WHEN** 場景需要取得該資料
- **THEN** 場景 MUST 委派 twstock-module（twstock-data-fetching）取得
- **AND** 場景 SHALL NOT 直接呼叫任何現有／未來的資料源 API

### Requirement: 健檢看板輸出契約

場景對每一檔持股的輸出 MUST 遵循固定健檢看板契約，六個欄位 SHALL 全數齊備、順序固定：

1. **健康燈號**：列舉值，MUST 為「綠」「黃」「紅」三者之一
2. **警訊清單**：條列，無警訊時 MUST 明示「無重大警訊」，SHALL NOT 省略此欄
3. **建議行動**：列舉值，MUST 為「續抱」「留意」「減碼」三者之一（long-only 持有語意，非做空）
4. **核心理由**：條列，MUST 為 1 至 3 點
5. **風險提示**：非空文字
6. **data_gaps**：陣列，忠實反映模組回傳之資料缺口，MUST NOT 省略或偽裝為空

任一欄位缺漏、燈號或建議行動超出列舉集合，該輸出 MUST 視為不合規。

#### Scenario: 六欄位齊備且列舉合規

- **GIVEN** 一檔待健檢的持股
- **WHEN** 場景輸出該持股健檢看板
- **THEN** 看板 MUST 依序含健康燈號、警訊清單、建議行動、核心理由、風險提示、data_gaps 全部六欄位
- **AND** 燈號 MUST 屬「綠／黃／紅」、建議行動 MUST 屬「續抱／留意／減碼」

#### Scenario: 建議行動為 long-only 持有語意

- **GIVEN** 某持股健康惡化
- **WHEN** 場景給出建議行動
- **THEN** MUST 為「續抱／留意／減碼」之一，SHALL NOT 出現做空／放空語意

### Requirement: 財報與籌碼警訊偵測

警訊偵測 SHALL 沿用 scoring-model.md 的指標與 tw-market-rules.md 的市場規則，至少涵蓋：三大法人連續賣超、融資餘額大增、EPS／月營收轉弱、標的觸及漲跌停（±10%）或列入 TWSE 處置名單。場景 SHALL NOT 於場景層重新定義指標算法或硬編碼交易成本／處置規則，一律引用既有真相來源。

#### Scenario: 法人連續賣超觸發警訊

- **GIVEN** 某持股外資或投信於 scoring-model.md 定義之回看窗口內連續淨賣超
- **WHEN** 掃描警訊
- **THEN** 警訊清單 MUST 列出該法人賣超警訊，並反映於健康燈號

#### Scenario: 處置股／漲跌停標註風險

- **GIVEN** 某持股列入 TWSE 處置名單或觸及 ±10% 漲跌停
- **WHEN** 輸出健檢看板
- **THEN** 風險提示 MUST 依 tw-market-rules.md 標註流動性風險

#### Scenario: 警訊指標引用真相來源

- **WHEN** 場景判定任一警訊
- **THEN** 指標算法 MUST 引用 scoring-model.md、成本／處置規則 MUST 引用 tw-market-rules.md
- **AND** SHALL NOT 於場景層另定義指標或硬編碼參數

### Requirement: data_gaps 明示與免責聲明

當某持股的 data_gaps 非空時，該持股健檢看板 SHALL 明示「以下健檢基於不完整資料」；為空則不加此警語。場景 SHALL NOT 以舊資料或推估值填補缺漏。場景對每一檔持股的輸出 SHALL 附投資免責聲明，SHALL NOT 輸出「保證」「必漲」「穩賺」等表述。

#### Scenario: data_gaps 非空明示

- **GIVEN** twstock-module 回傳某持股 data_gaps 非空
- **WHEN** 輸出健檢看板
- **THEN** 看板 MUST 明示「以下健檢基於不完整資料」
- **AND** SHALL NOT 以推估值或過期資料填補缺口

#### Scenario: 每檔持股附免責

- **GIVEN** 場景輸出一或多檔持股健檢
- **WHEN** 呈現任一持股看板
- **THEN** 該持股 MUST 附投資免責聲明，且 MUST NOT 含保證獲利類表述

### Requirement: 持股健檢觸發語涵蓋

twstock-reviewing-portfolio 的 SKILL.md description MUST 含足以路由持股健檢意圖的自然語言觸發語，SHALL 至少涵蓋：「幫我健檢持股…」、「我手上的 X 還能抱嗎」、「檢查我的持股有沒有警訊」。這些觸發語 MUST 路由至健檢場景，而非選股場景或 L2 模組。

#### Scenario: 健檢類觸發語命中

- **GIVEN** 使用者輸入「幫我健檢持股 2330、2454」
- **WHEN** 意圖路由比對 SKILL.md description
- **THEN** 該請求 MUST 命中 twstock-reviewing-portfolio 場景
- **AND** MUST NOT 被路由至 twstock-screening-stocks 或 twstock-module

#### Scenario: 個股續抱詢問命中

- **GIVEN** 使用者輸入「我手上的 2317 還能抱嗎」
- **WHEN** 意圖路由比對 SKILL.md description
- **THEN** 該請求 MUST 命中 twstock-reviewing-portfolio 場景
