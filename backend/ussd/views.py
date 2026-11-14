"""USSD webhook views (Africa's Talking callbacks)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from transfers.models import USSDSession

from .handlers import handle
from .session import get_or_start_session
from .validators import normalize_phone, sanitize_text

logger = logging.getLogger(__name__)


def _get_at_config():
    cfg = getattr(settings, "SWIFTSEND_INTEGRATIONS", {}) or {}
    return {
        "username": getattr(settings, "AT_USERNAME", "") or cfg.get("at_username", "sandbox"),
        "api_key": getattr(settings, "AT_API_KEY", "") or cfg.get("at_api_key", ""),
        "shortcode": cfg.get("ussd_shortcode") or getattr(settings, "USSD_SHORTCODE", "*384#"),
        "webhook_secret": cfg.get("ussd_webhook_secret") or getattr(settings, "USSD_WEBHOOK_SECRET", ""),
    }


def _extract_payload(request):
    data = getattr(request, "data", None) or {}
    post = getattr(request, "POST", None) or {}
    def get(*keys):
        for k in keys:
            if isinstance(data, dict) and data.get(k) not in (None, ""):
                return data.get(k)
            if post.get(k) not in (None, ""):
                return post.get(k)
        return ""
    return {
        "session_id": sanitize_text(get("sessionId", "session_id", "sessionID")) or "unknown",
        "service_code": sanitize_text(get("serviceCode", "shortcode")) ,
        "phone_number": sanitize_text(get("phoneNumber", "msisdn", "MSISDN")),
        "text": sanitize_text(get("text", "USSDString")),
        "network_code": sanitize_text(get("networkCode", "network")),
    }


def _authorized(request, cfg) -> bool:
    secret = cfg.get("webhook_secret") or ""
    if not secret:
        # In sandbox/dev without secret configured, accept callbacks (still log).
        return True
    token = (
        request.headers.get("X-SwiftSend-Signature")
        or request.headers.get("X-Webhook-Signature")
        or request.headers.get("X-AT-Signature")
        or (request.headers.get("Authorization", "").replace("Bearer ", "").replace("Token ", ""))
        or (getattr(request, "data", {}) or {}).get("signature")
        or (getattr(request, "data", {}) or {}).get("token")
    )
    return token == secret


class USSDCallbackView(APIView):
    """Africa's Talking USSD callback endpoint.

    POST with sessionId, serviceCode, phoneNumber, text.
    Returns plain text with CON/END prefix (and JSON when requested for testing).
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        cfg = _get_at_config()
        payload = _extract_payload(request)
        shortcode = payload["service_code"] or cfg.get("shortcode") or "*384#"

        logger.info(
            "USSD callback received session=%s service=%s msisdn=%s text=%r network=%s",
            payload["session_id"],
            shortcode,
            "***" + payload["phone_number"][-4:] if len(payload["phone_number"]) >= 4 else "***",
            payload["text"][:80],
            payload["network_code"],
        )

        if not _authorized(request, cfg):
            logger.warning("USSD callback unauthorized session=%s", payload["session_id"])
            return HttpResponse("END Invalid request.", content_type="text/plain", status=401)

        try:
            session, _new = get_or_start_session(
                session_id=payload["session_id"],
                shortcode=shortcode,
                msisdn=payload["phone_number"],
                network=payload["network_code"],
                text=payload["text"],
            )
            raw_msisdn = normalize_phone(payload["phone_number"])
            result = handle(session, raw_msisdn, payload["text"])
            # ensure raw msisdn is never persisted
            meta = session.metadata or {}
            meta.pop("_msisdn", None)
            session.metadata = meta
            session.last_response = (result.get("text") or "")[:1000]
            if result.get("type") == "END" and session.status == USSDSession.Status.ACTIVE:
                session.status = USSDSession.Status.COMPLETED
            session.save()

            body = f"{result.get('type', 'END')} {result.get('text', '')}".strip()
            logger.info(
                "USSD callback response session=%s state=%s status=%s type=%s",
                payload["session_id"], session.state, session.status, result.get("type"),
            )

            wants_json = "application/json" in (request.META.get("HTTP_ACCEPT") or "") or request.query_params.get("format") == "json"
            if wants_json:
                return Response({
                    "session": payload["session_id"],
                    "state": session.state,
                    "status": session.status,
                    "response": body,
                    "result": result,
                })
            return HttpResponse(body, content_type="text/plain")

        except Exception:
            logger.exception("USSD callback fatal error session=%s", payload["session_id"])
            return HttpResponse("END Service temporarily unavailable. Please try again.", content_type="text/plain", status=200)
