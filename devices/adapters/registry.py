"""
devices/adapters/registry.py

Zentrale Adapter-Registry für alle Wechselrichter- und Speicher-Hersteller.
Ermöglicht Plug-and-Play Hinzufügen, Entfernen oder Austauschen von Herstellern.
"""

import logging
from typing import Dict, Optional, List, Type
from devices.adapters.contracts import BaseInverterAdapter
from devices.adapters.sungrow import SungrowAdapter
from devices.adapters.growatt import GrowattAdapter
from devices.adapters.declarative import DeclarativeProfileAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Singleton Registry für Wechselrichter-Adapter.
    """
    _adapters: Dict[str, BaseInverterAdapter] = {}

    @classmethod
    def register(cls, adapter: BaseInverterAdapter):
        """
        Registriert einen Adapter unter seiner profile_id.
        """
        cls._adapters[adapter.profile_id] = adapter
        logger.debug("Registered Inverter Adapter: %s (%s)", adapter.profile_id, adapter.name)

    @classmethod
    def get(cls, profile_id: str) -> BaseInverterAdapter:
        """
        Liefert den passenden Adapter für ein Profil.
        Falls kein dedizierter Python-Adapter vorliegt, wird ein DeclarativeProfileAdapter geladen.
        """
        if profile_id in cls._adapters:
            return cls._adapters[profile_id]

        # Dynamischer Fallback auf deklaratives JSON/YAML-Profil
        from devices.services_profile_runner import load_profile
        profile_data = load_profile(profile_id)
        adapter = DeclarativeProfileAdapter(profile_data)
        cls._adapters[profile_id] = adapter
        return adapter

    @classmethod
    def list_available(cls) -> List[dict]:
        """
        Liefert alle registrierten und deklarativen Profile.
        """
        from devices.services_profile_runner import list_available_profiles
        return list_available_profiles()


# Standard-Adapter initial registrieren
AdapterRegistry.register(SungrowAdapter())
AdapterRegistry.register(GrowattAdapter())


def get_adapter(profile_id: str) -> BaseInverterAdapter:
    return AdapterRegistry.get(profile_id)


def register_adapter(adapter: BaseInverterAdapter):
    AdapterRegistry.register(adapter)


def list_adapters() -> List[dict]:
    return AdapterRegistry.list_available()
