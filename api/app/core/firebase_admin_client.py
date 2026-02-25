"""
Firebase Admin SDK helper utilities.
"""

import json
import base64
import os
from functools import lru_cache
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings


def _try_parse_service_account_json(raw: str) -> Optional[dict]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _resolve_project_id() -> str:
    # Prefer explicit env, else infer from service account JSON, else fall back to Google env.
    if settings.FIREBASE_PROJECT_ID:
        return settings.FIREBASE_PROJECT_ID

    raw = settings.FIREBASE_SERVICE_ACCOUNT
    data = _try_parse_service_account_json(raw) if raw else None
    if not data and settings.FIREBASE_SERVICE_ACCOUNT_B64:
        try:
            decoded = base64.b64decode(settings.FIREBASE_SERVICE_ACCOUNT_B64).decode("utf-8")
            data = _try_parse_service_account_json(decoded)
        except Exception:
            data = None
    if data and data.get("project_id"):
        return str(data["project_id"])

    return os.getenv("GOOGLE_CLOUD_PROJECT", "") or os.getenv("GCLOUD_PROJECT", "") or ""


def _build_credential() -> credentials.Base:
    service_account = settings.FIREBASE_SERVICE_ACCOUNT
    service_account_b64 = settings.FIREBASE_SERVICE_ACCOUNT_B64
    service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH

    if service_account:
        # Supports raw JSON string in env.
        cert_data = _try_parse_service_account_json(service_account)
        if cert_data:
            return credentials.Certificate(cert_data)

        # Some hosts make it easier to paste base64.
        try:
            decoded = base64.b64decode(service_account).decode("utf-8")
            cert_data = _try_parse_service_account_json(decoded)
            if cert_data:
                return credentials.Certificate(cert_data)
        except Exception:
            pass

        # If someone accidentally points FIREBASE_SERVICE_ACCOUNT to a JSON file path.
        if service_account.endswith(".json") and os.path.exists(service_account):
            return credentials.Certificate(service_account)

        raise RuntimeError(
            "Invalid FIREBASE_SERVICE_ACCOUNT. Provide raw service account JSON or base64-encoded JSON."
        )

    if service_account_b64:
        try:
            decoded = base64.b64decode(service_account_b64).decode("utf-8")
            cert_data = json.loads(decoded)
            return credentials.Certificate(cert_data)
        except Exception as exc:
            raise RuntimeError("Invalid FIREBASE_SERVICE_ACCOUNT_B64. Must be base64-encoded service account JSON.") from exc

    if service_account_path:
        try:
            return credentials.Certificate(service_account_path)
        except FileNotFoundError as exc:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_PATH points to a missing file in this environment. "
                "On Railway, prefer setting FIREBASE_SERVICE_ACCOUNT (raw JSON) instead of a file path."
            ) from exc

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
    project_id = _resolve_project_id()
    if project_id:
        options["projectId"] = project_id
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
