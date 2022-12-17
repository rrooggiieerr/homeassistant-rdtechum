"""
Created on 11 Dec 2022

@author: Rogier van Staveren
"""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyummeter.ummeter import UMmeter

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

    entities_config = [
        ["voltage", "Voltage", SensorDeviceClass.VOLTAGE, None, "V", None],
        ["intensity", "Current", SensorDeviceClass.CURRENT, None, "A", None],
        ["power", "Power", SensorDeviceClass.POWER, None, "W", None],
        ["resistance", "Resistance", None, "mdi:resistor", "Ω", None],
        [
            "temperature_celsius",
            "Temperature",
            SensorDeviceClass.TEMPERATURE,
            None,
            "°C",
            EntityCategory.DIAGNOSTIC,
        ],
        [
            "usb_voltage_dp",
            "USB D+ Voltage",
            SensorDeviceClass.VOLTAGE,
            None,
            "V",
            None,
        ],
        [
            "usb_voltage_dn",
            "USB D- Voltage",
            SensorDeviceClass.VOLTAGE,
            None,
            "V",
            None,
        ],
        [
            "record_duration",
            "Recording Duration",
            SensorDeviceClass.DURATION,
            None,
            None,
            None,
        ],
        ["record_capacity_threshold", "Recorded Capacity", None, None, "Ah", None],
        [
            "record_energy_threshold",
            "Recorded Energy",
            SensorDeviceClass.ENERGY,
            None,
            "Wh",
            None,
        ],
    ]
    for entity_config in entities_config:
        entities.append(
            RDTechUMNumericSensor(
                coordinator,
                entity_config[0],
                entity_config[1],
                entity_config[2],
                entity_config[3],
                entity_config[4],
                entity_config[5],
            )
        )

    entities.append(RDTechUMChargingModeSensor(coordinator))

    for i in range(0, 10):
        entities.append(
            RDTechUMDataGroupSensor(
                coordinator,
                i,
                "capacity",
                f"Data Group {i} Capacity",
                None,
                None,
                "Ah",
            )
        )
        entities.append(
            RDTechUMDataGroupSensor(
                coordinator,
                i,
                "energy",
                f"Data Group {i} Energy",
                SensorDeviceClass.ENERGY,
                None,
                "Wh",
            )
        )

    async_add_entities(entities)


class RDTechUMSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_available = False

    _attr_native_value = None

    def __init__(
        self,
        coordinator: RDTechUMCoordinator,
        idx,
        name: str,
        device_class: str = None,
        icon: str = None,
        unit_of_measurement: str = None,
        entity_category=None,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.address}-{idx}"

        self.idx = idx
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_entity_category = entity_category

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if self.coordinator.data and self.idx in self.coordinator.data:
            self._attr_native_value = self.coordinator.data[self.idx]
            self._attr_available = True
            self.async_write_ha_state()
        else:
            _LOGGER.debug("%s is not available", self.idx)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated = False

        if self.coordinator.data and self.idx in self.coordinator.data:
            new_value = self.coordinator.data[self.idx]
            if self._attr_native_value != new_value:
                self._attr_native_value = new_value
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


class RDTechUMNumericSensor(RDTechUMSensor):
    _attr_state_class = SensorStateClass.MEASUREMENT


class RDTechUMChargingModeSensor(RDTechUMSensor):
    # _attr_options = [item[0] for item in UMmeter._CHARGING_MODE.items()]
    _attr_options = [item[1] for item in UMmeter._CHARGING_MODE.items()]

    def __init__(self, coordinator: RDTechUMCoordinator):
        """Pass coordinator to CoordinatorEntity."""
        # super().__init__(coordinator, idx, "charging_mode", "Charging Mode")
        super().__init__(coordinator, "charging_mode_full", "Charging Mode")


class RDTechUMDataGroupSensor(RDTechUMNumericSensor):
    entity_registry_enabled_default = False

    def __init__(
        self,
        coordinator: RDTechUMCoordinator,
        idx,
        idx2,
        name: str,
        device_class: str = None,
        icon: str = None,
        unit_of_measurement: str = None,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(
            coordinator, idx, name, device_class, icon, unit_of_measurement
        )

        self._attr_unique_id = f"{coordinator.address}-datagroup{idx}-{idx2}"
        self.idx2 = idx

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if self.coordinator.data and "data_group" in self.coordinator.data:
            self._attr_native_value = self.coordinator.data["data_group"][self.idx][
                self.idx2
            ]
            self._attr_available = True
            self.async_write_ha_state()
        else:
            _LOGGER.debug("Data group %s %s is not available", self.idx, self.idx2)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        updated = False

        if self.coordinator.data and "data_group" in self.coordinator.data:
            new_value = self.coordinator.data["data_group"][self.idx][self.idx2]
            if self._attr_native_value != new_value:
                self._attr_native_value = new_value
                updated = True

            if self._attr_available is not True:
                self._attr_available = True
                updated = True
        elif self._attr_available is not False:
            _LOGGER.debug("Data group %s %s is not available", self.command)
            self._attr_available = False
            updated = True

        # Only update the HA state if state has updated.
        if updated:
            self.async_write_ha_state()
