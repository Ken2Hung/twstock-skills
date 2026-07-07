## 1. scoring-model.md 整合

- [ ] 1.1 籌碼面重配置為 法人 50%／融資融券 30%／股權分散 20%（清「股權分散 v-next」於 :17）
- [ ] 1.2 新增股權分散指標段：TDCC 分級 15（大戶）占集保比例 → 產業內百分位（snapshot level），大戶高→正向；趨勢列 v-next
- [ ] 1.3 更新 :45「股權分散未納入 v-next」→ 改為已納入（snapshot level）；保留 :44 融資結合股價位置 v-next
- [ ] 1.4 dataset 對應表補 shareholding

## 2. 文件同步

- [ ] 2.1 CLAUDE.md:86 籌碼面 → 「三大法人買賣超、融資融券變化、集保股權分散（大戶持股）」（移除 v-next）
- [ ] 2.2 finmind-api-cheatsheet.md 股權分散節補「評分用分級 15（大戶）占比、產業內百分位」

## 3. 驗證

- [ ] 3.1 核對 MODIFIED twstock-scoring R2（50/30/20 + 股權分散 snapshot 百分位 scenario）
- [ ] 3.2 全 repo 掃「股權分散 v-next」殘留（除 :44 融資位置那條）= 0
