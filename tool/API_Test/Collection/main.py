#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
DeviceID=input("請輸入您的裝置ID:")
# API URL
url = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code="+DeviceID


headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*"
}
KingnetAuthValue=""
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
if response.status_code == 200:
    print("Success!\nResult:\n")
    print(response.text)  # 查看回應的實際內容
    try:
        data = response.json()  # 嘗試解析 JSON
        KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
        print(KingnetAuthValue)
    except json.JSONDecodeError:
        print("無法解析 JSON，請檢查回應格式")
else:
    print("請求失敗，狀態碼:", response.status_code)
    exit()

# 自定義headers
headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*"
}
url = "https://api.smartdaily.com.tw/api/Community/GetUserCommunityList"
response = requests.get(url, headers=headers)
community_dict = {}
if response.status_code == 200:
    print("成功，以下是您的社區列表:\n")
    # 解析JSON數據
    data = response.json()

    i = 1
    for com in data["Data"]:
        print(f"{i}. 社區名稱: {com['community']}, ID: {com['id']}")
        community_dict[i] = com['id']
        i += 1
else:
    print("請求失敗，狀態碼:", response.status_code)
    print(response.text)
    exit()
Com_ID=0
# 让用户选择社区ID
try:
    choice = int(input("\n請輸入要查詢的社區編號: "))
    Com_ID = community_dict[choice]
except ValueError:
    print("請輸入有效的編號！")
    exit()
except KeyError:
    print("編號不在列表中！")
    exit()

url = "https://api.smartdaily.com.tw/api/Collection/getCollectionPayment"

# 自定義headers
headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*"
}


# 如果有需要發送的數據
data = {
    # 在這裡添加您的數據
}

# 發送請求
response = requests.get(url, headers=headers)


# 檢查是否成功獲得響應
if response.status_code == 200:
    print("Success!\nResult:\n")
    print(response.text)
    print("\n------Beautify------\n")
    # 解析JSON數據
    data = response.json()
        # 遍歷並按照指定格式打印每個寄放物品的詳細信息
    for collection in data["Data"]:
        # 處理寄放狀態
        status_text = "未領取" if collection["is_end"] == 'no' else "已領取"

        print(f'#{collection["serial_num"]} {collection["date"]} {status_text}')
        print(f'寄放者姓名: {collection["from_name"]}')
        print(f'領取者姓名: {collection["to_name"]}')
        print(f'寄放者住址: {collection.get("from_tablet", "Unavailable")}')
        print(f'領取者住址: {collection["to_tablet"]}')
        print(f'內容: {collection["c_dtype"]}')
        print(f'現金金額: {collection["c_money"]}')
        print(f'寄放日期: {collection["sdate"]}')
        print(f'領取日期: {collection["ddate"]}')
        print(f'寄放物照片(如果可用): {collection["CollectionImage"]}')
        
else:
    print("請求失敗，狀態碼:", response.status_code)