###############################
# core/services_validation.py
###############################

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Maximal plausibler Verbrauch/Erzeugung für ein 15-Minuten-Intervall
# (250 kWh in 15 Min entspricht 1000 kW Dauerleistung - Obergrenze für normale Anschlüsse)
MAX_15M_KWH_THRESHOLD = Decimal("250.0")

VALID_OBIS_PREFIXES = ("1.8", "2.8", "16.7", "36.7", "56.7", "76.7")


def validate_obis_reading(obis_code: str, value: Decimal, unit: str = "kWh") -> dict:
    """
    Validiert einen eintreffenden Zählerwert auf Plausibilität:
    - Verhindert negative Energiewerte
    - Prüft auf physikalisch unplausible Spitzen
    - Validiert OBIS-Präfixe
    """
    is_valid = True
    warning = None
    flags = []

    if value is None:
        return {
            "is_valid": False,
            "error": "Value cannot be null",
            "flags": ["null_value"],
        }

    # 1. Negative Energiewerte abfangen (Verbrauch / Einspeisung kann nicht negativ sein)
    if obis_code.startswith(("1.8", "2.8")) and value < Decimal("0"):
        logger.warning(
            "Plausibilitätsfehler: Negativer Energiewert empfangen. OBIS=%s, Value=%s %s",
            obis_code,
            value,
            unit,
        )
        return {
            "is_valid": False,
            "error": f"Negative energy value ({value} {unit}) for OBIS {obis_code} is not allowed.",
            "flags": ["negative_energy"],
        }

    # 2. Extremspitzen-Prüfung (Schutz vor Ingest-Überläufen / Multiplikationsfehlern)
    if obis_code.startswith(("1.8", "2.8")) and value > MAX_15M_KWH_THRESHOLD:
        logger.warning(
            "Plausibilitätswarnung: Extremwert überschritten. OBIS=%s, Value=%s %s > %s",
            obis_code,
            value,
            unit,
            MAX_15M_KWH_THRESHOLD,
        )
        warning = f"High energy reading ({value} {unit}) exceeds 15m safety threshold."
        flags.append("high_spike")

    # 3. Unbekannter OBIS-Code Check
    if not any(obis_code.startswith(prefix) for prefix in VALID_OBIS_PREFIXES):
        flags.append("unknown_obis")

    return {
        "is_valid": is_valid,
        "warning": warning,
        "flags": flags,
        "sanitized_value": value,
    }
