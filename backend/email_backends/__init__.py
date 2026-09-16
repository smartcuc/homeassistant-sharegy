# backend/email_backends/__init__.py
from .msgraph import MSGraphEmailBackend

__all__ = ["MSGraphEmailBackend"]
