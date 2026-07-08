## MODIFIED Requirements

### Requirement: 策略 preset 骨架

`strategy-presets.md` SHALL 定義五個策略 preset：動能、價值、成長、高股息、法人籌碼。每個 preset MUST 含：面向權重覆寫（基本面／技術面／籌碼面，加總 100%）、3~5 個強調指標（含對應 twstock-module dataset 與方向語意）、所需 dataset、一句 rationale。強調指標之算法定義 SHALL 以 `scoring-model.md` 為準（preset SHALL NOT 另定義指標細節）；強調指標為 soft 連續評分，SHALL NOT 為硬門檻。

#### Scenario: 五 preset 皆完整定義

- **WHEN** 檢視 `strategy-presets.md`
- **THEN** MUST 含動能／價值／成長／高股息／法人籌碼五 preset，每個具面向權重（加總 100）、強調指標（含 dataset 與方向）、所需 dataset

#### Scenario: 指標引用 scoring-model 不另定義

- **WHEN** preset 指定某強調指標
- **THEN** 指標算法 MUST 引用 `scoring-model.md`，SHALL NOT 於 preset 內重新定義指標細節
