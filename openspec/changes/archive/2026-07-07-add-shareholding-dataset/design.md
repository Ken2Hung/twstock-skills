## Context

`twstock-module` 目前以 `FINMIND_METHODS` 字典把 5 個單次呼叫資料集映射到 FinMind DataLoader 方法，另有 `financial` 組合資料集。要新增「股權分散」以供籌碼面使用。實作階段實測發現：FinMind 的股權分散端點 `taiwan_stock_holding_shares_per` 為**付費層專屬**，free tier 帳號回「your level is free」而取不到資料；且使用者短期不升級付費層。因此改採**免費的官方開放資料源**——這正符合本專案資料源降級鏈「FinMind（主）→ 官方開放資料 → yfinance」的既定哲學。

## Goals / Non-Goals

**Goals:**
- 以免費且可長期取得的來源補齊籌碼面第三項訊號「股權分散」，輸出契約與現有資料集一致（`source`/`fetched_at`/`data_gaps` 恆存）。

**Non-Goals:**
- 不做評分模型權重重分配、不建 `scoring-model.md`、不動 CLAUDE.md 評分段落（屬 `add-scoring-model`）。
- 不引入付費 FinMind 方案、不新增第三方套件（用既有 pandas 讀 CSV）。
- 不做歷史回補（TDCC `id=1-5` 僅最新週結快照；歷史序列若日後需要另開 change）。

## Decisions

**D1：股權分散改採 TDCC 集保結算所開放資料，放棄 FinMind 付費端點。**
- 實測：`taiwan_stock_holding_shares_per` 在 free tier 回「your level is free / update your user level」，帳號不升級則永遠取不到。
- TDCC `https://opendata.tdcc.com.tw/getOD.ashx?id=1-5` 免費、全市場、週更，回傳 CSV 含各持股分級人數／股數／占比，實測 2330 有 17 個分級（分級 15 = 大戶，占 85.09%），完全滿足籌碼面「大戶持股」訊號需求。
- 符合專案「官方開放資料」降級哲學；集保是股權分散的權威來源，比 FinMind 轉手更直接。

**D2：以獨立分支 `_tdcc_shareholding` 處理，不塞進 `FINMIND_METHODS`。**
- 股權分散非 FinMind 端點、來源機制不同（HTTP CSV 全市場過濾 vs DataLoader 單檔），比照 `financial` 組合資料集用專屬分支。`dataset == "shareholding"` 於 `fetch()` 最前分支攔截。
- Ponytail：直接 `pd.read_csv(url)`（pandas 已是既有依賴，階梯 5/6），不自建 requests 封裝、不引入 HTTP 套件。TDCC 無 SDK，直接讀 CSV 是平台原生最短路徑。

**D3：`shareholding` 不吃日期區間，只回最新週結快照。**
- `id=1-5` 端點本身僅含最新一週（實測資料日期單一值），無區間參數。`start_date`/`end_date` 給了也忽略，於 SKILL.md／cheatsheet 明確標註，避免下游誤以為可取歷史。
- `資料日期` 欄已在回傳資料列中，下游可讀取快照日期，故成功時 `data_gaps` 仍為 `[]`（不硬塞快照註記）。

**D4：fail-open。TDCC 取數失敗或查無證券 → `data_gaps` + `source: none`，不降級。**
- yfinance 無股權分散，無其他降級源。任何 fetch 例外（網路／格式）一律 fail-open 進 `data_gaps`，主鏈路不中斷（外部開放資料屬 best-effort，比照非 daily 資料集不降級）。
- 因改走 TDCC，FinMind「付費層等級不足」錯誤已無觸發者，實作階段一度加入 `_is_source_failure` 的等級判斷已 revert（Ponytail：無觸發者即 YAGNI）。

## Risks / Trade-offs

- [TDCC 僅最新週快照、無歷史] → 本 change 只提供當週大戶持股水位；「趨勢」需跨週累積，屬日後另開 change 的歷史回補，非本次範圍。已於文件標註，不腦補歷史。
- [TDCC 欄位為中文、`證券代號` 有空白 padding] → 過濾前 `str.strip()`；欄位以實測為準寫入 cheatsheet，不硬編碼假設。
- [TDCC 端點格式若日後變動] → 比照現有資料集由實測修訂；fail-open 確保格式異動不會 crash 主鏈路。
