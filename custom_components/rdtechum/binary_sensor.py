"""
Created on 15 Dec 2022

@author: rogier
"""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
    """Set up the BenQ Projector media player."""
    coordinator: RDTechUMCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    entities.append(
        RDTechUMBinarySensor(
            coordinator, "record_enabled", "Recording", None, "mdi:record"
        )
    )

    async_add_entities(entities)


class RDTechUMBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_available = False

    _attr_is_on = None

    def __init__(
        self,
        coordinator: RDTechUMCoordinator,
        idx: str,
        name: str,
        device_class: str = None,
        icon=None,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.address}-{idx}"

        self.idx = idx
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_icon = icon

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if self.coordinator.data and self.idx in self.coordinator.data:
            self._attr_is_on = self.coordinator.data[self.idx]
            self._attr_available = True
            self.async_write_ha_state()
        else:
            _LOGGER.debug("%s is not available", self.idx)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated = False

        if self.coordinator.data and self.idx in self.coordinator.data:
            new_state = self.coordinator.data[self.idx]
            if self._attr_is_on != new_state:
                self._attr_is_on = new_state
                updated = True

            if self._attr_available is not True:
                self._attr_available = True
                updated = True
        elif self._attr_available is not False:
            _LOGGER.debug("%s is not available", self.command)
            self._attr_available = False
            updated = True

        # Only update the HA state if state has updated.
        if updated:
            self.async_write_ha_state()
