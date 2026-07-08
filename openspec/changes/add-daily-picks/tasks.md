## 1. daily_screen.py（Python 前濾）

- [ ] 1.1 建立 `twstock-notifying-dailypicks/scripts/daily_screen.py`
- [ ] 1.2 `screen(watchlist, asof)`：逐檔經 twstock-module 取日K、算今日 `signal_ma_bull` 最後一根 → 入選 shortlist
- [ ] 1.3 重用 backtest `signal_ma_bull`（import），不另定義訊號
- [ ] 1.4 逐檔 fail-open：取不到 → 跳過 + data_gaps
- [ ] 1.5 CLI `--watchlist 2330,2454,...` + `--selftest`（離線：合成 df 的入選判定）

## 2. SKILL.md（L3 編排）

- [ ] 2.1 `twstock-notifying-dailypicks/SKILL.md` 11 區塊
- [ ] 2.2 編排：前濾 → Claude 決策看板（shortlist）→ 委派 twstock-notifying-line 推播
- [ ] 2.3 推播文字含免責、data_gaps 明示；排程外置（不內建 cron）；stateless

## 3. 驗證

- [ ] 3.1 daily_screen selftest（離線：`_is_picked` 合成 df）
- [ ] 3.2 實測 watchlist 前濾（如 2330,2454,2317,2412），確認 shortlist 與 data_gaps
- [ ] 3.3 對抗式驗證（workflow）：整條 alpha 管線（前濾/推播/憑證/fail-open）
- [ ] 3.4 核對 twstock-daily-picks 5 requirement scenario
