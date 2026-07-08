## ADDED Requirements

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
