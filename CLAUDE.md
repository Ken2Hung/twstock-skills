# CLAUDE.md

本文件是 Claude Code 開發 twstock-skills 時的模型參考資料，包含專案架構、設計約束與開發規範。修改任何 skill 前請先完整閱讀本文件。

## 專案定位

台股選股 AI Skills 集合。資料層封裝 FinMind API，分析層由 Claude 本體執行（**禁止引入任何外部 LLM API 依賴**，如 OpenAI／Gemini／LiteLLM），輸出決策看板格式。

## 兩層 Skill 架構（核心設計約束）

採「業務模組 → 企業場景」分層，**場景不得直接呼叫 FinMind API**，必須委派模組取數。模組與場景為 N:M 重用關係。

| 層級 | 類型 | 職責 | 禁止事項 |
|---|---|---|---|
| L2 業務模組 | 組合型 | 封裝資料源取數、回傳結構化 JSON | 不做分析判讀、不排版報告 |
| L3 企業場景 | 編排型 | 委派模組取數 → 分析 → 決策看板呈現 | 不自己碰 API、不寫取數邏輯 |

新增功能時先判斷歸屬：純取數能力 → 加進 `twstock-module`；面向使用者的分析流程 → 開新的 L3 場景 skill。**不要把取數邏輯寫進場景層**，這會破壞分層存在原則。

## 目錄結構

```
twstock-skills/
├── README.md                        # 使用者文件（不含架構細節）
├── CLAUDE.md                        # 本文件
├── LICENSE                          # AGPL-3.0
├── twstock-module/                  # L2 業務模組
│   ├── SKILL.md
│   └── scripts/
│       └── finmind_fetcher.py       # FinMind API 封裝（唯一允許碰 API 的地方）
├── twstock-screening-stocks/        # L3 企業場景：多策略選股
│   ├── SKILL.md
│   └── references/
│       ├── strategy-presets.md      # 策略知識庫
│       ├── tw-market-rules.md       # 台股市場規則
│       └── finmind-api-cheatsheet.md# FinMind 資料集速查（源自官方 llms.txt）
└── twstock-reviewing-portfolio/     # L3 企業場景：持股健檢（規劃中）
    └── SKILL.md
```

## 命名規範

- Skill 命名一律採 `${domain}-${gerund}-${noun}`，domain 固定為 `twstock`
  - ✅ `twstock-screening-stocks`、`twstock-reviewing-portfolio`
  - ❌ `stock-screener`、`twstock-screen`（非動名詞）
- 例外：L2 業務模組採 `${domain}-module` 命名（`twstock-module`）
- SKILL.md 採 11 區塊標準骨架，含 YAML frontmatter（name / description）
- description 必須包含觸發語例句（自然語言講法），供意圖路由使用

## 資料層規範（finmind_fetcher.py）

### 資料源優先級與降級鏈

```
FinMind（主）→ TWSE/TPEx 官方開放資料（法人、處置股）→ yfinance（fallback）
```

- **fail-open 原則**：單一資料源失效時記錄錯誤並降級，不中斷主鏈路
- 取不到的欄位在回傳 JSON 中以 `data_gaps: []` 陣列誠實標註，**禁止腦補或以舊資料填充**
- 回傳一律為結構化 JSON，欄位含 `source`（實際使用的資料源）與 `fetched_at`

### Rate Limit（寫程式時必須遵守）

| 資料源 | 限制 | 處理方式 |
|---|---|---|
| FinMind（無 token） | 300 req/hr | 讀取環境變數 `FINMIND_TOKEN`，有 token 提升至 600 req/hr |
| TWSE / TPEx | 未明文，經驗值 | 每次 request 間隔 ≥ 1 秒，禁止並發轟炸 |
| yfinance | ~2000 req/hr | 僅作 fallback，台股報價延遲 20 分鐘需在輸出標註 |

批量取數（如全市場篩選）必須實作節流與快取，避免觸發封鎖。

### 市場別判斷

- 上市 → yfinance ticker 加 `.TW`；上櫃 → 加 `.TWO`
- 證券清單以 FinMind `TaiwanStockInfo` 為準（含產業別），不要硬編碼股票清單

## 選股評分模型

```
綜合分 = 基本面 × 30% + 技術面 × 30% + 籌碼面 × 40%
```

- 籌碼面權重 40% 是刻意設計（台股散戶佔比高、法人動向指標性強），調整權重需先討論
- **基本面**：月營收 YoY、EPS、ROE（FinMind 月營收表 + 財報三表）
- **技術面**：均線多頭排列、乖離率、量價關係
- **籌碼面**：三大法人買賣超、融資融券變化、股權分散趨勢

## 台股在地化規則（分析與回測必須內建）

- 交易成本：買進 0.1425%（手續費）＋ 賣出 0.4425%（手續費 + 證交稅 0.3%）
- 漲跌停：±10%；觸及漲跌停的訊號需標註流動性風險
- 處置股：分析標的若在 TWSE 處置名單需明確警示
- 停損停利與回測損益計算，一律先扣除交易成本

## 輸出格式（決策看板）

L3 場景輸出遵循固定看板結構：

```
評分（0-100）｜信號（買進/持有/觀望/賣出）｜目標價｜止損價｜核心理由（≤3 點）｜風險提示｜data_gaps
```

- 每檔標的必附風險提示與免責聲明
- data_gaps 非空時，必須在看板中明示「以下判讀基於不完整資料」

## 開發工作流

```bash
# 依賴安裝
pip install FinMind pandas

# 取數腳本單測（不經過 Claude）
python -X utf8 twstock-module/scripts/finmind_fetcher.py --stock-id 2330 --dataset daily

# Skill 本機安裝驗證
cp -R twstock-module ~/.claude/skills/ && cp -R twstock-screening-stocks ~/.claude/skills/
```

- Python 腳本一律以 `-X utf8` 執行（繁中欄位名避免編碼問題）
- 修改 SKILL.md 後需重新安裝到 `~/.claude/skills/` 驗證觸發語是否命中
- 新增策略 preset 時同步更新 `references/strategy-presets.md` 與 SKILL.md 的觸發語

## 開發流程：OpenSpec × Ponytail 雙層治理

本專案採 [OpenSpec](https://github.com/Fission-AI/OpenSpec)（spec-driven，治理 **What**）＋ [Ponytail](https://github.com/DietrichGebert/ponytail)（極簡實作紀律，治理 **How**）融合開發。兩者分工與衝突裁決規則如下，**Claude Code 在本 repo 工作時必須同時遵守**。

### 分工

| 層 | 工具 | 職責 |
|---|---|---|
| 規格層 | OpenSpec（`/opsx:*`） | 行為真相在 `openspec/specs/`；每個變更走 propose → apply → archive；delta spec 以 ADDED/MODIFIED/REMOVED 標註 |
| 實作層 | Ponytail（`/ponytail*`，預設 full mode） | 寫碼前走七階梯：需要存在嗎 → codebase 已有 → stdlib → 平台原生 → 已裝依賴 → 一行 → 最小可行實作 |

### 衝突裁決（優先序，由高到低）

1. **紅線 > 一切**：本文件「紅線」與 `openspec/project.md` 的禁令，任何工具都不得推翻
2. **Spec > Ponytail**：`openspec/specs/` 已 archive 的 requirement 定義了「必要」。Ponytail 不得以 YAGNI 為由砍掉 spec 明列的行為——降級鏈、data_gaps 標註、rate limit 節流、免責聲明都是 spec 要求，不是過度工程
3. **Ponytail > 實作慣性**：spec 未明列的東西一律不建。具體到本專案：
   - FinMind 官方 SDK 已有 `DataLoader`，禁止自建 requests 封裝層（階梯 5）
   - 節流用 `time.sleep`，禁止為此引入 ratelimit 套件（階梯 3）
   - 快取在 v1.0 回測前不做（階梯 1——spec 還沒要求它存在）
   - 資料轉換能用 pandas 一行解決就一行（階梯 6）
4. **Ponytail 安全底線與紅線重疊**：trust-boundary 驗證、資料遺失處理、安全性永不上砍除清單——這與本專案「data_gaps 不腦補」「token 不進版控」是同一件事的兩種表述

### 每個 Change 的標準循環

```
/opsx:propose <change-id>
  ↓ 人工 review：delta spec 是否符合意圖 + 用 Ponytail 眼光審 design.md
  ↓（design 若出現「框架」「抽象層」「以後會用到」字眼 → 砍掉重提）
/opsx:apply             ← Ponytail full mode 生效，diff 自然最小化
  ↓
/ponytail-review        ← 對 diff 出 delete-list，逐項處理
  ↓
本機驗證 spec scenarios（python -X utf8 實測 + skill 觸發語實測）
  ↓
/opsx:archive           ← delta 併入 specs/，成為新真相
```

### 債務閉環（兩工具的接縫）

實作中被 Ponytail 標註 `ponytail:` 延後的捷徑，定期用 `/ponytail-debt` 收割成債務清單；**每一條債務評估後轉成 OpenSpec change proposal 或明確棄置**，禁止讓債務停留在 ledger 裡無人認領。這是本專案的 govern 機制：OpenSpec 管「該做而未做」，Ponytail 管「不該做而想做」。

### 工具安裝（一次性）

```bash
npm install -g @fission-ai/openspec && openspec init   # 選 Claude Code
# Claude Code 內分兩則訊息執行：
#   /plugin marketplace add DietrichGebert/ponytail
#   /plugin install ponytail@ponytail
```

## 上游參考專案（設計取材對照）

| 上游 | GitHub 來源 | 本專案取用 | 注意 |
|---|---|---|---|
| daily_stock_analysis | https://github.com/ZhuLinsen/daily_stock_analysis | 決策看板格式、資料源降級鏈設計 | 其台股僅走 yfinance offshore 路徑，資料深度不足，勿直接沿用其台股 data provider |
| Stock-Analysis-Skill | https://github.com/liusai0820/Stock-Analysis-Skill | SKILL.md + scripts + references 封裝結構 | 其資料源為 A 股（Tushare），僅參考結構不參考取數 |
| claude-trading-skills | https://github.com/tradermonty/claude-trading-skills | 選股方法論 skill 化寫法、多 skill 工作流 | 美股語境（FMP/FinViz API），方法論可移植、API 不可 |
| stock-strategies-only | https://github.com/kevin801221/stock-strategies-only | 台股評分模型、FinMind 串接實戰、交易成本模型 | 個人專案，串接細節自行驗證後再採用 |
| FinMind | https://github.com/FinMind/FinMind | 主要資料層（75+ 台股資料集） | 注意 rate limit，見「資料層規範」 |
| twstock | https://github.com/mlouielu/twstock | 台股證券編碼慣例參考 | 僅參考編碼規則，取數以 FinMind 為主 |

## 紅線（絕對禁止）

1. 引入外部 LLM API 依賴（OpenAI / Gemini / LiteLLM 等）
2. 場景層（L3）直接呼叫資料源 API
3. 以任何形式輸出「保證獲利」、「必漲」等表述；所有輸出必附免責聲明
4. 硬編碼股票代碼清單、API token 或任何憑證進版控
5. data_gaps 存在時假裝資料完整
