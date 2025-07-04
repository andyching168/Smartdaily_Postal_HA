"""Sensor platform for the package tracker component."""

import asyncio
from datetime import datetime, timedelta
import re
import aiohttp
import requests
import pytz
from homeassistant.core import _LOGGER
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

DOMAIN = "smartdaily_postal_ha"
SCAN_INTERVAL = timedelta(minutes=5)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=12)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor based on a config entry."""
    DeviceID = config_entry.data.get("DeviceID")
    com_id = config_entry.data.get("com_id")
    async_add_entities([PackageTrackerSensor(DeviceID, com_id)], True)


class PackageTrackerSensor(Entity):
    """Representation of a Package Tracker Sensor."""

    scan_interval = SCAN_INTERVAL

    def added_to_hass(self):
        """When entity is added to hass."""
        # 每隔一段时间自动刷新令牌
        
        self.update_token()
        

    def update_token(self):
        """Update the KingnetAuth token."""
        headers_update_token = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*"
        }
        response = requests.get(
            "https://api.smartdaily.com.tw/api/Valid/getHashCodeV2?code="
            + self._device_id,
            headers=headers_update_token,
        )
        if response.status_code == 200:
            print("Success!\nResult:\n")
            print(response.text)
            print("\n------Beautify------\n")
            # 解析JSON數據
            data = response.json()

            KingnetAuthValue = "CommunityUser " + data["Data"]["token"]
            self._kingnet_auth = KingnetAuthValue
            print(self._kingnet_auth)
        else:
            print("請求失敗，狀態碼:", response.status_code)

        # 这里添加调用API刷新令牌的逻辑
        # 更新 self._kingnet_auth

    def __init__(self, DeviceID, com_id):
        """Initialize the sensor."""
        self._state = None
        self._name = "My Package Tracker"
        self._kingnet_auth = ""
        self._com_id = com_id
        self._device_id = DeviceID
        self._unique_id = f"{DeviceID}_{com_id}"
        self._attributes = {}
        self._interval = timedelta(hours=1)  # 初始间隔时间
        self._max_interval = timedelta(hours=12)  # 最大间隔时间
        self._backoff_factor = 2  # 退避因子
        
    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": "智生活包裹追蹤",
            "manufacturer": "今網智生活",
        }

    @property
    def icon(self):
        """Return the icon of the sensor based on its state."""
        if self._state is None:
            return "mdi:package-variant-remove"
        elif self._state == "未領取":
            return "mdi:package-variant-closed"
        elif self._state == "已取件":
            return "mdi:package-variant-closed-check"
        else:
            return "mdi:package-variant"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        return self._attributes

    def parse_time(self, time_str):
        # 检查时间字符串是否匹配相对时间格式（如 "1小时以前"）
        print(time_str)
        if "剛剛" in time_str:
            # 获取当前时间并回退到最近的整点
            now = datetime.now(pytz.timezone("Asia/Taipei"))
            now_at_hour = now.replace(minute=0, second=0, microsecond=0)
            print(now_at_hour.strftime("%Y/%m/%d %H:%M"))
            return now_at_hour.strftime("%Y/%m/%d %H:%M")
        elif "昨天" in time_str:
            time_part = time_str.split(" ")[1]  # noqa: E999
            try:
                yesterday_time = datetime.strptime(time_part, "%H:%M")
                # 获取昨天的日期
                yesterday = datetime.now(pytz.timezone("Asia/Taipei")) - timedelta(
                    days=1
                )
                # 组合日期和时间
                combined_datetime = yesterday.replace(
                    hour=yesterday_time.hour, minute=yesterday_time.minute
                )
                return combined_datetime.strftime("%Y/%m/%d %H:%M")
            except ValueError:
                # 无法解析的时间格式
                return None
        else:
            match = re.match(r"(\d+)小時以前", time_str)
            if match:
                hours_ago = int(match.group(1))
                # 获取当前时间
                now = datetime.now(pytz.timezone("Asia/Taipei"))
                # 回退到最近的整点
                now_at_hour = now.replace(minute=0, second=0, microsecond=0)
                # 减去相对时间
                estimated_time = now_at_hour - timedelta(hours=hours_ago)
                return estimated_time.strftime("%Y/%m/%d %H:%M")
            else:
                match = re.match(r"(\d+)分鐘以前", time_str)
                if match:
                    minutes_ago = int(match.group(1))
                    # 获取当前时间
                    now = datetime.now(pytz.timezone("Asia/Taipei"))
                    # 减去相对时间
                    estimated_time = now - timedelta(minutes=minutes_ago)
                    return estimated_time.strftime("%Y/%m/%d %H:%M")
                else:
                    # 如果是标准时间格式，假设它是UTC时间，转换为GMT+8时区
                    try:
                        utc_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
                        return (
                            pytz.utc.localize(utc_time)
                            .astimezone(pytz.timezone("Asia/Taipei"))
                            .strftime("%Y/%m/%d %H:%M")
                        )
                    except ValueError:
                        # 无法解析的时间格式
                        return None

    def update(self):
        """Fetch new state data for the sensor."""
        # This is where you would make your API call
        # For example:
        if DOMAIN not in self.hass.data:
                self.hass.data[DOMAIN] = {}
        self.update_token()
        url = f"https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id={self._com_id}"
        
        headers = {
            "Connection": "keep-alive",
            "KingnetAuth": self._kingnet_auth,
            "Accept": "application/json, text/plain, */*"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            latest_package = None
            latest_time = None
            unclaimed_packages_count = 0
            for package in data["Data"]:
                package_time_str = package["create_date"]
                package_time = self.parse_time(package_time_str)
                if package["p_status"] == 1:  # 假设状态1表示未领取
                    unclaimed_packages_count += 1  # 未领取包裹计数器加一
                # 忽略无法解析的时间
                if package_time is None:
                    print("無法解析")
                    continue

                if latest_time is None or package_time > latest_time:
                    latest_time = package_time
                    latest_package = package

            if latest_package:
                self._state = "已取件" if latest_package["p_status"] == 2 else "未領取"

                # 检查 'postal_img' 是否存在，如果为空字符串则标记为 "Unavailable"
                postal_img_url = latest_package.get("postal_img", "")
                if postal_img_url:
                    # 只保留第一個問號前的部分
                    postal_img_url = postal_img_url.split("?")[0]
                else:
                    postal_img_url = "Unavailable"
                    
                self._attributes = {
                    "pd_id": latest_package["pd_id"],
                    "create_date": self.parse_time(latest_package["create_date"]),
                    "p_name": latest_package["p_name"],
                    "postal_typeText": latest_package["postal_typeText"],
                    "transport_code": latest_package["transport_code"],
                    "privacy": latest_package.get("privacy") == "privacy",
                    "p_note": latest_package["p_note"],
                    "postal_logisticsText": latest_package.get("postal_logisticsText", "Unavailable"),
                    "postal_img": postal_img_url,  # 直接使用变量
                    "unclaimed_packages_count": unclaimed_packages_count
                }

                # 根据 'postal_img' 属性决定存储在全局变量中的URL
                if self._attributes["postal_img"] == "Unavailable":
                    self.hass.data[DOMAIN]["parcel_image_url"] = "https://img.smartdaily.com.tw/wordpress/smartdaily/homepage/LOGO.png"
                else:
                    self.hass.data[DOMAIN]["parcel_image_url"] = self._attributes["postal_img"]

        else:
            # Handle errors
            self._state = "Error"
            print(response.text)
