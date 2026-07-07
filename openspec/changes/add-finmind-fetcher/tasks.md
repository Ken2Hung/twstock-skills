## 1. Setup

- [ ] 1.1 `pip install yfinance`（日K fallback 依賴；FinMind、pandas 已裝）
- [ ] 1.2 建立 `twstock-module/scripts/` 目錄，移除 `twstock-module/.gitkeep`
- [ ] 1.3 確認 `FINMIND_TOKEN` 讀取方式（`os.environ.get`）；token 以 session-scoped 注入，不寫入任何檔案

## 2. 核心取得器（finmind_fetcher.py）

- [ ] 2.1 以 FinMind `DataLoader` 實作 6 資料集取得：日K、PER/PBR、三大法人買賣超、融資融券、月營收、財報三表（不自建 HTTP 封裝）
- [ ] 2.2 實作輸出組裝函式：所有 dataset 路徑統一補齊 `source` / `fetched_at` / `data_gaps`，保證 JSON 形狀恆定（`data_gaps` 空時仍為 `[]`）
- [ ] 2.3 CLI 介面：`--stock-id`、`--dataset`、日期區間參數，可 `python -X utf8 finmind_fetcher.py ...` 獨立執行
- [ ] 2.4 缺漏欄位一律進 `data_gaps`，禁止以舊資料／預設值填充（紅線 #5）

## 3. 韌性（降級／節流／市場別）

- [ ] 3.1 日K降級鏈：FinMind 回 402/429/逾時 → 改 yfinance，標註 `source: "yfinance"` 與 20 分鐘延遲警示
- [ ] 3.2 非日K資料集取不到 → 直接進 `data_gaps`，不降級、不中斷（fail-open）
- [ ] 3.3 Rate limit：依 `FINMIND_TOKEN` 有無切換 300/600 req/hr 上限，請求間以 `time.sleep` 節流（不引入 ratelimit 套件）
- [ ] 3.4 市場別：查 `TaiwanStockInfo` 判斷上市/上櫃，組 `.TW`/`.TWO` ticker；未知代碼回報無法判斷，不猜測（禁止硬編碼清單）
- [ ] 3.5 例外處理只覆蓋 spec scenario 定義情境，不做 catch-all 吞錯

## 4. SKILL.md 封裝

- [ ] 4.1 `twstock-module/SKILL.md` 採 11 區塊標準骨架 + YAML frontmatter（`name`、`description`），`description` 含觸發語例句，命名採 `${domain}-${gerund}-${noun}`（L2 模組為 `${domain}-module` 例外）
- [ ] 4.2 `description` 含自然語言觸發語例句供意圖路由
- [ ] 4.3 明示本模組為 L2：僅回傳結構化資料，不做分析判讀／排版（越界屬 L3）

## 5. 本機驗證（對照 spec scenario）

- [ ] 5.1 對 6 資料集各跑一次：`python -X utf8 twstock-module/scripts/finmind_fetcher.py --stock-id 2330 --dataset {daily,per_pbr,institutional,margin,revenue,financial}`，確認全通
- [ ] 5.2 驗證輸出 JSON 恆含 `source`/`fetched_at`/`data_gaps`（含 `data_gaps: []` 形狀）
- [ ] 5.3 逐條核對 spec 13 個 scenario 的 WHEN/THEN 是否成立，產出核對表
- [ ] 5.4 確認 token 未出現在任何輸出 JSON、log 或版控檔案；驗證存檔前先掃內容確認不含 token；腳本無寫死憑證（紅線 #4）
