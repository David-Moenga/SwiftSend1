from django.db import connections
from django.http import JsonResponse


def health_check(request):
    try:
        connections["default"].ensure_connection()
    except Exception:
        return JsonResponse(
            {"status": "error", "database": "unreachable"},
            status=503,
        )

    return JsonResponse({"status": "ok", "database": "ok"})
