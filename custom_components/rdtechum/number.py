"""
Created on 15 Dec 2022

@author: Rogier van Staveren
"""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import RDTechUMCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RDTech UM series number."""
    coordinator: RDTechUMCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    entities = []

    entities.append(RDTechUMScreenBrightness(coordinator))
    entities.append(RDTechUMScreenTimeout(coordinator))
    entities.append(RDTechUMRecordingThreshold(coordinator))

    async_add_entities(entities)


class RDTechUMNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_available = False
    _attr_native_min_value = 0
    _attr_native_step = 1
    _attr_native_value = None

    def __init__(self, coordinator: RDTechUMCoordinator, idx: str) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.address}-{idx}"

        self.idx = idx

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if self.coordinator.data and self.idx in self.coordinator.data:
            self._attr_native_value = float(self.coordinator.data[self.idx])
            self._attr_available = True
            self.async_write_ha_state()
        else:
            _LOGGER.debug("%s is not available", self.idx)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated = False

        if self.coordinator.data and self.idx in self.coordinator.data:
            try:
                new_value = float(self.coordinator.data[self.idx])
                if self._attr_native_value != new_value:
                    self._attr_native_value = new_value
                    updated = True

                if self._attr_available is not True:
                    self._attr_available = True
                    updated = True
            except ValueError as ex:
                _LOGGER.error(
                    "ValueError for %s = %s, %s",
                    self.idx,
                    self.coordinator.data[self.idx],
                    ex,
                )
                if self._attr_available is not False:
                    self._attr_available = False
                    updated = True
            except TypeError as ex:
                _LOGGER.error("TypeError for %s, %s", self.idx, ex)
                if self._attr_available is not False:
                    self._attr_available = False
                    updated = True
        elif self._attr_available is not False:
            _LOGGER.debug("%s is not available", self.idx)
            self._attr_available = False
            updated = True

        # Only update the HA state if state has updated.
        if updated:
            self.async_write_ha_state()


class RDTechUMScreenBrightness(RDTechUMNumber):
    _attr_name = "Screen Brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_max_value = 5
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RDTechUMCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "screen_brightness")

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.debug("async_set_native_value")
        if self._attr_native_value == value:
            return

        self.coordinator.screen_brightness(int(value))


class RDTechUMScreenTimeout(RDTechUMNumber):
    _attr_name = "Screen Timeout"
    _attr_icon = "mdi:timer-outline"
    _attr_native_max_value = 9
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RDTechUMCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "screen_timeout")

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.debug("async_set_native_value")
        if self._attr_native_value == value:
            return

        self.coordinator.screen_timeout(int(value))


class RDTechUMRecordingThreshold(RDTechUMNumber):
    _attr_name = "Recording Threshold"
    _attr_native_step = 0.01
    _attr_native_max_value = 0.3
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RDTechUMCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "record_intensity_threshold")

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.debug("async_set_native_value")
        if self._attr_native_value == value:
            return

        self.coordinator.data_threshold(int(value * 1000))
