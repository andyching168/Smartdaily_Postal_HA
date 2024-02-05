import aiohttp
import logging

from homeassistant.components.camera import Camera
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)
DOMAIN = "smartdaily_postal_ha"


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the camera platform."""
    DeviceID = config_entry.data.get("DeviceID")
    com_id = config_entry.data.get("com_id")
    unique_id = f"{DeviceID}_{com_id}_camera"
    camera = SmartDailyPostalCamera(unique_id, hass)
    async_add_entities([camera], True)



class SmartDailyPostalCamera(Camera):
    """Representation of the SmartDaily Postal Camera."""

    def __init__(self,unique_id, hass):
        """Initialize the camera."""
        super().__init__()
        self.hass = hass
        self._name = "SmartDaily Postal Image"
        self._unique_id = unique_id
        print(unique_id)
        self._image_url = None
    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id
    @property
    def name(self):
        """Return the name of the camera."""
        return self._name

    async def async_camera_image(self, width=None, height=None):
        """Return the image of the package."""
        self.image_url = self.hass.data[DOMAIN].get("parcel_image_url")
        # print(self.image_url)
        if not self.image_url:
            _LOGGER.error("No parcel image URL available")
            return None

        websession = async_get_clientsession(self.hass)
        try:
            # 设置超时时间为10秒
            timeout = aiohttp.ClientTimeout(total=10)
            response = await websession.get(self.image_url, timeout=timeout)

            if response.status == 200:
                return await response.read()
            else:
                _LOGGER.error(f"Error fetching parcel image, status: {response.status}")
                return None

        except aiohttp.ClientError as e:
            _LOGGER.error(f"Error fetching parcel image: {e}")
            return None
