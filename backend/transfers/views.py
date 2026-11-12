from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .integrations import get_ussd_adapter
from .models import Corridor, Remittance, USSDSession, Withdrawal
from .serializers import (
    CorridorSerializer,
    QuoteSerializer,
    RemittanceCreateSerializer,
    RemittanceSerializer,
    USSDWebhookSerializer,
    WithdrawalSerializer,
)
from .services import advance_remittance, build_evidence_report, create_remittance, record_event, run_to_completion


User = get_user_model()


def mask_msisdn(value: str) -> str:
    value = (value or "").strip()
    if len(value) <= 4:
        return "*" * len(value)
    return f"{'*' * (len(value) - 4)}{value[-4:]}"


class WithdrawalListCreateView(generics.ListCreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WithdrawalDetailView(generics.RetrieveAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(owner=self.request.user)


class CorridorListView(generics.ListAPIView):
    serializer_class = CorridorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Corridor.objects.filter(is_active=True)
        send = self.request.query_params.get("send_country")
        receive = self.request.query_params.get("receive_country")
        if send:
            qs = qs.filter(send_country__iexact=send)
        if receive:
            qs = qs.filter(receive_country__iexact=receive)
        return qs


class CorridorQuoteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = QuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        corridor = get_object_or_404(Corridor, code=serializer.validated_data["corridor"], is_active=True)
        return Response(corridor.quote(serializer.validated_data["send_amount"]))


class RemittanceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RemittanceCreateSerializer
        return RemittanceSerializer

    def get_queryset(self):
        return Remittance.objects.filter(owner=self.request.user).select_related("corridor").prefetch_related("events", "ussd_sessions")

    def create(self, request, *args, **kwargs):
        serializer = RemittanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        corridor = get_object_or_404(Corridor, code=serializer.validated_data["corridor"], is_active=True)
        idempotency_key = (
            request.headers.get("Idempotency-Key")
            or request.headers.get("X-Idempotency-Key")
            or serializer.validated_data.get("idempotency_key")
            or ""
        )
        remittance, created = create_remittance(
            owner=request.user,
            corridor=corridor,
            validated=serializer.validated_data,
            idempotency_key=idempotency_key,
        )
        return Response(
            RemittanceSerializer(remittance).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RemittanceDetailView(generics.RetrieveAPIView):
    serializer_class = RemittanceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "reference"
    lookup_url_kwarg = "reference"

    def get_queryset(self):
        return Remittance.objects.filter(owner=self.request.user).select_related("corridor").prefetch_related("events", "ussd_sessions")


class RemittanceAdvanceView(APIView):
    """Pilot/validation hook: advance the E2E flow by one step (app-side/mock or configured adapters)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        remittance = get_object_or_404(Remittance, reference=reference, owner=request.user)
        remittance = advance_remittance(remittance)
        return Response(RemittanceSerializer(remittance).data)


class RemittanceValidateView(APIView):
    """Deliverable 3 hook: run the E2E corridor validation flow and return evidence."""

    permission_classes = [IsAuthenticated]

    def post(self, request, reference):
        remittance = get_object_or_404(Remittance, reference=reference, owner=request.user)
        remittance = run_to_completion(remittance)
        return Response({
            "remittance": RemittanceSerializer(remittance).data,
            "evidence_report": build_evidence_report(remittance),
        })


class RemittanceTrackView(APIView):
    """Public tracking by reference (used by Track UI / recipient)."""

    permission_classes = [AllowAny]

    def get(self, request, reference):
        remittance = get_object_or_404(
            Remittance.objects.select_related("corridor").prefetch_related("events", "ussd_sessions"),
            reference__iexact=reference,
        )
        # Minimal public view + verification refs (evidence visibility)
        data = RemittanceSerializer(remittance).data
        data["evidence_report"] = build_evidence_report(remittance)
        return Response(data)


class RemittanceEvidenceView(APIView):
    """Deliverable 3 evidence package (JSON) for a remittance."""

    permission_classes = [AllowAny]

    def get(self, request, reference):
        remittance = get_object_or_404(
            Remittance.objects.select_related("corridor").prefetch_related("events", "ussd_sessions"),
            reference__iexact=reference,
        )
        return Response(build_evidence_report(remittance))


class USSDWebhookView(APIView):
    """Deliverable 2 app-side hook: USSD gateway callback for *384# pilot flow.

    Accepts common aggregator payload shapes and returns gateway-friendly text.
    Configure the real gateway to POST here; logic/state is recorded as evidence.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        # Optional authentication/signature validation hook (configurable)
        from django.conf import settings

        cfg = getattr(settings, "SWIFTSEND_INTEGRATIONS", {}) or {}
        secret = cfg.get("ussd_webhook_secret") or getattr(settings, "USSD_WEBHOOK_SECRET", "")
        if secret:
            token = (
                request.headers.get("X-SwiftSend-Signature")
                or request.headers.get("X-Webhook-Signature")
                or request.headers.get("Authorization", "").replace("Bearer ", "").replace("Token ", "")
                or request.data.get("signature")
                or request.data.get("token")
            )
            if token != secret:
                return HttpResponse("END Invalid request.", content_type="text/plain", status=401)

        serializer = USSDWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        session_id = d.get("sessionId") or d.get("session_id") or d.get("sessionID") or "unknown"
        shortcode = d.get("serviceCode") or d.get("shortcode") or cfg.get("ussd_shortcode") or "*384#"
        msisdn = d.get("phoneNumber") or d.get("msisdn") or d.get("MSISDN") or ""
        text = d.get("text") or d.get("USSDString") or ""
        network = d.get("networkCode") or d.get("network") or ""

        session, _ = USSDSession.objects.get_or_create(
            session_external_id=session_id,
            defaults={
                "shortcode": shortcode,
                "msisdn_masked": mask_msisdn(msisdn),
                "network": network,
                "state": "start",
                "input_text": text,
            },
        )
        session.input_text = text
        session.network = network or session.network
        if msisdn and not session.msisdn_masked.strip("*"):
            session.msisdn_masked = mask_msisdn(msisdn)

        adapter = get_ussd_adapter()
        result = adapter.handle_input(session, text)
        session.state = result.get("state", session.state)
        session.last_response = result.get("text", "")
        session.status = USSDSession.Status.COMPLETED if result.get("type") == "END" else USSDSession.Status.ACTIVE

        # Link to remittance if a reference was provided (evidence hook)
        ref = result.get("reference")
        if ref:
            rem = Remittance.objects.filter(reference__iexact=ref).first()
            if rem:
                session.remittance = rem
                record_event(rem, stage="ussd_access", provider="ussd", channel="ussd",
                             external_reference=session_id, message=f"USSD {shortcode} session {session.state}",
                             payload={"msisdn_masked": session.msisdn_masked, "state": session.state})

        session.save()

        # Africa's Talking style CON/END response; also JSON for app-side testing
        wants_json = "application/json" in (request.META.get("HTTP_ACCEPT") or "") or request.query_params.get("format") == "json"
        body = f"{result.get('type', 'END')} {result.get('text', '')}"
        if wants_json:
            return Response({"session": session_id, "state": session.state, "status": session.status, "response": body, "result": result})
        return HttpResponse(body, content_type="text/plain")


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("-id")

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        data = []
        for u in users:
            data.append(
                {
                    "id": u.id,
                    "email": getattr(u, "email", ""),
                    "username": getattr(u, "username", ""),
                    "first_name": getattr(u, "first_name", ""),
                    "last_name": getattr(u, "last_name", ""),
                    "name": (u.get_full_name() or getattr(u, "email", "") or getattr(u, "username", "")),
                    "is_active": u.is_active,
                    "is_staff": u.is_staff,
                    "is_superuser": u.is_superuser,
                    "date_joined": u.date_joined.isoformat() if getattr(u, "date_joined", None) else None,
                    "last_login": u.last_login.isoformat() if getattr(u, "last_login", None) else None,
                    "roles": list(u.groups.values_list("name", flat=True)) or ["user"],
                }
            )
        return Response({"users": data, "count": len(data)})


class AdminRemittanceListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Remittance.objects.all().select_related("corridor", "owner").order_by("-created_at")

    def get(self, request, *args, **kwargs):
        remittances = self.get_queryset()[:500]
        data = []
        for r in remittances:
            data.append(
                {
                    "reference": r.reference,
                    "status": r.status,
                    "channel": r.channel,
                    "corridor_code": r.corridor.code if r.corridor else None,
                    "corridor_name": r.corridor.name if r.corridor else None,
                    "sender_name": r.sender_name,
                    "sender_country": r.sender_country,
                    "recipient_name": r.recipient_name,
                    "recipient_country": r.recipient_country,
                    "send_amount": str(r.send_amount),
                    "send_currency": r.send_currency,
                    "receive_amount": str(r.receive_amount),
                    "receive_currency": r.receive_currency,
                    "fee_amount": str(r.fee_amount),
                    "stellar_tx_hash": r.stellar_tx_hash,
                    "payout_reference": r.payout_reference,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "owner_email": getattr(r.owner, "email", None) if r.owner else None,
                }
            )
        return Response({"remittances": data, "count": len(data)})


class AdminOverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_remittances = Remittance.objects.count()
        completed = Remittance.objects.filter(status="completed").count()
        pending = Remittance.objects.exclude(status__in=["completed", "failed"]).count()
        failed = Remittance.objects.filter(status="failed").count()
        recent = Remittance.objects.order_by("-created_at")[:10]
        recent_data = []
        for r in recent:
            recent_data.append(
                {
                    "reference": r.reference,
                    "status": r.status,
                    "send_amount": str(r.send_amount),
                    "send_currency": r.send_currency,
                    "receive_amount": str(r.receive_amount),
                    "receive_currency": r.receive_currency,
                    "corridor_code": r.corridor.code if r.corridor else None,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
            )
        return Response(
            {
                "users": {"total": total_users},
                "remittances": {"total": total_remittances, "completed": completed, "pending": pending, "failed": failed},
                "recent_remittances": recent_data,
            }
        )
