## Why

v2.0-alpha 要驗證「每日選股 → 推播」管線端到端。Change 1 已備推播模組；本 change 補上前端：每日對 watchlist 做 Python 前濾（C 混合）、Claude 判讀 shortlist、委派推播模組送 LINE。

## 範圍評估（Ponytail / v2.0-alpha）

- **watchlist 範圍**（非全市場）：先驗證管線，避開全市場快取/節流的大工程（列 v2.0-beta）。
- **單一策略**（均線多頭，重用 backtest 之 `signal_ma_bull`——不另定義訊號，避免漂移）。
- **stateless**：alpha 無「新進/跌出」歷史 diff，故**不需持久化**（YAGNI；歷史 diff 為 next，屆時用 JSON 檔非 DB）。
- **排程外置**：每日觸發由使用者 cowork 自設 cron，**不寫進 skill**。
- **C 混合**：Python 前濾（快、可算）縮到 shortlist → Claude 本體對 shortlist 做決策看板 → 委派推播。

## What Changes

- 新增 `twstock-notifying-dailypicks/scripts/daily_screen.py`：對 watchlist 逐檔經 twstock-module 取日K、算今日是否入選（`signal_ma_bull` 最後一根）、回 shortlist；逐檔 fail-open
- 新增 `twstock-notifying-dailypicks/SKILL.md`（L3 場景）：前濾 → Claude 決策看板 → 委派 `twstock-notifying-line` 推播
- 推播內容含免責；data_gaps 非空明示

**Out of scope**：全市場掃描、快取/跨檔節流、Dashboard、歷史 diff/持久化、排程、多策略（皆 v2.0-beta/future）。

## Capabilities

### New Capabilities
- `twstock-daily-picks`: L3 每日選股推播編排——對 watchlist 做 Python 前濾（可算訊號）、委派 twstock-module 取數、Claude 判讀 shortlist、委派 twstock-notify 推播；排程外置、stateless。

## Impact

- **新增檔案**：`twstock-notifying-dailypicks/scripts/daily_screen.py`、`.../SKILL.md`
- **依賴**：`twstock-data-fetching`（取數）、`twstock-scoring`/`twstock-screening-orchestration`（判讀）、`twstock-notify`（推播）；重用 backtest `signal_ma_bull`
- **無新 pip 依賴**
- **紅線**：委派非直呼 API（#2）、推播含免責（#3）、data_gaps 不腦補（#5）
