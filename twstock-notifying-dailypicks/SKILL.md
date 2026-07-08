---
name: twstock-notifying-dailypicks
description: >-
  台股每日選股推播企業場景（L3，編排型，v2.0-alpha）。對一份 watchlist 做每日前濾
  （Python 可算訊號縮成 shortlist）→ Claude 本體判讀決策看板 → 委派 twstock-notifying-line
  推播到 LINE。本場景不自己碰資料源 API 或 LINE API，一律委派。觸發語例句：「每日選股
  推到我 LINE」「跑今日自動選股並通知」「把 watchlist 今天入選的推給我」「幫我掃這幾檔
  今天有沒有進場訊號並通知」。排程由你外部自設（cowork/cron），本 skill 只負責可被呼叫。
---

# twstock-notifying-dailypicks

## 1. 觸發時機

當使用者想「每日自動選股 + 推播到手機」時觸發，例如：
- 「**每日選股推到我 LINE**」
- 「**跑今日自動選股並通知**我」
- 「把 watchlist 今天入選的**推給我**」

單次互動選股用 `twstock-screening-stocks`；只推播文字用 `twstock-notifying-line`。

## 2. 能力總覽（C 混合編排）

```
Python 前濾（快、可算） → Claude 本體判讀 shortlist → 委派推播
```
1. **前濾**：`scripts/daily_screen.py` 對 watchlist 逐檔算今日訊號 → shortlist
2. **判讀**：Claude 本體對 shortlist 套 scoring-model / 決策看板（重用選股場景邏輯）
3. **推播**：委派 `twstock-notifying-line` 送 LINE

**分層鐵律（紅線 #2）**：SHALL NOT 直接碰資料源 API 或 LINE API——取數委派 twstock-module、推播委派 twstock-notifying-line。

## 3. 輸入

- watchlist（股票代碼清單，使用者提供）；截止日（預設今日）；策略（v2.0-alpha 為均線多頭）。

## 4. 前濾（委派引擎）

呼叫 [`scripts/daily_screen.py`](scripts/daily_screen.py)：`--watchlist 2330,2454,...`。逐檔經 twstock-module 取日K、以 **`signal_ma_bull`（最後一根＝今日）** 判入選；重用回測之可算訊號、不另定義。逐檔 **fail-open**：取不到 → 跳過 + `data_gaps`。

## 5. 判讀（Claude 本體）

對 shortlist 套 [`scoring-model.md`](../twstock-screening-stocks/references/scoring-model.md) 與決策看板邏輯（同 `twstock-screening-stocks`）。shortlist 通常已很小，判讀成本低。

## 6. 推播（委派模組）

組好推播文字（入選標的 + 重點 + 免責）→ 委派 [`twstock-notifying-line`](../twstock-notifying-line/SKILL.md) `push(text)`。**推播失敗（回 ok:false）不中斷選股結果**，於輸出標註。

## 7. 推播文字內容

```
【每日選股 2024-XX-XX｜均線多頭】
今日入選：2330、2454、2412
（各附一句重點）
data_gaps：無
⚠️ 僅供研究參考，不構成投資建議，請自行判斷並自負風險。
```

## 8. 合規（紅線）

- **data_gaps 非空** → 推播 MUST 明示「以下基於不完整資料」。
- 推播 MUST 附**免責**；**禁止**「保證/必賺/穩賺」等表述。
- 前濾 fail-open、不腦補；取不到之個股列 data_gaps。

## 9. 排程（外置，不寫進 skill）

**本 skill 不含 cron/排程**。每日觸發請於外部自設，例如 cowork 或 OS cron 排一條：
```bash
claude -p "跑今日自動選股並推到 LINE，watchlist 2330,2454,2317"
```
（`claude -p` 是 Claude 本人，非外部 LLM，符合紅線 #1。）

## 10. 限制（v2.0-alpha 範圍）

- **watchlist 範圍**（非全市場）、**單一策略**、**stateless**（無「新進/跌出」歷史 diff）。
- 全市場掃描（需快取 + 跨檔節流）、Dashboard、歷史 diff、多策略 = **v2.0-beta / future**。

## 11. 分層邊界與免責

- 本場景為 **L3 企業場景**：編排前濾/判讀/推播；取數委派 twstock-module、推播委派 twstock-notifying-line。
- 所有輸出**不構成投資建議**；台股有漲跌停與流動性風險，投資決策請自行判斷並諮詢專業人士。
