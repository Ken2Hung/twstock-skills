## Why

v1.0 回測為單檔 MVP。實務選股是**一籃子**標的，單檔回測無法反映投組層級的分散、整體回撤與成本。v1.1 擴充引擎支援多檔投組回測，重用單檔核心邏輯（成本、無 look-ahead 不變）。

## 範圍評估（Ponytail）

- **等權固定 sleeve 模型**：資本均分給 N 檔（`capital/N`），每檔獨立跑單檔訊號，**無跨檔動態再平衡**。這是最省的正確投組模型——重用 `_equity_curves`，只加「按日期對齊、加總權益曲線」。
- **跨檔動態再平衡**（資金流向在訊號的標的、依評分加權）列 **v-next**——需 rebalance 頻率、turnover 成本、權重規則，範圍大且易錯，不在 v1.1 硬塞。
- **成本與無 look-ahead 不變**：沿用單檔的 `position=signal.shift(1)` 與台股成本，每檔 sleeve 各自套用。

## What Changes

- 重構 `backtest.py`：抽出 `_equity_curves`（日權益曲線）+ `_metrics`（指標）純函式；`run_backtest`（單檔）沿用
- 新增 `run_portfolio_backtest(stock_ids, ...)`：各檔取 sleeve 權益曲線 → 按日期對齊（union + ffill，開始前視為現金）→ 加總 → 投組指標
- 取不到的個股：排除於 sleeve 分母、列入 data_gaps（誠實，不腦補）
- CLI：`--stock-id` 支援逗號多檔 → 自動走投組回測
- 投組指標：總報酬(淨/毛)、成本侵蝕、年化、最大回撤、勝率、總交易次數、納入檔數

**Out of scope**：跨檔動態再平衡、依評分加權、滑價、放空（皆 v-next/future）。

## Capabilities

### Modified Capabilities
- `twstock-backtesting`: 新增「多檔投組回測」requirement——等權固定 sleeve、按日期對齊加總、投組層級指標；沿用單檔之成本與無 look-ahead 保證。

## Impact

- **修改**：`twstock-backtesting/scripts/backtest.py`（重構 + 投組函式 + CLI）、`twstock-backtesting/SKILL.md`（投組用法與報告）
- **spec**：MODIFIED twstock-backtesting（ADDED 投組 requirement）
- **無新增依賴**（pandas 對齊）
