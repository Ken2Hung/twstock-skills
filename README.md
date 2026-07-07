# twstock-skills

> 🇹🇼 台股選股 AI Skills — 讓 Claude 直接讀取 FinMind 台股開放資料，做基本面 × 技術面 × 籌碼面的選股分析
>
> Taiwan Stock Screening Skills for Claude — powered by [FinMind](https://github.com/FinMind/FinMind) open data. No external LLM API required.

![License](https://img.shields.io/badge/license-AGPL--3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Claude](https://img.shields.io/badge/Claude-Desktop%20%7C%20Code-orange)
![Market](https://img.shields.io/badge/market-TWSE%20%7C%20TPEx-green)

---

## 為什麼做這個專案？

台股在開源 AI 選股生態裡一直是個尷尬的缺口：

| 現有專案 | 星星數 | 台股支援程度 |
|---|---|---|
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 60k+ | ❌ 無台股特化，僅 yfinance ticker 可通 |
| [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | 高 | ⚠️ 台股走 yfinance offshore 路徑，僅日線 + 三大法人；資金流／板塊／基本面深度為 not_supported |
| 台股專屬專案（twstock、FinMind 等） | 中 | ✅ 資料層完整，但缺「選股邏輯 + AI 分析」層 |

**twstock-skills 的定位：取各家之長，補上缺口。**

- 資料層用 **FinMind**（75+ 台股資料集：財報三表、月營收、三大法人、融資融券、股權分散、借券明細）——深度遠超 yfinance
- 分析層直接用 **Claude 本體**——不需要 OpenAI／Gemini 等外部 LLM API Key，也不需要 LiteLLM 多模型路由
- 選股評分模型針對台股在地化：交易成本、漲跌停、處置股規則全部內建

## 能做什麼？

安裝後，直接在 Claude 用自然語言選股與分析：

```
幫我篩選：外資連續買超 5 天以上、月營收年增率 > 20%、股價站上 60 日均線的上市電子股
```

```
2330 最近的籌碼面健康嗎？給我三大法人和融資券的判讀
```

```
用高股息策略幫我從金融股裡挑 5 檔，附上目標價和止損價
```

Claude 會自動取得台股資料、套用選股策略、輸出決策看板（評分／信號／目標價／止損價）。

| Skill | 功能 | 狀態 |
|---|---|---|
| `twstock-module` | 台股資料取得：行情、基本面、籌碼面 | 🚧 v0.1 |
| `twstock-screening-stocks` | 自然語言多策略選股 → 決策看板 | 🚧 v0.1 |
| `twstock-reviewing-portfolio` | 持股健檢：法人動向、財報警訊掃描 | 📋 規劃中 |

## 快速開始

### Claude Desktop / Claude Code

```bash
# 1. 取得專案
git clone https://github.com/<your-account>/twstock-skills.git

# 2. 安裝 skills
mkdir -p ~/.claude/skills
cp -R twstock-skills/twstock-module ~/.claude/skills/
cp -R twstock-skills/twstock-screening-stocks ~/.claude/skills/

# 3. 安裝依賴
pip install FinMind pandas

# 4. （選用）設定 FinMind token，將 rate limit 從 300/hr 提升到 600/hr
export FINMIND_TOKEN=your_token   # 免費註冊：https://finmindtrade.com/
```

## 資料來源與限制

| 資料源 | 用途 | 限制 |
|---|---|---|
| [FinMind](https://finmind.github.io/) | 主要資料源（技術／基本／籌碼面） | 未註冊 300 req/hr、免費會員 600 req/hr |
| TWSE / TPEx 開放資料 | 三大法人、處置股 | 官方源，建議間隔 ≥ 1 秒 |
| yfinance | Fallback（FinMind 失效時降級） | 台股延遲報價 20 分鐘 |

單一資料源失效不會中斷分析，缺失的欄位會誠實標註、不會腦補。

## 交易成本與市場規則（在地化基準）

選股與回測的損益計算，交易成本與市場規則集中於 [tw-market-rules.md](twstock-screening-stocks/references/tw-market-rules.md)，作為**單一基準**（不散落魔術數字）：

- **交易成本**（牌告費率為保守基準）：買進 0.1425%、賣出 0.4425%（含證交稅 0.3%），來回約 **0.585%**
- **漲跌停 ±10%**；觸及時標註流動性風險
- **處置股**列入警示（分盤交易／預收款券）
- 現實性註記：手續費低消 20 元、現股當沖證交稅減半（時限性制度，使用前查證）

FinMind 資料集用法見 [finmind-api-cheatsheet.md](twstock-screening-stocks/references/finmind-api-cheatsheet.md)；策略 preset 骨架見 [strategy-presets.md](twstock-screening-stocks/references/strategy-presets.md)（實際權重與門檻 v0.2 填寫）。

## Roadmap

- [x] v0.1 — 基礎取資料 + 基礎選股
- [ ] v0.2 — 策略 preset 參數化（value / momentum / high-dividend / institutional）
- [ ] v0.3 — 持股健檢場景
- [ ] v1.0 — 歷史回測（含台股交易成本模型）
- [ ] v2.0 — Dashboard 化：每日自動選股 + LINE Notify 推播

## 開發者文件

程式架構、Skill 分層設計、開發規範請見 [CLAUDE.md](./CLAUDE.md)——該文件同時也是 Claude Code 開發本專案時的模型參考資料。

## 致謝（Standing on the Shoulders of Giants）

本專案的設計取材自以下優秀開源專案，特此致謝：

- [FinMind](https://github.com/FinMind/FinMind) — 台股開放資料的事實標準
- [daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) — 決策看板格式與多資料源降級鏈設計
- [Stock-Analysis-Skill](https://github.com/liusai0820/Stock-Analysis-Skill) — 「去 LLM API 依賴、Claude 本體分析」的 Skill 封裝哲學
- [claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) — 選股方法論 skill 化的架構參考
- [stock-strategies-only](https://github.com/kevin801221/stock-strategies-only) — 台股在地化評分模型與 FinMind 串接實戰
- [twstock](https://github.com/mlouielu/twstock) — 台股證券編碼與即時資訊

## ⚠️ 免責聲明

本專案僅供技術研究與教育用途，所有輸出**不構成任何投資建議**。台股有漲跌停與流動性風險，AI 模型分析存在不確定性，投資決策請自行判斷並諮詢專業人士。使用本專案即表示同意自行承擔所有投資風險。

## License

[AGPL-3.0](./LICENSE) — 允許自由使用、修改與散布；若你修改本專案並以**網路服務形式**提供他人使用（含 SaaS／Dashboard 部署），必須以相同授權公開你的修改後原始碼。
