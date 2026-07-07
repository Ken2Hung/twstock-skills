## 1. 資料層實作（finmind_fetcher.py）

- [x] 1.1 實測確認 FinMind `taiwan_stock_holding_shares_per` 為付費層專屬（free tier 回「your level is free」），改採 TDCC 開放資料 `id=1-5`
- [x] 1.2 新增 `TDCC_SHAREHOLDING_URL` 常數與 `_tdcc_shareholding()`：`pd.read_csv` 讀全市場 CSV、`證券代號` strip 後過濾單檔，回原始持股分級列
- [x] 1.3 `fetch()` 最前加 `dataset == "shareholding"` 分支；`DATASETS` 加入 `shareholding`
- [x] 1.4 fail-open：TDCC 取數失敗或查無證券 → `data_gaps` + `source: none`，不降級、不 crash
- [x] 1.5 Revert 實作中一度為 FinMind 付費層加的 `_is_source_failure`/`_reason`/selftest 等級判斷（改走 TDCC 後無觸發者，Ponytail YAGNI）
- [x] 1.6 `--selftest` 離線形狀自檢通過

## 2. 文件同步

- [x] 2.1 `twstock-module/SKILL.md`：能力總覽表（來源欄改標；shareholding 標 TDCC）、輸入契約（shareholding 不吃日期區間）、資料源段（TDCC fail-open）
- [x] 2.2 `finmind-api-cheatsheet.md`：標題改「7 種＝6 FinMind + 1 TDCC」，shareholding 改為 TDCC 專節（端點、中文欄位、持股分級對照含分級 15 大戶、僅最新快照）

## 3. 本機驗證（spec scenarios）

- [x] 3.1 實測 `--stock-id 2330 --dataset shareholding`：`source: "TDCC"`、`data_gaps: []`、17 個持股分級全取、分級 15（大戶）占比 85.09% ✓（正向路徑通過）
- [x] 3.2 驗證 dataset choices 已含 `shareholding`（CLI 不報未知 dataset）

## 4. 後續依賴註記（不在本 change 範圍）

- [x] 4.1 於 change 說明明載：籌碼面權重重分配（法人/融資券/股權分散三分法）、`scoring-model.md`、CLAUDE.md 評分模型段落，均由後續 `add-scoring-model`（Change 4）處理，本 change 僅補資料層取數能力
- [x] 4.2 標註限制：TDCC `id=1-5` 僅最新週快照，「股權分散趨勢」需跨週歷史累積，屬日後另開 change 的歷史回補，非本次範圍
