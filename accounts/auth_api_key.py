#############################
# accounts/auth_api_key.py
#############################

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class APIKeyOrTokenAuthentication(BaseAuthentication):
    """
    Authentifiziert Requests via:
    1. Header: `X-API-Key: <token>`
    2. Header: `Authorization: Bearer <token>` oder `Authorization: Token <token>`
    3. Query-Parameter: `?api_key=<token>` (optional für Grafana-Datasource Pings)

    Der Token wird gegen:
    - Home.mqtt_token (Home-spezifischer Schlüssel)
    - User Token / Username
    geprüft.
    """

    def authenticate(self, request):
        token = None

        # 1. Check X-API-Key Header
        api_key_header = request.headers.get("X-API-Key") or request.META.get("HTTP_X_API_KEY")
        if api_key_header:
            token = api_key_header.strip()

        # 2. Check Authorization Header (Bearer / Token)
        if not token:
            auth_header = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION")
            if auth_header:
                parts = auth_header.strip().split()
                if len(parts) == 2 and parts[0].lower() in ["bearer", "token", "apikey"]:
                    token = parts[1]

        # 3. Check Query-Parameter (nur explizites 'api_key', um Konflikte mit magic token zu verhindern)
        if not token:
            token = request.GET.get("api_key")

        if not token:
            return None  # Keine Token-Auth versucht -> andere Auth-Klassen dürfen greifen

        from django.contrib.auth import get_user_model
        from django.db.models import Q
        from devices.models import Home

        User = get_user_model()

        # Match against Home mqtt_token, mqtt_password, or mqtt_username
        home = Home.objects.filter(
            Q(mqtt_token__iexact=token) | Q(mqtt_password__iexact=token) | Q(mqtt_username__iexact=token)
        ).select_related("user").first()
        if home and home.user and home.user.is_active:
            return (home.user, token)

        # Match against User username/email if token matches in dev/demo
        user = User.objects.filter(
            Q(username__iexact=token) | Q(email__iexact=token),
            is_active=True,
        ).first()
        if user:
            return (user, token)

        raise AuthenticationFailed("Ungültiger oder abgelaufener API-Key / Token.")

