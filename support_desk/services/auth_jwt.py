###################################
# support_desk/services/auth_jwt.py
###################################

import base64
import hashlib
import hmac
import json
import time
from typing import Optional, Tuple, Dict, Any
from django.conf import settings
from django.core.exceptions import ValidationError

from support_desk.models import SupportProjectConfig


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(s: str) -> bytes:
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s.encode("utf-8"))


def generate_support_jwt(
    project_key: str,
    user_id: str,
    email: str,
    name: str = "",
    expires_in_seconds: int = 86400 * 7, # 7 days
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generates an HMAC-SHA256 JWT for external client authentication (e.g. for testing or issuance).
    """
    config = SupportProjectConfig.objects.filter(project_key=project_key).first()
    secret = config.secret_key if config and config.secret_key else getattr(settings, "SUPPORT_SHARED_SECRET", "sharegy-factofy-default-secret-2026")

    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": f"support-hub-{project_key}",
        "project": project_key,
        "sub": str(user_id),
        "email": str(email),
        "name": str(name),
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def verify_support_jwt(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Verifies an incoming JWT token and returns (is_valid, payload, error_message).
    """
    if not token or not isinstance(token, str):
        return False, None, "Token missing or invalid format"

    parts = token.strip().split(".")
    if len(parts) != 3:
        return False, None, "Invalid JWT structure (must have 3 parts)"

    encoded_header, encoded_payload, encoded_signature = parts

    try:
        header_bytes = _base64url_decode(encoded_header)
        header = json.loads(header_bytes.decode("utf-8"))
        if header.get("alg") != "HS256":
            return False, None, f"Unsupported algorithm: {header.get('alg')}"

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception as e:
        return False, None, f"Failed to decode token segments: {str(e)}"

    # Check Expiration
    exp = payload.get("exp")
    if exp and int(exp) < int(time.time()):
        return False, None, "Token has expired"

    # Identify project secret
    project_key = payload.get("project") or "sharegy"
    config = SupportProjectConfig.objects.filter(project_key=project_key, is_active=True).first()
    secret = config.secret_key if config and config.secret_key else getattr(settings, "SUPPORT_SHARED_SECRET", "sharegy-factofy-default-secret-2026")

    # Verify Signature
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(encoded_signature)

    if not hmac.compare_digest(expected_signature, actual_signature):
        return False, None, "Invalid token signature"

    return True, payload, None

