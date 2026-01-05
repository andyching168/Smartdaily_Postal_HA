#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
單獨查詢退貨包裹清單的輕量腳本。
使用方式：
1. 填入 DeviceID 與 ComID。
2. 上傳到 Home Assistant 的 config 資料夾後，以 command_line sensor 執行。
"""
import json
import sys
import requests

# 設置說明：請填入您的裝置ID與社區ID
DeviceID = ""
ComID = ""

TOKEN_URL = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code={device_id}"
RETURN_URL = "https://api.smartdaily.com.tw/api/Postal/getReturnPostalList?com_id={com_id}"


def _status_text(status_val):
    if status_val in (0, 1):
        return "未取件"
    if status_val == 2:
        return "已取件"
    return f"未知狀態({status_val})" if status_val is not None else "未知"


def _build_item(pkg):
    status_val = pkg.get("p_status", pkg.get("status"))
    return {
        "serial_num": pkg.get("serial_num", ""),
        "create_date": pkg.get("create_date", ""),
        "status": _status_text(status_val),
        "status_code": status_val,
        "transport_code": pkg.get("transport_code", ""),
        "postal_type": pkg.get("postal_typeText", ""),
        "logistics": pkg.get("postal_logisticsText") or pkg.get("logisticsName", ""),
        "storage": pkg.get("tablet_note", pkg.get("p_note", "")),
        "image": pkg.get("postal_img", ""),
        "sign_image": pkg.get("sign_image", ""),
        "return_date": pkg.get("retuen_date", ""),  # API 的欄位即為 retuen_date
    }


def main():
    if not DeviceID or not ComID:
        print(json.dumps({"error": "請先在腳本中填入 DeviceID 與 ComID"}, ensure_ascii=False))
        sys.exit(0)

    try:
        token_resp = requests.get(TOKEN_URL.format(device_id=DeviceID), headers={
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
        })
        token_resp.raise_for_status()
        token = "CommunityUser " + token_resp.json()["Data"]["token"]
    except Exception:
        print(json.dumps({"error": "取得權杖失敗，請確認 DeviceID"}, ensure_ascii=False))
        sys.exit(0)

    try:
        resp = requests.get(
            RETURN_URL.format(com_id=ComID),
            headers={
                "Connection": "keep-alive",
                "KingnetAuth": token,
                "Accept": "application/json, text/plain, */*",
            },
        )
        resp.raise_for_status()
        data = resp.json().get("Data", [])
    except Exception:
        print(json.dumps({"error": "取得退貨清單失敗，請確認 ComID"}, ensure_ascii=False))
        sys.exit(0)

    items = [_build_item(pkg) for pkg in data]
    latest = items[0] if items else {"status": "無退貨包裹"}

    output = {
        "latest": latest,
        "count": len(items),
        "items": items,
    }
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
