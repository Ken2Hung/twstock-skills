## ADDED Requirements

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
