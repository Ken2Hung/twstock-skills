"""twstock-notifying-line：LINE Messaging API 文字推播（零 pip 依賴，stdlib urllib）。

憑證只從環境變數讀（不寫死、不進版控）：
    LINE_CHANNEL_TOKEN  # LINE Official Account channel access token
    LINE_TO             # 推播對象 userId / groupId

token 永不出現在回傳結果或 log。所有失敗 fail-safe 回結構化結果、不 crash。

用法：
    LINE_CHANNEL_TOKEN=xxx LINE_TO=Uxxx python -X utf8 line_push.py --text "今日選股：..."
    python -X utf8 line_push.py --text "測試" --dry-run   # 離線組 payload，不送
    python -X utf8 line_push.py --selftest                 # 離線自我檢查
"""
import argparse
import json
import os
import urllib.error
import urllib.request

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def _payload(text, to):
    return {"to": to, "messages": [{"type": "text", "text": text}]}


def push(text, token=None, to=None, dry_run=False):
    """推播文字。回結構化結果 dict（不含 token）。失敗不 crash。"""
    token = token if token is not None else os.environ.get("LINE_CHANNEL_TOKEN", "")
    to = to if to is not None else os.environ.get("LINE_TO", "")
    payload = _payload(text, to)
    if dry_run:
        return {"ok": True, "dry_run": True, "payload": payload}   # 不含 token
    if not token or not to:
        return {"ok": False, "error": "缺 LINE_CHANNEL_TOKEN 或 LINE_TO（環境變數）"}
    req = urllib.request.Request(
        LINE_PUSH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"ok": resp.status == 200, "status": resp.status}
    except urllib.error.HTTPError as exc:
        # 回應內容可能含錯誤訊息，但不含我方 token；仍截斷避免其他洩漏
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", "replace")[:200]}
    except Exception as exc:  # noqa: BLE001 - 推播失敗一律 fail-safe，不中斷呼叫端
        return {"ok": False, "error": str(exc)[:200]}


def _selftest():
    tok = "SECRET_TOKEN_123"
    # 1) dry-run：回 payload、不送；token 不入回傳
    r = push("嗨", token=tok, to="Uabc", dry_run=True)
    assert r["ok"] and r["dry_run"], r
    assert r["payload"]["to"] == "Uabc"
    assert r["payload"]["messages"][0]["text"] == "嗨"
    assert tok not in json.dumps(r, ensure_ascii=False), "token 洩漏到回傳"
    # 2) 缺憑證 → fail-safe，不 crash
    r2 = push("嗨", token="", to="", dry_run=False)
    assert r2["ok"] is False and "error" in r2, r2
    # 3) payload 結構
    p = _payload("x", "Uy")
    assert p["messages"][0]["type"] == "text"
    print("selftest OK")


def main():
    p = argparse.ArgumentParser(description="LINE Messaging API 文字推播")
    p.add_argument("--text")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--selftest", action="store_true", help="離線自我檢查")
    args = p.parse_args()
    if args.selftest:
        _selftest()
        return
    if not args.text:
        p.error("--text 為必填（或用 --selftest）")
    print(json.dumps(push(args.text, dry_run=args.dry_run), ensure_ascii=False))


if __name__ == "__main__":
    main()
