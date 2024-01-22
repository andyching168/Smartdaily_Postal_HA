# Smartdaily_Postal_HA

將今網智生活的包裹領取狀態串接到Home Assistant的工具

## 安裝

### 前提條件

- Home Assistant安裝。
- HACS (Home Assistant Community Store) 安裝。

### 抓取封包以獲取所需信息

為了使用這個組件，您需要從您的手機應用程序中抓取封包以獲取`KingnetAuth`信息。這可以通過以下方式完成：

#### iOS：

- 使用iOS上的Stream應用程序抓取封包。

#### Android：

- 使用電腦上的Fiddler工具抓取封包。

您將會找到像這樣的請求：

```
"GET https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id=20061501"
```

從此請求的Header中複製`KingnetAuth`的值。

### 通過HACS安裝

1. 在HACS中，選擇“Integrations”。
2. 點擊右上角的選單按鈕，選擇`Custom repositories`，將此repo貼上，類型選擇`Integration`。
3. 搜索“智生活包裹追蹤”並安裝。

### 配置Home Assistant

1. 重新啟動您的Home Assistant。
2. 在Home Assistant的“配置” > “整合”頁面上，點擊“添加集成”。
3. 搜索“智生活包裹追蹤”並選擇它。
4. 在出現的窗口中，輸入先前從封包中抓取的`KingnetAuth`值。
5. 點擊“提交”完成設置。

## 使用

一旦完成安裝和配置，您將可以在Home Assistant中看到一個新的感應器，顯示您的包裹追蹤信息。
