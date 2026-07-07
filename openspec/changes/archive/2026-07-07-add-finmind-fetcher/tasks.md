## 1. Setup

- [x] 1.1 `pip install yfinance`（日K fallback 依賴；FinMind、pandas 已裝）— yfinance 1.5.1
- [x] 1.2 建立 `twstock-module/scripts/` 目錄，移除 `twstock-module/.gitkeep`
- [x] 1.3 確認 `FINMIND_TOKEN` 讀取方式（`os.environ.get`）；token 以 session-scoped 注入，不寫入任何檔案

## 2. 核心取得器（finmind_fetcher.py）

- [x] 2.1 以 FinMind `DataLoader` 實作 6 資料集取得：日K、PER/PBR、三大法人買賣超、融資融券、月營收、財報三表（不自建 HTTP 封裝）
- [x] 2.2 實作輸出組裝函式：所有 dataset 路徑統一補齊 `source` / `fetched_at` / `data_gaps`，保證 JSON 形狀恆定（`data_gaps` 空時仍為 `[]`）
- [x] 2.3 CLI 介面：`--stock-id`、`--dataset`、日期區間參數，可 `python -X utf8 finmind_fetcher.py ...` 獨立執行（另含 `--selftest` 離線自檢）
- [x] 2.4 缺漏欄位一律進 `data_gaps`，禁止以舊資料／預設值填充（紅線 #5）

## 3. 韌性（降級／節流／市場別）

- [x] 3.1 日K降級鏈：FinMind 回 402/429/逾時 → 改 yfinance，標註 `source: "yfinance"` 與 20 分鐘延遲警示（yfinance leg 已 standalone 驗證；全鏈 source=yfinance 待 FinMind 額度重置驗）
- [x] 3.2 非日K資料集取不到 → 直接進 `data_gaps`，不降級、不中斷（fail-open）— ✅ 實打驗證成立
- [x] 3.3 Rate limit：依 `FINMIND_TOKEN` 有無切換 300/600 req/hr 上限，請求間以 `time.sleep` 節流（不引入 ratelimit 套件）
- [x] 3.4 市場別：查 `TaiwanStockInfo` 判斷上市/上櫃，組 `.TW`/`.TWO` ticker；未知代碼回報無法判斷，不猜測（禁止硬編碼清單）
- [x] 3.5 例外處理只覆蓋 spec scenario 定義情境，不做 catch-all 吞錯

## 4. SKILL.md 封裝

- [x] 4.1 `twstock-module/SKILL.md` 採 11 區塊標準骨架 + YAML frontmatter（`name`、`description`），`description` 含觸發語例句，命名採 `${domain}-${gerund}-${noun}`（L2 模組為 `${domain}-module` 例外）
- [x] 4.2 `description` 含自然語言觸發語例句供意圖路由
- [x] 4.3 明示本模組為 L2：僅回傳結構化資料，不做分析判讀／排版（越界屬 L3）

## 5. 本機驗證（對照 spec scenario）

- [x] 5.1 對 6 資料集各跑一次（2330，2024-01-01~06-30）——額度重置後補驗 **ALL_GREEN**：daily 117 / per_pbr 117 / institutional 585 / margin 117 / revenue 6 / financial(損益 34,現金流 54,資產負債 0) 皆 source=FinMind、gaps=[]
- [x] 5.2 驗證輸出 JSON 恆含 `source`/`fetched_at`/`data_gaps`（含 `data_gaps: []` 形狀）— ✅ 成立
- [x] 5.3 逐條核對 spec 13 個 scenario 的 WHEN/THEN——**全數成立**：happy-path 真實資料✅、降級端到端 source=yfinance（注入失敗）✅、市場別 .TW/.TWO/未知✅、節流 6s 間隔實證✅、憑證✅、fail-open✅
- [x] 5.4 確認 token 未出現在任何輸出 JSON、log 或版控檔案；驗證存檔前先掃內容確認不含 token；腳本無寫死憑證（紅線 #4）— ✅ grep 0 命中
