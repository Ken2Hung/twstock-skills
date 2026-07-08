## Context

v2.0 首個 side-effect（輸出）能力——專案至此皆為取數(L2)/分析(L3)，推播是新類。最小、零依賴、可攜。排程不寫進 skill（使用者 cowork 自設 cron）。

## Goals / Non-Goals

**Goals:** stdlib LINE push、憑證環境變數不外洩、fail-safe、離線 dry-run 可測。
**Non-Goals:** 排程、Dashboard、持久化、flex/圖訊息、多渠道（Telegram/Discord 待需要）。

## Decisions

- **stdlib `urllib.request`**（非 requests/line-bot-sdk）：單一 POST，零 pip 依賴＝最大可攜（Ponytail 階梯 2）。
- **憑證只從 env**：`LINE_CHANNEL_TOKEN`/`LINE_TO`；回傳結構化結果，token 永不入回傳/log。
- **fail-safe**：所有失敗（缺憑證/HTTP 錯/逾時）捕捉回 `{ok:false,...}`，不 crash——呼叫端每日跑，推播失敗不該中斷選股。
- **dry-run**：離線組 payload、不送，供 selftest 與無憑證驗證。

## Risks / Trade-offs

- [LINE Messaging API 免費層 push 有月額度限制] → 每日單則推播遠低於額度；文件註明
- [live 送出需使用者憑證] → 本 change 離線可驗；live 驗證待使用者提供 channel token + userId

## Migration Plan
- 新增模組；無既有變更
## Open Questions
- 無（渠道已定 LINE Messaging API）。
