#########################################
# devices/services/export_manager.py
#########################################

import csv
import json
from io import BytesIO, StringIO
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from devices.models import (
    Device,
    MetricDefinition,
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
    DeviceLatestMetric,
)


POWER_KEYS = {"power", "value", "active_power", "p_total", "val", "w", "watt"}


def get_device_timeseries_dataset(device, range_str="24h", requested_metric=None, start_date=None, end_date=None):
    """
    Extracts timeseries points and statistics for a given device, metric, and time range.
    Supports standard periods (1h, 6h, 24h, 5d, 7d, 30d, today, yesterday) and custom date ranges.
    """
    home = getattr(device, "home", None)
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("Europe/Berlin")

    now = timezone.now().astimezone(tz)

    # 1. Determine Start & End Times + Period Label
    if start_date and end_date:
        range_str = "custom"
        try:
            sd = datetime.strptime(str(start_date).strip(), "%Y-%m-%d").date()
            ed = datetime.strptime(str(end_date).strip(), "%Y-%m-%d").date()
        except ValueError:
            sd = (now - timedelta(days=7)).date()
            ed = now.date()

        start = datetime.combine(sd, time.min, tzinfo=tz)
        end = datetime.combine(ed, time.max, tzinfo=tz)
        period_label = f"{sd.strftime('%d.%m.%Y')} - {ed.strftime('%d.%m.%Y')}"
        delta = end - start
    elif range_str == "today":
        start = datetime.combine(now.date(), time.min, tzinfo=tz)
        end = now
        period_label = f"Heute ({now.strftime('%d.%m.%Y')})"
        delta = end - start
    elif range_str == "yesterday":
        y_date = (now - timedelta(days=1)).date()
        start = datetime.combine(y_date, time.min, tzinfo=tz)
        end = datetime.combine(y_date, time.max, tzinfo=tz)
        period_label = f"Gestern ({y_date.strftime('%d.%m.%Y')})"
        delta = end - start
    elif range_str == "1h":
        delta = timedelta(hours=1)
        start = now - delta
        end = now
        period_label = "Letzte 1 Stunde"
    elif range_str == "6h":
        delta = timedelta(hours=6)
        start = now - delta
        end = now
        period_label = "Letzte 6 Stunden"
    elif range_str == "24h":
        delta = timedelta(hours=24)
        start = now - delta
        end = now
        period_label = "Letzte 24 Stunden"
    elif range_str == "5d":
        delta = timedelta(days=5)
        start = now - delta
        end = now
        period_label = "Letzte 5 Tage"
    elif range_str == "7d":
        delta = timedelta(days=7)
        start = now - delta
        end = now
        period_label = "Letzte 7 Tage"
    elif range_str == "30d":
        delta = timedelta(days=30)
        start = now - delta
        end = now
        period_label = "Letzte 30 Tage"
    else:
        delta = timedelta(hours=24)
        start = now - delta
        end = now
        period_label = f"Zeitraum ({range_str})"

    # 2. Metric Filtering & Unit Determination
    lead_key = (
        device.config.metric_definition.key
        if hasattr(device, "config") and device.config and device.config.metric_definition
        else None
    )

    effective_metric = requested_metric or lead_key or "power"
    is_power_query = (effective_metric.lower() in POWER_KEYS)

    if is_power_query:
        possible_keys = list(POWER_KEYS)
        if lead_key and lead_key in POWER_KEYS and lead_key not in possible_keys:
            possible_keys.append(lead_key)
        metric_filter = Q(metric_key__in=possible_keys) | Q(metric_key__isnull=True)
    else:
        # Exakter Filter für Nicht-Leistungs-Metriken (Temperatur, Spannung, Strom, SoC etc.)
        metric_filter = Q(metric_key=effective_metric) | Q(metric_key__iexact=effective_metric)

    # Determine Metric Unit & Display Name
    unit = "W"
    metric_display_name = effective_metric
    def_obj = MetricDefinition.objects.filter(key=effective_metric).first()
    if def_obj:
        if def_obj.name:
            metric_display_name = def_obj.name
        if def_obj.unit:
            unit = def_obj.unit

    latest_m = DeviceLatestMetric.objects.filter(device_id=device.id, metric_key=effective_metric).first()
    if latest_m and latest_m.unit:
        unit = latest_m.unit

    # 3. Model Tier Selection based on Duration
    if delta <= timedelta(hours=3):
        primary_model = DeviceMetric1m
        primary_field = "bucket"
        primary_val = "avg"
    elif delta <= timedelta(hours=24):
        primary_model = DeviceMetric5m
        primary_field = "bucket"
        primary_val = "avg"
    elif delta <= timedelta(days=7):
        primary_model = DeviceMetric15m
        primary_field = "bucket"
        primary_val = "avg"
    else:
        primary_model = DeviceMetric1h
        primary_field = "bucket"
        primary_val = "avg"

    # Query Primary Aggregation Table
    qs = list(
        primary_model.objects.filter(device_id=device.id)
        .filter(metric_filter)
        .filter(**{f"{primary_field}__gte": start, f"{primary_field}__lte": end})
        .order_by(primary_field)
    )
    field = primary_field
    value_field = primary_val

    # Multi-Tier Fallback Cascade if primary aggregation has no data
    if not qs:
        fallback_chain = [
            (DeviceMetric15m, "bucket", "avg"),
            (DeviceMetric5m, "bucket", "avg"),
            (DeviceMetric1m, "bucket", "avg"),
            (DeviceMetric, "timestamp", "value"),
        ]
        for fb_model, fb_field, fb_val in fallback_chain:
            qs = list(
                fb_model.objects.filter(device_id=device.id)
                .filter(metric_filter)
                .filter(**{f"{fb_field}__gte": start, f"{fb_field}__lte": end})
                .order_by(fb_field)
            )
            if qs:
                field = fb_field
                value_field = fb_val
                break

    # 4. Format Data Points
    points = []
    values_list = []

    for row in qs:
        dt_val = getattr(row, field)
        if timezone.is_aware(dt_val):
            dt_local = dt_val.astimezone(tz)
        else:
            dt_local = dt_val.replace(tzinfo=tz)

        raw_val = getattr(row, value_field)
        val_float = round(float(raw_val), 2) if raw_val is not None else 0.0

        min_val = getattr(row, "min", None)
        max_val = getattr(row, "max", None)
        min_float = round(float(min_val), 2) if min_val is not None else val_float
        max_float = round(float(max_val), 2) if max_val is not None else val_float

        values_list.append(val_float)
        points.append({
            "t": int(dt_local.timestamp()),
            "datetime": dt_local,
            "time_str": dt_local.strftime("%d.%m.%Y %H:%M"),
            "v": val_float,
            "min": min_float,
            "max": max_float,
        })

    # 5. Compute Statistics
    if values_list:
        min_stat = round(min(values_list), 2)
        max_stat = round(max(values_list), 2)
        avg_stat = round(sum(values_list) / len(values_list), 2)
        latest_stat = round(values_list[-1], 2)
    else:
        min_stat = 0.0
        max_stat = 0.0
        avg_stat = 0.0
        latest_stat = round(float(latest_m.value), 2) if latest_m and latest_m.value is not None else 0.0

    stats = {
        "min": min_stat,
        "max": max_stat,
        "avg": avg_stat,
        "latest": latest_stat,
        "count": len(points),
        "unit": unit,
    }

    device_name = (
        (device.config.display_name() if hasattr(device, "config") and device.config and callable(getattr(device.config, "display_name", None)) else None)
        or (device.config.name if hasattr(device, "config") and device.config and device.config.name else None)
        or getattr(device, "display_name", None)
        or device.identifier
    )

    return {
        "device": device,
        "device_id": device.id,
        "device_name": device_name,
        "device_identifier": device.identifier,
        "metric_key": effective_metric,
        "metric_name": metric_display_name,
        "unit": unit,
        "range_str": range_str,
        "period_label": period_label,
        "start": start,
        "end": end,
        "timezone": tz_name,
        "points": points,
        "stats": stats,
    }


def export_device_timeseries(user, device_id, range_str="24h", requested_metric=None, start_date=None, end_date=None, export_format="xlsx") -> HttpResponse:
    """
    Generates and returns an export file (XLSX, PDF, CSV, JSON) for a device's timeseries data.
    """
    device = get_object_or_404(
        Device.objects.select_related("home"),
        id=device_id,
    )

    dataset = get_device_timeseries_dataset(
        device=device,
        range_str=range_str,
        requested_metric=requested_metric,
        start_date=start_date,
        end_date=end_date,
    )

    device_name = dataset["device_name"]
    metric_name = dataset["metric_name"]
    unit = dataset["unit"]
    period_label = dataset["period_label"]
    points = dataset["points"]
    stats = dataset["stats"]
    tz_name = dataset["timezone"]

    export_ts_str = timezone.now().astimezone(ZoneInfo(tz_name)).strftime("%d.%m.%Y %H:%M")
    safe_dev_name = str(device.identifier).replace(" ", "_").replace("/", "-")
    safe_metric = str(dataset["metric_key"]).replace(" ", "_")
    safe_period = str(period_label).replace(".", "-").replace("/", "-").replace(" ", "_").replace(":", "-")

    filename_base = f"sharegy_geraet_{device.id}_{safe_metric}_{safe_period}"

    # 1. JSON Export
    if export_format == "json":
        payload = {
            "meta": {
                "system": "Sharegy HEMS Cloud",
                "user": user.username if user and user.is_authenticated else "anonymous",
                "exported_at": export_ts_str,
                "device_id": device.id,
                "device_name": device_name,
                "device_identifier": device.identifier,
                "metric_key": dataset["metric_key"],
                "metric_name": metric_name,
                "unit": unit,
                "period": dataset["range_str"],
                "period_label": period_label,
                "start": dataset["start"].isoformat(),
                "end": dataset["end"].isoformat(),
                "timezone": tz_name,
            },
            "statistics": stats,
            "points": [
                {
                    "timestamp": p["time_str"],
                    "epoch": p["t"],
                    "value": p["v"],
                    "min": p["min"],
                    "max": p["max"],
                }
                for p in points
            ],
        }
        resp = HttpResponse(json.dumps(payload, indent=2, ensure_ascii=False), content_type="application/json; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename_base}.json"'
        return resp

    # 2. CSV Export
    elif export_format == "csv":
        string_io = StringIO()
        writer = csv.writer(string_io, delimiter=";", lineterminator="\r\n")

        writer.writerow(["# Sharegy HEMS - Geräte-Zeitreihenexport"])
        writer.writerow(["# Gerät:", f"{device_name} ({device.identifier})"])
        writer.writerow(["# Messkanal:", f"{metric_name} [{unit}]"])
        writer.writerow(["# Zeitraum:", period_label])
        writer.writerow(["# Exportdatum:", export_ts_str])
        writer.writerow(["# Benutzer:", user.username if user and user.is_authenticated else "-"])
        writer.writerow([
            "# Statistiken:",
            f"Min: {stats['min']} {unit}",
            f"Max: {stats['max']} {unit}",
            f"Schnitt: {stats['avg']} {unit}",
            f"Aktuell: {stats['latest']} {unit}",
            f"Datenpunkte: {stats['count']}",
        ])
        writer.writerow([])

        writer.writerow([
            "Zeitpunkt",
            f"Messwert ({unit})",
            f"Minimum ({unit})",
            f"Maximum ({unit})",
        ])

        for p in points:
            writer.writerow([
                p["time_str"],
                str(p["v"]).replace(".", ","),
                str(p["min"]).replace(".", ","),
                str(p["max"]).replace(".", ","),
            ])

        csv_content = b"\xef\xbb\xbf" + string_io.getvalue().encode("utf-8")
        resp = HttpResponse(csv_content, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename_base}.csv"'
        return resp

    # 3. Excel Export (.xlsx)
    elif export_format == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.title = f"{metric_name[:20]}"
        ws.views.sheetView[0].showGridLines = True

        header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
        card_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        title_font = Font(name="Calibri", size=15, bold=True, color="1E1B4B")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        bold_font = Font(name="Calibri", size=11, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="E2E8F0"),
            right=Side(style="thin", color="E2E8F0"),
            top=Side(style="thin", color="E2E8F0"),
            bottom=Side(style="thin", color="E2E8F0"),
        )

        # Title & Meta Info
        ws["A1"] = f"Sharegy HEMS — {device_name}"
        ws["A1"].font = title_font
        ws["A2"] = f"Messkanal: {metric_name} [{unit}] | Identifikator: {device.identifier} | Zeitraum: {period_label}"
        ws["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")
        ws["A3"] = f"Exportiert am: {export_ts_str} | Benutzer: {user.username if user and user.is_authenticated else '-'}"
        ws["A3"].font = Font(name="Calibri", size=9, italic=True, color="94A3B8")

        # Stats Summary Cards (Row 5-7)
        stat_headers = ["Kennzahl", "Wert", "Einheit", "Beschreibung"]
        for col_idx, h in enumerate(stat_headers, 1):
            c = ws.cell(row=5, column=col_idx, value=h)
            c.font = header_font
            c.fill = header_fill

        stat_rows = [
            ("Minimum", stats["min"], unit, "Niedrigster erfasster Wert im Zeitraum"),
            ("Maximum", stats["max"], unit, "Höchster erfasster Wert im Zeitraum"),
            ("Durchschnitt (Ø)", stats["avg"], unit, "Arithmetischer Mittelwert"),
            ("Aktueller Wert", stats["latest"], unit, "Letzter gemessener Stand"),
            ("Messpunkte Anzahl", stats["count"], "Punkte", "Erfasste Datenpunkte im gewählten Intervall"),
        ]

        curr_row = 6
        for label, val, u_str, desc in stat_rows:
            ws.cell(row=curr_row, column=1, value=label).border = thin_border
            ws.cell(row=curr_row, column=2, value=val).border = thin_border
            ws.cell(row=curr_row, column=3, value=u_str).border = thin_border
            ws.cell(row=curr_row, column=4, value=desc).border = thin_border
            for col in range(1, 5):
                ws.cell(row=curr_row, column=col).fill = card_fill
            curr_row += 1

        curr_row += 2
        ws.cell(row=curr_row, column=1, value="Zeitreihen-Messdaten").font = Font(size=13, bold=True, color="1E1B4B")
        curr_row += 1

        # Table Header
        table_headers = ["Zeitpunkt", f"Messwert ({unit})", f"Minimum ({unit})", f"Maximum ({unit})"]
        for col_idx, h in enumerate(table_headers, 1):
            c = ws.cell(row=curr_row, column=col_idx, value=h)
            c.font = header_font
            c.fill = header_fill
        curr_row += 1

        for idx, p in enumerate(points):
            row_fill = zebra_fill if idx % 2 == 1 else None
            c1 = ws.cell(row=curr_row, column=1, value=p["time_str"])
            c2 = ws.cell(row=curr_row, column=2, value=p["v"])
            c3 = ws.cell(row=curr_row, column=3, value=p["min"])
            c4 = ws.cell(row=curr_row, column=4, value=p["max"])

            for cell in (c1, c2, c3, c4):
                cell.border = thin_border
                if row_fill:
                    cell.fill = row_fill
            curr_row += 1

        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 16)

        resp = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = f'attachment; filename="{filename_base}.xlsx"'
        wb.save(resp)
        return resp

    # 4. PDF Export (.pdf)
    else:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "SharegyTitle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1E1B4B"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "SharegySubtitle",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "SharegySection",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4F46E5"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "SharegyBody",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
        )

        elements = []
        elements.append(Paragraph(f"📈 Sharegy HEMS — {device_name}", title_style))
        elements.append(Paragraph(
            f"Messkanal: <b>{metric_name} [{unit}]</b> &nbsp;|&nbsp; ID: <code>{device.identifier}</code> &nbsp;|&nbsp; Zeitraum: <b>{period_label}</b><br/>"
            f"Erstellt am: {export_ts_str} &nbsp;|&nbsp; Benutzer: {user.username if user and user.is_authenticated else '-'}",
            subtitle_style,
        ))

        # KPI Summary Table
        elements.append(Paragraph("1. Statistische Kennzahlen", section_style))
        stats_table_data = [
            [
                Paragraph("<b>Statistische Kennzahl</b>", body_style),
                Paragraph("<b>Wert</b>", body_style),
                Paragraph("<b>Einheit</b>", body_style),
                Paragraph("<b>Erläuterung</b>", body_style),
            ],
            ["Minimum (Tiefstwert)", f"{stats['min']:.2f}", unit, "Niedrigster Messwert im Zeitraum"],
            ["Maximum (Spitzenwert)", f"{stats['max']:.2f}", unit, "Höchster Messwert im Zeitraum"],
            ["Durchschnitt (Ø)", f"{stats['avg']:.2f}", unit, "Arithmetischer Mittelwert"],
            ["Aktueller Wert", f"{stats['latest']:.2f}", unit, "Letzter gemessener Stand"],
            ["Anzahl Datenpunkte", f"{stats['count']}", "Punkte", "Erfasste Datenpunkte"],
        ]

        t_stats = Table(stats_table_data, colWidths=[140, 70, 60, 240])
        t_stats.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(t_stats)
        elements.append(Spacer(1, 10))

        # Timeseries Summary (First 60 points to avoid overflowing pages)
        elements.append(Paragraph(f"2. Zeitreihen-Messdaten ({min(len(points), 60)} von {len(points)} Intervallen)", section_style))
        sample_points = points[:60] if len(points) > 60 else points
        ts_table_data = [[
            Paragraph("<b>Zeitpunkt</b>", body_style),
            Paragraph(f"<b>Messwert ({unit})</b>", body_style),
            Paragraph(f"<b>Min ({unit})</b>", body_style),
            Paragraph(f"<b>Max ({unit})</b>", body_style),
        ]]
        for p in sample_points:
            ts_table_data.append([
                p["time_str"],
                f"{p['v']:.2f}",
                f"{p['min']:.2f}",
                f"{p['max']:.2f}",
            ])

        t_ts = Table(ts_table_data, colWidths=[150, 120, 120, 120])
        t_ts.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366F1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
            ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        elements.append(t_ts)

        if len(points) > 60:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(f"<i>Hinweis: Im PDF-Auszug werden die ersten 60 von insgesamt {len(points)} Datenpunkten angezeigt. Für den vollständigen Datensatz nutze bitte den Excel- (.xlsx) oder CSV-Export.</i>", body_style))

        doc.build(elements)
        resp = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename_base}.pdf"'
        return resp
