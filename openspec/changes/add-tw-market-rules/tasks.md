## 1. tw-market-rules.md

- [ ] 1.1 建立 `twstock-screening-stocks/references/tw-market-rules.md`
- [ ] 1.2 交易成本：買進 0.1425%（手續費）、賣出 0.4425%（手續費 0.1425% + 證交稅 0.3%），明列拆解
- [ ] 1.3 漲跌停 ±10%、觸及時的流動性風險註記
- [ ] 1.4 處置股警示規則（TWSE 處置名單來源與處置期間交易限制）
- [ ] 1.5 上市（`.TW`）／上櫃（`.TWO`）市場別對照
- [ ] 1.6 明示：本檔為下游損益計算的成本單一真相來源，禁止程式碼硬編碼
- [ ] 1.7 成本現實性註記（知識備註，非 spec requirement）：(a) 0.1425% 為**牌告費率**，實務券商多有折扣，本專案採牌告價為**保守基準**；(b) 手續費**低消 20 元**，小額單實際成本率高於名目費率；(c) 現股當沖證交稅減半（0.15%）為**時限性制度**，標註「使用前查證現行狀態」，不寫死

## 2. finmind-api-cheatsheet.md

- [ ] 2.1 建立 `references/finmind-api-cheatsheet.md`
- [ ] 2.2 逐列 6 資料集（daily/per_pbr/institutional/margin/revenue/financial）：dataset key、DataLoader 方法名、關鍵欄位、參數、呼叫範例
- [ ] 2.3 方法名對齊 `twstock-module/scripts/finmind_fetcher.py`（不憑空列端點）

## 3. strategy-presets.md

- [ ] 3.1 建立 `references/strategy-presets.md`
- [ ] 3.2 五個 preset 空骨架：動能／價值／成長／高股息／法人籌碼
- [ ] 3.3 每個 preset 採一致模板欄位（名稱／面向權重／門檻／所需資料集），值留空
- [ ] 3.4 每個 preset 標註「內容 v0.2 待填」，不寫實際門檻值

## 4. 收尾與驗證

- [ ] 4.1 移除 `twstock-screening-stocks/references/.gitkeep`
- [ ] 4.2 核對 spec 3 requirement 的 scenario：成本/規則齊備、cheatsheet 六資料集且與實作一致、五 preset 骨架標註待填
