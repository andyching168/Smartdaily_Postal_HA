#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

# 設置說明
# 請在此輸入您的裝置ID,儲存後把檔案上傳到config資料夾(有時被稱為homeassistant資料夾)中
DeviceID = ""

# API URL
url = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code=" + DeviceID

headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*"
}
KingnetAuthValue = ""
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
if response.status_code == 200:
    try:
        data = response.json()  # 嘗試解析 JSON
        KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
    except json.JSONDecodeError:
        #print("無法解析 JSON，請檢查回應格式")
        pass
else:
    exit()

url = "https://api.smartdaily.com.tw/api/Collection/getCollectionPayment"

# 自定義headers
headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*"
}

# 發送請求
response = requests.get(url, headers=headers)

# 檢查是否成功獲得響應
if response.status_code == 200:
    data = response.json()  # 解析JSON數據
    if "Data" in data and len(data["Data"]) > 0:
        # 未領取物品清單
        uncollected_items = [item for item in data["Data"] if item["is_end"] == 'no']
        # 已領取物品清單
        collected_items = [item for item in data["Data"] if item["is_end"] == 'yes']

        # 1. 優先抓取最新一筆未領取的寄放物，若沒有則抓取最新一筆記錄
        if uncollected_items:
            latest_collection = max(uncollected_items, key=lambda x: x["date"])
        else:
            latest_collection = max(data["Data"], key=lambda x: x["date"])

        status_text = "未領取" if latest_collection["is_end"] == 'no' else "已領取"
        # --- 修改處 1: 移除 .split("?")[0]，保留完整 URL ---
        collection_image = latest_collection["CollectionImage"] if latest_collection["CollectionImage"] else "https://img.smartdaily.com.tw/wordpress/smartdaily/homepage/LOGO.png"
        latest_info = {
            "serial_num": latest_collection["serial_num"],
            "date": latest_collection["date"],
            "status": status_text,
            "from_name": latest_collection["from_name"],
            "to_name": latest_collection["to_name"],
            "from_tablet": latest_collection.get("from_tablet", "Unavailable"),
            "to_tablet": latest_collection["to_tablet"],
            "c_dtype": latest_collection["c_dtype"],
            "c_money": latest_collection["c_money"],
            "sdate": latest_collection["sdate"],
            "ddate": latest_collection["ddate"],
            "collection_image": collection_image
        }

        # 計算尚未領取寄放物的數量
        uncollected_count = len(uncollected_items)
        latest_info["uncollected_count"] = uncollected_count

        # 2. 抓取最新一筆已領取的寄放物
        if collected_items:
            latest_collected = max(collected_items, key=lambda x: x["date"])
            collected_status_text = "已領取"
            # --- 修改處 2: 移除 .split("?")[0]，保留完整 URL ---
            collected_collection_image = latest_collected["CollectionImage"] if latest_collected["CollectionImage"] else "https://img.smartdaily.com.tw/wordpress/smartdaily/homepage/LOGO.png"
            collected_info = {
                "serial_num": latest_collected["serial_num"],
                "date": latest_collected["date"],
                "status": collected_status_text,
                "from_name": latest_collected["from_name"],
                "to_name": latest_collected["to_name"],
                "from_tablet": latest_collected.get("from_tablet", "Unavailable"),
                "to_tablet": latest_collected["to_tablet"],
                "c_dtype": latest_collected["c_dtype"],
                "c_money": latest_collected["c_money"],
                "sdate": latest_collected["sdate"],
                "ddate": latest_collected["ddate"],
                "collection_image": collected_collection_image
            }
        else:
            collected_info = {}

        # 用 JSON 輸出，分兩個區域：latest 和 collected
        output = {
            "latest": latest_info,
            "collected": collected_info
        }
        print(json.dumps(output, ensure_ascii=False, indent=4))
    else:
        print("沒有可用的記錄")
else:
    print("請求失敗，狀態碼:", response.status_code)
