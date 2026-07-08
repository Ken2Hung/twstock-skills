## Why

Change 2 建了 `strategy-presets.md` 空骨架、Change 4 定了 `scoring-model.md` 指標。v0.2 把 5 個 preset 參數化：各自覆寫面向權重、指定強調指標，讓「用 XX 策略挑…」能真正套用不同風格，且指標定義仍集中於 scoring-model.md。

## What Changes

- 填寫 `strategy-presets.md` 五個 preset（動能／價值／成長／高股息／法人籌碼），每個含：**面向權重覆寫**（基/技/籌，加總 100）、**3~5 個強調指標**（含 dataset 與方向）、所需 dataset、一句 rationale
- 強調指標為 **soft 連續評分**（非硬門檻），算法一律引用 `scoring-model.md`，preset 不另定義指標細節
- L3 場景 `twstock-screening-stocks`：使用者指名策略時 SHALL 套用該 preset 的權重覆寫與強調指標；未指名用預設 30/30/40

**Out of scope**：回測（v1.0）、新指標（只用 scoring-model 既有）、preset 的硬門檻（保持 soft）。

## Capabilities

### Modified Capabilities
- `tw-market-reference`: 「策略 preset 骨架」requirement → 「策略 preset 定義」，五 preset 由空骨架改為完整參數（面向權重覆寫 + 強調指標 + dataset）。
- `twstock-screening-orchestration`: 新增「策略 preset 套用」requirement——指名策略時套用其權重覆寫與強調指標，未指名用預設。

## Impact

- **修改**：`twstock-screening-stocks/references/strategy-presets.md`（填內容）、`twstock-screening-stocks/SKILL.md`（§7 註明可套 preset）
- **spec**：MODIFIED tw-market-reference、MODIFIED/ADDED twstock-screening-orchestration
- **無 code**（Claude 本體依 preset + scoring-model 執行）
- **依賴**：`scoring-model.md`（指標）、`tw-market-rules.md`（成本）
