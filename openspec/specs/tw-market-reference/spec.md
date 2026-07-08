# tw-market-reference

## Purpose

台股在地化規則與 FinMind 資料集的知識基準層：交易成本／漲跌停／處置股／市場別為下游損益計算的
單一真相來源，外加資料集速查與策略 preset 骨架。實體文件位於
`twstock-screening-stocks/references/`。

## Requirements

### Requirement: 交易成本與市場規則基準

`tw-market-rules.md` SHALL 定義台股在地化規則作為下游損益計算的單一真相來源，至少含：買進成本 0.1425%（手續費）、賣出成本 0.4425%（手續費 0.1425% + 證交稅 0.3%）、漲跌停 ±10%、處置股警示規則、上市（`.TW`）／上櫃（`.TWO`）市場別。所有涉及損益計算的下游能力 SHALL 引用本文件的成本參數，SHALL NOT 在程式碼中散落魔術數字。

#### Scenario: 成本與規則參數齊備
- **WHEN** 檢視 `twstock-screening-stocks/references/tw-market-rules.md`
- **THEN** MUST 含買進 0.1425%、賣出 0.4425%（明列含證交稅 0.3%）、漲跌停 ±10%、處置股警示、上市/上櫃市場別

#### Scenario: 下游引用單一成本來源
- **GIVEN** 某下游能力需計算交易損益
- **WHEN** 取用交易成本
- **THEN** SHALL 引用 `tw-market-rules.md` 的參數，SHALL NOT 於程式碼硬編碼成本數字（避免魔術數字散落）

### Requirement: FinMind 資料集速查

`finmind-api-cheatsheet.md` SHALL 提供本專案用到的 FinMind 資料集速查，涵蓋 `twstock-module` 的 6 種資料集，每項含：dataset key、對應 DataLoader 方法名、關鍵欄位、參數、呼叫範例。內容 SHALL 與 `twstock-module` 實作一致。

#### Scenario: 速查涵蓋六資料集且與實作一致
- **WHEN** 檢視 `finmind-api-cheatsheet.md`
- **THEN** MUST 含 daily／per_pbr／institutional／margin／revenue／financial 六項，每項列出方法名、關鍵欄位、參數與範例，且方法名與 `twstock-module/scripts/finmind_fetcher.py` 一致

### Requirement: 策略 preset 定義

`strategy-presets.md` SHALL 定義五個策略 preset：動能、價值、成長、高股息、法人籌碼。每個 preset MUST 含：面向權重覆寫（基本面／技術面／籌碼面，加總 100%）、3~5 個強調指標（含對應 twstock-module dataset 與方向語意）、所需 dataset、一句 rationale。強調指標之算法定義 SHALL 以 `scoring-model.md` 為準（preset SHALL NOT 另定義指標細節）；強調指標為 soft 連續評分，SHALL NOT 為硬門檻。

#### Scenario: 五 preset 皆完整定義

- **WHEN** 檢視 `strategy-presets.md`
- **THEN** MUST 含動能／價值／成長／高股息／法人籌碼五 preset，每個具面向權重（加總 100）、強調指標（含 dataset 與方向）、所需 dataset

#### Scenario: 指標引用 scoring-model 不另定義

- **WHEN** preset 指定某強調指標
- **THEN** 指標算法 MUST 引用 `scoring-model.md`，SHALL NOT 於 preset 內重新定義指標細節
