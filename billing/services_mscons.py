"""
billing/services_mscons.py

Standardisierte Marktkommunikations-Bridge (EDIFACT / MSCONS) gem. BNetzA-Vorgaben.
Unterstützt das Format MSCONS:D:04B:UN:EAN008 für 15-Minuten-Lastgänge (OBIS 1.8.0 Bezug & 2.8.0 Einspeisung).
Ermöglicht den Im- und Export von Zähler- und Community-Messdaten für Verteilnetzbetreiber (VNB) und Messstellenbetreiber (wMSB).
"""

import re
import uuid
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, time
from django.utils import timezone
from django.db import transaction

from core.models import Tenant, Meter, AggregatedReading, IntervalReading

logger = logging.getLogger(__name__)


# =========================================================================
# 1. EDIFACT / MSCONS GENERATOR (EXPORT)
# =========================================================================

def format_edifact_dtm(dt: datetime, format_code: str = "203") -> str:
    """Formatiert datetime in EDIFACT DTM Format (203: CCYYMMDDHHMM)."""
    if timezone.is_aware(dt):
        dt = timezone.localtime(dt)
    return dt.strftime("%Y%m%d%H%M")


def escape_edifact(val: str) -> str:
    """Escaped Sonderzeichen in EDIFACT (: -> ?:)."""
    return str(val).replace("?", "??").replace(":", "?:").replace("'", "?'").replace("+", "?+")


def generate_community_mscons_export(
    tenant: Tenant,
    period_start: date,
    period_end: date,
    obis_codes: list[str] = None,
    sender_mp_id: str = "9901234567890",
    receiver_mp_id: str = "9909876543210",
    document_number: str = None,
) -> str:
    """
    Erzeugt einen standardkonformen BNetzA EDIFACT / MSCONS Datenstrom für alle Zähler einer Energy Community.
    """
    if obis_codes is None:
        obis_codes = ["1.8.0", "2.8.0"]

    start_dt = timezone.make_aware(datetime.combine(period_start, time.min))
    end_dt = timezone.make_aware(datetime.combine(period_end, time.max))

    now_dt = timezone.localtime()
    msg_ref = str(uuid.uuid4())[:14].replace("-", "").upper()
    doc_nr = document_number or f"MSCONS-{tenant.id}-{now_dt.strftime('%Y%m%d%H%M')}"

    segments = []

    # 1. UNA Segment (Service String Advice)
    segments.append("UNA:+.? '")

    # 2. UNB Segment (Interchange Header)
    unb_date = now_dt.strftime("%y%m%d")
    unb_time = now_dt.strftime("%H%M")
    segments.append(f"UNB+UNOC:3+{sender_mp_id}:500+{receiver_mp_id}:500+{unb_date}:{unb_time}+{msg_ref}++MSCONS'")

    # 3. UNH Segment (Message Header)
    segments.append("UNH+1+MSCONS:D:04B:UN:EAN008'")

    # 4. BGM Segment (Beginning of Message: E03 = Lastgang/Messwerte)
    segments.append(f"BGM+E03+{doc_nr}+9'")

    # 5. DTM Segment (Dokumentenerstellungsdatum)
    segments.append(f"DTM+137:{format_edifact_dtm(now_dt)}:203'")

    # 6. NAD Segmente (Marktpartner: MS = Sender, MR = Empfänger)
    segments.append(f"NAD+MS+{sender_mp_id}::293'")
    segments.append(f"NAD+MR+{receiver_mp_id}::293'")

    # 7. RFF Segment (BNetzA Prüfidentifikator für MSCONS Lastgang)
    segments.append("RFF+Z13:13002'")

    # 8. Zähler und Messwerte durchlaufen
    meters = Meter.objects.filter(tenant=tenant, removed_at__isnull=True).order_by("serial_number")
    line_item_nr = 1

    for meter in meters:
        malo_id = meter.serial_number or f"DE{str(meter.id)[:31].upper()}"

        for obis in obis_codes:
            # 15-Minuten Aggregierte Ablesungen holen
            readings = AggregatedReading.objects.filter(
                meter=meter,
                obis_code=obis,
                period_start__gte=start_dt,
                period_start__lte=end_dt,
            ).order_by("period_start")

            if not readings.exists():
                continue

            # LOC (Marktlokation / Zählpunkt)
            segments.append(f"LOC+172+{escape_edifact(malo_id)}'")

            # DTM (Messzeitraum von / bis)
            first_start = readings.first().period_start
            last_end = readings.last().period_end or readings.last().period_start
            segments.append(f"DTM+163:{format_edifact_dtm(first_start)}:203'")
            segments.append(f"DTM+164:{format_edifact_dtm(last_end)}:203'")

            # LIN (Positionsnummer)
            segments.append(f"LIN+{line_item_nr}'")
            line_item_nr += 1

            # PIA (OBIS Kennzahl, z. B. 1-1?:1.8.0:SRX)
            pia_obis = f"1-1?:{escape_edifact(obis)}:SRX"
            segments.append(f"PIA+5+{pia_obis}'")

            # QTY + DTM Werte-Schleife für 15m Intervalle
            for r in readings:
                val_str = f"{float(r.value):.3f}"
                unit_code = "KWH" if (r.unit or "kWh").upper() == "KWH" else "KWH"
                segments.append(f"QTY+220:{val_str}:{unit_code}'")
                segments.append(f"DTM+163:{format_edifact_dtm(r.period_start)}:203'")

    # 9. UNT Segment (Message Trailer)
    # UNT zählt alle Segmente von UNH bis UNT (ohne UNA und UNB)
    seg_count = len(segments) - 1  # abzüglich UNA
    segments.append(f"UNT+{seg_count}+1'")

    # 10. UNZ Segment (Interchange Trailer)
    segments.append(f"UNZ+1+{msg_ref}'")

    return "\n".join(segments)


# =========================================================================
# 2. EDIFACT / MSCONS PARSER & INGEST (IMPORT)
# =========================================================================

def parse_mscons_payload(edi_content: str) -> list[dict]:
    """
    Parst einen eingehenden MSCONS-Datenstrom und extrahiert Zählpunkte, OBIS-Codes und 15m-Messwerte.
    """
    raw_segments = [s.strip() for s in edi_content.replace("\r", "").replace("\n", "").split("'") if s.strip()]
    
    extracted_records = []
    current_malo_id = None
    current_obis = "1.8.0"
    current_unit = "kWh"
    current_qty = None

    for seg in raw_segments:
        if seg.startswith("UNA"):
            continue

        parts = seg.split("+")
        tag = parts[0]

        # LOC: Zählpunkt / Marktlokation
        if tag == "LOC" and len(parts) >= 3:
            loc_id = parts[2].replace("?:", ":").replace("??", "?")
            current_malo_id = loc_id

        # PIA: OBIS Kennzahl
        elif tag == "PIA" and len(parts) >= 3:
            item_ident = parts[2]
            # Format: 1-1?:1.8.0:SRX oder 1.8.0
            obis_match = re.search(r"(\d+\.\d+\.\d+)", item_ident)
            if obis_match:
                current_obis = obis_match.group(1)

        # QTY: Messwert
        elif tag == "QTY" and len(parts) >= 2:
            qty_part = parts[1].split(":")
            if len(qty_part) >= 2:
                try:
                    current_qty = Decimal(qty_part[1])
                    if len(qty_part) >= 3:
                        current_unit = qty_part[2]
                except (InvalidOperation, ValueError):
                    current_qty = None

        # DTM: Zeitstempel zum Messwert
        elif tag == "DTM" and len(parts) >= 2:
            dtm_part = parts[1].split(":")
            if len(dtm_part) >= 2 and current_qty is not None and current_malo_id is not None:
                dt_qualifier = dtm_part[0]
                dt_val = dtm_part[1]
                
                # 163 = Start-Zeitpunkt des Intervalls
                if dt_qualifier in ("163", "203", "324"):
                    try:
                        # CCYYMMDDHHMM
                        if len(dt_val) >= 12:
                            dt = datetime.strptime(dt_val[:12], "%Y%m%d%H%M")
                            aware_dt = timezone.make_aware(dt)
                            extracted_records.append({
                                "malo_id": current_malo_id,
                                "obis_code": current_obis,
                                "period_start": aware_dt,
                                "value": current_qty,
                                "unit": current_unit,
                            })
                    except ValueError as ex:
                        logger.warning("Ungültiges Datum im DTM Segment: %s (%s)", dt_val, ex)

    return extracted_records


@transaction.atomic
def import_mscons_to_database(tenant: Tenant, edi_content: str) -> dict:
    """
    Parst eine empfangene MSCONS-Datei und speichert die Messwerte direkt in core.AggregatedReading.
    Ordnet Zähler anhand der serial_number oder ID zu.
    """
    parsed_records = parse_mscons_payload(edi_content)
    if not parsed_records:
        return {
            "success": False,
            "imported_count": 0,
            "message": "Keine validen Messwerte in der MSCONS-Datei gefunden.",
        }

    imported_count = 0
    unknown_meters = set()
    meters_cache = {}

    for item in parsed_records:
        malo_id = item["malo_id"]
        
        if malo_id not in meters_cache:
            # Suche Zähler nach serial_number oder ID
            meter = Meter.objects.filter(
                tenant=tenant,
                serial_number__iexact=malo_id,
            ).first()
            if not meter:
                # Suche nach Teilstring oder ID
                meter = Meter.objects.filter(tenant=tenant).filter(
                    serial_number__icontains=malo_id
                ).first()
            meters_cache[malo_id] = meter

        meter = meters_cache[malo_id]
        if not meter:
            unknown_meters.add(malo_id)
            continue

        AggregatedReading.objects.update_or_create(
            meter=meter,
            period_start=item["period_start"],
            obis_code=item["obis_code"],
            defaults={
                "tenant": tenant,
                "value": item["value"],
                "unit": item["unit"],
            },
        )
        imported_count += 1

    return {
        "success": True,
        "imported_count": imported_count,
        "unknown_meters": list(unknown_meters),
        "message": f"{imported_count} Messwerte erfolgreich aus MSCONS-Datei importiert.",
    }


def import_obis_json_readings(tenant: Tenant, readings: list) -> dict:
    """
    Importiert eine Liste von 15-Minuten-OBIS-Readings (JSON) von einem wMSB oder Smart Meter Gateway.
    Unterstützt Standard-Formate von inexogy, Solandeo, Discovergy und Smart Meter Gateways.
    """
    if not isinstance(readings, list) or not readings:
        return {
            "success": False,
            "imported_count": 0,
            "message": "Keine Messwert-Liste übergeben.",
        }

    imported_count = 0
    unknown_meters = set()
    meters_cache = {}

    for item in readings:
        if not isinstance(item, dict):
            continue

        malo_id = str(item.get("meter_serial") or item.get("malo_id") or item.get("serial_number") or "").strip()
        if not malo_id:
            continue

        ts_str = item.get("ts_start") or item.get("timestamp") or item.get("period_start")
        if not ts_str:
            continue

        try:
            if isinstance(ts_str, datetime):
                period_start = ts_str
            else:
                period_start = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
            if timezone.is_naive(period_start):
                period_start = timezone.make_aware(period_start)
        except Exception:
            continue

        obis = str(item.get("obis") or item.get("obis_code") or "1.8.0").strip()
        try:
            val = Decimal(str(item.get("value_kwh") if item.get("value_kwh") is not None else item.get("value", 0)))
        except (InvalidOperation, TypeError):
            continue

        if malo_id not in meters_cache:
            meter = Meter.objects.filter(
                tenant=tenant,
                serial_number__iexact=malo_id,
            ).first()
            if not meter:
                meter = Meter.objects.filter(tenant=tenant).filter(
                    serial_number__icontains=malo_id
                ).first()
            meters_cache[malo_id] = meter

        meter = meters_cache[malo_id]
        if not meter:
            unknown_meters.add(malo_id)
            continue

        AggregatedReading.objects.update_or_create(
            meter=meter,
            period_start=period_start,
            obis_code=obis,
            defaults={
                "tenant": tenant,
                "value": val,
                "unit": item.get("unit", "kWh"),
            },
        )
        imported_count += 1

    return {
        "success": True,
        "imported_count": imported_count,
        "unknown_meters": list(unknown_meters),
        "message": f"{imported_count} 15m-OBIS-Messwerte erfolgreich eingelesen.",
    }

