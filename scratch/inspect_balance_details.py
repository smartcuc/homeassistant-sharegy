import os, sys, django
sys.path.insert(0, r"c:\Users\Public\Dev\eswes")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev")
django.setup()

from django.contrib.auth import get_user_model
from energy.services.balance import get_energy_balance
from devices.models import Device, DeviceMetric, DeviceMetric15m
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
for u in User.objects.all():
    try:
        bal = get_energy_balance(u, period="today")
        if bal and bal.get("kpis"):
            k = bal["kpis"]
            print(f"User: {u.username} (ID: {u.id})")
            print(f"  PV: {k.get('pv_generation_kwh')} kWh")
            print(f"  Load: {k.get('house_consumption_kwh')} kWh")
            print(f"  Grid Import: {k.get('grid_import_kwh')} kWh")
            print(f"  Grid Export: {k.get('grid_export_kwh')} kWh")
            print(f"  Battery Charge: {k.get('battery_charge_kwh')} kWh")
            print(f"  Battery Discharge: {k.get('battery_discharge_kwh')} kWh")
            print(f"  Autarky Rate: {k.get('autarky_rate')}%")
            print(f"  Self Consumption: {k.get('self_consumption_rate')}%")
            print("-" * 50)
    except Exception as e:
        print(f"Error for user {u.username}: {e}")
