##################################
# integrations/views_monitoring.py
##################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.core.cache import cache

from core.models import Tenant
from django.conf import settings

from market.services_price_analysis import get_price_insights
from market.services_validation import validate_spot_prices

from forecast.services_weather_monitoring import validate_weather_data
from forecast.services_forecast_accuracy import calculate_forecast_accuracy
from forecast.services_bias import calculate_bias


class EnergyHealthView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        try:
            now = timezone.now()
            result = {}

            # =========================
            # ⚡ ENERGY STREAM MONITOR
            # =========================

            meter_ids = cache.get("energy:meters") or []

            for meter_id in meter_ids:
                ts_str = cache.get(f"energy:last_event:{meter_id}")
                power = cache.get(f"energy:last_power:{meter_id}")

                if not ts_str:
                    result[meter_id] = {"status": "error", "reason": "no-data"}
                    continue

                ts = timezone.datetime.fromisoformat(ts_str)
                diff = (now - ts).total_seconds()

                if diff < 30:
                    status = "ok"
                elif diff < 90:
                    status = "warning"
                else:
                    status = "error"

                if power is not None and power == 0 and diff < 30:
                    status = "warning"

                result[meter_id] = {
                    "last_event_seconds_ago": diff,
                    "power": power,
                    "status": status,
                }

            # =========================
            # 💰 SPOT PRICE MONITOR
            # =========================

            spot_update = cache.get("spot:last_update")
            spot_success = cache.get("spot:last_success")
            spot_ready = cache.get("spot:ready")

            if not spot_update:
                result["spot"] = {"status": "error", "reason": "never-loaded"}
            else:
                ts = timezone.datetime.fromisoformat(spot_update)

                last_day = ts.date()
                today = now.date()

                before_release_window = now.hour < 13 or (
                    now.hour == 13 and now.minute <= 30
                )

                if last_day < today:
                    if before_release_window:
                        status = "ok"
                    else:
                        status = "error"
                else:
                    status = "ok"

                if spot_success is False:
                    status = "warning"

                if spot_ready:
                    status = "ok"

                result["spot"] = {
                    "last_update": ts.isoformat(),
                    "status": status,
                }

            # =========================
            # ✅ SPOT VALIDATION (NEU)
            # =========================

            try:
                result["spot_validation"] = validate_spot_prices()
            except Exception as e:
                result["spot_validation"] = {"status": "error", "exception": str(e)}

            # =========================
            # 📊 SPOT ANALYSIS
            # =========================

            try:
                result["spot_analysis"] = get_price_insights()
            except Exception as e:
                result["spot_analysis"] = {"status": "error", "exception": str(e)}

            # =========================
            # 🌦️ WEATHER MONITORING
            # =========================

            try:
                tenant = Tenant.objects.first()
                print("VIEW DEBUG:", tenant, type(tenant))  # Debug

                print("VIEW DEBUG → tenant:", tenant)
                print("VIEW DEBUG → type:", type(tenant))

                if tenant is None:
                    result["weather"] = {"status": "error", "reason": "no-tenant"}

                result["weather"] = validate_weather_data(tenant)
            except Exception as e:
                result["weather"] = {"status": "error", "exception": str(e)}

            # =========================
            # 🎯 FORECAST ACCURACY
            # =========================

            try:
                result["forecast_accuracy"] = calculate_forecast_accuracy(
                    tenant,
                    start_date=now.date(),
                    end_date=now.date(),
                )
            except Exception as e:
                result["forecast_accuracy"] = {"status": "error", "exception": str(e)}

            # =========================
            # 🎯 FORECAST bias
            # =========================
            try:
                from datetime import date, timedelta

                today = date.today()
                start = today - timedelta(days=2)

                result["forecast_bias"] = calculate_bias(
                    tenant,
                    start_date=start,
                    end_date=today,
                )
            except Exception as e:
                result["forecast_bias"] = {"status": "error", "exception": str(e)}

            # ✅ WICHTIG
            return Response(result)

        except Exception as e:
            return Response({"status": "error", "exception": str(e)})
