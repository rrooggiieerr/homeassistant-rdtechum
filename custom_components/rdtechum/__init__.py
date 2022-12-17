"""The RDTech UM series integration."""
from __future__ import annotations

import asyncio
import logging
import socket
from datetime import timedelta

import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .ummeter import UMmeter, UMmeterData

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER]


class RDTechUMCoordinator(DataUpdateCoordinator):
    device_info = None

    _ummeter: UMmeter = None

    """RDTech UM series Data Update Coordinator."""

    def __init__(self, hass, address):
        """Initialize RDTech UM series Data Update Coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=__name__,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=1),
        )

        _LOGGER.debug(address)
        self.address = address
        self._ummeter = UMmeter(self.address)

    async def connect(self):
        try:
            self._ummeter.open()
        except IOError:
            raise ConfigEntryNotReady(
                f"Unable to connect to RDTech UM meter on {self.address}"
            )

        self.data = self._ummeter.get_data()
        self.model = self.data["model"]

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.address)},
            name=f"RDTech {self.model}",
            model=self.model,
            manufacturer="RDTech",
        )

    async def disconnect(self):
        if self._ummeter:
            self._ummeter.close()

    async def _async_update_data(self):
        """Fetch data from RDTech UM series device."""
        data = self._ummeter.get_data()
        data["screen_timeout"] = data["screen_timeout"].total_seconds() / 60
        return data

    def screen_brightness(self, brightness: int):
        self._ummeter.screen_brightness(brightness)

    def screen_timeout(self, minutes: int):
        self._ummeter.screen_timeout(minutes)

    def data_threshold(self, threshold_ma):
        self._ummeter.data_threshold(threshold_ma)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RDTech UM series from a config entry."""
    address: str = entry.data[CONF_ADDRESS]

    um_coordinator = RDTechUMCoordinator(hass, address)
    await um_coordinator.connect()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = um_coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    um_coordinator = hass.data[DOMAIN][entry.entry_id]
    await um_coordinator.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
