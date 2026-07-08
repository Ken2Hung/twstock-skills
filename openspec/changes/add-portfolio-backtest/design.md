## Context

擴充 v1.0 單檔引擎為多檔投組。重用單檔核心，只加日期對齊加總。約束見 proposal 範圍評估。

## Goals / Non-Goals

**Goals:** 等權固定 sleeve 投組回測、沿用成本與無 look-ahead、投組層級指標、個股 fail-open。
**Non-Goals:** 跨檔動態再平衡、評分加權、滑價、放空（v-next/future）。

## Decisions

- **重構為純函式**：抽 `_equity_curves(close, hold, capital) → (net, gross, trades)`（日權益曲線）與 `_metrics(net, gross, trades, n) → dict`。單檔 `run_backtest` = 兩者串接；投組重用之。維持行為不變。
- **等權固定 sleeve**：`sleeve = capital / n_tradable`（分母只算可回測檔）。各檔獨立跑 `_equity_curves`，得日期索引的 net/gross Series。
- **對齊加總**：union 全檔日期 → 各 Series `reindex(union).ffill()`；某檔首日之前的 NaN 以其 sleeve 初始資本填（=現金，無報酬）。逐日加總為投組 net/gross 曲線 → `_metrics`。
- **指標一致**：投組 total/annualized/MDD 由加總曲線算；n_trades = 各檔加總；win_rate = 各檔 per-trade 勝負加總。
- **fail-open**：個股取不到 → 排除、列 data_gaps；全部取不到 → tradable:False。
- **CLI**：`--stock-id 2330,2454,2317`（逗號）→ 走投組；單一 → 沿用單檔。

## Risks / Trade-offs

- [日期對齊 ffill 的正確性] → selftest 以 2 條合成 Series 驗證加總與 MDD
- [等權非最優、無再平衡] → 明列 v-next；v1.1 為分散基準
- [個股排除改變 sleeve 分母] → data_gaps 誠實標註納入檔數

## Migration Plan
- 重構 backtest.py（單檔行為不變）+ 投組函式 + CLI + SKILL.md
## Open Questions
- 無（等權固定 sleeve 為 v1.1 定案）。
