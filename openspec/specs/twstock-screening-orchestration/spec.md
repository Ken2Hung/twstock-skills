# twstock-screening-orchestration

## Purpose

L3 選股編排場景 twstock-screening-stocks 的行為契約：解析自然語言選股條件、委派 L2
twstock-module 取得資料（場景層絕不直接碰資料源 API）、套用篩選、輸出固定七欄位決策看板，
並落實免責聲明與 data_gaps 誠實揭露。評分權重採 30/30/40 佔位，指標細節與價位算法留待後續 change。

## Requirements

### Requirement: 選股編排流程委派模組取數

L3 場景 twstock-screening-stocks SHALL 執行完整編排流程：解析使用者以自然語言表達的選股條件、委派 L2 業務模組 twstock-module 取得所需資料、對回傳資料套用篩選邏輯、最後輸出決策看板。凡本場景所需之任何資料，一律 MUST 委派 twstock-module 取得（capability twstock-data-fetching），場景 SHALL NOT 直接呼叫或撰寫任何取數邏輯，包含 FinMind、yfinance、TWSE、TPEx 及任何未來新增之資料源 API。此委派邊界以 catch-all 表述，不逐一列舉 dataset，以免與 twstock-data-fetching 產生維護耦合。

#### Scenario: 端到端編排一次選股請求

- **GIVEN** 使用者輸入一段自然語言選股條件
- **WHEN** 場景接收該請求
- **THEN** 場景 MUST 依序完成「解析條件 → 委派 twstock-module 取數 → 套用篩選 → 輸出決策看板」四階段
- **AND** 場景 MUST NOT 於任一階段自行呼叫 FinMind／yfinance／TWSE／TPEx 或撰寫任何取數邏輯

#### Scenario: 需要任何資料一律委派 twstock-module（catch-all）

- **GIVEN** 場景在編排任一階段需要任何台股資料
- **WHEN** 場景需要取得該資料
- **THEN** 場景 MUST 委派 twstock-module（twstock-data-fetching）取得
- **AND** 場景 SHALL NOT 直接呼叫 FinMind、yfinance、TWSE、TPEx 或任何現有／未來的資料源 API，亦不自行撰寫取數邏輯

#### Scenario: 需要日K資料時委派而非直呼 API（代表例）

- **GIVEN** 篩選條件需要日K（daily）價量資料以計算技術面
- **WHEN** 場景需要取得日K資料
- **THEN** 場景 MUST 呼叫 twstock-module 的 daily 資料集
- **AND** 場景 MUST NOT 直接呼叫 FinMind、yfinance 或任何資料源 API 取得日K資料

#### Scenario: 多類需求全數委派後才進入篩選

- **GIVEN** 使用者條件同時涉及基本面、技術面、籌碼面
- **WHEN** 場景解析出多類資料需求
- **THEN** 場景 MUST 全數委派 twstock-module 取得對應資料
- **AND** 場景 MUST 僅在所有委派回傳結構化 JSON 後才進入篩選與評分階段

### Requirement: 決策看板七欄位固定輸出契約

場景層每檔通過篩選之標的的輸出 MUST 遵循固定決策看板契約，七個欄位 SHALL 全數齊備、順序固定、可驗證，依序為：

1. **評分**：整數，範圍 0-100（含端點 0 與 100）
2. **信號**：列舉值，MUST 為「買進」「持有」「觀望」「賣出」四者之一
3. **目標價**：數值（新台幣元，**市場價**，供觸價判定）——交易成本不扣入價位，語意詳見「目標價與止損價引用交易成本真相來源」requirement
4. **止損價**：數值（新台幣元，**市場價**）——同目標價，成本不入價位
5. **核心理由**：條列，MUST 為 1 至 3 點
6. **風險提示**：非空文字
7. **data_gaps**：陣列，忠實反映模組回傳之資料缺口，MUST NOT 省略或偽裝為空

綜合評分 SHALL 依 `scoring-model.md` 定義之面向權重加權（預設基本面 30% × 技術面 30% × 籌碼面 40%，並可由 `strategy-presets.md` 之指名 preset 覆寫）；各面向指標定義以 `scoring-model.md` 為單一真相來源。任一欄位缺漏、信號超出列舉集合、評分超出 0-100、或核心理由不在 1 至 3 點範圍內，該輸出 MUST 視為不合規。

#### Scenario: 七欄位齊備且格式合規

- **GIVEN** 一檔通過使用者選股條件篩選的標的
- **WHEN** 場景輸出該標的的決策看板
- **THEN** 看板 MUST 依序包含評分、信號、目標價、止損價、核心理由、風險提示、data_gaps 全部七欄位
- **AND** 評分 MUST 為 0 至 100（含端點）的整數、信號 MUST 屬於「買進／持有／觀望／賣出」、核心理由 MUST 為 1 至 3 點、風險提示 MUST 為非空文字

#### Scenario: 信號超出列舉集合視為不合規

- **GIVEN** 場景準備輸出某標的的信號欄位
- **WHEN** 信號值不屬於「買進」「持有」「觀望」「賣出」
- **THEN** 該輸出 MUST 視為不合規
- **AND** 場景 SHALL NOT 產出該看板

#### Scenario: 評分採 scoring-model 權重，preset 可覆寫

- **GIVEN** 場景計算某標的的綜合評分
- **WHEN** 加權基本面、技術面、籌碼面三個面向
- **THEN** 綜合評分 MUST 依 `scoring-model.md` 之權重（預設 30/30/40；使用者指名 preset 時採其覆寫）
- **AND** 各面向指標定義 MUST 引用 `scoring-model.md`，SHALL NOT 於本場景另定義

### Requirement: 目標價與止損價引用交易成本真相來源

目標價與止損價 MUST 以**市場價**（新台幣元）呈現，供觸價判定使用；交易成本 SHALL NOT 扣入價位數字本身。**預期報酬率**（期望損益）之計算 MUST 引用 tw-market-reference（twstock-screening-stocks/references/tw-market-rules.md）之來回交易成本（買 0.1425% + 賣 0.4425%）扣除，場景層 SHALL NOT 硬編碼另一套交易成本數字。在 v1.0 **long-only 假設**下（信號「賣出／觀望」= 不建議買進／退出已持有，非做空），價位 SHALL 滿足 止損價 ≤ 現價 ≤ 目標價；做空／減碼之方向反轉語意列為 future scope（脈絡見已歸檔的 add-screening-skill design.md）。標的若觸及漲跌停（±10%）或位於 TWSE 處置名單，場景 MUST 依 tw-market-reference 於風險提示欄位標註流動性風險。

#### Scenario: 價位以市場價呈現、成本不入價位

- **GIVEN** 場景輸出某標的的目標價與止損價
- **WHEN** 呈現這兩個價位
- **THEN** 兩者 MUST 為市場價（新台幣元），供觸價判定使用
- **AND** 交易成本 SHALL NOT 扣入價位數字本身

#### Scenario: 預期報酬率扣除來回成本

- **GIVEN** 場景計算某標的的預期報酬率或期望損益
- **WHEN** 計算報酬
- **THEN** MUST 引用 tw-market-reference 的來回交易成本（買 0.1425% + 賣 0.4425%）扣除
- **AND** SHALL NOT 於場景層硬編碼另一套交易成本數字

#### Scenario: long-only 假設下價位不等式成立

- **GIVEN** v1.0 採 long-only（信號賣出／觀望為不建議買進／退出，非做空）
- **WHEN** 產出目標價與止損價
- **THEN** 價位 MUST 滿足 止損價 ≤ 現價 ≤ 目標價
- **AND** 做空／減碼之方向反轉語意 SHALL 列為 future scope

#### Scenario: 觸及漲跌停或處置股標註流動性風險

- **GIVEN** 某標的觸及 ±10% 漲跌停或位於 TWSE 處置名單
- **WHEN** 場景輸出該標的看板
- **THEN** 風險提示欄位 MUST 依 tw-market-reference 明確標註流動性風險

### Requirement: data_gaps 非空時明示判讀基於不完整資料

當任一標的的 data_gaps 陣列非空時，該標的的決策看板 SHALL 明示警語「以下判讀基於不完整資料」。場景層 SHALL NOT 以舊資料、推估值或任何腦補填補缺漏欄位，缺漏 SHALL 誠實保留於 data_gaps 中。當 data_gaps 為空時，看板 SHALL NOT 誤加該警語。

#### Scenario: data_gaps 非空觸發警示字樣

- **GIVEN** twstock-module 回傳某標的的 data_gaps 陣列非空（如三大法人資料缺漏）
- **WHEN** 場景輸出該標的看板
- **THEN** 看板 MUST 明示「以下判讀基於不完整資料」字樣
- **AND** 看板的 data_gaps 欄位 MUST 如實列出缺漏項
- **AND** 場景 SHALL NOT 以推估值、過期資料或任何腦補填補 data_gaps 所列缺口

#### Scenario: data_gaps 為空時不誤加警示

- **GIVEN** twstock-module 回傳某標的的 data_gaps 為空陣列
- **WHEN** 場景輸出該標的看板
- **THEN** 看板 data_gaps 欄位 MUST 誠實標示為空
- **AND** 看板 SHALL NOT 加註「以下判讀基於不完整資料」警語

### Requirement: 每檔標的附免責聲明且禁止保證獲利表述

場景層對每一檔標的的輸出 SHALL 附帶投資免責聲明，無論該標的的 data_gaps 是否為空皆須附上。場景層 SHALL NOT 輸出「保證獲利」「必漲」「穩賺」或任何等同保證報酬的表述；所有評分、信號、目標價與止損價 SHALL 僅作為參考資訊呈現，SHALL NOT 暗示或宣稱達成目標價為必然。

#### Scenario: 每檔標的皆附免責聲明

- **GIVEN** 場景輸出一檔或多檔標的的決策看板（不論 data_gaps 是否為空）
- **WHEN** 呈現任一標的看板
- **THEN** 該標的 MUST 附帶投資免責聲明
- **AND** 輸出 MUST NOT 含「保證獲利」「必漲」「穩賺」或任何等同保證報酬的表述

#### Scenario: 信號與目標價以參考資訊呈現

- **GIVEN** 某標的評為「買進」信號並附目標價
- **WHEN** 場景呈現該看板
- **THEN** 目標價與信號 MUST 以參考資訊形式呈現
- **AND** 輸出 SHALL NOT 暗示或宣稱達成該目標價為必然

### Requirement: 自然語言選股觸發語涵蓋

twstock-screening-stocks 的 SKILL.md description MUST 包含足以路由選股意圖的自然語言觸發語例句，且 SHALL 至少涵蓋以下三類講法，各自獨立可命中：「幫我篩選…」、「找出…的股票」、「用XX策略挑…」。這些觸發語 MUST 路由至選股編排場景，而非 L2 業務模組。

#### Scenario: 篩選類觸發語命中

- **GIVEN** 使用者輸入「幫我篩選近期法人買超的股票」
- **WHEN** 意圖路由比對 SKILL.md description 的觸發語
- **THEN** 該請求 MUST 命中 twstock-screening-stocks 場景
- **AND** 該請求 MUST NOT 被路由至 L2 業務模組 twstock-module

#### Scenario: 找出類觸發語命中

- **GIVEN** 使用者輸入「找出月營收年增率高的股票」
- **WHEN** 意圖路由比對 SKILL.md description 的觸發語
- **THEN** 該請求 MUST 命中 twstock-screening-stocks 場景
- **AND** 該請求 MUST NOT 被路由至 L2 業務模組 twstock-module

#### Scenario: 策略類觸發語命中

- **GIVEN** 使用者輸入「用多頭排列策略挑幾檔標的」
- **WHEN** 意圖路由比對 SKILL.md description 的觸發語
- **THEN** 該請求 MUST 命中 twstock-screening-stocks 場景
- **AND** 該請求 MUST NOT 被路由至 L2 業務模組 twstock-module

### Requirement: 策略 preset 套用

當使用者於選股請求中指名某策略 preset（如「用高股息策略挑…」），場景 SHALL 套用 `strategy-presets.md` 所定義該 preset 的面向權重覆寫與強調指標，覆寫 `scoring-model.md` 的預設 30/30/40。未指名 preset 時，場景 SHALL 採 `scoring-model.md` 預設權重，SHALL NOT 擅自套用某 preset。

#### Scenario: 指名策略套用其權重與強調指標

- **GIVEN** 使用者輸入「用法人籌碼策略挑 5 檔」
- **WHEN** 場景評分
- **THEN** MUST 套用 `strategy-presets.md` 之 institutional preset 的面向權重覆寫與強調指標

#### Scenario: 未指名策略採預設權重

- **GIVEN** 使用者未指名任何策略 preset
- **WHEN** 場景評分
- **THEN** MUST 採 `scoring-model.md` 預設 30/30/40
