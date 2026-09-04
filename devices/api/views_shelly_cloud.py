#######################################
# devices/api/views_shelly_cloud.py
#######################################

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from devices.services_shelly_cloud import ShellyCloudService

logger = logging.getLogger("devices.api.shelly_cloud")


class ShellyCloudTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_key = request.data.get("auth_key")
        server_url = request.data.get("server_url")

        if not auth_key:
            return Response(
                {"success": False, "error": "auth_key ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        res = ShellyCloudService.test_connection(auth_key, server_url)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)


class ShellyCloudImportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_key = request.data.get("auth_key")
        server_url = request.data.get("server_url")
        home_id = request.data.get("home_id")

        if not auth_key:
            return Response(
                {"success": False, "error": "auth_key ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        home = None
        if home_id:
            home = user.homes.filter(id=home_id).first()
        if not home:
            home = user.homes.first()

        if not home:
            return Response(
                {"success": False, "error": "Kein Zuhause (Home) für diesen Benutzer gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        res = ShellyCloudService.import_all_devices(home, auth_key, server_url)
        http_status = status.HTTP_200_OK if res.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(res, status=http_status)
