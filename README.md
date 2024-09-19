# Smartdaily_Postal_HA
<a href="https://www.buymeacoffee.com/andyching168" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
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
