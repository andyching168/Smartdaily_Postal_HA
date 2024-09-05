
DOMAIN = "smartdaily_postal_ha"

async def async_setup_entry(hass, config_entry):
    """Set up smartdaily_postal_ha from a config entry."""
    # Forward the setup to the sensor and camera platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor", "camera"])
    return True
