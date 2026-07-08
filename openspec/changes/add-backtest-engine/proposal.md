## Why

Roadmap v1.0 = 歷史回測（含台股交易成本模型）。前四個 change 的分析都由 Claude 本體執行、無計算引擎；但回測**無法**這樣做——不可能讓 Claude 逐日 eyeball 250 個交易日 × N 檔。回測是專案第一個需要**確定性計算 code** 的能力。本 change 建最小可行回測引擎，核心價值是**忠實的台股交易成本模型**（roadmap 強調處）。

## 範圍評估（Ponytail）

- **純 pandas，不引入回測框架**：backtrader／vectorbt／zipline 為重依賴；long-only 向量化回測 pandas 百行內可完成（階梯 4：已裝依賴優先，不為此加新依賴）。
- **不在 Python 重寫完整三面向評分**：scoring-model.md 由 Claude 本體執行；若在回測 code 重寫全部指標＝製造**第二個會漂移的真相來源**。改採**可插拔訊號 + 一個參考訊號**（動能：均線多頭排列，直接由日K可算），示範引擎。完整多因子回測待訊號驗證後再擴（future）。
- **MVP 為單檔 long-only**：引擎對「單檔 + 訊號規則 + 期間」回測；多檔投組回測列 future（引擎可延伸）。
- **不建快取**：MVP 單/少檔，twstock-module 取歷史日K 一次即可（階梯 1：spec 未要求，不建）。
- **資料一律經 twstock-module**：回測 import twstock-module 取歷史資料，**不直接碰 FinMind/yfinance**（紅線 #2）。

## What Changes

- 新增 `twstock-backtesting/scripts/backtest.py`：回測引擎——歷史日K逐日模擬 long-only 進出場、套用台股成本、輸出指標。CLI + `--selftest`
- 新增 `twstock-backtesting/SKILL.md`：L3 場景——回測某策略某期間 → 呼叫引擎 → 回測報告看板
- **台股成本模型**：買 0.1425%（低消 20 元）、賣 0.4425%（手續費 0.1425% 低消 20 + 證交稅 0.3%）；損益一律扣成本；報告併陳**扣成本前/後**
- **無 look-ahead bias**：訊號僅用截至當日（含）資料決定**次日**進出場
- 指標：總報酬、年化報酬、最大回撤（MDD）、勝率、交易次數、扣成本前後對比

**Out of scope**：多檔投組回測、完整三面向評分回測、快取、參數優化/walk-forward、放空（皆 future）。

## Capabilities

### New Capabilities
- `twstock-backtesting`: 台股 long-only 歷史回測引擎——經 twstock-module 取歷史日K、以可插拔訊號逐日模擬、忠實套用台股交易成本、無 look-ahead bias、輸出含扣成本前後對比的績效指標；L3 場景呈現回測報告。

## Impact

- **新增檔案**：`twstock-backtesting/scripts/backtest.py`、`twstock-backtesting/SKILL.md`
- **無新增依賴**（pandas 已裝）；資料經 twstock-module
- **依賴**：`twstock-data-fetching`（歷史日K）、`tw-market-rules.md`（成本）、`scoring-model.md`（訊號指標定義）
- **紅線關聯**：委派非直呼（#2）、成本不散落魔術數字（引用 tw-market-rules）、回測報告附免責（#3）
