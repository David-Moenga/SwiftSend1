"""Input validation and sanitization for USSD flows."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from django.conf import settings


PHONE_RE = re.compile(r"^\+?\d{9,15}$")


def sanitize_text(value: str | None) -> str:
    if value is None:
        return ""
    # USSD text is simple; strip control chars and trim.
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", str(value))
    return cleaned.strip()


def normalize_phone(value: str | None) -> str:
    return re.sub(r"\s+", "", sanitize_text(value))


def is_valid_phone(value: str | None) -> bool:
    phone = normalize_phone(value)
    return bool(PHONE_RE.match(phone))


def mask_msisdn(value: str | None) -> str:
    phone = normalize_phone(value)
    if len(phone) <= 4:
        return "*" * len(phone)
    return f"{'*' * (len(phone) - 4)}{phone[-4:]}"


def parse_menu_choice(value: str | None) -> str:
    return sanitize_text(value)


def parse_amount_kes(value: str | None):
    """Return Decimal amount or None if invalid."""
    raw = sanitize_text(value).replace(",", "")
    if not raw or not re.fullmatch(r"\d+(?:\.\d{1,2})?", raw):
        return None
    try:
        amount = Decimal(raw)
    except (InvalidOperation, ValueError):
        return None
    return amount


def validate_amount_limits(amount: Decimal):
    """Return (ok, error_message). Limits configurable via settings/env."""
    min_amount = Decimal(str(getattr(settings, "USSD_MIN_AMOUNT_KES", "100")))
    max_amount = Decimal(str(getattr(settings, "USSD_MAX_AMOUNT_KES", "70000")))
    if amount <= 0:
        return False, "Amount must be greater than zero."
    if amount < min_amount:
        return False, f"Minimum amount is KES {min_amount}."
    if amount > max_amount:
        return False, f"Maximum amount is KES {max_amount}."
    return True, ""


def parse_reference(value: str | None) -> str:
    ref = sanitize_text(value).upper()
    if not re.fullmatch(r"[A-Z0-9-]{4,32}", ref):
        return ""
    return ref
