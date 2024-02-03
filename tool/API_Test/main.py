import requests
import json
DeviceID=input("請輸入您的裝置ID:")
# API URL
url = "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code="+DeviceID


headers = {
    "Host": "api.smartdaily.com.tw",
    "Sec-Fetch-Site": "cross-site",
    "Connection": "keep-alive",
    "Sec-Fetch-Mode": "cors",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Accept-Language": "zh-TW,zh-Hant;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br"
}
KingnetAuthValue=""
response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Success!\nResult:\n")
    print(response.text)
    print("\n------Beautify------\n")
    # 解析JSON數據
    data = response.json()

    KingnetAuthValue="CommunityUser "+data["Data"]["token"]
    print(KingnetAuthValue)
else:
    print("請求失敗，狀態碼:", response.status_code)
    exit()

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

url = "https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id="+Com_ID

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
        print(f'物流業者: {package["postal_logisticsText"]}')
        print(f'存放位置: {package["p_note"]}\n-----------\n')
else:
    print("請求失敗，狀態碼:", response.status_code)
