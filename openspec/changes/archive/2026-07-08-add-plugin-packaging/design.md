## Context

打包為 Claude Code plugin。官方結構：`.claude-plugin/plugin.json` + `skills/<name>/SKILL.md` 自動發現 + `.claude-plugin/marketplace.json` 分發（見 code.claude.com/docs/plugins）。

## Goals / Non-Goals

**Goals:** plugin 一鍵安裝、零 code 變更、路徑無 drift、雙安裝法並存。
**Non-Goals:** 多 plugin 拆分、hooks/agents/MCP、CI 發布（future）。

## Decisions

- **import 不改**：`../../<skill>/scripts` 在手動（`~/.claude/skills/`）與 plugin（`<cache>/skills/`）下，皆為「scripts 上兩層的兄弟 skill」，相對不變。發布前 `claude --plugin-dir ./` 本機驗證（使用者側），此 change 以 selftest 驗 import 未斷。
- **git mv 保留歷史**：`git mv twstock-* skills/`。
- **路徑同步範圍**：README（指令/連結/CLI 範例）、CLAUDE.md（目錄樹）、canonical specs、references 內文的 `twstock-*/…` → `skills/twstock-*/…`。SKILL.md 的 `../<skill>/…` 與 scripts 的相對 import 不動。
- **version 顯式 semver**（避免每 commit 都提示更新）。

## Risks / Trade-offs

- [plugin 安裝時 skills 是否同層 cached] → 官方以整個 repo 快取，`skills/` 樹完整；發布前 `--plugin-dir` 實測
- [路徑引用遺漏] → 完成後 grep 掃 `(^|[^/])twstock-[a-z-]*/(scripts|references)` 殘留（排除 archive/相對）

## Migration Plan
- 加 manifest → git mv → 同步路徑 → selftest → validate → 手動安裝指令改 `skills/twstock-*`
- Rollback：git mv 回 root、移除 manifest
## Open Questions
- 無（結構已由官方 docs 確認）。
