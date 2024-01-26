"""Example of a custom component for a package tracker."""

DOMAIN = "smartdaily_postal_ha"


async def async_setup_entry(hass, config_entry):
    """Set up smartdaily_postal_ha from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True
