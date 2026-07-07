## MODIFIED Requirements

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
