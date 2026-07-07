## Context

`twstock-module` 是專案首個 skill，也是唯一允許碰資料源 API 的地方（紅線 #2 守門人）。它引入新外部依賴（yfinance），並須處理降級、rate limit、市場別等跨關注點，故值得一份 design 先定調技術取向再寫碼。約束見 `openspec/project.md`：Ponytail full mode、FinMind SDK 已有 `DataLoader`、節流用 `time.sleep`。

## Goals / Non-Goals

**Goals:**
- 單一檔案 `scripts/finmind_fetcher.py` 提供 6 資料集取得 + 降級 + 節流 + 市場別，CLI 可獨立單測（不經 Claude）
- 輸出 JSON 形狀恆定（`source` / `fetched_at` / `data_gaps` 恆存在）
- 降級與缺漏誠實反映在 `data_gaps`，fail-open 不中斷主鏈路

**Non-Goals:**
- 快取、資料庫、重試框架、設定系統（Ponytail 階梯 1——spec 未要求，不建）
- 任何分析判讀／評分／排版（屬 L3 場景）
- 全市場批量取得的排程與並發（本 change 只做單檔）

## Decisions

- **用 FinMind 官方 `DataLoader`，不自建 HTTP/requests 封裝層**（Ponytail 階梯 5）。SDK 已封裝端點、認證、分頁；自建 wrapper 是重造輪子。
- **節流用 `time.sleep`，不引入 ratelimit 套件**（Ponytail 階梯 3）。單檔、低頻請求下，記錄上次請求時間戳、以固定最小間隔 sleep 即足。上限值（300/600）依 `FINMIND_TOKEN` 是否存在切換。
- **降級只針對日K**。理由：yfinance 對台股只有 OHLCV 有意義，籌碼/財報/月營收它本就給不了；對這些做降級是假動作，直接進 `data_gaps` 才誠實。
- **市場別查 `TaiwanStockInfo`，不硬編碼清單**（紅線 #4 精神）。`.TW`/`.TWO` 後綴僅在降級組 yfinance ticker 時才需要。
- **輸出契約集中在一個組裝函式**：所有 dataset 路徑最後都經同一處補齊 `source`/`fetched_at`/`data_gaps`，保證形狀一致，避免各分支各自拼 JSON 而漂移。
- **capability 二分**：`twstock-data-fetching`（取得契約：資料集/輸出形狀/市場別/封裝）與 `twstock-data-resilience`（降級鏈/rate limit/憑證安全）分立於同一支 `finmind_fetcher.py`，但 spec 分檔——讓降級與節流策略日後可獨立改動而不牽動取得契約。
- **憑證安全**：`FINMIND_TOKEN` 只從環境變數讀，腳本零寫死；token 不入任何輸出/log/存檔，驗證存檔前先掃內容。
- **例外處理只包 spec scenario 定義的情境**（FinMind 402/429/逾時 → 降級或 data_gaps），不做 catch-all 吞錯。

## Risks / Trade-offs

- [pandas 3.0.0 與 FinMind 2.0.4 相容性未實測] → 本機驗證階段對 6 資料集各跑一次；若遇 API 破壞性變更再議降版
- [yfinance 台股報價延遲約 20 分鐘] → 降級輸出強制標註延遲警示，不讓下游誤判為即時
- [無 token 時 300 req/hr，6 資料集 × 驗證會吃額度] → 已由使用者提供 token（session-scoped 注入，不持久化）；節流避免爆量
- [`time.sleep` 是行程內全域節流，非跨行程] → 單檔 CLI 場景足夠；未來全市場批量若需跨行程協調再走新 change（`ponytail:` 標註上限與升級路徑）

## Migration Plan

- 新增檔案，無既有行為變更；`twstock-module/.gitkeep` 由實檔取代
- 需 `pip install yfinance`（日K fallback 依賴）
- Rollback：移除 `twstock-module/` 即可，無資料遷移、無下游破壞（尚無 L3 場景依賴）

## Open Questions

- 無阻斷性未決項。降級鏈範圍、rate limit 值、驗證深度已於 review 前拍板。
