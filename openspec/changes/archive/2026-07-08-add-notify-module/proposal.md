## Why

v2.0 每日自動選股需把結果**推播到手機**。原 roadmap 寫「LINE Notify」，但 **LINE Notify 已於 2025-03-31 停止服務**，改用 **LINE Messaging API**（push message）。本 change 建最小推播模組，可獨立驗證「手機收得到」，供後續每日選股場景委派。

## 範圍評估（Ponytail）

- **零 pip 依賴**：用 stdlib `urllib.request` 發 HTTPS POST，不引 requests/line-bot-sdk——這是**可帶走的 skill**，可攜性優先（呼應「非 web app」）。
- **憑證走環境變數**：`LINE_CHANNEL_TOKEN`（channel access token）、`LINE_TO`（推播對象 userId/groupId），不寫死、不進版控（紅線 #4）。
- **dry-run 模式**：離線組 payload 不發送，供 selftest 與無 token 環境驗證。

## What Changes

- 新增 `twstock-notifying-line/scripts/line_push.py`：`push(text, dry_run=)` → POST `api.line.me/v2/bot/message/push`；token/target 從環境變數讀；錯誤不 crash、回結構化結果；token 不入任何回傳/log
- 新增 `twstock-notifying-line/SKILL.md`：推播模組（供場景委派）
- CLI：`--text`、`--dry-run`；`--selftest`（離線）

**Out of scope**：排程/cron（使用者 cowork 自設，不寫進 skill）、Dashboard、歷史持久化、非文字訊息（flex/圖）。

## Capabilities

### New Capabilities
- `twstock-notify`: 訊息推播模組——透過 LINE Messaging API push 將文字訊息送至指定對象；憑證從環境變數讀、不外洩；錯誤 fail-safe 回結構化結果、不中斷呼叫端。

## Impact

- **新增檔案**：`twstock-notifying-line/scripts/line_push.py`、`twstock-notifying-line/SKILL.md`
- **無 pip 依賴**（stdlib urllib）
- **環境變數**：`LINE_CHANNEL_TOKEN`、`LINE_TO`（使用者自備 LINE Official Account channel）
- **紅線關聯**：憑證環境變數、不進版控（#4）；LINE Messaging API 是渠道非 LLM（不涉 #1）
- **註**：live 送出需使用者的 LINE channel token + 對象 id；本 change 可離線 dry-run 驗證，live 驗證待使用者提供憑證
