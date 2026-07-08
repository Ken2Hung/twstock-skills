# twstock-backtesting

## Purpose

台股 long-only 歷史回測引擎與 L3 場景：經 twstock-module 取歷史日K、以可插拔訊號逐日模擬、
忠實套用台股交易成本（引用 tw-market-rules.md）、無 look-ahead bias（position=signal.shift(1)）、
輸出含扣成本前後對比的績效指標。v1.0 單檔 MVP；多檔投組、完整評分回測、參數優化為 future。

## Requirements

### Requirement: 歷史回測引擎（long-only 逐日重放）

引擎 SHALL 對「單檔證券 + 訊號規則 + 日期區間」進行 long-only 歷史回測：經 twstock-module 取得歷史日K，依訊號逐日模擬進出場，回傳結構化結果。歷史資料 SHALL 一律經 twstock-module 取得，引擎 SHALL NOT 直接呼叫 FinMind／yfinance／任何資料源 API。訊號 SHALL 為可插拔設計，本 change 附一個參考訊號（均線多頭排列），SHALL NOT 於引擎重寫完整三面向評分。

#### Scenario: 單檔回測輸出結構化結果
- **GIVEN** 一檔證券、日期區間與訊號規則
- **WHEN** 執行回測
- **THEN** 引擎 MUST 經 twstock-module 取歷史日K、逐日模擬 long-only 進出場，輸出含績效指標的結構化結果（JSON）
- **AND** 引擎 SHALL NOT 直接呼叫任何資料源 API

#### Scenario: 取不到資料時 fail-open
- **GIVEN** twstock-module 回傳 data_gaps 或空日K
- **WHEN** 執行回測
- **THEN** 引擎 MUST NOT crash，SHALL 於結果標註 data_gaps 並回報無法回測，SHALL NOT 以腦補資料續算

### Requirement: 台股交易成本模型

回測損益 MUST 逐筆扣除台股交易成本，參數引用 tw-market-rules.md：買進手續費 0.1425%、賣出手續費 0.1425% + 證交稅 0.3%（賣出合計 0.4425%），手續費**單筆低消 20 元**。引擎 SHALL NOT 於程式碼硬編碼另一套成本數字。回測報告 MUST 併陳**扣成本前**與**扣成本後**之報酬，使成本侵蝕可見。

#### Scenario: 每筆交易扣成本
- **GIVEN** 回測產生一筆買進與一筆賣出
- **WHEN** 計算該筆損益
- **THEN** 買進 MUST 扣 0.1425%（低消 20 元）、賣出 MUST 扣 0.4425%（低消 20 元 + 證交稅），成本參數引用 tw-market-rules.md

#### Scenario: 報告併陳扣成本前後
- **WHEN** 輸出回測績效
- **THEN** MUST 同時呈現扣成本前與扣成本後之總報酬，使成本影響可比較

### Requirement: 無 look-ahead bias

訊號 SHALL 僅使用截至當日（含）之歷史資料決定**次一交易日**之進出場動作；引擎 SHALL NOT 以當日或未來資料在同日成交，SHALL NOT 於訊號計算中引用未來 K 棒。

#### Scenario: 訊號用當日資料決定次日部位
- **GIVEN** 第 T 日收盤產生進場訊號
- **WHEN** 引擎決定持倉
- **THEN** 部位 MUST 於第 T+1 日起生效（以 `position = signal.shift(1)` 實作、close-to-close 計酬），SHALL NOT 於第 T 日或更早以該訊號成交

#### Scenario: 訊號計算不引用未來 K 棒
- **WHEN** 計算第 T 日之訊號
- **THEN** 僅 MUST 使用第 T 日及之前的 K 棒，SHALL NOT 引用第 T+1 日（含）之後任何資料

### Requirement: 回測績效指標

回測結果 MUST 含以下指標：總報酬率、年化報酬率、最大回撤（MDD）、勝率、交易次數，以及扣成本前後對比。指標計算 SHALL 為確定性（相同輸入得相同輸出）。

#### Scenario: 指標齊備
- **WHEN** 輸出回測結果
- **THEN** MUST 含總報酬率、年化報酬率、最大回撤、勝率、交易次數、扣成本前後對比

### Requirement: 回測報告與免責（L3 場景）

L3 場景 twstock-backtesting SHALL 以 SKILL.md 呈現回測報告，委派引擎執行、不自行碰 API。報告 SHALL 附投資免責聲明，SHALL NOT 輸出「保證」「必賺」等表述；data_gaps 非空時 SHALL 明示回測基於不完整資料。

#### Scenario: 回測報告附免責與 data_gaps 揭露
- **GIVEN** 一次回測完成
- **WHEN** 場景呈現回測報告
- **THEN** MUST 附投資免責聲明；若 data_gaps 非空 MUST 明示「回測基於不完整資料」
- **AND** MUST NOT 含「保證獲利／必賺」等表述

### Requirement: 多檔投組回測（等權固定 sleeve）

引擎 SHALL 支援多檔等權投組回測：資本均分給可回測之 N 檔（每檔 sleeve = `capital / N`），每檔獨立以單檔訊號模擬其權益曲線，再按**日期對齊**（union 日期、ffill）加總為投組權益曲線。每檔 sleeve SHALL 沿用單檔之台股交易成本與無 look-ahead 保證（`position = signal.shift(1)`）。取不到或資料不足之個股 SHALL 排除於 sleeve 分母並列入 `data_gaps`，SHALL NOT 以腦補資料補足；某檔於其首個交易日之前 SHALL 視為現金（不產生報酬）。投組結果 MUST 含：總報酬（淨/毛）、成本侵蝕、年化報酬、最大回撤、勝率、總交易次數、納入檔數。

#### Scenario: 等權投組回測輸出投組指標
- **GIVEN** N 檔可回測證券、期間與訊號規則
- **WHEN** 執行投組回測
- **THEN** 資本 MUST 均分為 `capital/N` 之 sleeve，各檔獨立模擬、按日期對齊加總為投組權益曲線
- **AND** 輸出 MUST 含總報酬（淨/毛）、成本侵蝕、年化、最大回撤、勝率、總交易次數、納入檔數

#### Scenario: 個股取不到時排除並誠實標註
- **GIVEN** 投組中某檔資料不足或取不到
- **WHEN** 執行投組回測
- **THEN** 該檔 MUST 排除於 sleeve 分母（不佔資本）、列入 `data_gaps`，SHALL NOT 以腦補資料補足
- **AND** 其餘可回測個股 MUST 照常納入投組

#### Scenario: 沿用成本與無 look-ahead
- **WHEN** 各 sleeve 模擬
- **THEN** MUST 沿用單檔之 `position = signal.shift(1)`（無 look-ahead）與台股交易成本，SHALL NOT 於投組層另編成本或引入未來資訊
