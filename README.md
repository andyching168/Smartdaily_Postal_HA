# Smartdaily\_Postal\_HA



### 將今網智生活的包裹領取狀態串接到Home Assistant的工具

## 安裝

### 前提條件

- Home Assistant安裝。
- HACS (Home Assistant Community Store) 安裝。

### 取得DeviceSn (也就是裝置識別)

為了使用這個組件，你需要取得DeviceSn。
別擔心，這非常好取得，可依照以下步驟

1. 在智生活APP首頁，點擊右上角的「條碼」（也就是領取包裹時給管理員掃描的頁面）
2. 將此頁面截圖
3. 到[條碼掃瞄網站](https://online-barcode-reader.inliteresearch.com/)，將截圖上傳到網站辨識。
4. 複製辨識出來的字串（也就是`DeviceSn(或DeviceCode)`的值）。

### 通過HACS安裝

1. 在HACS中，選擇“Integrations”。
2. 點擊右上角的選單按鈕，選擇`Custom repositories`，將此repo貼上，類型選擇`Integration`。
3. 搜索“智生活包裹追蹤”並安裝。

### 配置Home Assistant

1. 重新啟動您的Home Assistant。
2. 在Home Assistant的“配置” > “整合”頁面上，點擊“添加集成”。
3. 搜索“智生活包裹追蹤”並選擇它。
4. 在出現的窗口中，輸入先前辨識出來的`DeviceSn(或DeviceCode)`值。
5. 點擊“提交”，並選擇自己的社區，完成設置。

## 使用

一旦完成安裝和配置，您將可以在Home Assistant中看到一個新的感應器，顯示您的包裹追蹤信息。

### 額外配置查看寄放物品詳情

如果您想查看寄放物的詳細信息，請按照以下步驟進行設置：

1. 下載在collection資料夾內的`collection_fetch.py`，編輯 `collection_fetch.py` 文件中的 `DeviceID` ，將其設置為您的裝置ID。

2. 將編輯好的 Python 腳本 (`collection_fetch.py`) 上傳到 Home Assistant 的配置資料夾（通常是 `/config` 或 `/homeassistant`）。

3. 在 Home Assistant 的 `configuration.yaml` 文件中添加以下 Command Line Sensor 設置：

   ```yaml
   command_line:
      - sensor:
            name: "最新寄放物狀態"
            command: "python /config/collection_fetch.py"
            value_template: "{{ value_json.latest.status }}"
            json_attributes_path: "$.latest"
            json_attributes:
               - serial_num
               - date
               - from_name
               - to_name
               - from_tablet
               - to_tablet
               - c_dtype
               - c_money
               - sdate
               - ddate
               - collection_image
               - uncollected_count
            scan_interval: 300
      - sensor:
            name: "已領取寄放物狀態"
            command: "python /config/collection_fetch.py"
            value_template: "{{ value_json.collected.ddate }}"
            json_attributes_path: "$.collected"
            json_attributes:
               - serial_num
               - date
               - from_name
               - to_name
               - from_tablet
               - to_tablet
               - c_dtype
               - c_money
               - sdate
               - ddate
               - collection_image
            scan_interval: 300

   ```

4. 為了顯示寄放物的圖片，您可以在 Home Assistant 中配置兩個 Template Image：

   ```yaml
   {{ state_attr("sensor.zui_xin_ji_fang_wu_zhuang_tai", "collection_image") }}
   ```
   ```yaml
   {{ state_attr("sensor.yi_ling_qu_ji_fang_wu_zhuang_tai", "collection_image") }}
   ```
這樣，您就可以在 Home Assistant 中查看最新的寄放物狀態、最後領取的寄放物狀態以及相關的圖片等信息。

## 📜 授權 License

本專案採用 [MIT License](LICENSE) 授權，詳情請見 LICENSE 檔案。

## ⚠️ 免責聲明 Disclaimer

本工具為非官方開發，僅供學術研究與個人自動化用途。  
使用本專案所造成之任何資料損失、帳號問題或法律糾紛，開發者不負任何責任。  
若官方對 API 做出限制或變更，本工具功能亦可能失效。

本專案無與今網智生活有任何關聯或合作。
