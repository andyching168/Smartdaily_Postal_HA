"""Sensor platform for the package tracker component."""

from datetime import datetime, timedelta

import requests

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.entity import Entity

DOMAIN = "my_parcel_tracker"
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor based on a config entry."""
    kingnet_auth = config_entry.data.get("KingnetAuth")
    async_add_entities([PackageTrackerSensor(kingnet_auth, kingnet_auth)], True)


class PackageTrackerSensor(Entity):
    """Representation of a Package Tracker Sensor."""

    scan_interval = SCAN_INTERVAL

    def __init__(self, kingnet_auth, unique_id):
        """Initialize the sensor."""
        self._state = None
        self._name = "My Package Tracker"
        self._kingnet_auth = kingnet_auth
        self._unique_id = unique_id  # 设置唯一ID
        self._attributes = {}

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

    def update(self):
        """Fetch new state data for the sensor."""
        # This is where you would make your API call
        # For example:
        url = (
            "https://api.smartdaily.com.tw/api/Postal/getUserPostalList?com_id=20061501"
        )
        headers = {
            "Host": "api.smartdaily.com.tw",
            "Sec-Fetch-Site": "cross-site",
            "Connection": "keep-alive",
            "KingnetAuth": self._kingnet_auth,
            "Sec-Fetch-Mode": "cors",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Accept-Language": "zh-TW,zh-Hant;q=0.9",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            latest_package = None
            latest_time = None

            for package in data["Data"]:
                package_time = datetime.strptime(
                    package["create_date"], "%Y/%m/%d %H:%M"
                )
                if latest_time is None or package_time > latest_time:
                    latest_time = package_time
                    latest_package = package

            if latest_package:
                self._state = "已取件" if latest_package["p_status"] == 2 else "未領取"
                self._attributes = {
                    "pd_id": latest_package["pd_id"],
                    "create_date": latest_package["create_date"],
                    "p_name": latest_package["p_name"],
                    "postal_typeText": latest_package["postal_typeText"],
                    "transport_code": latest_package["transport_code"],
                    "p_note": latest_package["p_note"],
                }
        else:
            # Handle errors
            self._state = "Error"
