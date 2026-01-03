#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

# 設置說明
# 請在此輸入您的裝置ID和社區ID，儲存後把檔案上傳到config資料夾(有時被稱為homeassistant資料夾)中
DeviceID = ""
ComID = ""  # 社區ID，可在智生活APP或透過API_Test取得

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
        data = response.json()
        KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
    except json.JSONDecodeError:
        pass
else:
    print(json.dumps({"error": "Token request failed"}))
    exit()

# 獲取社區公告列表
list_url = f"https://api.smartdaily.com.tw/api/v3.24/Announcement/Community/List?ComId={ComID}&Offset=0&MaxCount=10"
list_headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*",
    "x-app-version": "4.5.2",
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(list_url, headers=list_headers)

if response.status_code == 200:
    data = response.json()
    announcements = data.get("Data", {}).get("Announcements", [])
    
    if announcements:
        # 取得最新一筆公告
        latest = announcements[0]
        announcement_id = latest.get("Id")
        
        # 獲取公告詳細內容
        detail_url = f"https://api.smartdaily.com.tw/api/v3.2/Announcement/Detail?com_id={ComID}&id={announcement_id}"
        detail_response = requests.get(detail_url, headers=list_headers)
        
        detail_data = {}
        attachments = []
        if detail_response.status_code == 200:
            detail_data = detail_response.json().get("Data", {})
            # 處理附件
            attached_files = detail_data.get("AttachedFile", [])
            attachments = [f.get("Url", "") for f in attached_files if f.get("Url")]
        
        # 處理內容，將 <br> 轉換為換行
        content = detail_data.get("Content") or detail_data.get("Detail", "")
        content = content.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
        # 移除其他 HTML 標籤
        import re
        content = re.sub(r'<[^>]+>', '', content)
        
        # 計算未讀公告數量（這裡簡化為總公告數）
        total_count = len(announcements)
        
        # 輸出結果
        result = {
            "latest": {
                "id": announcement_id,
                "title": latest.get("Title", ""),
                "start_date": latest.get("Start", ""),
                "end_date": latest.get("End", ""),
                "content": content,
                "attachments": attachments,
                "attachment_count": len(attachments)
            },
            "total_count": total_count,
            "announcements": [
                {
                    "id": ann.get("Id"),
                    "title": ann.get("Title", ""),
                    "start_date": ann.get("Start", "")
                }
                for ann in announcements[:5]  # 最多列出5筆
            ]
        }
        
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({
            "latest": {
                "id": "",
                "title": "無公告",
                "start_date": "",
                "end_date": "",
                "content": "",
                "attachments": [],
                "attachment_count": 0
            },
            "total_count": 0,
            "announcements": []
        }, ensure_ascii=False))
else:
    print(json.dumps({"error": f"API request failed: {response.status_code}"}, ensure_ascii=False))
