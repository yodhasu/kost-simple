"""
Firebase Admin SDK helper utilities.
"""

import json
from functools import lru_cache
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings


def _build_credential() -> credentials.Base:
    service_account = settings.FIREBASE_SERVICE_ACCOUNT
    service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH

    if service_account:
        # Supports raw JSON string in env.
        cert_data = json.loads(service_account)
        return credentials.Certificate(cert_data)

    if service_account_path:
        return credentials.Certificate(service_account_path)

    # Fallback to Google Application Default Credentials if configured via
    # GOOGLE_APPLICATION_CREDENTIALS environment variable.
    try:
        return credentials.ApplicationDefault()
    except Exception as exc:
        raise RuntimeError(
            "Firebase Admin credentials not configured. "
            "Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_SERVICE_ACCOUNT_PATH, "
            "or configure GOOGLE_APPLICATION_CREDENTIALS."
        ) from exc


@lru_cache
def get_firebase_app() -> firebase_admin.App:
    if firebase_admin._apps:
        return firebase_admin.get_app()
    cred = _build_credential()
    options = {}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID
    return firebase_admin.initialize_app(cred, options=options or None)


def create_firebase_user(email: str, password: str, display_name: str) -> auth.UserRecord:
    get_firebase_app()
    return auth.create_user(email=email, password=password, display_name=display_name)


def get_firebase_user_by_uid(uid: str) -> Optional[auth.UserRecord]:
    get_firebase_app()
    try:
        return auth.get_user(uid)
    except auth.UserNotFoundError:
        return None


def generate_password_reset_link(email: str) -> str:
    get_firebase_app()
    return auth.generate_password_reset_link(email)


def delete_firebase_user(uid: str) -> None:
    get_firebase_app()
    auth.delete_user(uid)
