# 策略 Preset 參數化

本文件定義 5 組選股風格 preset，供 `twstock-screening-stocks` 場景引用。每個 preset 是**精簡參數集**——覆寫面向權重 + 3~5 個強調指標與方向 + 一句 rationale，不發明新指標，只從既有可用指標中挑選。

- **面向權重覆寫**：綜合評分預設權重為 基本面 30% / 技術面 30% / 籌碼面 40%。各 preset 可覆寫此三面向權重以凸顯風格，**三者加總必為 100**。權重僅調面向間配比，面向內指標定義不變。
- **強調指標為 soft 連續評分**：所有強調指標皆為連續評分 / 產業內百分位，**非硬門檻**——不做「未達標即剔除」的 filter，只影響該面向得分高低。方向欄標示指標對得分的正負作用。
- **指標定義以 `scoring-model.md` 為準**：本文件只列「哪個 preset 強調哪些指標與方向」，指標的計算方式（百分位窗口、連續日數、量比基準等）一律以 `scoring-model.md` 為單一真相，此處 note 僅為風格說明。
- **交易成本引用 `tw-market-rules.md`**：回測與損益計算的成本（買 0.1425% / 賣 0.4425%）一律引用 `tw-market-rules.md`，preset 不重複定義成本參數。
- **v1.0 long-only**：所有 preset 於 v1.0 僅作多，方向欄的「正 / 負」意指「拉高 / 壓低多方評分」，不含放空語意。
- **產業別百分位 universe**：凡標示「產業內百分位」的指標，其產業分組以 `TaiwanStockInfo.industry_category` 為 universe 界定，此為分組依據而非取數 dataset。

可用 dataset：`daily`、`per_pbr`、`institutional`、`margin`、`revenue`、`financial`、`shareholding`。

---

## 動能（momentum）

追強勢股：技術面與法人動能雙主軸並列加重，基本面僅留輕量護欄。

**面向權重（加總 100）**：基本面 20 ｜ 技術面 40 ｜ 籌碼面 40

**強調指標**

| 指標 | dataset | 方向 |
|---|---|---|
| 均線多頭排列（5>20>60） | `daily` | 多頭排列＝正（核心趨勢骨幹，追強勢股的技術結構） |
| 量價關係 | `daily` | 量增價漲＝正（以 5 日均量比確認量能推動，濾掉無量假突破） |
| 三大法人淨買超 | `institutional` | 淨買超佔成交量比 >3%、連 5 日＝正（法人連買為主力點火訊號，越連續分越高） |
| 融資融券 | `margin` | 融券大幅回補＝正、融資淨減＝正（軋空回補提供上攻動能，浮額洗清減輕賣壓） |
| 月營收 YoY | `revenue` | 近 6 月百分位高＝正（輕量品質護欄，確保追的是有基本面撐腰的強勢股） |

**所需 dataset**：`daily`、`institutional`、`margin`、`revenue`

**Rationale**：追強勢股——以技術面（均線多頭 + 量增價漲）與法人動能（連 5 日淨買、軋空回補）為雙主軸並列加重，基本面僅留月營收 YoY 作輕量護欄，過濾無基本面撐腰的空頭拉抬。

---

## 價值（value）

找便宜好公司：低估值選標的，品質指標排除價值陷阱。

**面向權重（加總 100）**：基本面 55 ｜ 技術面 20 ｜ 籌碼面 25

**強調指標**

| 指標 | dataset | 方向 |
|---|---|---|
| PER 本益比 | `per_pbr` | 低＝正（同產業內百分位，愈低愈便宜，價值風格第一訴求） |
| PBR 股價淨值比 | `per_pbr` | 低＝正（同產業內百分位，與 PER 互補，避免景氣循環股單看 PER 失真） |
| ROE | `financial` | 高＝正（近 4 季同產業百分位，過濾「便宜但爛」的價值陷阱） |
| EPS 成長 | `financial` | 轉正 / 成長＝正（近 4 季，確保便宜非來自獲利衰退） |
| 三大法人淨買超 | `institutional` | 連續淨買＝正（外資 + 投信佔量比連 5 日，避免價值股長期被冷落無催化） |

**所需 dataset**：`per_pbr`、`financial`、`institutional`（產業分組依 `TaiwanStockInfo.industry_category`）

**Rationale**：找便宜好公司——以低 PER/PBR 選便宜、ROE 把關品質、EPS 成長排除價值陷阱，基本面為主軸，技術與籌碼僅作進場時機與催化的輔助確認。

---

## 成長（growth）

高成長選股：營收與獲利成長主導，容忍較高估值。

**面向權重（加總 100）**：基本面 50 ｜ 技術面 30 ｜ 籌碼面 20

**強調指標**

| 指標 | dataset | 方向 |
|---|---|---|
| 月營收 YoY | `revenue` | 正（近 6 月產業內百分位 + 近 3 月二階改善；1、2 月合併計 YoY 規避農曆年落點失真） |
| EPS 成長 | `financial` | 正（近 4 季產業內百分位；由負轉正加分，不硬性要求 EPS>0 以保留 pre-profit 成長股） |
| ROE | `financial` | 正（近 4 季產業內百分位，確認成長由真實獲利驅動而非單純營收膨脹） |
| 均線多頭排列（5>20>60） | `daily` | 正（確認市場已認同成長趨勢，避免價格未反映的價值陷阱） |
| 三大法人淨買超 | `institutional` | 正（外資 + 投信佔量比連 5 日，成長股常見法人卡位，作輕量籌碼佐證） |

**所需 dataset**：`revenue`、`financial`、`daily`、`institutional`（產業分組依 `TaiwanStockInfo.industry_category`）

**Rationale**：高成長選股以月營收 YoY 與 EPS 成長為主軸、ROE 確認獲利品質，基本面加重至 50%；容忍較高估值故不納入 PER/PBR，技術面 30% 以均線多頭確認趨勢已被市場認同，籌碼降至 20% 作法人卡位佐證。

---

## 高股息（high-dividend）

鎖定穩定高殖利率，品質指標濾除硬配息的價值陷阱。

**面向權重（加總 100）**：基本面 55 ｜ 技術面 25 ｜ 籌碼面 20

**強調指標**

| 指標 | dataset | 方向 |
|---|---|---|
| 殖利率 dividend_yield | `per_pbr` | 高＝正（同產業百分位愈高愈佳，高股息核心強調指標） |
| EPS 成長 | `financial` | 正（近 4 季成長 / 由負轉正加分，濾除賺不到錢卻硬配息者） |
| ROE | `financial` | 正（近 4 季同產業百分位，佐證獲利品質可支撐配息持續性） |
| 三大法人淨買超 | `institutional` | 正（外資 + 投信佔量比連 5 日，法人不棄守作為避免價值陷阱旁證） |

**所需 dataset**：`per_pbr`、`financial`、`institutional`（產業分組依 `TaiwanStockInfo.industry_category`）

**Rationale**：以基本面主導（55）鎖定穩定高殖利率並用 EPS/ROE 品質濾除價值陷阱，籌碼壓至 20 僅留法人不棄守作旁證，技術 25 供進場擇時。

---

## 法人籌碼（institutional）

跟法人籌碼：外資投信連買、融資減、大戶集中為主導訊號。

**面向權重（加總 100）**：基本面 15 ｜ 技術面 30 ｜ 籌碼面 55

**強調指標**

| 指標 | dataset | 方向 |
|---|---|---|
| 三大法人淨買超（外資 + 投信連買） | `institutional` | 正（佔同期成交量比連 5 日 >3%；僅計 Foreign_Investor + Investment_Trust，排除自營避險雜訊，連買愈久分愈高） |
| 融資淨變動 | `margin` | 正（5 日融資淨減佔量比 >5%＝正之浮額洗清、淨增＝負之散戶槓桿過熱；法人進場同時融資減＝籌碼由散戶轉法人） |
| 融券回補 | `margin` | 正（融券大幅回補＝正之軋空動能、餘額增＝負之賣壓；法人主導下的次要籌碼確認） |
| 集保大戶持股集中（分級 15，≥1,000,001 股） | `shareholding` | 正（大戶占集保庫存比之同產業內百分位愈高＝正；snapshot level 水位計，不算趨勢） |
| 量價關係確認 | `daily` | 正（量增價漲＝正、量增價跌＝負，以 5 日均量比判斷；驗證法人買超是否有真實承接量能） |

**所需 dataset**：`institutional`、`margin`、`shareholding`、`daily`（產業分組依 `TaiwanStockInfo.industry_category`）

**Rationale**：跟法人籌碼——外資投信連買、融資減、大戶持股集中，籌碼面加重至 55% 為主導訊號，技術面量價僅作進場承接量能確認，基本面留 15% 防基本面惡化的籌碼陷阱。

---

## 設計註記

- **面向權重加總皆 100**：momentum 20/40/40、value 55/20/25、growth 50/30/20、high-dividend 55/25/20、institutional 15/30/55。
- **`TaiwanStockInfo` 非評分 dataset**：它是「產業內百分位」的分組 universe（`industry_category`），非取數 dataset，故不列入各 preset 的「所需 dataset」，改以括號標註。
- **門檻校準**：各方向 note 內的量化門檻（法人 >3%、融資 >5% 等）以 `scoring-model.md` 為準，v1.0 回測後統一校準。
