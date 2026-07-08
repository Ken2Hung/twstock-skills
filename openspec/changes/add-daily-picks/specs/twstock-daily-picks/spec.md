## ADDED Requirements

### Requirement: 每日選股推播編排（C 混合）

L3 場景 twstock-notifying-dailypicks SHALL 編排：對 watchlist 做 **Python 前濾**（可算訊號縮成 shortlist）→ **Claude 本體判讀** shortlist（決策看板）→ **委派 `twstock-notify`** 推播結果。所有台股資料 SHALL 經 twstock-module 取得，推播 SHALL 委派 twstock-notify，場景 SHALL NOT 直接呼叫任何資料源 API 或 LINE API。前濾之訊號 SHALL 重用既有可算訊號（`signal_ma_bull`），SHALL NOT 於場景另定義指標。

#### Scenario: 端到端每日選股推播
- **GIVEN** 一份 watchlist 與策略
- **WHEN** 場景執行
- **THEN** MUST 依序：Python 前濾 → Claude 判讀 shortlist → 委派 twstock-notify 推播
- **AND** MUST NOT 直接呼叫資料源 API 或 LINE API（一律委派 twstock-module / twstock-notify）

#### Scenario: 前濾使用既有可算訊號
- **WHEN** 對 watchlist 前濾
- **THEN** MUST 以既有 `signal_ma_bull`（最後一根為今日訊號）判定入選，SHALL NOT 於場景重定義指標

### Requirement: 前濾與推播 fail-open

watchlist 中某檔取不到/資料不足 SHALL 跳過並列入 data_gaps，SHALL NOT 中斷整體前濾、SHALL NOT 腦補。推播失敗（twstock-notify 回 ok:false）SHALL NOT 中斷選股主流程，SHALL 於結果標註。

#### Scenario: 個股取不到不中斷
- **GIVEN** watchlist 某檔資料不足
- **WHEN** 前濾
- **THEN** 該檔 MUST 跳過並列入 data_gaps，其餘照常，SHALL NOT 腦補

#### Scenario: 推播失敗不中斷
- **GIVEN** twstock-notify 推播回 ok:false（如缺憑證）
- **WHEN** 場景處理
- **THEN** MUST 標註推播失敗、SHALL NOT crash 或中斷選股結果

### Requirement: 排程外置、stateless

場景 SHALL NOT 內建排程/cron；每日觸發由使用者外部（cowork/OS cron）自設。v2.0-alpha 場景 SHALL 為 stateless（不需持久化歷史）。

#### Scenario: 不內建排程
- **WHEN** 檢視 skill
- **THEN** MUST NOT 含 cron/排程設定；skill 僅提供「可被呼叫」的每日選股推播能力

### Requirement: 推播內容免責與揭露

推播訊息 SHALL 附投資免責、SHALL NOT 含「保證/必賺」表述；data_gaps 非空時 SHALL 明示「以下基於不完整資料」。

#### Scenario: 推播附免責與 data_gaps 揭露
- **GIVEN** 一次每日選股完成
- **WHEN** 組推播訊息
- **THEN** MUST 附免責；data_gaps 非空 MUST 明示不完整；MUST NOT 含保證獲利類表述

### Requirement: 觸發語涵蓋

SKILL.md description MUST 含觸發語，SHALL 至少涵蓋：「每日選股推到 LINE」、「跑今日自動選股並通知」、「把 watchlist 今天入選的推給我」。

#### Scenario: 觸發語命中
- **GIVEN** 使用者輸入「跑今日自動選股並推到 LINE」
- **WHEN** 意圖路由
- **THEN** MUST 命中 twstock-notifying-dailypicks 場景
