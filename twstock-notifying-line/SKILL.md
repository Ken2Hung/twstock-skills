---
name: twstock-notifying-line
description: >-
  LINE 推播模組（輸出型）。透過 LINE Messaging API 把文字訊息推播到手機，供每日
  自動選股等場景委派通知。憑證從環境變數讀（LINE_CHANNEL_TOKEN / LINE_TO），零 pip
  依賴（stdlib urllib），推播失敗 fail-safe 不中斷呼叫端。觸發語例句：「把今日選股推到
  我 LINE」「用 LINE 通知我這些標的」「測試 LINE 推播收不收得到」「dry-run 看看要送
  什麼」。註：LINE Notify 已停用，本模組用 LINE Messaging API（Official Account）。
---

# twstock-notifying-line

## 1. 觸發時機

當任何流程需要「把結果推播到手機（LINE）」時委派本模組——典型情境：每日自動選股完成後通知。單純想推一段文字也可直接用。

## 2. 能力總覽

- 透過 **LINE Messaging API**（`POST /v2/bot/message/push`）推播**文字訊息**至指定對象。
- 供上層場景委派（如每日選股 → 委派本模組推播結果）。

## 3. 輸入契約

- `text`：要推播的文字。
- 憑證與對象（環境變數，非參數）：
  - `LINE_CHANNEL_TOKEN`：LINE Official Account 的 channel access token
  - `LINE_TO`：推播對象 userId / groupId

## 4. 輸出契約

回結構化 dict：成功 `{"ok": true, "status": 200}`；失敗 `{"ok": false, "error": ...}`；dry-run `{"ok": true, "dry_run": true, "payload": {...}}`。**token 永不出現在回傳或 log。**

## 5. 憑證與安全

- 憑證**只從環境變數讀**，腳本零寫死、不進版控（紅線 #4）。
- LINE Official Account 設定（一次性，使用者自備）：建 Messaging API channel → 取 channel access token → 取推播對象 id。
- token 不入任何輸出/log；HTTP 錯誤回應截斷後回傳。

## 6. 可攜性（零依賴）

用 stdlib `urllib.request` 發送，**不需 pip install** 任何套件——本 skill 可帶走即用。

## 7. 使用方式

```bash
export LINE_CHANNEL_TOKEN=<your_channel_token>
export LINE_TO=<userId 或 groupId>
python -X utf8 twstock-notifying-line/scripts/line_push.py --text "今日選股：2330、2454"
python -X utf8 twstock-notifying-line/scripts/line_push.py --text "測試" --dry-run   # 離線組 payload
python -X utf8 twstock-notifying-line/scripts/line_push.py --selftest                 # 離線自檢
```

## 8. fail-safe（不中斷呼叫端）

推播失敗（缺憑證、網路錯、API 非 2xx、逾時）一律**捕捉回結構化錯誤、不 crash**——每日排程下，推播失敗不該中斷選股主流程。

## 9. 限制（v2.0-alpha 範圍）

- 僅**文字**訊息（flex/圖卡、多渠道 Telegram/Discord = future）。
- **不含排程**：每日觸發由使用者自設 cron / cowork，不寫進本 skill。
- LINE Messaging API 免費層有月推播額度，每日單則遠低於上限。

## 10. 範例

「把今日選股結果推到我 LINE」→ 上層場景組好文字 → 委派本模組 `push(text)`。

## 11. 分層邊界與註記

- 本模組為**輸出/side-effect 能力**（v2.0 新類，別於取數 L2 / 分析 L3）：只負責推送，不做選股判讀。
- **LINE Notify 已於 2025-03-31 停用**，本模組改用 LINE Messaging API；使用前請確認 LINE 官方現行政策。
