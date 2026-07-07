# twstock-scoring

## Purpose

台股選股評分模型的知識層單一真相來源：綜合權重（基本面 30% / 技術面 30% / 籌碼面 40%）與
三面向指標定義（方向語意、回看窗口、量化門檻、對應 twstock-module dataset），以及缺面向降權重
正規化規則與 v1.0 long-only 假設。實體文件位於 twstock-screening-stocks/references/scoring-model.md，
由 twstock-screening-orchestration 消費。調整權重只改此層、不動選股流程。

## Requirements

### Requirement: 綜合評分權重為單一真相來源

評分模型的權重與各面向指標定義 SHALL 集中於 `twstock-screening-stocks/references/scoring-model.md` 作為單一真相來源。綜合評分 SHALL = 基本面 × 30% + 技術面 × 30% + 籌碼面 × 40%。調整任一權重 SHALL 只需修改 `scoring-model.md`，SHALL NOT 需改動 `twstock-screening-stocks` 的選股編排流程。各面向指標 MUST 於 `scoring-model.md` 標明對應之 twstock-module dataset。

#### Scenario: 權重與指標集中於單一檔案

- **WHEN** 檢視 `scoring-model.md`
- **THEN** MUST 含 30/30/40 綜合權重、三面向各自的指標定義，以及每個指標對應的 twstock-module dataset

#### Scenario: 調整權重不動選股流程

- **GIVEN** 需求為調整某面向的權重
- **WHEN** 套用調整
- **THEN** MUST 僅修改 `scoring-model.md`
- **AND** SHALL NOT 改動 `twstock-screening-stocks` 的選股編排流程

### Requirement: 籌碼面配置與指標方向語意

籌碼面 40% SHALL 內部配置為：三大法人買賣超連續性 50%、融資融券變化 30%、集保股權分散（大戶持股）20%。法人子項 SHALL 僅計外資（`Foreign_Investor`）與投信（`Investment_Trust`）之淨買超，SHALL NOT 計入自營避險（`Dealer_Hedging`、`Foreign_Dealer_Self`）。法人淨買超與融資／融券變化 MUST 以**相對量**（佔同期成交量比）計，SHALL NOT 以絕對張數或金額計，以免評分系統性偏向大型股。融資「大增」MUST 以量化門檻定義（5 日融資增量佔同期成交量比超過 `scoring-model.md` 所定門檻）。集保股權分散 SHALL 以 TDCC 集保分級 15（≥1,000,001 股，大戶）之占集保庫存比例計；因 TDCC 開放資料（`id=1-5`）僅最新週快照、無歷史，v1.0 SHALL 以該比例之**產業內百分位（snapshot level）**評分（大戶持股比例高 → 正向），SHALL NOT 依賴跨週趨勢；股權分散**趨勢**評分列 v-next（需歷史快照累積）。法人與融資融券之回看窗口 SHALL 統一為 5 日。`scoring-model.md` MUST 為每個籌碼指標定義方向語意（正向／負向）、回看窗口／評分基準與量化門檻，使評分可驗證。

#### Scenario: 法人子項排除自營避險

- **WHEN** 計算三大法人籌碼分
- **THEN** MUST 僅計外資與投信之淨買超
- **AND** MUST NOT 計入 `Dealer_Hedging`、`Foreign_Dealer_Self` 之避險部位

#### Scenario: 法人連續淨買為正向（回看窗口）

- **GIVEN** 外資或投信於 `scoring-model.md` 定義之回看窗口內連續淨買超
- **WHEN** 計算籌碼分
- **THEN** 法人子項 MUST 給正向分數，且連續性愈強分數愈高

#### Scenario: 以相對量計避免大型股偏差

- **WHEN** 計算法人或融資／融券籌碼分
- **THEN** MUST 以佔同期成交量比等相對量計
- **AND** SHALL NOT 以絕對張數或金額計，以免評分系統性偏向大型股

#### Scenario: 融資餘額短期大增為負向

- **GIVEN** 融資餘額於 5 日內之增量佔同期成交量比超過 `scoring-model.md` 所定門檻（散戶槓桿過熱）
- **WHEN** 計算籌碼分
- **THEN** 融資子項 MUST 給負向分數

#### Scenario: 融券／借券賣出增為負向、回補為正向

- **GIVEN** 融券餘額或借券賣出於回看窗口內增加
- **WHEN** 計算籌碼分
- **THEN** 該子項 MUST 給負向分數
- **AND** 當融券大幅回補時 MUST 給正向分數（軋空動能）

#### Scenario: 集保股權分散以大戶持股比例產業內百分位計

- **GIVEN** TDCC 回傳某標的最新週集保股權分散（含分級 15 大戶占比）
- **WHEN** 計算股權分散子項分數
- **THEN** MUST 以分級 15 之占集保庫存比例於同產業內百分位計（snapshot level），大戶持股比例高者給正向
- **AND** SHALL NOT 依賴跨週趨勢（TDCC `id=1-5` 僅最新快照），趨勢評分列 v-next

#### Scenario: 方向語意與回看窗口須明文定義

- **WHEN** 檢視 `scoring-model.md` 的籌碼面段落
- **THEN** 每個籌碼指標 MUST 標明方向語意（正向／負向）與回看窗口／評分基準，使 scenario 可驗證

### Requirement: 基本面同產業內百分位評分

基本面 SHALL 以標的在**同產業別**（依 `TaiwanStockInfo` 的 `industry_category`）內的百分位評分，指標含月營收 YoY、EPS 成長、ROE；SHALL 獎勵二階改善（連續改善／加速）。基本面 SHALL NOT 以絕對硬門檻二元排除標的（硬門檻屬 L3 使用者明訂之篩選條件，非評分模型職責），以免砍掉成長股。月營收 YoY 之百分位 SHALL 以近 6 月計、二階改善以近 3 月計；EPS 成長與 ROE 以近 4 季計。為消除農曆年落點失真，1 月與 2 月之月營收 YoY MUST 合併計算。

#### Scenario: 以同產業內百分位計分

- **GIVEN** 某標的的月營收 YoY／EPS 成長／ROE
- **WHEN** 計算基本面分
- **THEN** MUST 以該標的在同產業（`TaiwanStockInfo.industry_category`）內的百分位計，SHALL NOT 以跨產業絕對值直接比較

#### Scenario: 不以硬門檻砍掉成長股

- **GIVEN** 一檔 EPS 偏低或為負、但成長率高的成長股
- **WHEN** 計算基本面分
- **THEN** SHALL NOT 因未達某絕對門檻而二元排除
- **AND** MUST 以成長率與二階改善反映其分數

#### Scenario: 二階改善加分

- **GIVEN** 標的月營收 YoY 於近 3 月連續改善／加速
- **WHEN** 計算基本面分
- **THEN** 基本面分 MUST 反映此二階改善

#### Scenario: 農曆年 1、2 月營收合併計 YoY

- **GIVEN** 計算 1 月或 2 月的月營收 YoY
- **WHEN** 產生基本面月營收分
- **THEN** MUST 將 1、2 月合併計算 YoY，以消除農曆年落點造成的單月失真

### Requirement: 技術面核心與乖離率風險 overlay

技術面 30% SHALL 以均線多頭排列與量價關係為評分核心。乖離率 SHALL NOT 計入技術面評分；乖離率 SHALL 作為風險 overlay，於乖離過大時輸出至決策看板「風險提示」欄位。

#### Scenario: 技術面評分不含乖離率

- **WHEN** 計算技術面分
- **THEN** MUST 由均線多頭排列與量價關係構成
- **AND** MUST NOT 將乖離率計入技術面分數

#### Scenario: 乖離率作為風險提示 overlay

- **GIVEN** 標的正乖離過大（追高風險）
- **WHEN** 輸出決策看板
- **THEN** 乖離狀態 MUST 反映於「風險提示」欄位（如「乖離過大，追高留意回檔」）
- **AND** 該乖離 MUST NOT 影響技術面評分

### Requirement: 缺面向降權重正規化

當某面向因 `data_gaps` 缺關鍵資料而無法評分時，綜合評分 SHALL 以剩餘可評分面向的權重**重新正規化**後計算，SHALL NOT 以預設值、中位數或任何填充值補足缺失面向。缺面向情況 SHALL 反映於看板的 `data_gaps` 與「判讀基於不完整資料」揭露。

#### Scenario: 剩餘面向重新正規化

- **GIVEN** 籌碼面因 `data_gaps` 無法評分，而基本面與技術面可評分
- **WHEN** 計算綜合評分
- **THEN** MUST 以基本面、技術面各自權重重新正規化（30/(30+30)=50% 對 50%）後加權
- **AND** SHALL NOT 給籌碼面任何預設分數

#### Scenario: 禁止以預設值填充缺失面向

- **GIVEN** 某面向缺關鍵資料
- **WHEN** 計算綜合評分
- **THEN** SHALL NOT 以 0 分、中位數或預設分填充該面向充數
