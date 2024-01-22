"""Example of a custom component for a package tracker."""

DOMAIN = "my_parcel_tracker"


async def async_setup_entry(hass, config_entry):
    """Set up My Parcel Tracker from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True
