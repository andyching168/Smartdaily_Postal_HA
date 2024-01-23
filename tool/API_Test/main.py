import requests
import json

# API URL
url = "https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id=20061501"
KingnetAuthValue=input("Input your KingnetAuth value:")
# 自定義headers
headers = {
    "Host": "api.smartdaily.com.tw",
    "Sec-Fetch-Site": "cross-site",
    "Connection": "keep-alive",
    "KingnetAuth": KingnetAuthValue,
    "Sec-Fetch-Mode": "cors",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Accept-Language": "zh-TW,zh-Hant;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br"
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

    # 遍歷並按照指定格式打印每個包裹的詳細信息
    for package in data["Data"]:
        # 處理包裹狀態
        status_text = "未領取" if package["p_status"] == 1 else "已取件"

        print(f'#{package["serial_num"]} {package["create_date"]} {status_text}')
        print(f'姓名: {package["p_name"]}')
        print(f'內容: {package["postal_typeText"]}')
        print(f'物流: {package["postal_logisticsText"]}')
        print(f'條碼: {package["transport_code"]}')
        print(f'存放位置: {package["p_note"]}\n-----------\n')
else:
    print("請求失敗，狀態碼:", response.status_code)
