## 1. Manifest

- [ ] 1.1 `.claude-plugin/plugin.json`：name=twstock、description、version、author、repository、license
- [ ] 1.2 `.claude-plugin/marketplace.json`：git source 指向本 repo、plugin 列 twstock

## 2. 佈局

- [ ] 2.1 `git mv` 6 支 `twstock-*` → `skills/twstock-*`（保留歷史）

## 3. 路徑同步（無行為變更）

- [ ] 3.1 README：手動安裝改 `cp -R skills/twstock-*`、加 plugin 安裝法、CLI 範例與連結加 `skills/`
- [ ] 3.2 CLAUDE.md：目錄結構樹改為 `skills/` 佈局 + 路徑引用同步
- [ ] 3.3 canonical specs：`twstock-*/{scripts,references}` 引用 → `skills/twstock-*/...`
- [ ] 3.4 references 內文/腳本註解的路徑指標同步

## 4. 驗證

- [ ] 4.1 各腳本 `--selftest` 全通（import 未斷）
- [ ] 4.2 grep 掃殘留 drift（排除 archive/相對）
- [ ] 4.3 核對 twstock-plugin-packaging 3 requirement
