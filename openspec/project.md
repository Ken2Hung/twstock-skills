# Project Context

> 本檔為 OpenSpec 建立 artifact 時提供給 AI 的專案脈絡，內容源自 repo 根目錄 `CLAUDE.md`。
> 行為真相以 `openspec/specs/` 為準；本檔僅提供不可被 spec 推翻的治理前提。

## 技術棧

- **語言**：Python 3.10+（腳本一律以 `python -X utf8` 執行，繁中欄位名避免編碼問題）
- **資料層**：FinMind 官方 SDK（`DataLoader`）＋ pandas；禁止自建 requests/HTTP 封裝層
- **分析層**：Claude 本體執行，**禁止引入任何外部 LLM API 依賴**（OpenAI／Gemini／LiteLLM）
- **目標環境**：Claude Desktop / Claude Code，skill 安裝於 `~/.claude/skills/`

## 架構鐵律（原文照抄 CLAUDE.md 兩層架構約束）

採「業務模組 → 企業場景」分層，**場景不得直接呼叫 FinMind API，必須委派模組取得資料**。模組與場景為 N:M 重用關係。

- **L3 企業場景（編排型）**：委派模組取得資料 → 分析 → 決策看板呈現。**不自己碰 API、不寫取資料邏輯**。
- **L2 業務模組（組合型）**：封裝資料源的取資料能力、回傳結構化 JSON。**不做分析判讀、不排版報告**。

> L3 企業場景不得直接呼叫任何資料源 API，必須委派 twstock-module；L2 模組不做分析判讀、不排版報告。

新增功能先判斷歸屬：純取資料能力 → 加進 `twstock-module`；面向使用者的分析流程 → 開新的 L3 場景 skill。不要把取資料邏輯寫進場景層。

## 紅線（絕對禁止，全文照抄 CLAUDE.md）

1. 引入外部 LLM API 依賴（OpenAI / Gemini / LiteLLM 等）
2. 場景層（L3）直接呼叫資料源 API
3. 以任何形式輸出「保證獲利」、「必漲」等表述；所有輸出必附免責聲明
4. 硬編碼股票代碼清單、API token 或任何憑證進版控
5. data_gaps 存在時假裝資料完整

## 開發紀律

- 本專案採 **Ponytail full mode**：spec 未明列的**抽象層、框架、快取、設定系統一律不建**。寫碼前走七階梯（需要存在嗎 → codebase 已有 → stdlib → 平台原生 → 已裝依賴 → 一行 → 最小可行實作）。
- 具體約束：FinMind SDK 已有 `DataLoader`，禁止自建 requests 封裝（階梯 5）；節流用 `time.sleep`，禁止引入 ratelimit 套件（階梯 3）；快取在 v1.0 回測前不做（階梯 1）；資料轉換能用 pandas 一行就一行（階梯 6）。

### 衝突裁決優先序（由高到低）

1. **紅線 > 一切**：本檔紅線與 CLAUDE.md 禁令，任何工具都不得推翻。
2. **Spec > Ponytail**：`openspec/specs/` 已 archive 的 requirement 定義「必要」。降級鏈、data_gaps 標註、rate limit 節流、免責聲明都是 spec 要求，Ponytail 不得以 YAGNI 為由砍掉。
3. **Ponytail > 實作慣性**：spec 未明列的東西一律不建。
4. **Ponytail 安全底線與紅線重疊**：trust-boundary 驗證、資料遺失處理、安全性永不上砍除清單——與「data_gaps 不腦補」「token 不進版控」同一件事。
