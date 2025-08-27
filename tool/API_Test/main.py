#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
import cv2
from pyzbar.pyzbar import decode

def get_token(device_id):
    """根據裝置 ID 獲取 API 權杖"""
    url = f"https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code={device_id}"
    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果請求失敗，會拋出 HTTPError
        data = response.json()
        token = "CommunityUser " + data["Data"]["token"]
        print("成功取得更新權杖。")
        return token
    except requests.exceptions.RequestException as e:
        print(f"權杖請求失敗: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析 JSON 或取得權杖: {e}")
    return None

def barcode_reader(image_path):
    """從圖片路徑解碼條碼"""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print("無法載入圖片，請檢查路徑是否正確。")
            return None
        
        detected_barcodes = decode(img)
        if not detected_barcodes:
            print("未檢測到條碼。")
            return None
        
        for barcode in detected_barcodes:
            if barcode.data:
                return barcode.data.decode("utf-8")
    except Exception as e:
        print(f"條碼解碼發生錯誤: {e}")
    return None

def get_user_community_list(auth_token):
    """獲取用戶社區列表"""
    url = "https://api.smartdaily.com.tw/api/Community/GetUserCommunityList"
    headers = {
        "Connection": "keep-alive",
        "KingnetAuth": auth_token,
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("成功，以下是您的社區列表:")
        data = response.json()
        community_dict = {}
        for i, com in enumerate(data["Data"], 1):
            print(f"{i}. 社區名稱: {com['community']}, ID: {com['id']}")
            community_dict[i] = com['id']
        return community_dict
    except requests.exceptions.RequestException as e:
        print(f"獲取社區列表失敗: {e}")
        print(response.text)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析社區列表 JSON: {e}")
    return None

def get_user_postal_list(auth_token, community_id):
    """獲取指定社區的包裹清單"""
    url = f"https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id={community_id}"
    headers = {
        "Connection": "keep-alive",
        "KingnetAuth": auth_token,
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("成功取得包裹清單，結果如下:")
        data = response.json()
        print("------ 美化輸出 ------")
        for package in data["Data"]:
            status_text = "未領取" if package["p_status"] == 1 else "已取件"
            logistics_text = package.get("postal_logisticsText", "Unavailable")
            print(f'#{package["serial_num"]} {package["create_date"]} {status_text}')
            print(f'姓名: {package["p_name"]}')
            print(f'內容: {package["postal_typeText"]}')
            print(f'物流: {logistics_text}')
            print(f'條碼: {package["transport_code"]}')
            print(f'物流業者: {logistics_text}')
            print(f'包裹照片(如果可用): {package["postal_img"]}')
            print(f'存放位置: {package["p_note"]}\n-----------')
    except requests.exceptions.RequestException as e:
        print(f"獲取包裹清單失敗: {e}")
        print(response.text)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析包裹清單 JSON: {e}")

def get_community_announcements(auth_token, community_id):
    """獲取並讓使用者選擇社區公告"""
    list_url = f"https://api.smartdaily.com.tw/api/v3.24/Announcement/Community/List?ComId={community_id}&Offset=0&MaxCount=10"
    list_headers = {
        "Connection": "keep-alive",
        "KingnetAuth": auth_token,
        "Accept": "application/json, text/plain, */*",
        "x-app-version": "4.5.2",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    try:
        response = requests.get(list_url, headers=list_headers)
        response.raise_for_status()
        announcements = response.json()["Data"]["Announcements"]
        
        while True:
            print("\n------ 社區公告列表 ------")
            announcement_map = {}
            for i, ann in enumerate(announcements, 1):
                print(f"{i}. {ann.get('Title', 'N/A')} ({ann.get('Start', 'N/A')})")
                announcement_map[i] = ann.get('Id')

            print("-------------------------")
            choice = input("請輸入要查看的公告編號 (輸入 '0' 返回主選單): ").strip()

            if choice == '0':
                break
            
            try:
                choice_num = int(choice)
                if choice_num in announcement_map:
                    announcement_id = announcement_map[choice_num]
                    if announcement_id:
                        get_announcement_detail(auth_token, community_id, announcement_id)
                    else:
                        print("錯誤：此公告沒有有效的ID。")
                else:
                    print("無效的編號，請重新輸入。")
            except ValueError:
                print("輸入無效，請輸入數字。")

    except requests.exceptions.RequestException as e:
        print(f"獲取公告列表失敗: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析公告列表 JSON: {e}")

def get_announcement_detail(auth_token, community_id, announcement_id):
    """根據 .har 檔案獲取單一社區公告的詳細內容"""
    detail_url = f"https://api.smartdaily.com.tw/api/v3.2/Announcement/Detail?com_id={community_id}&id={announcement_id}"
    detail_headers = {
        "Connection": "keep-alive",
        "KingnetAuth": auth_token,
        "Accept": "application/json, text/plain, */*",
        "x-app-version": "4.5.2",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    try:
        response = requests.get(detail_url, headers=detail_headers)
        response.raise_for_status()
        data = response.json().get("Data", {})

        print("\n------ 公告詳細內容 ------")
        print(f"標題: {data.get('Title', 'N/A')}")
        
        # 檢查 'Content' 或 'Detail' 欄位，並將 <br> 轉換為換行
        content = data.get('Content') or data.get('Detail', '')
        content = content.replace('<br>', '\n')
        print(f"內容:\n{content if content else '無'}")
        
        # 修正：使用 'AttachedFile' 作為附件的鍵
        attachments = data.get("AttachedFile", [])
        if attachments:
            print("\n附件:")
            # 修正：附件物件沒有 'Name'，直接顯示 URL
            for i, attachment in enumerate(attachments, 1):
                print(f"  附件 {i}: {attachment.get('Url', 'N/A')}")
        else:
            print("\n附件: 無")
            
        print("-------------------------")
        input("按 Enter 鍵返回公告列表...")

    except requests.exceptions.RequestException as e:
        print(f"獲取公告詳細內容失敗: {e}")
        if 'response' in locals():
            print(response.text)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析公告詳細內容 JSON: {e}")




def get_user_profile(auth_token, community_id):
    """獲取並返回使用者個人資料"""
    url = "https://api.smartdaily.com.tw/api/Profile/GetProfileInfo"
    headers = {
        "Connection": "keep-alive",
        "KingnetAuth": auth_token,
        "Accept": "application/json, text/plain, */*"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()["Data"]
        pinfo = data.get("pinfo", {})
        
        community_info = next((p for p in data.get("plist", []) if p.get("com_id") == community_id), None)
        
        profile_data = {
            "name": pinfo.get("a_name", "N/A"),
            "email": pinfo.get("a_email", "N/A"),
            "phone": pinfo.get("a_phone", "N/A"),
            "community_name": "N/A",
            "address": "N/A"
        }

        if community_info:
            profile_data["community_name"] = community_info.get("community", "N/A")
            profile_data["address"] = community_info.get("tablet_note", "N/A")
        
        return profile_data

    except requests.exceptions.RequestException as e:
        print(f"獲取個人資料失敗: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"無法解析個人資料 JSON: {e}")
    return None

def get_user_deposited_items(auth_token, community_id):
    """獲取指定社區的寄放物清單 (佔位符)"""
    print("\n------ 寄放物清單 ------")
    print("此功能尚未開放，敬請期待。")
    print("---------------------\n")

def main():
    """主函式"""
    device_id_input = input("請輸入您的裝置ID,或是輸入0來貼上截圖路徑: ")
    auth_token = None
    device_id = None

    if device_id_input != "0":
        device_id = device_id_input
        auth_token = get_token(device_id)
    else:
        image_path = input("請輸入圖片路徑: ").strip()
        decoded_data = barcode_reader(image_path)
        if decoded_data:
            print(f"解碼後的 Device ID: {decoded_data}")
            device_id = decoded_data
            auth_token = get_token(device_id)
        else:
            print("無法從圖片解碼條碼，程序結束。")
            return

    if not auth_token:
        print("無法獲取權杖，程序結束。")
        return

    community_dict = get_user_community_list(auth_token)
    if not community_dict:
        print("無法獲取社區列表，程序結束。")
        return

    com_id = None
    while not com_id:
        try:
            choice = int(input("請輸入要查詢的社區編號: "))
            com_id = community_dict.get(choice)
            if not com_id:
                print("編號不在列表中！請重新輸入。")
        except ValueError:
            print("請輸入有效的數字編號！")

    profile = get_user_profile(auth_token, com_id)
    if not profile:
        print("無法獲取使用者資訊，程序結束。")
        return

    print(f"{profile['name']}, 你好, 你的email為：{profile['email']}, 手機號碼為： {profile['phone']}")
    print(f"社區為： {profile['community_name']}, 地址為：{profile['address']}")
    print("所以請您保管好您的DeviceID以及截圖，不要交給他人，感謝您")


    while True:
        print("\n" + "="*50)
        print(f" 使用者: {profile['name']} | DeviceID: {device_id} | 社區: {profile['community_name']} ({com_id})")
        print("="*50)
        print(" 1. 查詢包裹")
        print(" 2. 查詢寄放物")
        print(" 3. 查詢公告")
        print(" 4. 全部查詢")
        print(" 5. 離開")
        print("="*50)
        
        menu_choice = input("請選擇功能: ").strip()

        if menu_choice == '1':
            get_user_postal_list(auth_token, com_id)
        elif menu_choice == '2':
            get_user_deposited_items(auth_token, com_id)
        elif menu_choice == '3':
            get_community_announcements(auth_token, com_id)
        elif menu_choice == '4':
            print("\n--- 執行全部查詢 ---")
            get_user_postal_list(auth_token, com_id)
            get_user_deposited_items(auth_token, com_id)
            get_community_announcements(auth_token, com_id)
            print("\n--- 全部查詢完畢 ---")
        elif menu_choice == '5':
            print("感謝使用，再見！")
            break
        else:
            print("無效的選擇，請重新輸入。")


if __name__ == "__main__":
    main()

