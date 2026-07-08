## Context

完成 v2.0-alpha 管線。C 混合：Python 前濾（daily_screen.py）+ Claude 判讀 + 委派推播。watchlist 範圍、單策略、stateless、排程外置。

## Goals / Non-Goals

**Goals:** watchlist 每日前濾 → Claude 判讀 → LINE 推播，端到端管線驗證。
**Non-Goals:** 全市場、快取/節流、Dashboard、歷史 diff/持久化、排程、多策略（v2.0-beta/future）。

## Decisions

- **前濾重用 `signal_ma_bull`**（import 自 backtest.py）——單一可算訊號來源，不漂移。今日訊號 = `signal_fn(df).iloc[-1]`（live 選股用當日資料選當日，非回測，無 look-ahead 疑慮）。
- **逐檔 fail-open**：某檔取不到 → 跳過 + data_gaps；不中斷。
- **stateless**：alpha 不存歷史 → 無持久化（YAGNI）。歷史「新進/跌出」diff 為 next，屆時用**每日一個 JSON 檔**（非 SQLite——可攜 skill 非 web app）。
- **排程外置**：skill 不含 cron；使用者 `claude -p "跑今日選股推 LINE"` 由外部排程觸發（C 混合的 Claude 判讀步）。
- **推播委派**：組好文字 → `twstock-notifying-line` push，失敗不中斷。

## Risks / Trade-offs

- [watchlist 需使用者提供] → 場景接受股票清單參數；預設可給小型示範清單
- [live 送 LINE 需憑證] → daily_screen 可離線/dry-run 驗；live 推播待使用者 LINE 憑證
- [全市場 = 下一步大工程] → 明列 v2.0-beta（快取+跨檔節流，解 ponytail debt #1）

## Migration Plan
- 新增 daily_screen.py + SKILL.md；重用既有模組
## Open Questions
- watchlist 預設清單內容（可留給使用者提供）。
