## Why

目前安裝需手動 `cp -R` 6 支 skill 到 `~/.claude/skills/`。打包成 **Claude Code plugin** 可一鍵安裝 + 自動更新（`/plugin marketplace add` → `/plugin install`）。

## 範圍評估（Ponytail）

- **零 Python code 變更**：跨 skill import 用 `../../<skill>/scripts`；6 支一起移進 `skills/` 後仍是同層兄弟，相對關係不變 → import 照舊（已驗）。
- **SKILL.md `../<skill>/...` 連結不變**（同層兄弟）。
- **唯一churn**：路徑引用同步（README 指令/連結、CLAUDE 目錄樹、canonical specs、references 內文）加 `skills/` 前綴——純文件，無行為變更。
- **雙安裝法並存**：plugin 或手動皆可。

## What Changes

- 新增 `.claude-plugin/plugin.json`（name/description/version/author/repository/license）
- 新增 `.claude-plugin/marketplace.json`（git source 指向本 repo）
- `git mv` 6 支 `twstock-*` → `skills/twstock-*`
- 同步路徑引用（specs / CLAUDE.md / README / references）為 `skills/...`
- README 安裝段加 plugin 安裝法（保留手動法）

**Out of scope**：拆成多 plugin、hooks/agents/MCP 打包、CI 自動發布（future）。

## Capabilities

### New Capabilities
- `twstock-plugin-packaging`: 專案以 Claude Code plugin 形式可安裝——`.claude-plugin/` manifest + 6 skills 於 `skills/`；跨 skill 相對 import 於 plugin 佈局下仍解析；plugin 與手動兩種安裝法並存。

## Impact

- **新增**：`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`
- **移動**：`twstock-*/` → `skills/twstock-*/`（git mv，保留歷史）
- **修改**：路徑引用（README/CLAUDE/canonical specs/references）
- **無 Python code、無行為變更**；openspec/、LICENSE、README、CLAUDE 留 root
