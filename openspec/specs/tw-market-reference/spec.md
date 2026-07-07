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

### Requirement: 策略 preset 骨架

`strategy-presets.md` SHALL 提供五個策略 preset 的空骨架模板：動能、價值、成長、高股息、法人籌碼。每個 preset SHALL 採一致的模板欄位（名稱、面向權重、門檻、所需資料集），內容留待 v0.2 填寫，本 change 不寫實際策略邏輯或門檻值。

#### Scenario: 五 preset 骨架齊備且標註待填
- **WHEN** 檢視 `strategy-presets.md`
- **THEN** MUST 含動能／價值／成長／高股息／法人籌碼五個 preset，每個具一致模板欄位，且明確標註內容為 v0.2 待填（骨架不含實際門檻值）
