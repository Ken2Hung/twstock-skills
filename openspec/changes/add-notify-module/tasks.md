## 1. line_push.py

- [ ] 1.1 建立 `twstock-notifying-line/scripts/line_push.py`
- [ ] 1.2 `push(text, token=None, to=None, dry_run=False)`：token/to 預設從 `LINE_CHANNEL_TOKEN`/`LINE_TO` env 讀
- [ ] 1.3 stdlib `urllib.request` POST 至 LINE push 端點，Bearer token，body `{to, messages:[{type:text,text}]}`
- [ ] 1.4 fail-safe：缺憑證/HTTP 錯/逾時 → 回 `{ok:false,error}`，不 crash；token 不入回傳/log
- [ ] 1.5 dry-run：離線回 payload、不送
- [ ] 1.6 CLI `--text --dry-run` + `--selftest`

## 2. SKILL.md

- [ ] 2.1 `twstock-notifying-line/SKILL.md`：推播模組（供場景委派），憑證 env 說明

## 3. 驗證

- [ ] 3.1 selftest（離線）：dry-run payload 結構正確、token 不在回傳；缺憑證回 ok:false
- [ ] 3.2 掃描：token 不出現在任何輸出（模擬 token 測）
- [ ] 3.3 核對 twstock-notify 3 scenario
