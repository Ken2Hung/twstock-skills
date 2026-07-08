## 1. backtest.py 引擎

- [ ] 1.1 建立 `twstock-backtesting/scripts/backtest.py`；經 twstock-module 取歷史日K（import finmind_fetcher，不直接碰 API）
- [ ] 1.2 參考訊號：均線多頭 5MA>20MA>60MA（可插拔函式）
- [ ] 1.3 執行時序防 look-ahead：`position = signal.shift(1)`，T+1 開盤成交
- [ ] 1.4 台股成本模型：買 0.1425%(低消20)、賣 0.4425%(低消20+證交稅0.3%)，具名常數、註明引用 tw-market-rules.md
- [ ] 1.5 指標：總報酬、年化、MDD、勝率、交易次數、扣成本前後對比
- [ ] 1.6 fail-open：data_gaps／空日K → 不 crash、結果標註
- [ ] 1.7 CLI（--stock-id/--start/--end）+ `--selftest`（離線斷言：成本、無未來洩漏、指標形狀）

## 2. SKILL.md（L3 回測場景）

- [ ] 2.1 `twstock-backtesting/SKILL.md` 11 區塊；回測報告看板 + 免責 + data_gaps 明示
- [ ] 2.2 委派引擎、不自碰 API；報告含扣成本前後對比

## 3. 驗證

- [ ] 3.1 selftest 通過（離線）
- [ ] 3.2 實測 2330 一段期間回測，確認指標合理、成本前後有差
- [ ] 3.3 對抗式驗證（workflow）：look-ahead bias／成本錯誤／時序 off-by-one
- [ ] 3.4 核對 5 requirement scenario
