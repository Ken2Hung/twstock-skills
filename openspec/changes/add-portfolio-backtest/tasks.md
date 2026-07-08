## 1. 重構（單檔行為不變）

- [ ] 1.1 抽 `_equity_curves(close, hold, capital) → (net, gross, trades)`（日權益曲線）
- [ ] 1.2 抽 `_metrics(net, gross, trades, n) → dict`；`run_backtest` 改用兩者串接
- [ ] 1.3 selftest 確認單檔重構後指標不變

## 2. 投組回測

- [ ] 2.1 `run_portfolio_backtest(stock_ids, ...)`：可回測檔 sleeve=capital/n；各檔取 net/gross 曲線
- [ ] 2.2 按日期對齊（union+ffill，首日前視為現金）加總為投組曲線 → `_metrics`
- [ ] 2.3 個股取不到 → 排除分母、列 data_gaps；全不可回測 → tradable:False
- [ ] 2.4 投組指標加「納入檔數」；n_trades/win_rate 跨檔加總
- [ ] 2.5 CLI `--stock-id` 支援逗號多檔 → 自動投組

## 3. 驗證

- [ ] 3.1 selftest：`_equity_curves` 純函式 + 投組加總（2 合成 sleeve 對齊/MDD）
- [ ] 3.2 實測 3 檔投組回測（2330,2454,2317），確認納入檔數、成本前後、投組 MDD 合理
- [ ] 3.3 核對 MODIFIED twstock-backtesting 投組 scenario
