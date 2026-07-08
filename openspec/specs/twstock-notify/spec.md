# twstock-notify

## Purpose

訊息推播模組（輸出/side-effect 能力）：透過 LINE Messaging API 將文字訊息推播至指定對象，
供每日自動選股等場景委派通知。憑證從環境變數讀、不外洩；推播失敗 fail-safe、不中斷呼叫端。
零 pip 依賴（stdlib urllib）。實作於 twstock-notifying-line/scripts/line_push.py。

## Requirements

### Requirement: LINE Messaging API 文字推播

模組 SHALL 透過 LINE Messaging API（`POST https://api.line.me/v2/bot/message/push`）將文字訊息推播至指定對象。channel access token SHALL 從環境變數 `LINE_CHANNEL_TOKEN` 讀取、推播對象從 `LINE_TO` 讀取，SHALL NOT 於原始碼寫死或進版控。token SHALL NOT 出現在任何回傳結果、log 或存檔。模組 SHALL 以 stdlib 發送、不引入第三方 HTTP 依賴。

#### Scenario: 推播文字訊息
- **GIVEN** 環境有有效 `LINE_CHANNEL_TOKEN` 與 `LINE_TO`
- **WHEN** 呼叫 push(text)
- **THEN** MUST 以 Bearer token 對 LINE push 端點送出 `{to, messages:[{type:text,text}]}`，回結構化結果（成功/失敗）
- **AND** token SHALL NOT 出現在回傳結果或 log

#### Scenario: dry-run 離線組裝
- **WHEN** 以 dry_run 呼叫 push(text)
- **THEN** MUST 回傳將送出的 payload 結構而**不實際送出**，且 payload／回傳 MUST NOT 含 token

### Requirement: 推播 fail-safe

推播失敗（無 token、網路錯誤、API 非 2xx）時模組 SHALL NOT crash，MUST 回結構化錯誤結果，使呼叫端（每日選股場景）可判斷而不中斷主流程。

#### Scenario: 缺憑證不 crash
- **GIVEN** 環境無 `LINE_CHANNEL_TOKEN` 或 `LINE_TO`
- **WHEN** 非 dry-run 呼叫 push
- **THEN** MUST 回 `{ok: false, error: ...}`，SHALL NOT 拋例外中斷呼叫端

#### Scenario: API 錯誤不 crash
- **GIVEN** LINE API 回非 2xx（如 token 失效 401）
- **WHEN** 送出
- **THEN** MUST 捕捉並回結構化錯誤（含 status），SHALL NOT crash，且錯誤內容 SHALL NOT 洩漏 token
