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
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

DOMAIN = "smartdaily_postal_ha"
SCAN_INTERVAL = timedelta(minutes=5)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=12)
MAX_PACKAGE_SLOTS = 4  # 最多顯示 4 個包裹 slot


def parse_time(time_str):
    """Parse time string to standard format."""
    if "剛剛" in time_str:
        now = datetime.now(pytz.timezone("Asia/Taipei"))
        now_at_hour = now.replace(minute=0, second=0, microsecond=0)
        return now_at_hour.strftime("%Y/%m/%d %H:%M")
    elif "昨天" in time_str:
        time_part = time_str.split(" ")[1]
        try:
            yesterday_time = datetime.strptime(time_part, "%H:%M")
            yesterday = datetime.now(pytz.timezone("Asia/Taipei")) - timedelta(days=1)
            combined_datetime = yesterday.replace(
                hour=yesterday_time.hour, minute=yesterday_time.minute
            )
            return combined_datetime.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            return None
    else:
        match = re.match(r"(\d+)小時以前", time_str)
        if match:
            hours_ago = int(match.group(1))
            now = datetime.now(pytz.timezone("Asia/Taipei"))
            now_at_hour = now.replace(minute=0, second=0, microsecond=0)
            estimated_time = now_at_hour - timedelta(hours=hours_ago)
            return estimated_time.strftime("%Y/%m/%d %H:%M")
        else:
            match = re.match(r"(\d+)分鐘以前", time_str)
            if match:
                minutes_ago = int(match.group(1))
                now = datetime.now(pytz.timezone("Asia/Taipei"))
                estimated_time = now - timedelta(minutes=minutes_ago)
                return estimated_time.strftime("%Y/%m/%d %H:%M")
            else:
                try:
                    utc_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
                    return (
                        pytz.utc.localize(utc_time)
                        .astimezone(pytz.timezone("Asia/Taipei"))
                        .strftime("%Y/%m/%d %H:%M")
                    )
                except ValueError:
                    return None


class SmartdailyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Smartdaily data."""

    def __init__(self, hass, device_id, com_id):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Smartdaily Postal",
            update_interval=SCAN_INTERVAL,
        )
        self._device_id = device_id
        self._com_id = com_id
        self._kingnet_auth = ""

    def _update_token(self):
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
            data = response.json()
            self._kingnet_auth = "CommunityUser " + data["Data"]["token"]
        else:
            _LOGGER.error("Token update failed, status code: %s", response.status_code)

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

    def _fetch_data(self):
        """Fetch data from API (blocking)."""
        self._update_token()
        
        url = f"https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id={self._com_id}"
        headers = {
            "Connection": "keep-alive",
            "KingnetAuth": self._kingnet_auth,
            "Accept": "application/json, text/plain, */*"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise UpdateFailed(f"API request failed: {response.status_code}")

        data = response.json()
        
        # Process packages
        latest_package = None
        latest_time = None
        unclaimed_packages = []
        all_packages = []
        
        for package in data.get("Data", []):
            package_time_str = package.get("create_date", "")
            package_time = parse_time(package_time_str)
            
            # 收集未領取包裹
            if package.get("p_status") == 1:
                unclaimed_packages.append({
                    "package": package,
                    "parsed_time": package_time
                })
            
            all_packages.append({
                "package": package,
                "parsed_time": package_time
            })
            
            if package_time is None:
                continue
                
            if latest_time is None or package_time > latest_time:
                latest_time = package_time
                latest_package = package

        # 按時間排序未領取包裹（最新的在前）
        unclaimed_packages.sort(
            key=lambda x: x["parsed_time"] if x["parsed_time"] else "",
            reverse=True
        )
        
        return {
            "latest_package": latest_package,
            "unclaimed_packages": unclaimed_packages,
            "unclaimed_count": len(unclaimed_packages),
            "all_packages": all_packages,
        }


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor based on a config entry."""
    device_id = config_entry.data.get("DeviceID")
    com_id = config_entry.data.get("com_id")
    
    # Initialize domain data if not exists
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    # Create coordinator
    coordinator = SmartdailyDataUpdateCoordinator(hass, device_id, com_id)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    
    # Create entities
    entities = [
        PackageTrackerSensor(coordinator, device_id, com_id),
    ]
    
    # Add package slot sensors (1-4)
    for slot in range(1, MAX_PACKAGE_SLOTS + 1):
        entities.append(PackageSlotSensor(coordinator, device_id, com_id, slot))
    
    async_add_entities(entities, True)


class PackageTrackerSensor(CoordinatorEntity, Entity):
    """Representation of a Package Tracker Sensor (main sensor showing latest package)."""

    def __init__(self, coordinator, device_id, com_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._com_id = com_id
        self._unique_id = f"{device_id}_{com_id}"
        self._name = "My Package Tracker"
        self._attr_has_entity_name = False

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
        if self.state is None:
            return "mdi:package-variant-remove"
        elif self.state == "未領取":
            return "mdi:package-variant-closed"
        elif self.state == "已取件":
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
        if self.coordinator.data is None:
            return None
            
        latest_package = self.coordinator.data.get("latest_package")
        if latest_package is None:
            return None
            
        return "已取件" if latest_package.get("p_status") == 2 else "未領取"

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        if self.coordinator.data is None:
            return {}
            
        latest_package = self.coordinator.data.get("latest_package")
        if latest_package is None:
            return {}

        # Process postal_img (保留完整 URL，包含 Google Cloud Storage 簽名參數)
        postal_img_url = latest_package.get("postal_img", "")
        if not postal_img_url:
            postal_img_url = "Unavailable"

        # Update global image URL for camera
        if DOMAIN in self.hass.data:
            if postal_img_url == "Unavailable":
                self.hass.data[DOMAIN]["parcel_image_url"] = "https://img.smartdaily.com.tw/wordpress/smartdaily/homepage/LOGO.png"
            else:
                self.hass.data[DOMAIN]["parcel_image_url"] = postal_img_url

        return {
            "pd_id": latest_package.get("pd_id"),
            "create_date": parse_time(latest_package.get("create_date", "")),
            "p_name": latest_package.get("p_name"),
            "postal_typeText": latest_package.get("postal_typeText"),
            "transport_code": latest_package.get("transport_code"),
            "privacy": latest_package.get("privacy") == "privacy",
            "p_note": latest_package.get("p_note"),
            "postal_logisticsText": latest_package.get("postal_logisticsText", "Unavailable"),
            "postal_img": postal_img_url,
            "unclaimed_packages_count": self.coordinator.data.get("unclaimed_count", 0)
        }

    # Keep parse_time as instance method for backward compatibility with tests
    def parse_time(self, time_str):
        """Parse time string (wrapper for module function)."""
        return parse_time(time_str)


class PackageSlotSensor(CoordinatorEntity, Entity):
    """Representation of a Package Slot Sensor (showing individual unclaimed package)."""

    def __init__(self, coordinator, device_id, com_id, slot):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._com_id = com_id
        self._slot = slot
        self._unique_id = f"{device_id}_{com_id}_slot_{slot}"
        self._name = f"包裹 {slot}"
        self._attr_has_entity_name = False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, f"{self._device_id}_{self._com_id}")},
            "name": "智生活包裹追蹤",
            "manufacturer": "今網智生活",
        }

    @property
    def icon(self):
        """Return the icon of the sensor based on its state."""
        package = self._get_package()
        if package is None:
            return "mdi:package-variant-remove"
        return "mdi:package-variant-closed"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    def _get_package(self):
        """Get the package for this slot."""
        if self.coordinator.data is None:
            return None
            
        unclaimed = self.coordinator.data.get("unclaimed_packages", [])
        slot_index = self._slot - 1  # slot 1 = index 0
        
        if slot_index < len(unclaimed):
            return unclaimed[slot_index].get("package")
        return None

    @property
    def state(self):
        """Return the state of the sensor."""
        package = self._get_package()
        if package is None:
            return "無包裹"
        return package.get("p_name", "未知")

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        package = self._get_package()
        if package is None:
            return {
                "slot": self._slot,
                "has_package": False
            }

        # Process postal_img (保留完整 URL，包含 Google Cloud Storage 簽名參數)
        postal_img_url = package.get("postal_img", "")
        if not postal_img_url:
            postal_img_url = "Unavailable"

        return {
            "slot": self._slot,
            "has_package": True,
            "pd_id": package.get("pd_id"),
            "create_date": parse_time(package.get("create_date", "")),
            "p_name": package.get("p_name"),
            "postal_typeText": package.get("postal_typeText"),
            "transport_code": package.get("transport_code"),
            "privacy": package.get("privacy") == "privacy",
            "p_note": package.get("p_note"),
            "postal_logisticsText": package.get("postal_logisticsText", "Unavailable"),
            "postal_img": postal_img_url,
        }

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success
