## 1. 實作

- [ ] 1.1 `fetch` 組裝路徑偵測整體 0 筆：list 型資料集 `len==0` → data_gaps 標「<dataset>: 空結果(0 筆)」
- [ ] 1.2 財報三表 dict 型：逐表偵測 0 筆 → data_gaps 標「financial.<statement>: 空結果(0 筆)」
- [ ] 1.3 不對「有資料但個別欄位缺值」逐欄標註；不更動 source
- [ ] 1.4 移除 `finmind_fetcher.py:155` 的 `ponytail:` 延後註記（債務 #3 關閉）

## 2. 驗證

- [ ] 2.1 更新 `--selftest`：斷言「成功但空 → data_gaps 含空結果標註」「有資料 → 不誤標」
- [ ] 2.2 實測 `financial`（balance_sheet 常回 0 筆）確認標註出現、source 不變
- [ ] 2.3 核對 spec 2 scenario（空標入 data_gaps、有資料不誤標）
