## MODIFIED Requirements

### Requirement: 目標價與止損價引用交易成本真相來源

目標價與止損價 MUST 以**市場價**（新台幣元）呈現，供觸價判定使用；交易成本 SHALL NOT 扣入價位數字本身。**預期報酬率**（期望損益）之計算 MUST 引用 tw-market-reference（twstock-screening-stocks/references/tw-market-rules.md）之來回交易成本（買 0.1425% + 賣 0.4425%）扣除，場景層 SHALL NOT 硬編碼另一套交易成本數字。在 v1.0 **long-only 假設**下（信號「賣出／觀望」= 不建議買進／退出已持有，非做空），價位 SHALL 滿足 止損價 ≤ 現價 ≤ 目標價；做空／減碼之方向反轉語意列為 future scope（脈絡見已歸檔的 add-screening-skill design.md）。標的若觸及漲跌停（±10%）或位於 TWSE 處置名單，場景 MUST 依 tw-market-reference 於風險提示欄位標註流動性風險。

#### Scenario: 價位以市場價呈現、成本不入價位

- **GIVEN** 場景輸出某標的的目標價與止損價
- **WHEN** 呈現這兩個價位
- **THEN** 兩者 MUST 為市場價（新台幣元），供觸價判定使用
- **AND** 交易成本 SHALL NOT 扣入價位數字本身

#### Scenario: 預期報酬率扣除來回成本

- **GIVEN** 場景計算某標的的預期報酬率或期望損益
- **WHEN** 計算報酬
- **THEN** MUST 引用 tw-market-reference 的來回交易成本（買 0.1425% + 賣 0.4425%）扣除
- **AND** SHALL NOT 於場景層硬編碼另一套交易成本數字

#### Scenario: long-only 假設下價位不等式成立

- **GIVEN** v1.0 採 long-only（信號賣出／觀望為不建議買進／退出，非做空）
- **WHEN** 產出目標價與止損價
- **THEN** 價位 MUST 滿足 止損價 ≤ 現價 ≤ 目標價
- **AND** 做空／減碼之方向反轉語意 SHALL 列為 future scope

#### Scenario: 觸及漲跌停或處置股標註流動性風險

- **GIVEN** 某標的觸及 ±10% 漲跌停或位於 TWSE 處置名單
- **WHEN** 場景輸出該標的看板
- **THEN** 風險提示欄位 MUST 依 tw-market-reference 明確標註流動性風險
