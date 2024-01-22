import voluptuous as vol  # noqa: D100

from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "my_parcel_tracker"


class MyParcelTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """MyParcelTracker config flow."""

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}
        description = (
            "為了設置包裹追蹤組件，您需要提供KingnetAuth。"
            "您可以使用如Wireshark或Fiddler等網絡封包捕獲工具，"
            "從您的移動設備上抓取APP的封包，從而獲得這些信息。"
        )
        if user_input is not None:
            # Validate user input
            # 如果驗證成功:
            return self.async_create_entry(title="My Parcel Tracker", data=user_input)

        return self.async_show_form(
            step_id="user",
            description_placeholders={"description": description},
            data_schema=vol.Schema(
                {
                    vol.Required("KingnetAuth"): str,
                }
            ),
            errors=errors,
        )
