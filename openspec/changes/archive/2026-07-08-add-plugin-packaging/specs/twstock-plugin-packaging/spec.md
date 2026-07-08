## ADDED Requirements

### Requirement: Plugin manifest 與佈局

專案 SHALL 以 Claude Code plugin 形式可安裝：`.claude-plugin/plugin.json` MUST 存在於 repo 根，含 `name`、`description`、`version`；6 支 skill MUST 位於 `skills/<skill-name>/`（`skills/` 於 repo 根，非 `.claude-plugin/` 內）。`.claude-plugin/marketplace.json` MUST 存在使 repo 可經 `/plugin marketplace add` 註冊、`/plugin install` 安裝。

#### Scenario: manifest 與 skills 位置正確
- **WHEN** 檢視 repo
- **THEN** `.claude-plugin/plugin.json`（含 name/description/version）與 `.claude-plugin/marketplace.json` MUST 存在於根
- **AND** 全部 6 支 skill MUST 位於 `skills/twstock-*/`，各含其 SKILL.md

### Requirement: 跨 skill import 於 plugin 佈局下不斷

移入 `skills/` 後，各 skill 腳本之跨 skill 相對 import（`../../<skill>/scripts`）SHALL 仍解析——因 6 支為 `skills/` 下同層兄弟。所有腳本之 `--selftest` MUST 通過。

#### Scenario: selftest 全通
- **WHEN** 於新佈局執行各腳本 `--selftest`
- **THEN** finmind_fetcher／backtest／daily_screen／line_push 之 selftest MUST 全通過，import 不斷

### Requirement: 雙安裝法並存

專案 SHALL 同時支援 plugin 安裝（`/plugin install`）與手動安裝（`cp -R skills/twstock-* ~/.claude/skills/`）。README MUST 同時記載兩種安裝法。

#### Scenario: 兩種安裝法皆可
- **WHEN** 使用者選擇 plugin 或手動安裝
- **THEN** 兩法 MUST 皆可用，README MUST 皆記載
