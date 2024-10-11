#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
import cv2
from pyzbar.pyzbar import decode

url = ""
image_path = ""


def BarcodeReader(image):
    try:
        # read the image in numpy array using cv2
        img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        # Check if the image is loaded properly
        if img is None:
            print("無法載入圖片，請檢查路徑是否正確")
            return None
        # Decode the barcode image
        detectedBarcodes = decode(img)

        # If not detected then print the message
        if not detectedBarcodes:
            print("未檢測到條碼，請確認圖片是否包含條碼或條碼是否清晰")
            return None
        else:
            # Traverse through all the detected barcodes in image
            for barcode in detectedBarcodes:
                # Locate the barcode position in image
                (x, y, w, h) = barcode.rect

                # Put the rectangle in image using
                # cv2 to highlight the barcode
                cv2.rectangle(img, (x-10, y-10),
                              (x + w+10, y + h+10),
                              (255, 0, 0), 2)

                if barcode.data != "":
                    # Print the barcode data
                    return barcode.data.decode("utf-8")

    except Exception as e:
        print("條碼解碼發生錯誤:", e)
        return None


DeviceID = input("請輸入您的裝置ID,或是輸入0來貼上截圖路徑:")
if DeviceID != "0":
    # API URL
    url = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code=" + DeviceID
else:
    image_path = input("請輸入圖片路徑: ").strip()
    # Check if the barcode was successfully decoded
    decoded_data = str(BarcodeReader(image_path))
    if decoded_data is None:
        print("無法從圖片解碼條碼，程序結束")
        exit()
    DeviceID = decoded_data
    print(DeviceID)
    url = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code=" + DeviceID

headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*"
}
KingnetAuthValue = ""
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("成功取得更新權杖，結果如下:\n")
    print(response.text)  # 查看回應的實際內容
    try:
        data = response.json()  # 嘗試解析 JSON
        KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
        print(KingnetAuthValue)
    except (json.JSONDecodeError, KeyError) as e:
        print("無法解析 JSON 或取得權杖:", e)
        exit()
else:
    print("請求失敗，狀態碼:", response.status_code)
    exit()

# 自定義 headers
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
    # 解析 JSON 數據
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print("無法解析 JSON:", e)
        exit()

    i = 1
    for com in data["Data"]:
        print(f"{i}. 社區名稱: {com['community']}, ID: {com['id']}")
        community_dict[i] = com['id']
        i += 1
else:
    print("請求失敗，狀態碼:", response.status_code)
    print(response.text)
    exit()
Com_ID = 0
choice = 0
# 讓用戶選擇社區 ID
try:
    choice = int(input("\n請輸入要查詢的社區編號: "))
    Com_ID = community_dict[choice]
except ValueError:
    print("請輸入有效的編號！")
    exit()
except KeyError:
    print("編號不在列表中！")
    exit()

url = "https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id=" + Com_ID

# 自定義 headers
headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*"
}

# 發送請求
response = requests.get(url, headers=headers)

# 檢查是否成功獲得響應
if response.status_code == 200:
    print("成功取得包裹清單，結果如下:\n")
    print(response.text)
    print("\n------ 美化輸出 ------\n")
    try:
        # 解析 JSON 數據
        data = response.json()
        # 遍歷並按照指定格式打印每個包裹的詳細信息
        for package in data["Data"]:
            # 處理包裹狀態
            status_text = "未領取" if package["p_status"] == 1 else "已取件"
            # 使用 .get 方法處理可能缺失的 postal_logisticsText，如果缺失則顯示 "Unavailable"
            logistics_text = package.get("postal_logisticsText", "Unavailable")

            print(f'#{package["serial_num"]} {package["create_date"]} {status_text}')
            print(f'姓名: {package["p_name"]}')
            print(f'內容: {package["postal_typeText"]}')
            print(f'物流: {logistics_text}')
            print(f'條碼: {package["transport_code"]}')
            print(f'物流業者: {logistics_text}')
            print(f'包裹照片(如果可用): {package["postal_img"]}')
            print(f'存放位置: {package["p_note"]}\n-----------\n')
    except (json.JSONDecodeError, KeyError) as e:
        print("無法解析 JSON 或獲取包裹信息:", e)
else:
    print("請求失敗，狀態碼:", response.status_code)
    print(response.text)
url = "https://api.smartdaily.com.tw/api/Profile/GetProfileInfo"

# 自定義 headers
headers = {
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Accept": "application/json, text/plain, */*"
}

# 發送請求
response = requests.get(url, headers=headers)

# 檢查是否成功獲得響應
if response.status_code == 200:
    print("成功取得個資，結果如下:\n")
    print(response.text)
    try:
        # 解析 JSON 數據
        data = response.json()
        name=data["Data"]["pinfo"]["a_name"]
        email=data["Data"]["pinfo"]["a_email"]
        phone=data["Data"]["pinfo"]["a_phone"]
        comm=data["Data"]["plist"][choice-1]["community"]
        address=data["Data"]["plist"][choice-1]["tablet_note"]
        print(name+", 你好, 你的email為："+email+", 手機號碼為： "+phone+", 社區為： "+comm+", 地址為："+address)
        print("所以請您保管好您的DeviceSn以及截圖，不要交給他人，感謝您")
    except (json.JSONDecodeError, KeyError) as e:
        print("無法解析 JSON 或獲取包裹信息:", e)
else:
    print("請求失敗，狀態碼:", response.status_code)
    print(response.text)